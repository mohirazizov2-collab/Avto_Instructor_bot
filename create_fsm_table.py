import asyncio
from sqlalchemy import text

from project.database.database import engine


async def main():

    async with engine.begin() as conn:

        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS fsm_storage (
                    key TEXT PRIMARY KEY,
                    state TEXT,
                    data TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
        )

    print("✅ fsm_storage jadvali tayyor.")


asyncio.run(main())
