import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./avtomaktab.db",
    )
    APP_NAME: str = os.getenv(
        "APP_NAME",
        "Avtomaktab Bot",
    )
    LOG_LEVEL: str = os.getenv(
        "LOG_LEVEL",
        "INFO",
    )
    ADMIN_GROUP_ID: int = int(
        os.getenv(
            "ADMIN_GROUP_ID",
            "0",
        )
    )


settings = Settings()
