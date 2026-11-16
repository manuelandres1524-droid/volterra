from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_invalid_token_401():
    r = client.get("/api/v1/me/", headers={"Authorization": "Bearer invalid.token.here"})
    assert r.status_code == 401


def test_malformed_header_401():
    r = client.get("/api/v1/me/", headers={"Authorization": "Token abc"})
    assert r.status_code == 401


def test_cross_club_access_denied_shape():
    r = client.get("/api/v1/clubs/00000000-0000-0000-0000-000000000000", headers={"Authorization": "Bearer fake"})
    assert r.status_code in (401, 403, 404)
