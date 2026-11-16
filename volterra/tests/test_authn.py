from fastapi.testclient import TestClient
from main import app

from apps.core.config import settings

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200


def test_me_without_token_401():
    r = client.get("/api/v1/me/")
    assert r.status_code == 401


def test_clubs_me_without_token_401():
    r = client.get("/api/v1/clubs/me")
    assert r.status_code == 401


def test_security_headers_present():
    r = client.get("/health")

    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["referrer-policy"] == "no-referrer"


def test_api_responses_are_not_cached():
    r = client.get("/api/v1/me/")

    assert r.status_code == 401
    assert r.headers["cache-control"] == "no-store"


def test_cors_allows_configured_origin():
    origin = settings.CORS_ORIGINS[0]
    r = client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == origin
