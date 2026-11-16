"""Pruebas del servicio de escrituras y del mapeo SQLSTATE → error de dominio.

No tocan la base de datos: comprueban que cada función llama a la RPC correcta,
con los parámetros correctos, y que los errores de PostgREST se traducen al
error de dominio que corresponde. El estado HTTP lo decide
``apps.core.errors`` y se prueba en `tests/test_errors.py`. La autorización real
(rol, ámbito e invariantes) vive en las funciones ``SECURITY DEFINER`` y se
prueba en `supabase/tests/`.
"""

from types import SimpleNamespace

import pytest
from postgrest.exceptions import APIError

from apps.core.errors import (
    ConflictError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
    UnauthenticatedError,
    UnavailableError,
)
from apps.services.f1_writes import (
    add_member,
    change_member_role,
    create_club,
    end_membership,
    update_club,
)


class _Rpc:
    def __init__(self, data=None, error=None):
        self._data = data
        self._error = error

    def execute(self):
        if self._error is not None:
            raise self._error
        return SimpleNamespace(data=self._data)


class _Client:
    def __init__(self, data=None, error=None):
        self._data = data
        self._error = error
        self.calls: list[tuple[str, dict]] = []

    def rpc(self, name, params=None):
        self.calls.append((name, params or {}))
        return _Rpc(self._data, self._error)


def _api_error(code: str, message: str = "error de prueba") -> APIError:
    return APIError({"message": message, "code": code})


def test_create_club_pasa_parametros_y_devuelve_id():
    client = _Client(data="club-uuid")

    result = create_club(client, "  Club Demo  ", "  Bogotá  ", "co")

    assert result == "club-uuid"
    assert client.calls == [
        (
            "fn_create_club",
            {"p_name": "  Club Demo  ", "p_city": "  Bogotá  ", "p_country": "co"},
        )
    ]


def test_update_club_envia_estado_y_campos():
    client = _Client(data=None)

    update_club(client, "club-1", name="Nuevo", city="Cali", country="CO", club_status="suspended")

    name, params = client.calls[0]
    assert name == "fn_update_club"
    assert params == {
        "p_club_id": "club-1",
        "p_name": "Nuevo",
        "p_city": "Cali",
        "p_country": "CO",
        "p_status": "suspended",
    }


def test_add_member_y_change_role_devuelven_id():
    client = _Client(data="membership-uuid")

    assert add_member(client, "club-1", "user-2", "coach") == "membership-uuid"
    assert change_member_role(client, "membership-1", "club_admin") == "membership-uuid"

    assert client.calls[0] == (
        "fn_add_member",
        {"p_club_id": "club-1", "p_user_id": "user-2", "p_role": "coach"},
    )
    assert client.calls[1] == (
        "fn_change_member_role",
        {"p_membership_id": "membership-1", "p_new_role": "club_admin"},
    )


def test_end_membership_llama_a_la_rpc():
    client = _Client(data=None)

    end_membership(client, "membership-1")

    assert client.calls == [("fn_end_membership", {"p_membership_id": "membership-1"})]


@pytest.mark.parametrize(
    "code, expected_error",
    [
        ("28000", UnauthenticatedError),
        ("42501", ForbiddenError),
        ("P0002", NotFoundError),
        ("23505", ConflictError),
        ("40001", ConflictError),
        ("23503", InvalidInputError),
        ("23514", InvalidInputError),
        ("22023", InvalidInputError),
    ],
)
def test_mapeo_de_sqlstate_a_error_de_dominio(code, expected_error):
    client = _Client(error=_api_error(code, "mensaje de la base"))

    with pytest.raises(expected_error) as excinfo:
        create_club(client, "Club Demo")

    from apps.services.postgrest_errors import SQLSTATE_MESSAGES

    assert excinfo.value.message == SQLSTATE_MESSAGES[code]


def test_error_desconocido_o_de_red_es_503():
    client = _Client(error=RuntimeError("sin conexión"))

    with pytest.raises(UnavailableError) as excinfo:
        end_membership(client, "membership-1")

    assert "No se pudo completar la operación" in excinfo.value.message


def test_error_conocido_sin_mensaje_usa_mensaje_fijo():
    client = _Client(error=APIError({"code": "42501"}))

    with pytest.raises(ForbiddenError) as excinfo:
        add_member(client, "club-1", "user-2", "coach")

    assert excinfo.value.message == "Acceso denegado."
