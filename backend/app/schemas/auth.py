"""Pydantic schemas for authentication endpoints."""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenClaims(BaseModel):
    sub: str
    tenant_id: str
    roles: list[str] = []
    permissions: list[str] = []
    type: str
