"""Audit log endpoints (auditor-scoped)."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.deps import CurrentUser, DBSession, require_permission
from app.models.audit import AuditEvent
from app.schemas.audit import AuditEventOut, AuditEventPage

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditEventPage)
async def list_audit_events(
    current: Annotated[CurrentUser, Depends(require_permission("audit:read"))],
    db: DBSession,
    action: str | None = Query(None, description="Filter by action"),
    offset: int = 0,
    limit: int = 50,
):
    base = select(AuditEvent).where(AuditEvent.tenant_id == current.tenant_id)
    count_q = select(func.count()).select_from(AuditEvent).where(AuditEvent.tenant_id == current.tenant_id)
    if action:
        base = base.where(AuditEvent.action == action)
        count_q = count_q.where(AuditEvent.action == action)
    total = (await db.execute(count_q)).scalar_one()
    rows = await db.execute(
        base.order_by(AuditEvent.created_at.desc()).offset(offset).limit(limit)
    )
    return AuditEventPage(
        items=rows.scalars().all(), total=total, limit=limit, offset=offset
    )
