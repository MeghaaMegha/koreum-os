"""Vector store — pgvector-backed similarity search."""
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


async def search_similar(
    db: AsyncSession, tenant_id: Any, query_embedding: list[float], limit: int = 10
) -> list[dict]:
    """Search for similar chunks using cosine distance."""
    vec_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    result = await db.execute(
        text("""
            SELECT
                dc.id AS chunk_id,
                dc.document_id,
                d.title AS document_title,
                dc.content,
                dc.chunk_index,
                1 - (dc.embedding <=> CAST(:vec AS vector)) AS score
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE d.tenant_id = :tid AND dc.embedding IS NOT NULL
            ORDER BY dc.embedding <=> CAST(:vec AS vector)
            LIMIT :lim
        """),
        {"vec": vec_str, "tid": tenant_id, "lim": limit},
    )
    return [
        {
            "chunk_id": str(row.chunk_id),
            "document_id": str(row.document_id),
            "document_title": row.document_title,
            "content": row.content,
            "chunk_index": row.chunk_index,
            "score": float(row.score),
        }
        for row in result.fetchall()
    ]
