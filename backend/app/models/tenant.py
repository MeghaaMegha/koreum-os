"""Tenant model — the top-level isolation boundary."""
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDPK, TimestampMixin


class Tenant(UUIDPK, TimestampMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")  # noqa: F821
    roles: Mapped[list["Role"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Tenant {self.slug}>"
