import asyncio
from app.database import engine
from sqlalchemy import text


async def check():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
        print("Tables in database:")
        for row in result.fetchall():
            print(f"  - {row[0]}")


asyncio.run(check())
