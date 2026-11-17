"""Pruebas HTTP de F2 (altas y fichas de atletas, solo mayores de edad).

Usan un cliente de datos falso: no tocan Supabase. Comprueban el contrato del
BFF —CSRF, roles, validación de entrada (mayoria de edad, longitudes),
mapeo de errores y redirecciones— y dejan la autorización efectiva a las
pruebas SQL de RPC/RLS.
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from postgrest.exceptions import APIError

from apps.auth import deps
from apps.core.config import settings
from main import app

CLUB_ID = "00000000-0000-4000-8000-000000000001"
ATHLETE_ID = "00000000-0000-4000-8000-0000000000a1"
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

    def range(self, *args, **kwargs):
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
        athletes=None,
        rpc_errors=None,
    ):
        self.is_platform_admin = is_platform_admin
        self.memberships = memberships or []
        self.clubs = clubs or []
        self.athletes = athletes or []
        self.rpc_errors = rpc_errors or {}
        self.rpc_calls: list[tuple[str, dict]] = []

    def rpc(self, name, params=None):
        self.rpc_calls.append((name, params or {}))
        if name == "fn_is_platform_admin":
            return _Query(self.is_platform_admin)
        if name in self.rpc_errors:
            return _Query(error=self.rpc_errors[name])
        if name in {"fn_create_athlete", "fn_update_athlete"}:
            return _Query(NEW_ID)
        return _Query(None)

    def table(self, name):
        data = {
            "club_memberships": self.memberships,
            "clubs": self.clubs,
            "athletes": self.athletes,
        }.get(name, [])
        return _Query(data)

    def write_calls(self):
        return [(name, params) for name, params in self.rpc_calls if name != "fn_is_platform_admin"]


def _membership(club_id=CLUB_ID, role="club_admin"):
    return {
        "id": "00000000-0000-4000-8000-0000000000b1",
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


def _athlete():
    return {
        "id": ATHLETE_ID,
        "club_id": CLUB_ID,
        "display_name": "Alias Demo",
        "position": "Delantero",
        "birth_date": "1995-06-15",
        "gender": "male",
        "category": "Profesional",
        "status": "active",
        "created_at": "2026-01-01T00:00:00Z",
    }


def _api_error(code: str, message: str) -> APIError:
    return APIError({"code": code, "message": message})


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


def _fake_club_admin(monkeypatch):
    fake = _FakeClient(
        memberships=[_membership(role="club_admin")],
        clubs=[_club()],
        athletes=[_athlete()],
    )
    client, token = _session(monkeypatch, fake)
    return client, token, fake


def test_web_create_athlete_redirige(monkeypatch):
    client, token, fake = _fake_club_admin(monkeypatch)

    response = client.post(
        f"/clubs/{CLUB_ID}/athletes",
        data={
            "display_name": "Alias Demo",
            "birth_date": "1995-06-15",
            "position": "Delantero",
            "gender": "male",
            "category": "Profesional",
            "csrf_token": token,
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/clubs/{CLUB_ID}/athletes"
    write_calls = fake.write_calls()
    assert write_calls, "debe llamar a la RPC de creación"
    assert write_calls[0][0] == "fn_create_athlete"
    assert write_calls[0][1]["p_display_name"] == "Alias Demo"
    assert write_calls[0][1]["p_birth_date"] == "1995-06-15"


def test_web_create_athlete_sin_csrf_es_403(monkeypatch):
    client, token, fake = _fake_club_admin(monkeypatch)

    response = client.post(
        f"/clubs/{CLUB_ID}/athletes",
        data={
            "display_name": "Alias Demo",
            "birth_date": "1995-06-15",
            "position": "Delantero",
            "gender": "male",
            "category": "Profesional",
        },
    )

    assert response.status_code == 403
    assert fake.write_calls() == []


def test_web_create_athlete_menor_de_edad_es_400(monkeypatch):
    client, token, fake = _fake_club_admin(monkeypatch)

    from datetime import date, timedelta

    younger = (date.today() - timedelta(days=10 * 366)).isoformat()
    response = client.post(
        f"/clubs/{CLUB_ID}/athletes",
        data={
            "display_name": "Alias Demo",
            "birth_date": younger,
            "position": "Delantero",
            "gender": "male",
            "category": "Profesional",
            "csrf_token": token,
        },
    )

    assert response.status_code == 400
    assert fake.write_calls() == []


def test_web_create_athlete_coach_es_403(monkeypatch):
    fake = _FakeClient(
        memberships=[_membership(role="coach")],
        clubs=[_club()],
        athletes=[_athlete()],
    )
    client, token = _session(monkeypatch, fake)

    response = client.post(
        f"/clubs/{CLUB_ID}/athletes",
        data={
            "display_name": "Alias Demo",
            "birth_date": "1995-06-15",
            "position": "Delantero",
            "gender": "male",
            "category": "Profesional",
            "csrf_token": token,
        },
        follow_redirects=False,
    )

    assert response.status_code == 403
    assert fake.write_calls() == []


def test_api_list_athletes_en_club_200(monkeypatch):
    client, _, _ = _fake_club_admin(monkeypatch)

    response = client.get(f"/api/v1/clubs/{CLUB_ID}/athletes")

    assert response.status_code == 200
    body = response.json()
    assert body["club_id"] == CLUB_ID
    assert body["athletes"][0]["display_name"] == "Alias Demo"


def test_api_create_athlete_201(monkeypatch):
    client, token, fake = _fake_club_admin(monkeypatch)

    response = client.post(
        f"/api/v1/clubs/{CLUB_ID}/athletes",
        json={
            "display_name": "Alias Demo",
            "birth_date": "1995-06-15",
            "position": "Delantero",
            "gender": "male",
            "category": "Profesional",
        },
        headers={"X-CSRF-Token": token},
    )

    assert response.status_code == 201
    assert response.json()["id"] == NEW_ID
    write_calls = fake.write_calls()
    assert write_calls[0][0] == "fn_create_athlete"


def test_api_create_athlete_sin_csrf_es_403(monkeypatch):
    client, _, fake = _fake_club_admin(monkeypatch)

    response = client.post(
        f"/api/v1/clubs/{CLUB_ID}/athletes",
        json={
            "display_name": "Alias Demo",
            "birth_date": "1995-06-15",
            "position": "Delantero",
            "gender": "male",
            "category": "Profesional",
        },
    )

    assert response.status_code == 403
    assert fake.write_calls() == []
