"""Authentication endpoints: login, refresh, me."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import CurrentUser
from app.models.audit import AuditEvent
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


async def _record_audit(db: AsyncSession, tenant_id, actor_id, action: str, details: dict | None = None):
    db.add(
        AuditEvent(
            tenant_id=tenant_id,
            actor_user_id=actor_id,
            action=action,
            details=details,
            created_at=datetime.now(timezone.utc),
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(email: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        # still audit failed login attempts (without leaking whether email exists)
        if user:
            await _record_audit(
                db, user.tenant_id, user.id, "LOGIN_FAILED", {"email": email}
            )
            await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_access_token(user.id, user.tenant_id, user.role_names, user.permissions)
    refresh = create_refresh_token(user.id)

    await _record_audit(db, user.tenant_id, user.id, "USER_LOGIN", {"email": user.email})
    await db.commit()

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    from jose import JWTError

    try:
        decoded = decode_refresh_token(payload.refresh_token)
        user_id = decoded["sub"]
    except (JWTError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    access = create_access_token(user.id, user.tenant_id, user.role_names, user.permissions)
    refresh_tok = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh_tok,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", tags=["auth"])
async def me(current: CurrentUser):
    return {
        "id": str(current.id),
        "email": current.email,
        "full_name": current.full_name,
        "tenant_id": str(current.tenant_id),
        "roles": current.role_names,
        "permissions": current.permissions,
        "is_active": current.is_active,
    }
