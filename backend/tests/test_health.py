import pytest

pytestmark = pytest.mark.asyncio


async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["app"] == "Koreum OS"


async def test_openapi_available(client):
    r = await client.get("/openapi.json")
    assert r.status_code == 200
    assert "paths" in r.json()
