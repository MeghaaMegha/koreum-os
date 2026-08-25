import asyncio
from app.database import engine
from sqlalchemy import text


async def update_roles():
    async with engine.begin() as conn:
        result = await conn.execute(text(
            "UPDATE roles SET permissions = permissions || "
            "'\"vault:read\"' || '\"vault:write\"' || '\"vault:delete\"' "
            "WHERE name = 'ADMIN' "
            "RETURNING id, name, permissions"
        ))
        rows = result.fetchall()
        print(f"Updated {len(rows)} ADMIN role(s)")
        for row in rows:
            print(f"  Role: {row[1]}, Permissions: {row[2]}")


asyncio.run(update_roles())
