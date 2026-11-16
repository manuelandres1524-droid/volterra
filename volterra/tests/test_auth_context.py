import asyncio
from types import SimpleNamespace

import pytest

from apps.auth import deps
from apps.core.errors import UnauthenticatedError, UnavailableError, http_status
from apps.core.security import JWTUnavailableError, JWTValidationError


class _FakeResponse:
    def __init__(self, data):
        self.data = data


class _FakeRpc:
    def __init__(self, data, error):
        self.data = data
        self.error = error

    def execute(self):
        if self.error is not None:
            raise self.error
        return _FakeResponse(self.data)


class _FakeMembershipQuery:
    def __init__(self, data):
        self.data = data

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def is_(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def execute(self):
        return _FakeResponse(self.data)


class _FakeClient:
    """Cliente mínimo: falla si el backend intenta leer platform_admins."""

    def __init__(self, *, is_pa=True, memberships=None, rpc_error=None):
        self.is_pa = is_pa
        self.memberships = memberships or []
        self.rpc_error = rpc_error
        self.rpc_calls = []
        self.table_calls = []

    def rpc(self, name):
        self.rpc_calls.append(name)
        return _FakeRpc(self.is_pa, self.rpc_error)

    def table(self, name):
        self.table_calls.append(name)
        if name != "club_memberships":
            raise AssertionError(f"tabla inesperada: {name}")
        return _FakeMembershipQuery(self.memberships)


def _request():
    return SimpleNamespace(state=SimpleNamespace())


def _call(client, monkeypatch, token="token", payload=None, verify_error=None):
    async def fake_verify(_token):
        if verify_error is not None:
            raise verify_error
        return payload or {"sub": "user-1", "email": "user@example.com"}

    monkeypatch.setattr(deps, "verify_supabase_jwt_strict", fake_verify)
    monkeypatch.setattr(deps, "get_supabase_for_user", lambda _token: client)
    return asyncio.run(deps.get_auth_context(_request(), f"Bearer {token}"))


def test_platform_admin_uses_rpc_and_not_table(monkeypatch):
    memberships = [
        {"club_id": "club-1", "role": "coach", "ended_at": None, "user_id": "user-1"}
    ]
    client = _FakeClient(is_pa=True, memberships=memberships)

    ctx = _call(client, monkeypatch)

    assert ctx.is_platform_admin is True
    assert ctx.memberships == memberships
    assert client.rpc_calls == ["fn_is_platform_admin"]
    assert client.table_calls == ["club_memberships"]


def test_non_platform_admin(monkeypatch):
    client = _FakeClient(is_pa=False)

    ctx = _call(client, monkeypatch)

    assert ctx.is_platform_admin is False
    assert client.rpc_calls == ["fn_is_platform_admin"]


def test_rpc_failure_returns_503(monkeypatch):
    client = _FakeClient(rpc_error=RuntimeError("rpc caída"))

    with pytest.raises(UnavailableError) as exc:
        _call(client, monkeypatch)

    assert http_status(exc.value) == 503
    assert exc.value.message == "Error al verificar permisos"


def test_missing_header_returns_401():
    with pytest.raises(UnauthenticatedError) as exc:
        asyncio.run(deps.get_auth_context(_request(), None))

    assert http_status(exc.value) == 401


def test_invalid_token_returns_401(monkeypatch):
    client = _FakeClient()

    with pytest.raises(UnauthenticatedError) as exc:
        _call(client, monkeypatch, verify_error=JWTValidationError("token inválido"))

    assert http_status(exc.value) == 401


def test_jwks_unavailable_returns_503(monkeypatch):
    client = _FakeClient()

    with pytest.raises(UnavailableError) as exc:
        _call(client, monkeypatch, verify_error=JWTUnavailableError("jwks caído"))

    assert http_status(exc.value) == 503
    assert exc.value.message == "No se pudo verificar el token"


def test_client_init_failure_returns_503(monkeypatch):
    async def fake_verify(_token):
        return {"sub": "user-1", "email": "user@example.com"}

    monkeypatch.setattr(deps, "verify_supabase_jwt_strict", fake_verify)
    monkeypatch.setattr(
        deps, "get_supabase_for_user", lambda _token: (_ for _ in ()).throw(RuntimeError("sin cliente"))
    )

    with pytest.raises(UnavailableError) as exc:
        asyncio.run(deps.get_auth_context(_request(), "Bearer token"))

    assert http_status(exc.value) == 503
    assert exc.value.message == "Error al inicializar el cliente de datos"


@pytest.mark.parametrize(
    "value, expected",
    [
        (True, True),
        (False, False),
        ([True], True),
        ([False], False),
        ([], False),
        ("true", True),
        ("false", False),
        (None, False),
    ],
)
def test_as_bool_normalizes_postgrest_scalar(value, expected):
    assert deps._as_bool(value) == expected
