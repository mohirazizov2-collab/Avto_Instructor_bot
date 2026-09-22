import asyncio
import json
import traceback
from http.server import BaseHTTPRequestHandler

import asyncpg

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Update

from project.config import settings

from project.handlers.start import router as start_router
from project.handlers.registration import router as registration_router
from project.handlers.student import router as student_router
from project.handlers.profile import router as profile_router
from project.handlers.admin import router as admin_router


dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(registration_router)
dp.include_router(student_router)
dp.include_router(profile_router)
dp.include_router(admin_router)


def get_database_url():
    url = settings.DATABASE_URL.strip()

    if url.startswith("postgresql+asyncpg://"):
        url = url.replace(
            "postgresql+asyncpg://",
            "postgresql://",
            1,
        )

    if url.startswith("postgres://"):
        url = url.replace(
            "postgres://",
            "postgresql://",
            1,
        )

    return url


async def process_update(update_data: dict):
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    try:
        update = Update.model_validate(update_data)

        try:
            await dp.feed_update(bot, update)

        except TelegramBadRequest as e:
            print(
                f"TELEGRAM BAD REQUEST (ignored): {e}",
                flush=True,
            )

        except Exception as e:
            print(
                f"HANDLER ERROR: {type(e).__name__}: {e}",
                flush=True,
            )
            traceback.print_exc()

    finally:
        await bot.session.close()


async def database_test():
    url = get_database_url()

    conn = await asyncpg.connect(
        url,
        ssl="require",
        timeout=10,
        command_timeout=10,
    )

    try:
        result = await conn.fetchval("SELECT 1")
        return result

    finally:
        await conn.close()


class handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(
            data,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text, status=200):
        body = text.encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path == "/api/db_test":
            try:
                result = asyncio.run(database_test())

                self.send_json({
                    "ok": True,
                    "database": "connected",
                    "select_1": result,
                })

            except Exception as e:
                print(
                    f"DB_TEST_ERROR: {type(e).__name__}: {e}",
                    flush=True,
                )

                self.send_json({
                    "ok": False,
                    "database": "connection_failed",
                    "error_type": type(e).__name__,
                    "error": str(e),
                }, 500)

            return

        if path in ("/", "/api", "/api/webhook"):
            self.send_text(
                "Avtomaktab bot webhook ishlayapti"
            )
            return

        self.send_json({
            "ok": False,
            "error": "Not found",
            "path": path,
        }, 404)

    def do_POST(self):
        path = self.path.split("?", 1)[0]

        if path != "/api/webhook":
            self.send_json({
                "ok": False,
                "error": "Not found",
                "path": path,
            }, 404)
            return

        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            update_data = json.loads(
                body.decode("utf-8")
            )

            asyncio.run(
                process_update(update_data)
            )

            self.send_text("OK", 200)

        except Exception as e:
            error_text = (
                f"WEBHOOK ERROR: "
                f"{type(e).__name__}: {e}"
            )

            print(
                error_text,
                flush=True,
            )

            self.send_text(
                error_text,
                500,
            )
