"""User and Role models with RBAC."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Table, Column
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDPK, TimestampMixin

if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.audit import AuditEvent


# association table: many-to-many users <-> roles
user_role = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Role(UUIDPK, TimestampMixin):
    __tablename__ = "roles"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    permissions: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    tenant: Mapped["Tenant"] = relationship(back_populates="roles")
    users: Mapped[list["User"]] = relationship(secondary=user_role, back_populates="roles")

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class User(UUIDPK, TimestampMixin):
    __tablename__ = "users"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    roles: Mapped[list[Role]] = relationship(secondary=user_role, back_populates="users", lazy="selectin")
    audit_events: Mapped[list["AuditEvent"]] = relationship(back_populates="actor")  # noqa: F821

    @property
    def role_names(self) -> list[str]:
        return [r.name for r in self.roles]

    @property
    def permissions(self) -> list[str]:
        perms: set[str] = set()
        for r in self.roles:
            perms.update(r.permissions or [])
        return sorted(perms)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
