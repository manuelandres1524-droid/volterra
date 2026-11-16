import pytest
from pydantic import ValidationError

from apps.core.config import Settings


def _settings(**overrides):
    return Settings(_env_file=None, **overrides)


def test_cors_accepts_comma_separated_origins():
    settings = _settings(CORS_ORIGINS="http://localhost:3000, http://localhost:5173")

    assert settings.CORS_ORIGINS == ["http://localhost:3000", "http://localhost:5173"]


def test_cors_accepts_json_array():
    settings = _settings(CORS_ORIGINS='["http://localhost:3000", "http://localhost:5173"]')

    assert settings.CORS_ORIGINS == ["http://localhost:3000", "http://localhost:5173"]


def test_cors_accepts_python_list():
    settings = _settings(CORS_ORIGINS=["http://localhost:3000", "http://localhost:3000"])

    assert settings.CORS_ORIGINS == ["http://localhost:3000"]


def test_cors_empty_string_is_empty_list():
    assert _settings(CORS_ORIGINS="").CORS_ORIGINS == []


def test_cors_rejects_wildcard():
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        _settings(CORS_ORIGINS="*")


def test_cors_rejects_invalid_json():
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        _settings(CORS_ORIGINS='["http://localhost:3000"')


def test_service_role_key_is_not_a_setting():
    assert "SUPABASE_SERVICE_ROLE_KEY" not in Settings.model_fields
