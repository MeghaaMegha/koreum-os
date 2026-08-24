"""Tenant management endpoints (platform admin-scoped)."""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.deps import CurrentUser, DBSession, require_permission
from app.models.audit import AuditEvent
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantOut, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=list[TenantOut])
async def list_tenants(
    current: Annotated[CurrentUser, Depends(require_permission("tenants:read"))],
    db: DBSession,
    offset: int = 0,
    limit: int = 50,
):
    result = await db.execute(select(Tenant).offset(offset).limit(limit).order_by(Tenant.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreate,
    current: Annotated[CurrentUser, Depends(require_permission("tenants:write"))],
    db: DBSession,
):
    existing = await db.execute(select(Tenant).where(Tenant.slug == payload.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Slug already taken")
    tenant = Tenant(name=payload.name, slug=payload.slug, is_active=True)
    db.add(tenant)
    await db.flush()
    db.add(
        AuditEvent(
            tenant_id=tenant.id,
            actor_user_id=current.id,
            action="TENANT_CREATE",
            details={"tenant_id": str(tenant.id), "slug": tenant.slug},
            created_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.get("/{tenant_id}", response_model=TenantOut)
async def get_tenant(tenant_id: str, current: CurrentUser, db: DBSession):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.patch("/{tenant_id}", response_model=TenantOut)
async def update_tenant(
    tenant_id: str,
    payload: TenantUpdate,
    current: Annotated[CurrentUser, Depends(require_permission("tenants:write"))],
    db: DBSession,
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if payload.name is not None:
        tenant.name = payload.name
    if payload.is_active is not None:
        tenant.is_active = payload.is_active
    await db.commit()
    await db.refresh(tenant)
    return tenant
