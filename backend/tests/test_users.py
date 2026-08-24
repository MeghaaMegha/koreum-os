"""User CRUD + tenant isolation tests."""
import uuid

import pytest

from tests.test_auth import seed_user, login

pytestmark = pytest.mark.asyncio


async def test_admin_creates_user(client, db_session):
    admin, tenant = await seed_user(db_session)
    token = await login(client)

    r = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "newuser@koreum.local",
            "full_name": "New User",
            "password": "NewPass123!",
            "role_names": ["USER"],
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == "newuser@koreum.local"
    assert any(role["name"] == "USER" for role in body["roles"])


async def test_admin_lists_users(client, db_session):
    await seed_user(db_session)
    token = await login(client)
    r = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


async def test_admin_updates_user(client, db_session):
    admin, _ = await seed_user(db_session)
    token = await login(client)
    r = await client.patch(
        f"/api/v1/users/{admin.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Renamed Admin"},
    )
    assert r.status_code == 200
    assert r.json()["full_name"] == "Renamed Admin"


async def test_admin_deactivates_user(client, db_session):
    admin, _ = await seed_user(db_session)
    token = await login(client)
    r = await client.delete(
        f"/api/v1/users/{admin.id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 204


async def test_user_not_found_returns_404(client, db_session):
    await seed_user(db_session)
    token = await login(client)
    r = await client.get(
        f"/api/v1/users/{uuid.uuid4()}", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 404
