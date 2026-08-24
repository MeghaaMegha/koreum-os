"""Model package — import all models so SQLAlchemy registers them on Base.metadata."""
from app.models.audit import AuditEvent
from app.models.tenant import Tenant
from app.models.user import Role, User, user_role

__all__ = ["Tenant", "User", "Role", "user_role", "AuditEvent"]
