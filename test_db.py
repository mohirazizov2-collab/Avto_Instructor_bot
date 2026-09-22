import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

url = os.getenv("DATABASE_URL")

print("DATABASE_URL:", "BOR" if url else "YO'Q")

if not url:
    raise SystemExit(1)

if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql+asyncpg://", 1)
elif url.startswith("postgresql://"):
    url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

async def main():
    engine = create_async_engine(
        url,
        poolclass=NullPool,
        connect_args={
            "ssl": "require",
            "command_timeout": 10,
            "timeout": 10,
        },
    )

    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("DATABASE OK:", result.scalar())
    except Exception as e:
        print("DATABASE ERROR:", type(e).__name__)
        print("DETAIL:", str(e))
    finally:
        await engine.dispose()

asyncio.run(main())
