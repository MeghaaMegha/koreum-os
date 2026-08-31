"""Vector store — pgvector-backed similarity search with hybrid + keyword support."""
import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("koreum")


async def store_embedding(db: AsyncSession, chunk_id: Any, embedding: list[float]) -> None:
    """Store an embedding vector for a document chunk."""
    vec_str = "[" + ",".join(str(x) for x in embedding) + "]"
    await db.execute(
        text("UPDATE document_chunks SET embedding = CAST(:vec AS vector) WHERE id = :cid"),
        {"vec": vec_str, "cid": chunk_id},
    )


async def search_vector(
    db: AsyncSession, tenant_id: Any, query_embedding: list[float], limit: int = 10
) -> list[dict]:
    """Pure vector similarity search."""
    vec_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    result = await db.execute(
        text("""
            SELECT
                dc.id AS chunk_id,
                dc.document_id,
                d.title AS document_title,
                d.filename AS document_filename,
                dc.content,
                dc.chunk_index,
                1 - (dc.embedding <=> CAST(:vec AS vector)) AS score
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE d.tenant_id = :tid AND dc.embedding IS NOT NULL AND d.lifecycle_state = 'active'
            ORDER BY dc.embedding <=> CAST(:vec AS vector)
            LIMIT :lim
        """),
        {"vec": vec_str, "tid": tenant_id, "lim": limit},
    )
    hits = []
    for row in result.fetchall():
        hits.append({
            "chunk_id": str(row.chunk_id),
            "document_id": str(row.document_id),
            "document_title": row.document_title,
            "content": row.content,
            "chunk_index": row.chunk_index,
            "score": float(row.score),
            "search_type": "vector",
            "source_citation": f"{row.document_filename}, chunk {row.chunk_index}",
        })
    return hits


async def search_keyword(
    db: AsyncSession, tenant_id: Any, query: str, limit: int = 10
) -> list[dict]:
    """Pure keyword search using ILIKE."""
    result = await db.execute(
        text("""
            SELECT
                dc.id AS chunk_id,
                dc.document_id,
                d.title AS document_title,
                d.filename AS document_filename,
                dc.content,
                dc.chunk_index,
                0.5 AS score
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE d.tenant_id = :tid AND d.lifecycle_state = 'active'
              AND dc.content ILIKE :pattern
            ORDER BY dc.chunk_index
            LIMIT :lim
        """),
        {"tid": tenant_id, "pattern": f"%{query}%", "lim": limit},
    )
    hits = []
    for row in result.fetchall():
        hits.append({
            "chunk_id": str(row.chunk_id),
            "document_id": str(row.document_id),
            "document_title": row.document_title,
            "content": row.content,
            "chunk_index": row.chunk_index,
            "score": float(row.score),
            "search_type": "keyword",
            "source_citation": f"{row.document_filename}, chunk {row.chunk_index}",
        })
    return hits


async def search_hybrid(
    db: AsyncSession, tenant_id: Any, query: str, query_embedding: list[float], limit: int = 10
) -> list[dict]:
    """Hybrid search — combines vector + keyword, deduplicates, re-ranks."""
    vec_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    result = await db.execute(
        text("""
            SELECT
                dc.id AS chunk_id,
                dc.document_id,
                d.title AS document_title,
                d.filename AS document_filename,
                dc.content,
                dc.chunk_index,
                1 - (dc.embedding <=> CAST(:vec AS vector)) AS vector_score,
                CASE WHEN dc.content ILIKE :pattern THEN 0.3 ELSE 0 END AS keyword_bonus
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE d.tenant_id = :tid AND dc.embedding IS NOT NULL AND d.lifecycle_state = 'active'
            ORDER BY (1 - (dc.embedding <=> CAST(:vec AS vector))) + 
                     CASE WHEN dc.content ILIKE :pattern THEN 0.3 ELSE 0 END DESC
            LIMIT :lim
        """),
        {"vec": vec_str, "tid": tenant_id, "pattern": f"%{query}%", "lim": limit},
    )
    hits = []
    for row in result.fetchall():
        combined_score = float(row.vector_score) + float(row.keyword_bonus)
        hits.append({
            "chunk_id": str(row.chunk_id),
            "document_id": str(row.document_id),
            "document_title": row.document_title,
            "content": row.content,
            "chunk_index": row.chunk_index,
            "score": combined_score,
            "search_type": "hybrid",
            "source_citation": f"{row.document_filename}, chunk {row.chunk_index}",
        })
    return hits


async def search_similar(
    db: AsyncSession, tenant_id: Any, query_embedding: list[float], limit: int = 10
) -> list[dict]:
    """Backward-compatible wrapper — calls search_vector."""
    return await search_vector(db, tenant_id, query_embedding, limit)
