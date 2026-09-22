from __future__ import annotations

import json
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from ..config import settings
from .models import Base, Instructor, Student, User


# ============================================================
# DATABASE URL
# ============================================================

DATABASE_URL = settings.DATABASE_URL.strip()

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+asyncpg://",
        1,
    )

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )


# ============================================================
# REMOVE asyncpg-INCOMPATIBLE URL PARAMETERS
# ============================================================

parts = urlsplit(DATABASE_URL)

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

DATABASE_URL = urlunsplit(
    (
        parts.scheme,
        parts.netloc,
        parts.path,
        urlencode(query_params),
        parts.fragment,
    )
)


# ============================================================
# ENGINE
# ============================================================

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,
    connect_args={
        "ssl": "require",
        "command_timeout": 10,
        "timeout": 10,
    },
)


# ============================================================
# SESSION
# ============================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ============================================================
# INIT DATABASE
# ============================================================

async def init_db() -> None:

    async with engine.begin() as conn:

        await conn.run_sync(
            Base.metadata.create_all
        )

        if conn.dialect.name == "sqlite":
            await _migrate_sqlite(conn)


# ============================================================
# SQLITE MIGRATION
# ============================================================

async def _migrate_sqlite(conn) -> None:

    required_columns = {

        "instructors": {

            "date_of_birth":
                "DATE",

            "experience_years":
                "INTEGER NOT NULL DEFAULT 0",

            "hourly_price":
                "INTEGER NOT NULL DEFAULT 0",

            "gender":
                "VARCHAR(16) NOT NULL DEFAULT 'unknown'",

            "driving_license_number":
                "VARCHAR(64)",

            "driving_license_expiry":
                "DATE",

            "categories":
                "VARCHAR(500)",

            "region":
                "VARCHAR(128)",

            "rating":
                "FLOAT NOT NULL DEFAULT 5.0",

            "vehicle_info":
                "VARCHAR(500)",

            "vehicle_photo_id":
                "VARCHAR(255)",

            "driving_license_front_photo_id":
                "VARCHAR(255)",

            "driving_license_back_photo_id":
                "VARCHAR(255)",

            "profile_photo_id":
                "VARCHAR(255)",

            "tech_passport_front_photo_id":
                "VARCHAR(255)",

            "tech_passport_back_photo_id":
                "VARCHAR(255)",

            "instructor_certificate_photo_id":
                "VARCHAR(255)",

            "is_approved":
                "BOOLEAN NOT NULL DEFAULT 0",
        },

        "students": {

            "instructor_id":
                "INTEGER REFERENCES instructors(id) ON DELETE SET NULL",

            "date_of_birth":
                "DATE",

            "address":
                "VARCHAR(500)",

            "passport_id":
                "VARCHAR(64)",

            "profile_photo_id":
                "VARCHAR(255)",

            "desired_category":
                "VARCHAR(16)",
        },
    }

    for table, columns in required_columns.items():

        result = await conn.execute(
            text(f"PRAGMA table_info({table})")
        )

        existing_columns = {
            row[1]
            for row in result.fetchall()
        }

        for name, definition in columns.items():

            if name not in existing_columns:

                await conn.execute(
                    text(
                        f"ALTER TABLE {table} "
                        f"ADD COLUMN {name} {definition}"
                    )
                )


# ============================================================
# USER
# ============================================================

async def get_user_by_telegram_id(
    telegram_id: int,
) -> User | None:

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        return result.scalar_one_or_none()


# ============================================================
# INSTRUCTOR
# ============================================================

async def get_instructor_by_user_id(
    user_id: int,
) -> Instructor | None:

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Instructor).where(
                Instructor.user_id == user_id
            )
        )

        return result.scalar_one_or_none()


async def get_instructor_by_id(
    instructor_id: int,
) -> Instructor | None:

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Instructor).where(
                Instructor.id == instructor_id
            )
        )

        return result.scalar_one_or_none()


async def get_approved_instructors() -> list[Instructor]:

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Instructor)
            .where(
                Instructor.is_approved.is_(True)
            )
            .order_by(
                Instructor.full_name
            )
        )

        return list(
            result.scalars().all()
        )


async def get_instructors_for_category(
    category: str,
) -> list[Instructor]:

    instructors = await get_approved_instructors()

    category = category.strip().upper()

    result = []

    for instructor in instructors:

        raw_categories = (
            instructor.categories or ""
        ).strip()

        if not raw_categories:
            continue

        # Eski format: ["A", "B"]
        try:
            categories = json.loads(raw_categories)

            if isinstance(categories, list):
                normalized_categories = [
                    str(x).strip().upper()
                    for x in categories
                ]
            else:
                normalized_categories = []

        except (json.JSONDecodeError, TypeError):

            # Hozirgi format: A,B
            normalized_categories = [
                x.strip().upper()
                for x in raw_categories.split(",")
                if x.strip()
            ]

        if category in normalized_categories:
            result.append(instructor)

    return result

async def get_telegram_id_for_instructor(
    instructor: Instructor,
) -> int | None:

    async with AsyncSessionLocal() as session:

        user = await session.get(
            User,
            instructor.user_id,
        )

        if user:
            return user.telegram_id

        return None


# ============================================================
# STUDENT
# ============================================================

async def get_student_by_user_id(
    user_id: int,
) -> Student | None:

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Student).where(
                Student.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

