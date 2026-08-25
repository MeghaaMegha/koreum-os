"""Tenant management + audit log tests."""
import uuid

import pytest

from tests.test_auth import seed_user, login

pytestmark = pytest.mark.asyncio


async def test_admin_lists_tenants(client, db_session):
    await seed_user(db_session)
    token = await login(client)
    r = await client.get("/api/v1/tenants", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


async def test_admin_creates_tenant(client, db_session):
    await seed_user(db_session)
    token = await login(client)
    r = await client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Acme Corp", "slug": "acme"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["name"] == "Acme Corp"
    assert body["slug"] == "acme"
    assert body["is_active"] is True


async def test_duplicate_slug_rejected(client, db_session):
    await seed_user(db_session)
    token = await login(client)
    # First create
    await client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Acme Corp", "slug": "acme"},
    )
    # Duplicate slug
    r = await client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Acme Corp 2", "slug": "acme"},
    )
    assert r.status_code == 400
    assert "Slug already taken" in r.json()["detail"]


async def test_admin_lists_audit_events(client, db_session):
    await seed_user(db_session)
    token = await login(client)
    # Login generates an audit event
    r = await client.get(
        "/api/v1/audit?limit=100", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert body["total"] >= 1


async def test_rbac_user_cannot_list_tenants(client, db_session):
    await seed_user(db_session, email="plain@koreum.local", role_name="USER")
    token = await login(client, email="plain@koreum.local")
    r = await client.get(
        "/api/v1/tenants", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 403
