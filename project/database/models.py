from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # Telegram ID 32-bit INTEGER emas, BIGINT bo'lishi kerak
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    instructor: Mapped["Instructor"] = relationship(
        "Instructor",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="Student.user_id",
    )


# ============================================================
# INSTRUCTOR
# ============================================================

class Instructor(Base):
    __tablename__ = "instructors"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    experience_years: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    hourly_price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    gender: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="unknown",
    )

    driving_license_front_photo_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    driving_license_back_photo_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    categories: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    region: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    desired_category: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=5.0,
    )

    vehicle_info: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    vehicle_photo_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    profile_photo_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    tech_passport_front_photo_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    tech_passport_back_photo_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    instructor_certificate_photo_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_approved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="instructor",
    )

    students: Mapped[list["Student"]] = relationship(
        "Student",
        back_populates="instructor",
        foreign_keys="Student.instructor_id",
    )


# ============================================================
# STUDENT
# ============================================================

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    instructor_id: Mapped[int | None] = mapped_column(
        ForeignKey("instructors.id", ondelete="SET NULL"),
        nullable=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    passport_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    profile_photo_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    training_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    desired_category: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="student",
        foreign_keys=[user_id],
    )

    instructor: Mapped["Instructor"] = relationship(
        "Instructor",
        back_populates="students",
        foreign_keys=[instructor_id],
    )