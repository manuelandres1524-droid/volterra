"""Pruebas de accesibilidad y estados de la interfaz de F1.

No sustituyen a axe/Lighthouse ni a un lector de pantalla real: comprueban que
las garantías que sí dependen del código (regiones, captions, etiquetas,
avisos y confirmaciones) están presentes en el HTML servido.
"""

from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from apps.auth import deps
from apps.core.errors import UnauthenticatedError
from apps.core.config import settings
from apps.web.routes import auth as web_auth
from apps.web.templates import _fecha
from main import app

CLUB_ID = "00000000-0000-4000-8000-000000000001"
MEMBERSHIP_ID = "00000000-0000-4000-8000-0000000000b1"


class _Query:
    def __init__(self, data=None):
        self._data = data if data is not None else []

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


class _Client:
    def __init__(self, *, is_platform_admin=False, memberships=None, clubs=None, profiles=None):
        self.is_platform_admin = is_platform_admin
        self.memberships = memberships or []
        self.clubs = clubs or []
        self.profiles = profiles or []

    def rpc(self, name, params=None):
        return _Query(self.is_platform_admin)

    def table(self, name):
        return _Query(
            {
                "club_memberships": self.memberships,
                "clubs": self.clubs,
                "profiles": self.profiles,
            }.get(name, [])
        )


def _membership(role="club_admin", ended_at=None):
    return {
        "id": MEMBERSHIP_ID,
        "club_id": CLUB_ID,
        "user_id": "user-1",
        "role": role,
        "started_at": "2026-01-01T00:00:00Z",
        "ended_at": ended_at,
    }


def _club():
    return {
        "id": CLUB_ID,
        "name": "Club Demo",
        "city": "Bogotá",
        "country": "CO",
        "status": "active",
        "created_at": "2026-01-01T00:00:00Z",
    }


@pytest.fixture(autouse=True)
def _cookie_secure(monkeypatch):
    monkeypatch.setattr(settings, "COOKIE_SECURE", True)


def _client(monkeypatch, fake):
    async def fake_verify(_token):
        return {"sub": "user-1", "email": "demo@example.com", "role": "authenticated"}

    monkeypatch.setattr(deps, "verify_supabase_jwt_strict", fake_verify)
    monkeypatch.setattr(deps, "get_supabase_for_user", lambda _token: fake)
    client = TestClient(app, base_url="https://testserver")
    client.cookies.set("volterra_access", "valid-token")
    client.get("/login")
    return client


def test_la_estructura_base_tiene_salto_de_contenido_y_region_anunciada(monkeypatch):
    client = _client(monkeypatch, _Client(profiles=[{"id": "user-1", "display_name": "Demo"}]))

    response = client.get("/me")

    assert response.status_code == 200
    html = response.text
    assert 'href="#contenido"' in html
    assert 'id="contenido"' in html
    assert 'tabindex="-1"' in html
    assert 'id="live-status"' in html
    assert 'aria-live="polite"' in html


def test_la_navegacion_marca_la_pagina_actual(monkeypatch):
    client = _client(monkeypatch, _Client(profiles=[{"id": "user-1", "display_name": "Demo"}]))

    response = client.get("/me")

    assert 'aria-current="page"' in response.text


def test_la_tabla_de_mi_cuenta_es_una_region_con_caption(monkeypatch):
    fake = _Client(
        memberships=[_membership()],
        clubs=[_club()],
        profiles=[{"id": "user-1", "display_name": "Demo"}],
    )
    client = _client(monkeypatch, fake)

    response = client.get("/me")

    assert 'role="region"' in response.text
    assert "<caption" in response.text
    assert 'aria-label="Tabla de clubes y roles"' in response.text


def test_el_estado_vacio_se_anuncia(monkeypatch):
    client = _client(monkeypatch, _Client(profiles=[{"id": "user-1", "display_name": "Demo"}]))

    response = client.get("/clubs")

    assert response.status_code == 200
    assert 'role="status"' in response.text
    assert "No tienes clubes activos" in response.text


def test_las_acciones_de_miembros_tienen_etiqueta_y_confirmacion(monkeypatch):
    fake = _Client(
        is_platform_admin=True,
        memberships=[_membership()],
        clubs=[_club()],
        profiles=[{"id": "user-1", "display_name": "Demo"}],
    )
    client = _client(monkeypatch, fake)

    response = client.get(f"/clubs/{CLUB_ID}/members")

    assert response.status_code == 200
    html = response.text
    assert "<caption" in html
    assert 'aria-label="Tabla de miembros activos"' in html
    assert 'aria-label="Cerrar la pertenencia de Demo"' in html
    assert "data-confirm=" in html
    assert 'aria-describedby="user-id-hint"' in html


def test_el_formulario_de_club_describe_el_pais(monkeypatch):
    client = _client(monkeypatch, _Client(is_platform_admin=True))

    response = client.get("/clubs/new")

    assert response.status_code == 200
    assert 'aria-describedby="country-hint"' in response.text
    assert 'id="country-hint"' in response.text


def test_el_error_de_login_marca_los_campos(monkeypatch):
    async def fake_sign_in(_email, _password):
        raise UnauthenticatedError("Correo o contraseña incorrectos.")

    monkeypatch.setattr(web_auth, "sign_in", fake_sign_in)
    client = TestClient(app, base_url="https://testserver")
    client.get("/login")
    token = client.cookies.get("volterra_csrf")

    response = client.post(
        "/login",
        data={"email": "demo@example.com", "password": "x", "csrf_token": token},
    )

    assert response.status_code == 401
    assert 'id="login-error"' in response.text
    assert response.text.count('aria-invalid="true"') == 2
    assert 'aria-describedby="login-error"' in response.text


def test_la_confirmacion_usa_un_dialogo_nativo(monkeypatch):
    client = _client(monkeypatch, _Client(profiles=[{"id": "user-1", "display_name": "Demo"}]))

    html = client.get("/me").text

    assert '<dialog id="confirm-dialog"' in html
    assert 'aria-labelledby="confirm-dialog-title"' in html
    assert 'aria-describedby="confirm-dialog-message"' in html
    assert '<form method="dialog">' in html


def test_la_confirmacion_ofrece_la_accion_concreta(monkeypatch):
    fake = _Client(
        is_platform_admin=True,
        memberships=[_membership()],
        clubs=[_club()],
        profiles=[{"id": "user-1", "display_name": "Demo"}],
    )
    client = _client(monkeypatch, fake)

    html = client.get(f"/clubs/{CLUB_ID}/members").text

    assert 'data-confirm-action="Cerrar pertenencia"' in html


def test_la_fecha_se_muestra_en_hora_de_bogota():
    # 03:00 UTC del 1 de enero es 22:00 del 31 de diciembre en Bogotá (UTC-5).
    assert _fecha("2026-01-01T03:00:00Z") == "31/12/2025"
    assert _fecha("2026-01-01T12:00:00Z") == "01/01/2026"
    assert _fecha(datetime(2026, 1, 1)) == "01/01/2026"
    assert _fecha(None) == "—"
