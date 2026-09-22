import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


def get_db_url():
    url = os.getenv("DATABASE_URL", "")

    if not url:
        return "", "DATABASE_URL_MISSING"

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parts = urlsplit(url)

    query_params = [
        (key, value)
        for key, value in parse_qsl(
            parts.query,
            keep_blank_values=True,
        )
        if key.lower() not in {
            "sslmode",
            "channel_binding",
        }
    ]

    url = urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query_params),
            parts.fragment,
        )
    )

    return url, "OK"


async def test_db():
    url, status = get_db_url()

    if status != "OK":
        return {
            "status": "ERROR",
            "reason": status,
        }

    parts = urlsplit(url)

    # Parolni hech qachon response'ga chiqarmaymiz
    safe_info = {
        "scheme": parts.scheme,
        "hostname": parts.hostname,
        "port": parts.port,
        "database": parts.path,
    }

    try:
        engine = create_async_engine(
            url,
            echo=False,
            pool_pre_ping=True,
            connect_args={
                "ssl": "require",
                "timeout": 8,
            },
        )

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()

        await engine.dispose()

        return {
            "status": "OK",
            "database": safe_info,
            "select_1": value,
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "database": safe_info,
            "error_type": type(e).__name__,
            "error": str(e)[:500],
        }


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

    def do_GET(self):
        try:
            result = asyncio.run(test_db())

            status = 200 if result.get("status") == "OK" else 500

            self.send_json(result, status)

        except Exception as e:
            self.send_json(
                {
                    "status": "ERROR",
                    "error_type": type(e).__name__,
                    "error": str(e)[:500],
                },
                500,
            )