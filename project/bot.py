import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramNetworkError, TelegramServerError
from aiogram.fsm.storage.memory import MemoryStorage

try:
    from .config import settings

    from .handlers.start import router as start_router
    from .handlers.registration import router as registration_router
    from .handlers.student import router as student_router
    from .handlers.profile import router as profile_router
    from .handlers.admin import router as admin_router

except ImportError:
    from config import settings

    from handlers.start import router as start_router
    from handlers.registration import router as registration_router
    from handlers.student import router as student_router
    from handlers.profile import router as profile_router
    from handlers.admin import router as admin_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def delete_webhook_with_retry(
    bot: Bot,
    attempts: int = 5,
) -> bool:

    for attempt in range(1, attempts + 1):

        try:
            await bot.delete_webhook(
                drop_pending_updates=True
            )
            return True

        except (
            TelegramNetworkError,
            TelegramServerError,
        ) as exc:

            if attempt == attempts:

                logger.warning(
                    "Webhookni o'chirib bo'lmadi: %s. "
                    "Polling rejimi bilan davom etiladi.",
                    exc,
                )

                return False

            delay = attempt * 3

            logger.warning(
                "Telegram bilan ulanish muvaffaqiyatsiz "
                "(%s/%s): %s. "
                "%s soniyadan keyin qayta urinish.",
                attempt,
                attempts,
                exc,
                delay,
            )

            await asyncio.sleep(delay)


async def main() -> None:

    if not settings.BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN bo'sh. "
            ".env faylida qiymat kiriting."
        )

    dp = Dispatcher(
        storage=MemoryStorage()
    )

    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(student_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)

    async with Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        ),
    ) as bot:

        logger.info(
            "Avtomaktab bot ishga tushmoqda..."
        )

        await delete_webhook_with_retry(bot)

        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
