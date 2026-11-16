"""Pruebas del catálogo de errores y de su traducción única a HTTP.

Comprueban dos cosas: que el estado HTTP se decide en un solo lugar y que la
misma causa produce JSON en la API y HTML en la interfaz, sin que cada ruta
tenga que traducirla.
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from apps.auth import deps
from apps.auth.deps import AuthContext, get_auth_context
from apps.core import ratelimit
from apps.core.config import settings
from apps.core.errors import (
    ConflictError,
    DomainError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
    RateLimitedError,
    UnauthenticatedError,
    UnavailableError,
    headers,
    http_status,
    title,
)
from apps.integrations.supabase.deps import get_data_client
from main import app

client = TestClient(app, base_url="https://testserver")


@pytest.fixture(autouse=True)
def _limpia_overrides():
    yield
    app.dependency_overrides.clear()


class _Query:
    def __init__(self, data=None):
        self._data = [] if data is None else data

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def is_(self, *args, **kwargs):
        return self

    def in_(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def execute(self):
        return SimpleNamespace(data=self._data)


class _FakeClient:
    def rpc(self, name, params=None):
        return _Query(False)

    def table(self, name):
        return _Query([])


def _override_auth(*, is_pa: bool = False, memberships: list[dict] | None = None) -> AuthContext:
    ctx = AuthContext(
        user_id="user-1",
        email="demo@example.com",
        is_platform_admin=is_pa,
        memberships=memberships or [],
        token="token",
    )
    app.dependency_overrides[get_auth_context] = lambda: ctx
    app.dependency_overrides[get_data_client] = lambda: _FakeClient()
    return ctx


# --- Catálogo ---------------------------------------------------------------


@pytest.mark.parametrize(
    "error, expected",
    [
        (InvalidInputError(), 400),
        (UnauthenticatedError(), 401),
        (ForbiddenError(), 403),
        (NotFoundError(), 404),
        (ConflictError(), 409),
        (RateLimitedError(30), 429),
        (UnavailableError(), 503),
        (DomainError(), 500),
    ],
)
def test_estado_http_por_codigo(error, expected):
    assert http_status(error) == expected


def test_error_desconocido_cae_en_500():
    class _Raro(DomainError):
        code = "no_registrado"

    assert http_status(_Raro()) == 500


def test_solo_el_limite_aporta_cabecera_retry_after():
    assert headers(RateLimitedError(42)) == {"Retry-After": "42"}
    assert headers(ForbiddenError()) == {}


def test_titulos_html_no_exponen_codigos():
    assert title(NotFoundError()) == "Página no encontrada"
    assert title(RateLimitedError(10)) == "Demasiados intentos"
    assert title(DomainError()) == "No se pudo completar la operación"


def test_los_mensajes_por_defecto_son_mostrables():
    for error in (
        InvalidInputError(),
        UnauthenticatedError(),
        ForbiddenError(),
        NotFoundError(),
        ConflictError(),
        UnavailableError(),
    ):
        assert error.message and error.message[0].isupper()
        assert error.message == error.default_message


# --- Traducción en la API y en la interfaz ----------------------------------


def test_api_sin_sesion_devuelve_json_con_codigo():
    response = client.get("/api/v1/me/")

    assert response.status_code == 401
    assert response.json() == {"detail": "No autenticado", "code": "unauthenticated"}


def test_pagina_sin_sesion_redirige_al_login():
    response = client.get("/me", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"].startswith("/login?next_url=")


def test_pagina_sin_permisos_muestra_error_html():
    _override_auth(is_pa=False)

    response = client.get("/platform")

    assert response.status_code == 403
    assert "Acceso denegado" in response.text
    assert "Se requiere platform_admin" in response.text


def test_api_sin_permisos_devuelve_json():
    _override_auth(is_pa=False)

    response = client.post("/api/v1/clubs", json={"name": "Club Demo"})

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Se requiere platform_admin",
        "code": "forbidden",
    }


def test_pagina_con_recurso_inexistente_muestra_404():
    _override_auth(is_pa=True)

    response = client.get("/clubs/00000000-0000-4000-8000-000000000001/edit")

    assert response.status_code == 404
    assert "Página no encontrada" in response.text


def test_limite_por_usuario_devuelve_json_con_retry_after(monkeypatch):
    # Sin override de ``get_auth_context``: el límite por usuario vive dentro de
    # esa guarda y debe ejecutarse de verdad para poder probarlo.
    async def fake_verify(_token):
        return {"sub": "user-1", "email": "demo@example.com", "role": "authenticated"}

    monkeypatch.setattr(settings, "RATE_LIMIT_READ_REQUESTS", 1)
    monkeypatch.setattr(deps, "verify_supabase_jwt_strict", fake_verify)
    monkeypatch.setattr(deps, "get_supabase_for_user", lambda _token: _FakeClient())
    ratelimit.limiter.reset()

    headers = {"Authorization": "Bearer valid-token"}

    assert client.get("/api/v1/me/", headers=headers).status_code == 200
    blocked = client.get("/api/v1/me/", headers=headers)

    assert blocked.status_code == 429
    assert blocked.json()["code"] == "rate_limited"
    assert blocked.headers["retry-after"].isdigit()


def test_limite_anonimo_usa_el_mismo_contrato(monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_ANON_WRITE_REQUESTS", 1)
    ratelimit.limiter.reset()

    assert client.post("/api/v1/clubs", json={"name": "Club Demo"}).status_code == 401
    blocked = client.post("/api/v1/clubs", json={"name": "Club Demo"})

    assert blocked.status_code == 429
    assert blocked.json()["code"] == "rate_limited"
    assert blocked.headers["retry-after"].isdigit()


# --- Composición ------------------------------------------------------------


def test_un_solo_cliente_supabase_por_peticion(monkeypatch):
    calls: list[str] = []

    async def fake_verify(_token):
        return {"sub": "user-1", "email": "demo@example.com", "role": "authenticated"}

    def fake_client(token):
        calls.append(token)
        return _FakeClient()

    monkeypatch.setattr(deps, "verify_supabase_jwt_strict", fake_verify)
    monkeypatch.setattr(deps, "get_supabase_for_user", fake_client)

    response = client.get("/api/v1/me/", headers={"Authorization": "Bearer valid-token"})

    assert response.status_code == 200
    assert calls == ["valid-token"]
