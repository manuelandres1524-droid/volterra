from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_platform_requires_token():
    r = client.get("/api/v1/platform/overview")
    assert r.status_code == 401


def test_club_members_requires_auth():
    r = client.get("/api/v1/clubs/00000000-0000-0000-0000-000000000001/members")
    assert r.status_code in (401, 403)
