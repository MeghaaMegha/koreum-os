import asyncio
import logging
from app.database import engine, AsyncSession
from app.core.chunker import chunk_text
from app.core.embeddings import get_embedding_provider
from app.core.vector_store import store_embedding
from sqlalchemy import select
from app.models.document import Document, DocumentChunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("koreum")


async def reindex():
    async with AsyncSession(engine) as db:
        # Get all documents with raw_text
        result = await db.execute(select(Document))
        docs = result.scalars().all()
        print(f"Found {len(docs)} documents to re-index")

        provider = get_embedding_provider()

        for doc in docs:
            if not doc.raw_text:
                print(f"  Skipping {doc.title} — no raw_text")
                continue

            # Delete existing chunks
            result = await db.execute(
                select(DocumentChunk).where(DocumentChunk.document_id == doc.id)
            )
            old_chunks = result.scalars().all()
            for old_chunk in old_chunks:
                await db.delete(old_chunk)
            await db.flush()

            # Create new chunks
            chunks = chunk_text(doc.raw_text)
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

            # Generate embeddings
            if chunk_records:
                try:
                    texts = [c.content for c in chunk_records]
                    embeddings = provider.embed_batch(texts)
                    for chunk_record, embedding in zip(chunk_records, embeddings):
                        await store_embedding(db, chunk_record.id, embedding)
                    doc.status = "indexed"
                    print(f"  Indexed: {doc.title} ({len(chunks)} chunks)")
                except Exception as e:
                    print(f"  Failed: {doc.title} — {e}")
                    doc.status = "uploaded"

        await db.commit()
        print("\nRe-indexing complete!")


asyncio.run(reindex())
