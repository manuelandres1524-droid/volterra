from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from apps.auth import deps
from apps.auth.session import SessionTokens
from apps.core.config import settings
from apps.core.errors import UnauthenticatedError
from apps.web import routes
from apps.web.routes import auth as web_auth
from main import app


@pytest.fixture(autouse=True)
def _cookie_secure_por_defecto(monkeypatch):
    """Aísla estos tests del `.env` local (la demo usa COOKIE_SECURE=false)."""
    monkeypatch.setattr(settings, "COOKIE_SECURE", True)


class _Query:
    def __init__(self, data=None, error=None):
        self._data = data if data is not None else []
        self._error = error

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
        if self._error is not None:
            raise self._error
        return SimpleNamespace(data=self._data)


class _FakeClient:
    def __init__(
        self,
        *,
        is_platform_admin=False,
        memberships=None,
        clubs=None,
        profiles=None,
        club_memberships=None,
    ):
        self.is_platform_admin = is_platform_admin
        self.memberships = memberships or []
        self.clubs = clubs or []
        self.profiles = profiles or []
        self.club_memberships = club_memberships or []

    def rpc(self, name):
        assert name == "fn_is_platform_admin"
        return _Query(self.is_platform_admin)

    def table(self, name):
        return _Query(
            {
                "club_memberships": self.club_memberships or self.memberships,
                "clubs": self.clubs,
                "profiles": self.profiles,
            }.get(name, [])
        )


def _authenticate(monkeypatch, client, *, is_platform_admin=False):
    async def fake_verify(_token):
        return {
            "sub": "user-1",
            "email": "demo@example.com",
            "role": "authenticated",
        }

    monkeypatch.setattr(deps, "verify_supabase_jwt_strict", fake_verify)
    monkeypatch.setattr(deps, "get_supabase_for_user", lambda _token: client)


def _csrf(client: TestClient) -> str:
    client.get("/login")
    token = client.cookies.get("volterra_csrf")
    assert token
    return token


def _cookie_header(response, name: str) -> str:
    for header in response.headers.get_list("set-cookie"):
        if header.startswith(f"{name}="):
            return header
    raise AssertionError(f"no se encontró la cookie {name}: {response.headers.get_list('set-cookie')}")


def test_login_page_sets_csrf_cookie_without_httponly():
    client = TestClient(app, base_url="https://testserver")

    response = client.get("/login")

    assert response.status_code == 200
    header = _cookie_header(response, "volterra_csrf")
    assert "HttpOnly" not in header
    assert "Secure" in header
    assert "SameSite=lax" in header


def test_login_rejects_missing_or_wrong_csrf():
    client = TestClient(app, base_url="https://testserver")
    _csrf(client)

    response = client.post(
        "/login",
        data={"email": "demo@example.com", "password": "x", "csrf_token": "incorrecto"},
    )

    assert response.status_code == 403
    assert "El formulario expiró" in response.text
    assert "volterra_access" not in client.cookies


