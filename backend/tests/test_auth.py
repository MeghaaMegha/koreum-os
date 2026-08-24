"""Auth + RBAC + tenant-isolation tests.

These tests seed a tenant/user/roles directly (mirroring the init migration)
so they run against the in-memory SQLite DB without Alembic.
"""
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select

import app.models  # noqa: F401
from app.models.tenant import Tenant
from app.models.user import Role, User
from app.security import hash_password

pytestmark = pytest.mark.asyncio

ROLE_PERMS = {
    "ADMIN": ["users:read", "users:write", "users:delete", "audit:read"],
    "USER": ["agents:read"],
}


async def seed_user(db_session, email="admin@koreum.local", role_name="ADMIN"):
    tenant = Tenant(name="Test Tenant", slug=f"test-{uuid.uuid4().hex[:6]}", is_active=True)
    db_session.add(tenant)
    await db_session.flush()

    role = Role(tenant_id=tenant.id, name=role_name, permissions=ROLE_PERMS[role_name])
    db_session.add(role)
    await db_session.flush()

    user = User(
        tenant_id=tenant.id,
        email=email,
        hashed_password=hash_password("Admin123!"),
        full_name="Test Admin",
        is_active=True,
        roles=[role],
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user, tenant


async def login(client, email="admin@koreum.local", password="Admin123!"):
    r = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


async def test_login_success(client, db_session):
    await seed_user(db_session)
    token = await login(client)
    assert token


async def test_login_invalid_password(client, db_session):
    await seed_user(db_session)
    r = await client.post(
        "/api/v1/auth/login", json={"email": "admin@koreum.local", "password": "wrong"}
    )
    assert r.status_code == 401


async def test_me(client, db_session):
    await seed_user(db_session)
    token = await login(client)
    r = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "admin@koreum.local"
    assert "ADMIN" in body["roles"]


async def test_users_list_requires_auth(client):
    r = await client.get("/api/v1/users")
    assert r.status_code == 401


async def test_rbac_user_cannot_list_users(client, db_session):
    # A plain USER (no users:read) cannot list users
    await seed_user(db_session, email="plain@koreum.local", role_name="USER")
    token = await login(client, email="plain@koreum.local")
    r = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


async def test_refresh_token(client, db_session):
    await seed_user(db_session)
    r = await client.post(
        "/api/v1/auth/login", json={"email": "admin@koreum.local", "password": "Admin123!"}
    )
    refresh = r.json()["refresh_token"]
    r2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r2.status_code == 200
    assert "access_token" in r2.json()
