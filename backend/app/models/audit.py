"""AuditEvent — generic, append-only record of significant platform actions."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDPK
from app.models.types import GUID

if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.user import User


class AuditEvent(UUIDPK):
    __tablename__ = "audit_events"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    tenant: Mapped["Tenant"] = relationship()  # noqa: F821
    actor: Mapped["User | None"] = relationship(back_populates="audit_events")

    def __repr__(self) -> str:
        return f"<AuditEvent {self.action}>"