def test_login_sets_httponly_session_cookies_and_redirects(monkeypatch):
    client = TestClient(app, base_url="https://testserver")
    token = _csrf(client)

    async def fake_sign_in(email, password):
        assert email == "demo@example.com"
        assert password == "secreto"
        return SessionTokens("access-token", "refresh-token", 3600)

    monkeypatch.setattr(web_auth, "sign_in", fake_sign_in)

    response = client.post(
        "/login",
        data={
            "email": "demo@example.com",
            "password": "secreto",
            "csrf_token": token,
            "next_url": "/clubs",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/clubs"
    access = _cookie_header(response, "volterra_access")
    refresh = _cookie_header(response, "volterra_refresh")
    assert "HttpOnly" in access and "Secure" in access
    assert "HttpOnly" in refresh and "Secure" in refresh
    assert "access-token" not in response.text


def test_login_failure_returns_401_without_session(monkeypatch):
    client = TestClient(app, base_url="https://testserver")
    token = _csrf(client)

    async def fake_sign_in(_email, _password):
        raise UnauthenticatedError("Correo o contraseña incorrectos.")

    monkeypatch.setattr(web_auth, "sign_in", fake_sign_in)

    response = client.post(
        "/login",
        data={"email": "demo@example.com", "password": "mal", "csrf_token": token},
    )

    assert response.status_code == 401
    assert "Correo o contraseña incorrectos" in response.text
    assert "volterra_access" not in client.cookies


def test_logout_requires_csrf_and_clears_session(monkeypatch):
    client = TestClient(app, base_url="https://testserver")
    token = _csrf(client)

    async def fake_revoke(_token):
        return None

    monkeypatch.setattr(web_auth, "revoke_session", fake_revoke)

    rejected = client.post("/logout", data={"csrf_token": "incorrecto"})
    assert rejected.status_code == 403

    client.cookies.set("volterra_access", "access-token")
    client.cookies.set("volterra_refresh", "refresh-token")
    response = client.post(
        "/logout",
        data={"csrf_token": token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    assert 'volterra_access=""' in _cookie_header(response, "volterra_access")
    assert 'volterra_refresh=""' in _cookie_header(response, "volterra_refresh")


def test_refresh_requires_csrf_and_refresh_cookie(monkeypatch):
    client = TestClient(app, base_url="https://testserver")
    token = _csrf(client)

    rejected = client.post("/auth/refresh", headers={"X-CSRF-Token": "incorrecto"})
    assert rejected.status_code == 403

    missing = client.post("/auth/refresh", headers={"X-CSRF-Token": token})
    assert missing.status_code == 401

    async def fake_refresh(_token):
        return SessionTokens("new-access", "new-refresh", 3600)

    monkeypatch.setattr(web_auth, "refresh_session", fake_refresh)
    client.cookies.set("volterra_refresh", "refresh-token", path="/")

    response = client.post("/auth/refresh", headers={"X-CSRF-Token": token})

    assert response.status_code == 204
    assert "new-access" in _cookie_header(response, "volterra_access")
    assert "new-refresh" in _cookie_header(response, "volterra_refresh")


def test_html_pages_redirect_to_login_when_unauthenticated():
    client = TestClient(app, base_url="https://testserver")

    response = client.get("/me", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login?next_url=/me"


def test_cookie_auth_renders_me_with_club_name(monkeypatch):
    fake = _FakeClient(
        memberships=[
            {
                "club_id": "club-1",
                "role": "coach",
                "started_at": "2026-01-01T00:00:00Z",
                "ended_at": None,
                "user_id": "user-1",
            }
        ],
        clubs=[
            {"id": "club-1", "name": "Club Demo Volterra", "city": "Bogotá", "status": "active"}
        ],
        profiles=[{"id": "user-1", "display_name": "Demo Coach"}],
    )
    _authenticate(monkeypatch, fake)
    client = TestClient(app, base_url="https://testserver")

    client.cookies.set("volterra_access", "valid-token")
    response = client.get("/me")

    assert response.status_code == 200
    assert "Demo Coach" in response.text
    assert "Club Demo Volterra" in response.text
    assert "valid-token" not in response.text


def test_platform_page_is_403_for_non_platform_admin(monkeypatch):
    fake = _FakeClient(is_platform_admin=False)
    _authenticate(monkeypatch, fake)
    client = TestClient(app, base_url="https://testserver")

    client.cookies.set("volterra_access", "valid-token")
    response = client.get("/platform")

    assert response.status_code == 403
    assert "Acceso denegado" in response.text


def test_platform_page_is_visible_for_platform_admin(monkeypatch):
    fake = _FakeClient(is_platform_admin=True)
    _authenticate(monkeypatch, fake)
    client = TestClient(app, base_url="https://testserver")

    client.cookies.set("volterra_access", "valid-token")
    response = client.get("/platform")

    assert response.status_code == 200
    assert "fn_is_platform_admin" in response.text


def test_club_page_rejects_club_outside_memberships(monkeypatch):
    fake = _FakeClient(
        memberships=[
            {
                "club_id": "club-1",
                "role": "coach",
                "started_at": "2026-01-01T00:00:00Z",
                "ended_at": None,
                "user_id": "user-1",
            }
        ]
    )
    _authenticate(monkeypatch, fake)
    client = TestClient(app, base_url="https://testserver")

    client.cookies.set("volterra_access", "valid-token")
    response = client.get("/clubs/club-2")

    assert response.status_code == 403
    assert "Acceso denegado" in response.text


def test_members_page_shows_only_returned_display_names(monkeypatch):
    fake = _FakeClient(
        memberships=[
            {
                "club_id": "club-1",
                "role": "club_admin",
                "started_at": "2026-01-01T00:00:00Z",
                "ended_at": None,
                "user_id": "user-1",
            }
        ],
        clubs=[{"id": "club-1", "name": "Club Demo", "city": "Cali", "status": "active"}],
        club_memberships=[
            {
                "id": "m1",
                "club_id": "club-1",
                "user_id": "user-1",
                "role": "club_admin",
                "started_at": "2026-01-01T00:00:00Z",
            },
            {
                "id": "m2",
                "club_id": "club-1",
                "user_id": "user-2",
                "role": "coach",
                "started_at": "2026-01-02T00:00:00Z",
            },
        ],
        profiles=[{"id": "user-1", "display_name": "Demo Admin"}],
    )
    _authenticate(monkeypatch, fake)
    client = TestClient(app, base_url="https://testserver")

    client.cookies.set("volterra_access", "valid-token")
    response = client.get("/clubs/club-1/members")

    assert response.status_code == 200
    assert "Demo Admin" in response.text
    assert "Miembro del club" in response.text
    assert "demo@example.com" not in response.text


def test_authorization_header_has_priority_over_cookie(monkeypatch):
    async def forbidden(_token):
        raise AssertionError("no debe validar el token de la cabecera malformada")

    monkeypatch.setattr(deps, "verify_supabase_jwt_strict", forbidden)
    client = TestClient(app, base_url="https://testserver")

    client.cookies.set("volterra_access", "valid-token")
    response = client.get(
        "/api/v1/me/",
        headers={"Authorization": "Token abc"},
    )

    assert response.status_code == 401


def test_api_accepts_cookie_session(monkeypatch):
    fake = _FakeClient(profiles=[{"id": "user-1", "display_name": "Demo"}])
    _authenticate(monkeypatch, fake)
    client = TestClient(app, base_url="https://testserver")

    client.cookies.set("volterra_access", "valid-token")
    response = client.get("/api/v1/me/")

    assert response.status_code == 200
    assert response.json()["display_name"] == "Demo"


def test_security_headers_include_csp_and_no_store():
    client = TestClient(app, base_url="https://testserver")

    response = client.get("/login")

    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("/me", "/me"),
        ("/clubs/club-1", "/clubs/club-1"),
        ("https://evil.example", "/me"),
        ("//evil.example", "/me"),
        ("/\\evil.example", "/me"),
        ("/me\r\nLocation: https://evil.example", "/me"),
        (None, "/me"),
    ],
)
def test_safe_next_blocks_open_redirects(value, expected):
    assert routes._safe_next(value) == expected
