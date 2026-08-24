"""Shared FastAPI dependencies: current user, current tenant, RBAC checks, audit helper."""
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import Role, User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


class TokenData:
    """Resolved token data carried through the request."""

    def __init__(self, user: User):
        self.user = user
        self.tenant_id = user.tenant_id
        self.permissions = user.permissions
        self.role_names = user.role_names


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload["sub"]
    except (JWTError, KeyError) as exc:
        raise credentials_exc from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exc
    return user


def require_permission(*required: str):
    """Dependency factory: require any of the given permissions.

    Usage:
        @router.post(..., dependencies=[Depends(require_permission("users:write"))])
    """

    async def _checker(current: Annotated[User, Depends(get_current_user)]) -> User:
        user_perms = set(current.permissions)
        if not any(p in user_perms for p in required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission(s): {', '.join(required)}",
            )
        return current

    return _checker


def require_role(*roles: str):
    """Dependency factory: require any of the given role names."""

    async def _checker(current: Annotated[User, Depends(get_current_user)]) -> User:
        user_roles = set(current.role_names)
        if not any(r in user_roles for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing role(s): {', '.join(roles)}",
            )
        return current

    return _checker


CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]


# Default permission catalog for seed roles.
# (role name -> list of permissions)
DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "ADMIN": [
        "users:read", "users:write", "users:delete",
        "tenants:read", "tenants:write",
        "agents:read", "agents:write", "agents:execute",
        "workflows:read", "workflows:write", "workflows:execute",
        "audit:read", "policies:read", "policies:write",
    ],
    "PLATFORM_ADMIN": [
        "tenants:read", "tenants:write", "users:read", "audit:read",
    ],
    "AI_ADMIN": [
        "agents:read", "agents:write", "agents:execute",
        "workflows:read", "workflows:write", "workflows:execute",
        "policies:read", "audit:read",
    ],
    "MANAGER": [
        "users:read", "agents:read", "workflows:read", "audit:read",
    ],
    "USER": [
        "agents:read", "workflows:read",
    ],
    "AUDITOR": [
        "audit:read", "users:read", "agents:read", "workflows:read", "policies:read",
    ],
}
