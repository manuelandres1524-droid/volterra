"""Pruebas HTTP de las escrituras de F1 (API JSON y formularios HTML).

Usan un cliente de datos falso: no tocan Supabase. Comprueban el contrato del
BFF —CSRF, roles, validación de entrada, mapeo de errores y redirecciones— y
dejan la autorización efectiva a las pruebas SQL de RPC/RLS.
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from postgrest.exceptions import APIError

from apps.api.v1.endpoints import clubs as clubs_endpoint
from apps.auth import deps
from apps.core.config import settings
from apps.web.routes import common as routes_common
from main import app

CLUB_ID = "00000000-0000-4000-8000-000000000001"
MEMBERSHIP_ID = "00000000-0000-4000-8000-0000000000b1"
NEW_ID = "00000000-0000-4000-8000-0000000000aa"


@pytest.fixture(autouse=True)
def _cookie_secure_por_defecto(monkeypatch):
    monkeypatch.setattr(settings, "COOKIE_SECURE", True)


class _Query:
    def __init__(self, data=None, error=None):
        self._data = [] if data is None else data
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
        club_memberships=None,
        profiles=None,
        rpc_errors=None,
    ):
        self.is_platform_admin = is_platform_admin
        self.memberships = memberships or []
        self.clubs = clubs or []
        self.club_memberships = club_memberships or []
        self.profiles = profiles or []
        self.rpc_errors = rpc_errors or {}
        self.rpc_calls: list[tuple[str, dict]] = []

    def rpc(self, name, params=None):
        self.rpc_calls.append((name, params or {}))
        if name == "fn_is_platform_admin":
            return _Query(self.is_platform_admin)
        if name in self.rpc_errors:
            return _Query(error=self.rpc_errors[name])
        if name in {"fn_create_club", "fn_add_member", "fn_change_member_role"}:
            return _Query(NEW_ID)
        return _Query(None)

    def table(self, name):
        data = {
            "club_memberships": self.club_memberships or self.memberships,
            "clubs": self.clubs,
            "profiles": self.profiles,
        }.get(name, [])
        return _Query(data)

    def write_calls(self):
        return [(name, params) for name, params in self.rpc_calls if name != "fn_is_platform_admin"]


def _membership(club_id=CLUB_ID, role="club_admin", membership_id=MEMBERSHIP_ID):
    return {
        "id": membership_id,
        "club_id": club_id,
        "user_id": "user-1",
        "role": role,
        "started_at": "2026-01-01T00:00:00Z",
        "ended_at": None,
    }


def _club(club_id=CLUB_ID):
    return {
        "id": club_id,
        "name": "Club Demo",
        "city": "Bogotá",
        "country": "CO",
        "status": "active",
        "created_at": "2026-01-01T00:00:00Z",
    }


def _authenticate(monkeypatch, fake):
    async def fake_verify(_token):
        return {"sub": "user-1", "email": "demo@example.com", "role": "authenticated"}

    monkeypatch.setattr(deps, "verify_supabase_jwt_strict", fake_verify)
    monkeypatch.setattr(deps, "get_supabase_for_user", lambda _token: fake)


def _session(monkeypatch, fake):
    _authenticate(monkeypatch, fake)
    client = TestClient(app, base_url="https://testserver")
    client.cookies.set("volterra_access", "valid-token")
    client.get("/login")
    token = client.cookies.get("volterra_csrf")
    assert token
    return client, token


def _api_error(code: str, message: str) -> APIError:
    return APIError({"message": message, "code": code})


# --- API JSON ---------------------------------------------------------------


def test_api_create_club_exige_csrf_si_la_sesion_es_por_cookie(monkeypatch):
    fake = _FakeClient(is_platform_admin=True)
    client, _ = _session(monkeypatch, fake)

    response = client.post("/api/v1/clubs", json={"name": "Club Demo"})

    assert response.status_code == 403
    assert response.json()["detail"] == "CSRF inválido"
    assert fake.write_calls() == []


def test_api_create_club_con_csrf_llama_a_la_rpc(monkeypatch):
    fake = _FakeClient(is_platform_admin=True)
    client, token = _session(monkeypatch, fake)

    response = client.post(
        "/api/v1/clubs",
        json={"name": "  Club Demo  ", "city": "Bogotá", "country": "co"},
        headers={"X-CSRF-Token": token},
    )

    assert response.status_code == 201
    assert response.json() == {"id": NEW_ID}
    assert fake.write_calls() == [
        (
            "fn_create_club",
            {"p_name": "Club Demo", "p_city": "Bogotá", "p_country": "CO"},
        )
    ]


def test_api_create_club_rechaza_a_quien_no_es_platform_admin(monkeypatch):
    fake = _FakeClient(is_platform_admin=False, memberships=[_membership(role="coach")])
    client, token = _session(monkeypatch, fake)

    response = client.post(
        "/api/v1/clubs",
        json={"name": "Club Demo"},
        headers={"X-CSRF-Token": token},
    )

    assert response.status_code == 403
    assert fake.write_calls() == []


def test_api_bearer_no_exige_csrf(monkeypatch):
    fake = _FakeClient(is_platform_admin=True)
    _authenticate(monkeypatch, fake)
    client = TestClient(app, base_url="https://testserver")

    response = client.post(
        "/api/v1/clubs",
        json={"name": "Club Demo"},
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 201
    assert fake.write_calls()[0][0] == "fn_create_club"


def test_api_update_club_devuelve_204_y_envia_estado(monkeypatch):
    fake = _FakeClient(is_platform_admin=True, clubs=[_club()])
    client, token = _session(monkeypatch, fake)

    response = client.patch(
        f"/api/v1/clubs/{CLUB_ID}",
        json={"name": "Club Renombrado", "status": "suspended"},
        headers={"X-CSRF-Token": token},
    )

    assert response.status_code == 204
    name, params = fake.write_calls()[0]
    assert name == "fn_update_club"
    assert params["p_club_id"] == CLUB_ID
    assert params["p_name"] == "Club Renombrado"
    assert params["p_status"] == "suspended"


def test_api_add_member_traduce_42501_a_403(monkeypatch):
    fake = _FakeClient(
        memberships=[_membership(role="club_admin")],
        rpc_errors={
            "fn_add_member": _api_error("42501", "Un administrador de club solo puede gestionar entrenadores")
        },
    )
    client, token = _session(monkeypatch, fake)

    response = client.post(
        f"/api/v1/clubs/{CLUB_ID}/members",
        json={"user_id": "00000000-0000-4000-8000-000000000002", "role": "club_admin"},
        headers={"X-CSRF-Token": token},
    )

    assert response.status_code == 403
    assert "Acceso denegado" in response.json()["detail"]


def test_api_role_change_de_otro_club_devuelve_404_sin_escribir(monkeypatch):
    fake = _FakeClient(memberships=[_membership(role="club_admin")], clubs=[_club()])
    client, token = _session(monkeypatch, fake)
    monkeypatch.setattr(
        clubs_endpoint,
        "get_membership",
        lambda _client, _mid: {**_membership(club_id="otro-club"), "id": MEMBERSHIP_ID},
    )

    response = client.patch(
        f"/api/v1/clubs/{CLUB_ID}/members/{MEMBERSHIP_ID}",
        json={"role": "coach"},
        headers={"X-CSRF-Token": token},
    )

    assert response.status_code == 404
    assert fake.write_calls() == []


def test_api_end_membership_devuelve_204(monkeypatch):
    fake = _FakeClient(memberships=[_membership(role="club_admin")], clubs=[_club()])
    client, token = _session(monkeypatch, fake)

    response = client.delete(
        f"/api/v1/clubs/{CLUB_ID}/members/{MEMBERSHIP_ID}",
        headers={"X-CSRF-Token": token},
    )

    assert response.status_code == 204
    assert fake.write_calls() == [("fn_end_membership", {"p_membership_id": MEMBERSHIP_ID})]


# --- Formularios HTML -------------------------------------------------------


def test_web_new_club_es_solo_para_platform_admin(monkeypatch):
    fake = _FakeClient(is_platform_admin=False, memberships=[_membership(role="club_admin")])
    client, _ = _session(monkeypatch, fake)

    response = client.get("/clubs/new")

    assert response.status_code == 403
    assert "Acceso denegado" in response.text


def test_web_new_club_renderiza_formulario_para_platform_admin(monkeypatch):
    fake = _FakeClient(is_platform_admin=True)
    client, _ = _session(monkeypatch, fake)

    response = client.get("/clubs/new")

    assert response.status_code == 200
    assert "Crear club" in response.text
    assert 'name="csrf_token"' in response.text


def test_web_create_club_sin_csrf_no_escribe(monkeypatch):
    fake = _FakeClient(is_platform_admin=True)
    client, _ = _session(monkeypatch, fake)

    response = client.post("/clubs", data={"name": "Club Demo", "country": "CO"})

    assert response.status_code == 403
    assert "El formulario expiró" in response.text
    assert fake.write_calls() == []


def test_web_create_club_redirige_al_club_creado(monkeypatch):
    fake = _FakeClient(is_platform_admin=True)
    client, token = _session(monkeypatch, fake)

    response = client.post(
        "/clubs",
        data={"name": "  Club Demo  ", "city": "", "country": "co", "csrf_token": token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/clubs/{NEW_ID}"
    assert fake.write_calls() == [
        ("fn_create_club", {"p_name": "Club Demo", "p_city": None, "p_country": "CO"})
    ]


def test_web_create_club_rechaza_pais_invalido(monkeypatch):
    fake = _FakeClient(is_platform_admin=True)
    client, token = _session(monkeypatch, fake)

    response = client.post(
        "/clubs",
        data={"name": "Club Demo", "country": "C", "csrf_token": token},
    )

    assert response.status_code == 400
    assert "dos letras" in response.text
    assert fake.write_calls() == []


def test_web_add_member_rechaza_uuid_invalido(monkeypatch):
    fake = _FakeClient(memberships=[_membership(role="club_admin")], clubs=[_club()])
    client, token = _session(monkeypatch, fake)

    response = client.post(
        f"/clubs/{CLUB_ID}/members",
        data={"user_id": "no-es-uuid", "role": "coach", "csrf_token": token},
    )

    assert response.status_code == 400
    assert "UUID válido" in response.text
    assert fake.write_calls() == []


def test_web_club_admin_no_puede_asignar_rol_admin(monkeypatch):
    fake = _FakeClient(memberships=[_membership(role="club_admin")], clubs=[_club()])
    client, token = _session(monkeypatch, fake)

    response = client.post(
        f"/clubs/{CLUB_ID}/members",
        data={
            "user_id": "00000000-0000-4000-8000-000000000002",
            "role": "club_admin",
            "csrf_token": token,
        },
    )

    assert response.status_code == 403
    assert "No puedes asignar ese rol" in response.text
    assert fake.write_calls() == []


def test_web_add_member_valido_redirige(monkeypatch):
    fake = _FakeClient(memberships=[_membership(role="club_admin")], clubs=[_club()])
    client, token = _session(monkeypatch, fake)

    response = client.post(
        f"/clubs/{CLUB_ID}/members",
        data={
            "user_id": "00000000-0000-4000-8000-000000000002",
            "role": "coach",
            "csrf_token": token,
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/clubs/{CLUB_ID}/members"
    assert fake.write_calls() == [
        (
            "fn_add_member",
            {
                "p_club_id": CLUB_ID,
                "p_user_id": "00000000-0000-4000-8000-000000000002",
                "p_role": "coach",
            },
        )
    ]


def test_web_coach_no_puede_gestionar_miembros(monkeypatch):
    fake = _FakeClient(memberships=[_membership(role="coach")], clubs=[_club()])
    client, token = _session(monkeypatch, fake)

    response = client.post(
        f"/clubs/{CLUB_ID}/members",
        data={
            "user_id": "00000000-0000-4000-8000-000000000002",
            "role": "coach",
            "csrf_token": token,
        },
    )

    assert response.status_code == 403
    assert fake.write_calls() == []


def test_web_role_change_de_otro_club_devuelve_404(monkeypatch):
    fake = _FakeClient(memberships=[_membership(role="club_admin")], clubs=[_club()])
    client, token = _session(monkeypatch, fake)
    monkeypatch.setattr(
        routes_common,
        "get_membership",
        lambda _client, _mid: {**_membership(club_id="otro-club"), "id": MEMBERSHIP_ID},
    )

    response = client.post(
        f"/clubs/{CLUB_ID}/members/{MEMBERSHIP_ID}/role",
        data={"role": "coach", "csrf_token": token},
    )

    assert response.status_code == 404
    assert fake.write_calls() == []


def test_web_end_membership_redirige(monkeypatch):
    fake = _FakeClient(memberships=[_membership(role="club_admin")], clubs=[_club()])
    client, token = _session(monkeypatch, fake)

    response = client.post(
        f"/clubs/{CLUB_ID}/members/{MEMBERSHIP_ID}/end",
        data={"csrf_token": token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/clubs/{CLUB_ID}/members"
    assert fake.write_calls() == [("fn_end_membership", {"p_membership_id": MEMBERSHIP_ID})]
