from types import SimpleNamespace

import pytest

from apps.core.errors import ForbiddenError, InvalidInputError, UnavailableError
from apps.services.f1_reads import (
    get_club,
    list_club_members,
    list_my_clubs,
)


class _Query:
    def __init__(self, data=None, error=None):
        self._data = data or []
        self._error = error
        self.selected = None
        self.filters = []
        self.ordered = None
        self.limited = None

    def select(self, columns, *args, **kwargs):
        self.selected = columns
        return self

    def eq(self, column, value):
        self.filters.append(("eq", column, value))
        return self

    def is_(self, column, value):
        self.filters.append(("is", column, value))
        return self

    def in_(self, column, values):
        self.filters.append(("in", column, list(values)))
        return self

    def order(self, column, *args, **kwargs):
        self.ordered = column
        return self

    def limit(self, value):
        self.limited = value
        return self

    def execute(self):
        if self._error is not None:
            raise self._error
        return SimpleNamespace(data=self._data)


class _Client:
    def __init__(self, tables):
        self.tables = tables
        self.calls = []

    def table(self, name):
        self.calls.append(name)
        return _Query(self.tables.get(name, []))


def test_list_my_clubs_uses_explicit_fields_and_keeps_membership_order():
    client = _Client(
        {
            "clubs": [
                {"id": "club-b", "name": "Club Beta", "city": "Cali", "status": "active"},
                {"id": "club-a", "name": "Club Alfa", "city": "Bogotá", "status": "active"},
            ]
        }
    )
    memberships = [
        {"club_id": "club-b", "role": "coach", "started_at": "2026-01-01T00:00:00Z"},
        {"club_id": "club-a", "role": "club_admin", "started_at": "2026-02-01T00:00:00Z"},
    ]

    result = list_my_clubs(client, memberships)

    assert [row["club_name"] for row in result] == ["Club Alfa", "Club Beta"]
    assert result[0] == {
        "club_id": "club-a",
        "club_name": "Club Alfa",
        "city": "Bogotá",
        "status": "active",
        "role": "club_admin",
        "started_at": "2026-02-01T00:00:00Z",
        "ended_at": None,
    }
    assert client.calls == ["clubs"]


def test_list_my_clubs_without_memberships_does_not_query():
    client = _Client({})

    assert list_my_clubs(client, []) == []
    assert client.calls == []


def test_list_club_members_merges_visible_profiles_and_leaves_hidden_ones_none():
    client = _Client(
        {
            "club_memberships": [
                {
                    "id": "m1",
                    "user_id": "user-1",
                    "role": "club_admin",
                    "started_at": "2026-01-01T00:00:00Z",
                },
                {
                    "id": "m2",
                    "user_id": "user-2",
                    "role": "coach",
                    "started_at": "2026-01-02T00:00:00Z",
                },
            ],
            "profiles": [{"id": "user-1", "display_name": "Demo Admin"}],
        }
    )

    result = list_club_members(client, "club-1")

    assert result[0]["display_name"] == "Demo Admin"
    assert result[1]["display_name"] is None
    assert result[0]["role"] == "club_admin"
    assert "email" not in result[0]


def test_get_club_returns_none_when_rls_hides_it():
    client = _Client({"clubs": []})

    assert get_club(client, "club-1") is None


def test_data_error_is_wrapped():
    client = _Client({})
    client.table = lambda name: _Query(error=RuntimeError("postgrest caído"))

    with pytest.raises(UnavailableError):
        get_club(client, "club-1")


class _PostgrestError(Exception):
    def __init__(self, code: str, message: str | None = None) -> None:
        self.code = code
        self.message = message
        super().__init__(message or code)


def test_sqlstate_42501_en_lectura_se_traduce_a_403():
    client = _Client({})
    client.table = lambda name: _Query(error=_PostgrestError("42501", "sin permisos"))

    with pytest.raises(ForbiddenError) as excinfo:
        get_club(client, "club-1")

    assert excinfo.value.message == "Acceso denegado."


def test_sqlstate_22p02_en_lectura_se_traduce_a_400():
    client = _Client({})
    client.table = lambda name: _Query(error=_PostgrestError("22P02", "uuid inválido"))

    with pytest.raises(InvalidInputError):
        get_club(client, "no-es-un-uuid")


def test_sqlstate_desconocido_no_expone_el_mensaje_de_la_base():
    client = _Client({})
    client.table = lambda name: _Query(error=_PostgrestError("XX000", "detalle interno"))

    with pytest.raises(UnavailableError) as excinfo:
        get_club(client, "club-1")

    assert excinfo.value.message == "No se pudo consultar la base de datos"
