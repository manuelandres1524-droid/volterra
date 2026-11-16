import asyncio
import time

import jwt
import pytest

from apps.core.config import settings
from apps.core.security import (
    JWTUnavailableError,
    JWTValidationError,
    verify_supabase_jwt_strict,
)

SECRET = "test-secret-no-real-0123456789abcdef"
ISSUER = "https://example.supabase.co/auth/v1"


@pytest.fixture(autouse=True)
def _jwt_settings(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_JWT_ISSUER", None)
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", SECRET)
    monkeypatch.setattr(settings, "SUPABASE_JWT_AUDIENCE", "authenticated")
    monkeypatch.setattr(settings, "SUPABASE_JWT_ALGORITHMS", ["HS256"])


def _token(*, drop=(), **overrides):
    now = int(time.time())
    payload = {
        "sub": "user-1",
        "role": "authenticated",
        "aud": "authenticated",
        "iss": ISSUER,
        "iat": now,
        "exp": now + 300,
    }
    for claim in drop:
        payload.pop(claim, None)
    payload.update(overrides)
    return jwt.encode(payload, SECRET, algorithm="HS256")


def _verify(token):
    return asyncio.run(verify_supabase_jwt_strict(token))


def test_valid_user_token_is_accepted():
    payload = _verify(_token())

    assert payload["sub"] == "user-1"
    assert payload["role"] == "authenticated"


def test_service_role_is_rejected():
    with pytest.raises(JWTValidationError, match="service_role"):
        _verify(_token(role="service_role"))


@pytest.mark.parametrize("role", ["anon", "refresh_token", "supabase_admin", None])
def test_roles_other_than_authenticated_are_rejected(role):
    with pytest.raises(JWTValidationError):
        _verify(_token(role=role))


def test_missing_role_is_rejected():
    with pytest.raises(JWTValidationError):
        _verify(_token(drop=("role",)))


def test_missing_issued_at_is_rejected():
    with pytest.raises(JWTValidationError):
        _verify(_token(drop=("iat",)))


def test_missing_sub_is_rejected():
    with pytest.raises(JWTValidationError):
        _verify(_token(drop=("sub",)))


def test_missing_audience_is_rejected():
    with pytest.raises(JWTValidationError):
        _verify(_token(drop=("aud",)))


def test_wrong_issuer_is_rejected():
    with pytest.raises(JWTValidationError):
        _verify(_token(iss="https://example.supabase.co/otro"))


def test_expired_token_is_rejected():
    with pytest.raises(JWTValidationError):
        _verify(_token(exp=int(time.time()) - 60))


def test_missing_issuer_configuration_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_JWT_ISSUER", None)
    monkeypatch.setattr(settings, "SUPABASE_URL", "")

    with pytest.raises(JWTUnavailableError, match="Emisor"):
        _verify(_token())


def test_malformed_token_raises_validation_error_even_without_configuration(monkeypatch):
    """Un token ilegible es error del cliente, no del servidor."""
    monkeypatch.setattr(settings, "SUPABASE_JWT_ISSUER", None)
    monkeypatch.setattr(settings, "SUPABASE_URL", "")

    with pytest.raises(JWTValidationError, match="Header"):
        _verify("invalid.token.here")


def test_missing_audience_configuration_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_JWT_AUDIENCE", "")

    with pytest.raises(JWTUnavailableError, match="Audiencia"):
        _verify(_token())


def test_hs256_without_secret_is_unavailable(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", None)

    with pytest.raises(JWTUnavailableError, match="HS256"):
        _verify(_token())


def test_algorithm_not_allowed_is_rejected(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_JWT_ALGORITHMS", ["RS256"])

    with pytest.raises(JWTValidationError):
        _verify(_token())
