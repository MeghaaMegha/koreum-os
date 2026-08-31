import asyncio
from app.database import engine
from sqlalchemy import text


async def check():
    async with engine.begin() as conn:
        # Check lifecycle_state values
        result = await conn.execute(text("SELECT id, title, lifecycle_state FROM documents LIMIT 10"))
        print("Documents:")
        for row in result.fetchall():
            print(f"  {row[1]}: lifecycle_state = '{row[2]}'")

        # Check embeddings
        result = await conn.execute(text("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL"))
        print(f"\nChunks with embeddings: {result.fetchone()[0]}")

        # Test hybrid search directly
        result = await conn.execute(text("""
            SELECT COUNT(*) FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE d.lifecycle_state = 'active' AND dc.embedding IS NOT NULL
        """))
        print(f"Matching chunks (active + has embedding): {result.fetchone()[0]}")


asyncio.run(check())
