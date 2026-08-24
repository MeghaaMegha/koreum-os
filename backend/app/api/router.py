"""Top-level API router that aggregates all module routers."""
from fastapi import APIRouter

from app.api import audit, auth, tenants, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(tenants.router)
api_router.include_router(audit.router)
