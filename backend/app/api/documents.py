"""Koreum Vault — document upload, list, delete, search endpoints."""
import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select

from app.core.chunker import chunk_text
from app.core.embeddings import get_embedding_provider
from app.core.vector_store import search_similar, store_embedding
from app.database import get_db
from app.deps import CurrentUser, DBSession, require_permission
from app.models.audit import AuditEvent
from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentOut, SearchHit, SearchResponse

logger = logging.getLogger("koreum")
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
    if file.content_type in ("text/plain", "text/markdown", "text/csv"):
        raw_text = contents.decode("utf-8", errors="ignore")
    elif file.content_type == "application/pdf":
        try:
            import io
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(contents))
            raw_text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            raw_text = "[PDF parsing requires PyPDF2: pip install PyPDF2]"
        except Exception:
            raw_text = "[Failed to extract PDF text]"
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            import io
            from docx import Document as DocxDocument
            doc = DocxDocument(io.BytesIO(contents))
            raw_text = "\n\n".join(para.text for para in doc.paragraphs if para.text)
        except ImportError:
            raw_text = "[DOCX parsing requires python-docx: pip install python-docx]"
        except Exception:
            raw_text = "[Failed to extract DOCX text]"
    else:
        raw_text = "[Unsupported file type for text extraction]"

    # Create document
    doc = Document(
        tenant_id=current.tenant_id,
        uploaded_by=current.id,
        title=title or file.filename or "Untitled",
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        file_size=len(contents),
        status="processing",
        raw_text=raw_text,
    )
    db.add(doc)
    await db.flush()

    # Chunk the text
    chunks = chunk_text(raw_text) if raw_text else []

    # Create chunk records
    chunk_records = []
    for chunk in chunks:
        chunk_record = DocumentChunk(
            document_id=doc.id,
            chunk_index=chunk.index,
            content=chunk.content,
        )
        db.add(chunk_record)
        chunk_records.append(chunk_record)
    await db.flush()

    # Generate and store embeddings
    if chunk_records:
        try:
            provider = get_embedding_provider()
            texts = [c.content for c in chunk_records]
            embeddings = provider.embed_batch(texts)
            for chunk_record, embedding in zip(chunk_records, embeddings):
                await store_embedding(db, chunk_record.id, embedding)
            doc.status = "indexed"
            logger.info(f"Indexed document {doc.id} with {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            doc.status = "uploaded"
    else:
        doc.status = "uploaded"

    db.add(
        AuditEvent(
            tenant_id=current.tenant_id,
            actor_user_id=current.id,
            action="VAULT_DOCUMENT_UPLOAD",
            details={"document_id": str(doc.id), "filename": doc.filename, "chunks": len(chunks)},
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
    """Semantic vector search through document chunks."""
    if not query.strip():
        return SearchResponse(query=query, total=0, hits=[])

    try:
        provider = get_embedding_provider()
        query_embedding = provider.embed(query)
        hits = await search_similar(db, current.tenant_id, query_embedding, limit)
        return SearchResponse(
            query=query,
            total=len(hits),
            hits=[SearchHit(**hit) for hit in hits],
        )
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
