import asyncio
from project.config import settings
from aiogram import Bot

async def main():
    async with Bot(settings.BOT_TOKEN) as bot:
        info = await bot.get_webhook_info()
        print(info)

asyncio.run(main())