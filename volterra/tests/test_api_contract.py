"""Pruebas del contrato observable de la API JSON ``/api/v1``.

Comprueban que OpenAPI documenta los modelos reales, que los errores del
framework usan el mismo vocabulario ``code`` que los errores de dominio y que
la paginación opcional se valida antes de consultar la base.
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from apps.auth.deps import AuthContext, get_auth_context
from apps.integrations.supabase.deps import get_data_client
from main import app

client = TestClient(app, base_url="https://testserver")

CLUB_ID = "club-1"


@pytest.fixture(autouse=True)
def _limpia_overrides():
    yield
    app.dependency_overrides.clear()


class _Query:
    def __init__(self, name, rows, log):
        self._name = name
        self._rows = rows
        self._log = log
        self._range = None

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

    def range(self, start, end):
        self._range = (start, end)
        self._log.append(("range", self._name, start, end))
        return self

    def execute(self):
        rows = self._rows
        if self._range is not None:
            start, end = self._range
            rows = rows[start : end + 1]
        return SimpleNamespace(data=rows)


class _FakeClient:
    def __init__(self, tables=None, log=None):
        self._tables = tables or {}
        self.log = log if log is not None else []

    def table(self, name):
        return _Query(name, self._tables.get(name, []), self.log)

    def rpc(self, name, params=None):
        return _Query(name, [], self.log)


def _override(*, is_pa: bool = False, role: str = "club_admin", client_=None):
    ctx = AuthContext(
        user_id="user-1",
        email="demo@example.com",
        is_platform_admin=is_pa,
        memberships=[
            {"club_id": CLUB_ID, "role": role, "started_at": "2026-01-01", "ended_at": None}
        ],
        token="token",
    )
    fake = client_ or _FakeClient()
    app.dependency_overrides[get_auth_context] = lambda: ctx
    app.dependency_overrides[get_data_client] = lambda: fake
    return fake


# --- OpenAPI ----------------------------------------------------------------


def _schema_ref(response: dict) -> str:
    return response["content"]["application/json"]["schema"]["$ref"]


def test_openapi_documenta_los_modelos_de_respuesta():
    schema = app.openapi()

    assert _schema_ref(schema["paths"]["/api/v1/me/"]["get"]["responses"]["200"]).endswith(
        "/MeOut"
    )
    assert _schema_ref(schema["paths"]["/api/v1/clubs/me"]["get"]["responses"]["200"]).endswith(
        "/MyClubsOut"
    )
    assert _schema_ref(
        schema["paths"]["/api/v1/clubs/{club_id}"]["get"]["responses"]["200"]
    ).endswith("/ClubOut")
    members_get = schema["paths"]["/api/v1/clubs/{club_id}/members"]["get"]
    assert _schema_ref(members_get["responses"]["200"]).endswith("/MembersOut")
    assert _schema_ref(
        schema["paths"]["/api/v1/platform/overview"]["get"]["responses"]["200"]
    ).endswith("/PlatformOverviewOut")
    assert _schema_ref(schema["paths"]["/api/v1/"]["get"]["responses"]["200"]).endswith(
        "/HealthOut"
    )


def test_openapi_documenta_errores_y_paginacion():
    schema = app.openapi()

    me_responses = schema["paths"]["/api/v1/me/"]["get"]["responses"]
    assert _schema_ref(me_responses["401"]).endswith("/ErrorOut")
    assert "403" not in me_responses

    members_get = schema["paths"]["/api/v1/clubs/{club_id}/members"]["get"]
    assert _schema_ref(members_get["responses"]["422"]).endswith("/ValidationErrorOut")
    params = {param["name"]: param for param in members_get["parameters"]}
    assert params["limit"]["required"] is False
    limit_schema = params["limit"]["schema"]
    assert any(option.get("maximum") == 200 for option in limit_schema.get("anyOf", []))
    assert params["offset"]["schema"]["minimum"] == 0


# --- Cuerpo de respuesta ----------------------------------------------------


def test_me_devuelve_el_cuerpo_del_contrato():
    _override(client_=_FakeClient({"profiles": [{"id": "user-1", "display_name": "Demo"}]}))

    response = client.get("/api/v1/me/")

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "user-1",
        "email": "demo@example.com",
        "display_name": "Demo",
        "is_platform_admin": False,
        "memberships": [
            {
                "club_id": CLUB_ID,
                "role": "club_admin",
                "started_at": "2026-01-01",
                "ended_at": None,
                "user_id": None,
            }
        ],
    }


# --- Errores del framework con el mismo ``code`` ----------------------------


def test_ruta_inexistente_devuelve_codigo_estable():
    response = client.get("/api/v1/no-existe")

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_metodo_no_permitido_devuelve_codigo_estable():
    response = client.delete("/api/v1/me/")

    assert response.status_code == 405
    assert response.json()["code"] == "method_not_allowed"


def test_validacion_devuelve_codigo_y_detalle_estructurado():
    _override(is_pa=True)

    response = client.post(
        "/api/v1/clubs",
        json={"city": "Cali"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "invalid_input"
    assert isinstance(body["detail"], list) and body["detail"]
    assert all("input" not in item for item in body["detail"])


# --- Paginación opcional ----------------------------------------------------


def _members(count: int) -> list[dict]:
    return [
        {
            "id": f"m{index}",
            "user_id": f"user-{index}",
            "role": "coach",
            "started_at": f"2026-01-0{index + 1}T00:00:00Z",
        }
        for index in range(count)
    ]


def test_paginacion_aplica_rango_y_refleja_parametros():
    fake = _override(
        role="coach",
        client_=_FakeClient(
            {
                "club_memberships": _members(4),
                "profiles": [{"id": "user-2", "display_name": "Dos"}],
            }
        ),
    )

    response = client.get(f"/api/v1/clubs/{CLUB_ID}/members?limit=2&offset=2")

    assert response.status_code == 200
    body = response.json()
    assert body["limit"] == 2
    assert body["offset"] == 2
    assert [member["id"] for member in body["members"]] == ["m2", "m3"]
    assert body["members"][0]["display_name"] == "Dos"
    assert ("range", "club_memberships", 2, 3) in fake.log


def test_offset_sin_limit_se_rechaza_antes_de_consultar():
    fake = _override(role="coach")

    response = client.get(f"/api/v1/clubs/{CLUB_ID}/members?offset=2")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "El desplazamiento requiere indicar un límite",
        "code": "invalid_input",
    }
    assert fake.log == []


def test_limit_fuera_de_rango_devuelve_422():
    _override(role="coach")

    response = client.get(f"/api/v1/clubs/{CLUB_ID}/members?limit=201")

    assert response.status_code == 422
    assert response.json()["code"] == "invalid_input"
