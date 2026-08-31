import asyncio
from app.database import engine
from sqlalchemy import text


async def fix():
    async with engine.begin() as conn:
        # Check current column type
        result = await conn.execute(text("""
            SELECT data_type FROM information_schema.columns
            WHERE table_name = 'document_chunks' AND column_name = 'embedding'
        """))
        row = result.fetchone()
        print(f"Current embedding type: {row[0] if row else 'NOT FOUND'}")

        # Drop and recreate as vector(768)
        await conn.execute(text("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768) USING NULL"))
        print("Changed embedding column to vector(768)")


asyncio.run(fix())
