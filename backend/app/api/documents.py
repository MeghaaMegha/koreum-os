"""Koreum Vault — document upload, list, delete, search endpoints."""
import os
import tempfile
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select

from app.database import get_db
from app.deps import CurrentUser, DBSession, require_permission
from app.models.audit import AuditEvent
from app.models.document import Document
from app.schemas.document import DocumentOut, SearchHit, SearchResponse

router = APIRouter(prefix="/vault/documents", tags=["vault"])

MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB
ALLOWED_CONTENT_TYPES = {
    "text/plain", "text/markdown", "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/csv",
}


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    current: Annotated[CurrentUser, Depends(require_permission("vault:read"))],
    db: DBSession,
):
    result = await db.execute(
        select(Document)
        .where(Document.tenant_id == current.tenant_id)
        .order_by(Document.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    current: Annotated[CurrentUser, Depends(require_permission("vault:write"))],
    db: DBSession,
    file: UploadFile = File(...),
    title: str | None = None,
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 25MB)")

    # Extract text based on file type
    raw_text = None
    if file.content_type in ("text/plain", "text/markdown", "text/csv"):
        raw_text = contents.decode("utf-8", errors="ignore")
    else:
        # PDF/DOCX — placeholder for now, will use a parser later
        raw_text = "[Binary file — text extraction will be added with Gemini API integration]"

    doc = Document(
        tenant_id=current.tenant_id,
        uploaded_by=current.id,
        title=title or file.filename or "Untitled",
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        file_size=len(contents),
        status="uploaded",
        raw_text=raw_text,
    )
    db.add(doc)

    db.add(
        AuditEvent(
            tenant_id=current.tenant_id,
            actor_user_id=current.id,
            action="VAULT_DOCUMENT_UPLOAD",
            details={"document_id": str(doc.id), "filename": doc.filename},
            created_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: str,
    current: Annotated[CurrentUser, Depends(require_permission("vault:read"))],
    db: DBSession,
):
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.tenant_id == current.tenant_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current: Annotated[CurrentUser, Depends(require_permission("vault:delete"))],
    db: DBSession,
):
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.tenant_id == current.tenant_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)

    db.add(
        AuditEvent(
            tenant_id=current.tenant_id,
            actor_user_id=current.id,
            action="VAULT_DOCUMENT_DELETE",
            details={"document_id": str(document_id)},
            created_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    return None


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    current: Annotated[CurrentUser, Depends(require_permission("vault:read"))],
    db: DBSession,
    query: str = "",
    limit: int = 10,
):
    """Simple text search through document raw_text.

    Full semantic search with embeddings will be added with Gemini API integration.
    """
    if not query.strip():
        return SearchResponse(query=query, total=0, hits=[])

    # Simple ILIKE search for now
    result = await db.execute(
        select(Document)
        .where(Document.tenant_id == current.tenant_id, Document.raw_text.ilike(f"%{query}%"))
        .limit(limit)
    )
    docs = result.scalars().all()

    hits = [
        SearchHit(
            chunk_id=doc.id,  # Using doc id as chunk id for now
            document_id=doc.id,
            document_title=doc.title,
            content=doc.raw_text[:500] if doc.raw_text else "",
            chunk_index=0,
            score=1.0,
        )
        for doc in docs
    ]
    return SearchResponse(query=query, total=len(hits), hits=hits)
