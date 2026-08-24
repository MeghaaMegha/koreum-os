"""${message}

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=True)

    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("permissions", postgresql.JSONB, server_default="[]", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_roles_tenant_id", "roles", ["tenant_id"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("details", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_events_tenant_id", "audit_events", ["tenant_id"])
    op.create_index("ix_audit_events_actor_user_id", "audit_events", ["actor_user_id"])
    op.create_index("ix_audit_events_action", "audit_events", ["action"])
    op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"])

    # --- Seed default tenant, roles, and admin user ---
    from app.config import settings
    from app.deps import DEFAULT_ROLE_PERMISSIONS
    from passlib.context import CryptContext

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

    bind = op.get_bind()
    tenant_id = uuid.uuid4()
    admin_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    bind.execute(
        sa.text(
            "INSERT INTO tenants (id, name, slug, is_active, created_at, updated_at) "
            "VALUES (:id, :name, :slug, true, :now, :now)"
        ),
        {"id": tenant_id, "name": settings.SEED_TENANT_NAME, "slug": settings.SEED_TENANT_SLUG, "now": now},
    )

    role_ids: dict[str, uuid.UUID] = {}
    for role_name, perms in DEFAULT_ROLE_PERMISSIONS.items():
        rid = uuid.uuid4()
        role_ids[role_name] = rid
        bind.execute(
            sa.text(
                "INSERT INTO roles (id, tenant_id, name, permissions, created_at, updated_at) "
                "VALUES (:id, :tid, :name, CAST(:perms AS jsonb), :now, :now)"
            ),
            {"id": rid, "tid": tenant_id, "name": role_name, "perms": __import__("json").dumps(perms), "now": now},
        )

    bind.execute(
        sa.text(
            "INSERT INTO users (id, tenant_id, email, hashed_password, full_name, is_active, created_at, updated_at) "
            "VALUES (:id, :tid, :email, :hp, :fn, true, :now, :now)"
        ),
        {
            "id": admin_id,
            "tid": tenant_id,
            "email": settings.SEED_ADMIN_EMAIL,
            "hp": pwd.hash(settings.SEED_ADMIN_PASSWORD),
            "fn": "Koreum Admin",
            "now": now,
        },
    )

    # Assign ADMIN role to the seeded admin
    bind.execute(
        sa.text("INSERT INTO user_roles (user_id, role_id) VALUES (:uid, :rid)"),
        {"uid": admin_id, "rid": role_ids["ADMIN"]},
    )

    # Seed audit event
    bind.execute(
        sa.text(
            "INSERT INTO audit_events (id, tenant_id, actor_user_id, action, details, created_at) "
            "VALUES (:id, :tid, :uid, 'SYSTEM_SEED', CAST(:details AS jsonb), :now)"
        ),
        {
            "id": uuid.uuid4(),
            "tid": tenant_id,
            "uid": admin_id,
            "details": __import__("json").dumps({"tenant": settings.SEED_TENANT_SLUG, "admin_email": settings.SEED_ADMIN_EMAIL}),
            "now": now,
        },
    )


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("tenants")
