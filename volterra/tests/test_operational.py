"""Pruebas de robustez operativa: configuración, salud y cliente de datos.

No usan Supabase real: validan el contrato del BFF y el arranque ordenado.
"""

import pytest
from fastapi.testclient import TestClient

from apps.core import jwks
from apps.core.config import (
    Settings,
    docs_enabled,
    essential_config_problems,
    runtime_config_problems,
    validate_runtime_config,
)
from apps.core.config import settings
from apps.integrations.supabase import per_request
from main import app, create_app

client = TestClient(app)


def _settings(**overrides):
    base = {
        "_env_file": None,
        "SUPABASE_URL": "https://example.supabase.co",
        "SUPABASE_PUBLISHABLE_KEY": "anon",
    }
    base.update(overrides)
    return Settings(**base)


# --- Configuración ----------------------------------------------------------


def test_validate_runtime_config_raises_in_production():
    config = _settings(
        APP_ENV="prod",
        SUPABASE_URL="",
        SUPABASE_PUBLISHABLE_KEY="",
        TRUSTED_HOSTS=["example.com"],
    )

    with pytest.raises(RuntimeError, match="SUPABASE_URL"):
        validate_runtime_config(config)


def test_validate_runtime_config_in_dev_only_reports():
    config = _settings(APP_ENV="dev", SUPABASE_URL="", SUPABASE_PUBLISHABLE_KEY="")

    assert validate_runtime_config(config) == ["SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY"]


def test_production_requires_secure_cookies():
    config = _settings(APP_ENV="prod", COOKIE_SECURE=False, TRUSTED_HOSTS=["example.com"])

    assert "COOKIE_SECURE" in runtime_config_problems(config)


def test_production_rejects_wildcard_trusted_hosts():
    config = _settings(APP_ENV="prod", TRUSTED_HOSTS=["*"])

    assert "TRUSTED_HOSTS" in runtime_config_problems(config)


def test_production_requires_https_for_supabase_url():
    config = _settings(
        APP_ENV="prod",
        SUPABASE_URL="http://example.supabase.co",
        TRUSTED_HOSTS=["example.com"],
    )

    assert "SUPABASE_URL_HTTPS" in runtime_config_problems(config)


def test_production_requires_https_for_jwt_issuer():
    config = _settings(
        APP_ENV="prod",
        SUPABASE_JWT_ISSUER="http://example.supabase.co/auth/v1",
        TRUSTED_HOSTS=["example.com"],
    )

    assert "SUPABASE_JWT_ISSUER_HTTPS" in runtime_config_problems(config)


def test_trusted_hosts_accepts_comma_separated_values():
    config = _settings(TRUSTED_HOSTS="example.com, www.example.com")

    assert config.TRUSTED_HOSTS == ["example.com", "www.example.com"]


def test_docs_are_disabled_by_default_in_production():
    assert docs_enabled(_settings(APP_ENV="prod", TRUSTED_HOSTS=["example.com"])) is False
    assert docs_enabled(_settings(APP_ENV="dev")) is True
    assert (
        docs_enabled(_settings(APP_ENV="prod", ENABLE_DOCS=True, TRUSTED_HOSTS=["example.com"]))
        is True
    )


def test_essential_config_problems_never_returns_values():
    config = _settings(SUPABASE_URL="", SUPABASE_PUBLISHABLE_KEY="")

    assert essential_config_problems(config) == ["SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY"]


# --- Salud ------------------------------------------------------------------


def test_health_live_ok():
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_does_not_expose_environment():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_ready_ok_with_config(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_PUBLISHABLE_KEY", "anon")

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_health_ready_returns_503_without_config(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "")

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


def test_health_ready_returns_503_when_app_is_stopping(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_PUBLISHABLE_KEY", "anon")
    local_app = create_app()
    local_app.state.ready = False

    response = TestClient(local_app).get("/health/ready")

    assert response.status_code == 503


def test_health_endpoints_do_not_consume_rate_limit():
    for _ in range(10):
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").status_code in {200, 503}


# --- Arranque y middleware --------------------------------------------------


def test_lifespan_marks_ready_and_stopped(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_PUBLISHABLE_KEY", "anon")
    local_app = create_app()

    with TestClient(local_app) as local_client:
        assert local_app.state.ready is True
        assert local_client.get("/health/ready").status_code == 200

    assert local_app.state.ready is False


def test_lifespan_refuses_incomplete_production_config(monkeypatch):
    monkeypatch.setattr(settings, "APP_ENV", "prod")
    monkeypatch.setattr(settings, "SUPABASE_URL", "")
    monkeypatch.setattr(settings, "SUPABASE_PUBLISHABLE_KEY", "")
    monkeypatch.setattr(settings, "COOKIE_SECURE", True)
    monkeypatch.setattr(settings, "TRUSTED_HOSTS", ["example.com"])
    local_app = create_app()

    with pytest.raises(RuntimeError, match="SUPABASE_URL"):
        with TestClient(local_app):
            pass


def test_lifespan_clears_jwks_cache(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_PUBLISHABLE_KEY", "anon")
    jwks.jwks_cache._keys = {"kid": {"kty": "EC"}}
    local_app = create_app()

    try:
        with TestClient(local_app):
            pass
        assert jwks.jwks_cache._keys == {}
    finally:
        jwks.jwks_cache.clear()


def test_trusted_host_rejects_unknown_host(monkeypatch):
    monkeypatch.setattr(settings, "TRUSTED_HOSTS", ["allowed.example"])
    local_app = create_app()
    local_client = TestClient(local_app, base_url="http://allowed.example")

    assert local_client.get("/health", headers={"Host": "allowed.example"}).status_code == 200
    assert local_client.get("/health", headers={"Host": "evil.example"}).status_code == 400


def test_docs_can_be_disabled(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_DOCS", False)
    local_app = create_app()
    local_client = TestClient(local_app)

    assert local_app.openapi_url is None
    assert local_app.docs_url is None
    assert local_client.get("/openapi.json").status_code == 404


# --- Cliente Supabase -------------------------------------------------------


class _FakePostgrest:
    def __init__(self) -> None:
        self.token: str | None = None

    def auth(self, token: str) -> None:
        self.token = token


class _FakeClient:
    def __init__(self) -> None:
        self.postgrest = _FakePostgrest()


def test_per_request_client_uses_configured_timeout(monkeypatch):
    fake = _FakeClient()
    captured: dict = {}

    def fake_create_client(url, key, options=None):
        captured.update(url=url, key=key, options=options)
        return fake

    monkeypatch.setattr(per_request, "create_client", fake_create_client)
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_PUBLISHABLE_KEY", "anon")
    monkeypatch.setattr(settings, "SUPABASE_POSTGREST_TIMEOUT_SECONDS", 7.5)

    result = per_request.get_supabase_for_user("token-123")

    assert result is fake
    assert captured["options"].postgrest_client_timeout == 7.5
    assert fake.postgrest.token == "token-123"


def test_per_request_client_requires_access_token():
    with pytest.raises(RuntimeError, match="access_token"):
        per_request.get_supabase_for_user("")


def test_per_request_client_requires_configuration(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_URL", "")

    with pytest.raises(RuntimeError, match="SUPABASE_URL"):
        per_request.get_supabase_for_user("token-123")
