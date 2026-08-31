"""Add collections, versioning, lifecycle, lineage to documents

Revision ID: d3b2a4f8c012
Revises: c2a1f3e7b901
Create Date: 2026-08-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = "d3b2a4f8c012"
down_revision: Union[str, None] = "c2a1f3e7b901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create knowledge_collections table
    op.create_table(
        "knowledge_collections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Add new columns to documents
    op.add_column("documents", sa.Column("lifecycle_state", sa.String(50), server_default="active", nullable=False))
    op.add_column("documents", sa.Column("collection_id", UUID(as_uuid=True), sa.ForeignKey("knowledge_collections.id", ondelete="SET NULL"), nullable=True, index=True))
    op.add_column("documents", sa.Column("version", sa.Integer(), server_default="1", nullable=False))
    op.add_column("documents", sa.Column("parent_document_id", UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True))
    op.add_column("documents", sa.Column("source_type", sa.String(100), server_default="upload", nullable=False))
    op.add_column("documents", sa.Column("source_uri", sa.String(1000), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "source_uri")
    op.drop_column("documents", "source_type")
    op.drop_column("documents", "parent_document_id")
    op.drop_column("documents", "version")
    op.drop_column("documents", "collection_id")
    op.drop_column("documents", "lifecycle_state")
    op.drop_table("knowledge_collections")
