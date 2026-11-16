"""Pruebas del límite de peticiones (DEC-22).

Cubren la unidad (ventana fija, aislamiento de claves, poda) y el
comportamiento HTTP: login, escrituras anónimas y límite por usuario. No tocan
Supabase: la autenticación se sustituye por dobles de prueba.
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from apps.auth import deps
from apps.core.errors import UnauthenticatedError
from apps.core import ratelimit
from apps.core.config import settings
from apps.web.routes import auth as web_auth
from main import app


class _Clock:
    def __init__(self, now: float = 1_000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture(autouse=True)
def _entorno_limpio(monkeypatch):
    ratelimit.limiter.reset()
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_TRUST_FORWARDED_FOR", False)
    yield
    ratelimit.limiter.reset()


# --- Unidad -----------------------------------------------------------------


def test_ventana_fija_permite_hasta_el_limite_y_luego_bloquea():
    limiter = ratelimit.FixedWindowLimiter(clock=_Clock())
    limit = ratelimit.Limit(max_requests=2, window_seconds=60)

    first = limiter.check("read", "user-1", limit)
    second = limiter.check("read", "user-1", limit)
    third = limiter.check("read", "user-1", limit)

    assert (first.allowed, second.allowed, third.allowed) == (True, True, False)
    assert third.remaining == 0
    assert third.retry_after >= 1


def test_la_ventana_se_reinicia_al_expirar():
    clock = _Clock()
    limiter = ratelimit.FixedWindowLimiter(clock=clock)
    limit = ratelimit.Limit(max_requests=1, window_seconds=60)

    assert limiter.check("read", "user-1", limit).allowed is True
    assert limiter.check("read", "user-1", limit).allowed is False

    clock.advance(60)

    assert limiter.check("read", "user-1", limit).allowed is True


def test_claves_distintas_no_comparten_cupo():
    limiter = ratelimit.FixedWindowLimiter(clock=_Clock())
    limit = ratelimit.Limit(max_requests=1, window_seconds=60)

    assert limiter.check("read", "user-1", limit).allowed is True
    assert limiter.check("read", "user-2", limit).allowed is True
    assert limiter.check("write", "user-1", limit).allowed is True
    assert limiter.check("read", "user-1", limit).allowed is False


def test_la_poda_acota_el_estado_sin_crecer_sin_limite():
    clock = _Clock()
    limiter = ratelimit.FixedWindowLimiter(clock=clock, max_keys=2)
    limit = ratelimit.Limit(max_requests=5, window_seconds=10)

    for index in range(5):
        limiter.check("read", f"user-{index}", limit)
        assert len(limiter._buckets) <= 2

    clock.advance(11)
    limiter.check("read", "a", limit)
    limiter.check("read", "b", limit)

    assert len(limiter._buckets) <= 2
    assert all(expires > clock.now for _, _, expires in limiter._buckets.values())


def test_la_poda_expulsa_la_clave_mas_antigua_sin_reiniciar_el_estado():
    clock = _Clock()
    limiter = ratelimit.FixedWindowLimiter(clock=clock, max_keys=2)
    limit = ratelimit.Limit(max_requests=1, window_seconds=60)

    assert limiter.check("read", "user-0", limit).allowed is True
    clock.advance(1)
    assert limiter.check("read", "user-1", limit).allowed is True
    clock.advance(1)
    assert limiter.check("read", "user-2", limit).allowed is True

    # user-0 fue expulsada; user-1 conserva su contador y sigue bloqueada.
    assert limiter.check("read", "user-1", limit).allowed is False
    assert len(limiter._buckets) <= 2


def _request(headers=None, host="203.0.113.7", method="GET", path="/login"):
    return SimpleNamespace(
        headers=headers or {},
        client=SimpleNamespace(host=host),
        method=method,
        url=SimpleNamespace(path=path),
        cookies={},
    )


def test_ip_ignora_x_forwarded_for_por_defecto():
    request = _request(headers={"x-forwarded-for": "198.51.100.9"})

    assert ratelimit.client_ip(request) == "203.0.113.7"


def test_ip_usa_el_ultimo_valor_de_x_forwarded_for_si_se_confia(monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_TRUST_FORWARDED_FOR", True)
    request = _request(headers={"x-forwarded-for": "198.51.100.9, 203.0.113.7"})

    assert ratelimit.client_ip(request) == "203.0.113.7"


def test_ip_invalida_no_se_usa_como_clave():
    request = _request(host="no-es-una-ip")

    assert ratelimit.client_ip(request) == "unknown"


# --- HTTP -------------------------------------------------------------------


def _csrf(client: TestClient) -> str:
    client.get("/login")
    token = client.cookies.get("volterra_csrf")
    assert token
    return token


def test_login_bloquea_tras_cinco_intentos(monkeypatch):
    async def fake_sign_in(_email, _password):
        raise UnauthenticatedError("Correo o contraseña incorrectos.")

    monkeypatch.setattr(web_auth, "sign_in", fake_sign_in)
    client = TestClient(app, base_url="https://testserver")
    token = _csrf(client)

    for _ in range(settings.RATE_LIMIT_LOGIN_ATTEMPTS):
        response = client.post(
            "/login",
            data={"email": "demo@example.com", "password": "x", "csrf_token": token},
        )
        assert response.status_code == 401

    blocked = client.post(
        "/login",
        data={"email": "demo@example.com", "password": "x", "csrf_token": token},
    )

    assert blocked.status_code == 429
    assert blocked.headers["retry-after"].isdigit()
    assert "Demasiados intentos" in blocked.text
    assert "volterra_csrf" in client.cookies


def test_health_no_consume_cupo(monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_ANON_WRITE_REQUESTS", 1)
    client = TestClient(app, base_url="https://testserver")

    for _ in range(3):
        assert client.get("/health").status_code == 200


def test_escritura_anonima_se_limita_por_ip():
    client = TestClient(app, base_url="https://testserver")

    for _ in range(settings.RATE_LIMIT_ANON_WRITE_REQUESTS):
        assert client.post("/api/v1/clubs", json={"name": "Club"}).status_code == 401

    blocked = client.post("/api/v1/clubs", json={"name": "Club"})

    assert blocked.status_code == 429
    assert blocked.headers["retry-after"].isdigit()
    assert blocked.json()["detail"].startswith("Demasiadas peticiones")


def test_lectura_autenticada_se_limita_por_usuario(monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_READ_REQUESTS", 2)

    class _Query:
        def __init__(self, data):
            self._data = data

        def select(self, *args, **kwargs):
            return self

        def eq(self, *args, **kwargs):
            return self

        def is_(self, *args, **kwargs):
            return self

        def limit(self, *args, **kwargs):
            return self

        def execute(self):
            return SimpleNamespace(data=self._data)

    class _Client:
        def rpc(self, name, params=None):
            return _Query(False)

        def table(self, name):
            return _Query([])

    async def fake_verify(_token):
        return {"sub": "user-1", "email": "demo@example.com", "role": "authenticated"}

    monkeypatch.setattr(deps, "verify_supabase_jwt_strict", fake_verify)
    monkeypatch.setattr(deps, "get_supabase_for_user", lambda _token: _Client())

    client = TestClient(app, base_url="https://testserver")
    headers = {"Authorization": "Bearer valid-token"}

    assert client.get("/api/v1/me/", headers=headers).status_code == 200
    assert client.get("/api/v1/me/", headers=headers).status_code == 200
    blocked = client.get("/api/v1/me/", headers=headers)

    assert blocked.status_code == 429
    assert blocked.headers["retry-after"].isdigit()


def test_el_limite_se_puede_desactivar(monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", False)
    client = TestClient(app, base_url="https://testserver")

    for _ in range(settings.RATE_LIMIT_ANON_WRITE_REQUESTS + 2):
        assert client.post("/api/v1/clubs", json={"name": "Club"}).status_code == 401
