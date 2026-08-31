"""Pydantic schemas for Koreum Vault — documents, chunks, search, collections."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    uploaded_by: UUID | None = None
    title: str
    filename: str
    content_type: str
    file_size: int
    status: str
    created_at: datetime
    updated_at: datetime | None = None
    metadata_: dict[str, Any] | None = None
    collection_id: UUID | None = None
    version: int = 1
    parent_document_id: UUID | None = None


class SearchHit(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    chunk_index: int
    score: float
    search_type: str  # "vector", "keyword", "hybrid"
    source_citation: str  # e.g., "Koreum_OS.pdf, chunk 3"


class SearchResponse(BaseModel):
    query: str
    total: int
    hits: list[SearchHit]
    confidence: float  # 0.0 to 1.0 — based on top hit score
    evidence: list[dict[str, Any]]  # supporting evidence summary


class CollectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    description: str | None = None
    created_at: datetime
    document_count: int = 0
