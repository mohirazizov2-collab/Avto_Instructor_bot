import asyncio
from sqlalchemy import text
from project.database.database import engine

async def main():
    print("DB TEST: boshladi")

    async with engine.connect() as conn:
        print("DB TEST: connection OK")
        result = await conn.execute(text("SELECT 1"))
        print("DB TEST:", result.scalar())

asyncio.run(main())
