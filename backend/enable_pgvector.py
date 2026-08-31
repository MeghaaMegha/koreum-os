import asyncio
from app.database import engine
from sqlalchemy import text


async def enable():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        print("pgvector extension enabled")


asyncio.run(enable())
