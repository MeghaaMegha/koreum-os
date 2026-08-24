"""User management endpoints (admin-scoped)."""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.database import get_db
from app.deps import CurrentUser, DBSession, require_permission
from app.models.audit import AuditEvent
from app.models.user import Role, User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
async def list_users(
    current: Annotated[User, Depends(require_permission("users:read"))],
    db: DBSession,
    offset: int = 0,
    limit: int = 50,
):
    """List users in the current tenant only."""
    result = await db.execute(
        select(User)
        .where(User.tenant_id == current.tenant_id)
        .offset(offset)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    current: Annotated[User, Depends(require_permission("users:write"))],
    db: DBSession,
):
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Resolve roles within this tenant
    role_result = await db.execute(
        select(Role).where(Role.tenant_id == current.tenant_id, Role.name.in_(payload.role_names))
    )
    roles = role_result.scalars().all()
    if len(roles) != len(set(payload.role_names)):
        raise HTTPException(status_code=400, detail="One or more roles not found")

    from app.security import hash_password

    user = User(
        tenant_id=current.tenant_id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        is_active=True,
        roles=roles,
    )
    db.add(user)
    await db.flush()

    db.add(
        AuditEvent(
            tenant_id=current.tenant_id,
            actor_user_id=current.id,
            action="USER_CREATE",
            details={"user_id": str(user.id), "email": user.email, "roles": payload.role_names},
            created_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: str,
    current: Annotated[User, Depends(require_permission("users:read"))],
    db: DBSession,
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == current.tenant_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    current: Annotated[User, Depends(require_permission("users:write"))],
    db: DBSession,
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == current.tenant_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.email is not None:
        user.email = payload.email
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role_names is not None:
        role_result = await db.execute(
            select(Role).where(Role.tenant_id == current.tenant_id, Role.name.in_(payload.role_names))
        )
        user.roles = role_result.scalars().all()

    db.add(
        AuditEvent(
            tenant_id=current.tenant_id,
            actor_user_id=current.id,
            action="USER_UPDATE",
            details={"user_id": str(user.id), "changes": payload.model_dump(exclude_unset=True)},
            created_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: str,
    current: Annotated[User, Depends(require_permission("users:delete"))],
    db: DBSession,
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == current.tenant_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.add(
        AuditEvent(
            tenant_id=current.tenant_id,
            actor_user_id=current.id,
            action="USER_DEACTIVATE",
            details={"user_id": str(user.id)},
            created_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    return None
