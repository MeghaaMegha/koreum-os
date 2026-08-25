"""Pydantic schemas for documents and chunks."""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    uploaded_by: Optional[uuid.UUID]
    title: str
    filename: str
    content_type: str
    file_size: int
    status: str
    created_at: datetime
    metadata_: Optional[dict[str, Any]] = None


class SearchHit(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    content: str
    chunk_index: int
    score: float


class SearchResponse(BaseModel):
    query: str
    total: int
    hits: list[SearchHit]
