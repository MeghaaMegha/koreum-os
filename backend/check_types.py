import asyncio
from app.database import engine
from sqlalchemy import text


async def check():
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name IN ('tenants', 'documents', 'document_chunks')
            AND column_name IN ('id', 'tenant_id', 'document_id')
            ORDER BY table_name, column_name
        """))
        print("Column types:")
        for row in result.fetchall():
            print(f"  {row[0]}.{row[1]} = {row[2]}")


asyncio.run(check())
