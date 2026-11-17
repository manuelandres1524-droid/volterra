"""Pruebas unitarias de los servicios F2 (mock de PostgREST/RPC)."""

from types import SimpleNamespace

import pytest
from postgrest.exceptions import APIError

from apps.core.errors import ForbiddenError, InvalidInputError, UnavailableError
from apps.services import f2_reads, f2_writes

ATHLETE = {
    "id": "00000000-0000-4000-8000-0000000000a1",
    "club_id": "00000000-0000-4000-8000-000000000001",
    "display_name": "Alias Demo",
    "position": "Delantero",
    "birth_date": "1995-06-15",
    "gender": "male",
    "category": "Profesional",
    "status": "active",
    "created_at": "2026-01-01T00:00:00Z",
}


class _Query:
    def __init__(self, data=None, error=None):
        self._data = [] if data is None else data
        self._error = error

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def range(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def execute(self):
        if self._error is not None:
            raise self._error
        return SimpleNamespace(data=self._data)


class _Client:
    def __init__(self, data=None, error=None, rpc_data=None, rpc_error=None):
        self.data = ATHLETE if data is None else data
        self.error = error
        self.rpc_data = rpc_data
        self.rpc_error = rpc_error
        self.rpc_calls: list[tuple[str, dict]] = []

    def table(self, name):
        assert name == "athletes"
        return _Query([self.data] if isinstance(self.data, dict) else self.data, self.error)

    def rpc(self, name, params=None):
        self.rpc_calls.append((name, params or {}))
        if self.rpc_error is not None:
            return _Query(error=self.rpc_error)
        return _Query(self.rpc_data if self.rpc_data is not None else NEW_ID)


NEW_ID = "00000000-0000-4000-8000-0000000000aa"


def _api_error(code: str, message: str) -> APIError:
    return APIError({"code": code, "message": message})


def test_get_athlete_returns_row():
    client = _Client(data=ATHLETE)
    row = f2_reads.get_athlete(client, ATHLETE["id"])
    assert row == ATHLETE


def test_get_athlete_empty_returns_none():
    client = _Client(data=[])
    assert f2_reads.get_athlete(client, ATHLETE["id"]) is None


def test_list_club_athletes_filters_status():
    client = _Client(data=[ATHLETE])
    rows = f2_reads.list_club_athletes(client, ATHLETE["club_id"])
    assert rows == [ATHLETE]


def test_list_club_athletes_pgerror_is_503():
    client = _Client(error=RuntimeError("sin conexión"))
    with pytest.raises(UnavailableError):
        f2_reads.list_club_athletes(client, "club-1")


def test_create_athlete_calls_rpc_with_args():
    client = _Client(rpc_data=NEW_ID)
    result = f2_writes.create_athlete(
        client,
        "00000000-0000-4000-8000-000000000001",
        "Alias Demo",
        "1995-06-15",
        "Delantero",
        "male",
        "Profesional",
    )
    assert result == NEW_ID
    name, params = client.rpc_calls[0]
    assert name == "fn_create_athlete"
    assert params["p_display_name"] == "Alias Demo"
    assert params["p_birth_date"] == "1995-06-15"
    assert params["p_gender"] == "male"


def test_create_athlete_42501_is_forbidden():
    client = _Client(rpc_error=_api_error("42501", "no autorizado"))
    with pytest.raises(ForbiddenError):
        f2_writes.create_athlete(client, "club", "Alias", "1995-06-15")


def test_update_athlete_keeps_nulls():
    client = _Client(rpc_data=NEW_ID)
    f2_writes.update_athlete(client, ATHLETE["id"])
    name, params = client.rpc_calls[0]
    assert name == "fn_update_athlete"
    assert params["p_display_name"] is None
    assert params["p_position"] is None


def test_deactivate_athlete():
    client = _Client(rpc_data=None)
    f2_writes.deactivate_athlete(client, ATHLETE["id"])
    name, params = client.rpc_calls[0]
    assert name == "fn_deactivate_athlete"
    assert params["p_athlete_id"] == ATHLETE["id"]


def test_update_athlete_23514_is_invalid_input():
    client = _Client(rpc_error=_api_error("23514", "check"))
    with pytest.raises(InvalidInputError):
        f2_writes.update_athlete(client, ATHLETE["id"], "A")
