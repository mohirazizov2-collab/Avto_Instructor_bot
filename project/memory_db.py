"""
Bu fayl avvalgi xotira-asosidagi (RAM) memory_db.py o'rnini bosadi.
Endi barcha ma'lumotlar Firebase Firestore'da DOIMIY saqlanadi.

MUHIM: Barcha funksiya va klass nomlari eskisi bilan bir xil qoldirilgan,
shuning uchun handlers/*.py fayllarida hech narsani o'zgartirish shart emas.
"""

import json
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from google.cloud import firestore as gcf

from .database.firebase import get_firestore


@dataclass
class User:
    id: int
    telegram_id: int
    role: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Instructor:
    id: int
    user_id: int
    full_name: str = ""
    phone: str = ""
    date_of_birth: Optional[str] = None
    experience_years: int = 0
    hourly_price: int = 0
    gender: str = ""
    driving_license_number: Optional[str] = None
    driving_license_expiry: Optional[str] = None
    driving_license_front_photo_id: Optional[str] = None
    driving_license_back_photo_id: Optional[str] = None
    categories: str = "[]"
    region: Optional[str] = None
    desired_category: Optional[str] = None
    rating: float = 5.0
    vehicle_info: Optional[str] = None
    vehicle_photo_id: Optional[str] = None
    tech_passport_front_photo_id: Optional[str] = None
    tech_passport_back_photo_id: Optional[str] = None
    instructor_certificate_photo_id: Optional[str] = None
    profile_photo_id: Optional[str] = None
    is_approved: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Student:
    id: int
    user_id: int
    instructor_id: Optional[int] = None
    full_name: str = ""
    phone: str = ""
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    passport_id: Optional[str] = None
    profile_photo_id: Optional[str] = None
    training_type: str = ""
    desired_category: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


_USERS = "users"
_INSTRUCTORS = "instructors"
_STUDENTS = "students"
_COUNTERS = "counters"


def _next_id(name: str) -> int:
    """Firestore orqali xavfsiz (atomik) o'sib boruvchi ID yaratadi."""

    db = get_firestore()
    counter_ref = db.collection(_COUNTERS).document(name)
    transaction = db.transaction()

    @gcf.transactional
    def _bump(tx):
        snapshot = counter_ref.get(transaction=tx)
        current = (snapshot.get("value") if snapshot.exists else 0) or 0
        new_value = current + 1
        tx.set(counter_ref, {"value": new_value})
        return new_value

    return _bump(transaction)


def _user_from_doc(doc) -> Optional[User]:
    if doc is None or not doc.exists:
        return None

    data = doc.to_dict()

    return User(
        id=data.get("id"),
        telegram_id=data.get("telegram_id"),
        role=data.get("role", ""),
        created_at=data.get("created_at") or datetime.now(),
    )


def _instructor_from_doc(doc) -> Optional[Instructor]:
    if doc is None or not doc.exists:
        return None

    data = doc.to_dict()

    return Instructor(
        id=data.get("id"),
        user_id=data.get("user_id"),
        full_name=data.get("full_name", ""),
        phone=data.get("phone", ""),
        date_of_birth=data.get("date_of_birth"),
        experience_years=data.get("experience_years", 0) or 0,
        hourly_price=data.get("hourly_price", 0) or 0,
        gender=data.get("gender", ""),
        driving_license_number=data.get("driving_license_number"),
        driving_license_expiry=data.get("driving_license_expiry"),
        driving_license_front_photo_id=data.get(
            "driving_license_front_photo_id"
        ),
        driving_license_back_photo_id=data.get(
            "driving_license_back_photo_id"
        ),
        categories=data.get("categories", "[]"),
        region=data.get("region"),
        desired_category=data.get("desired_category"),
        rating=data.get("rating", 5.0),
        vehicle_info=data.get("vehicle_info"),
        vehicle_photo_id=data.get("vehicle_photo_id"),
        tech_passport_front_photo_id=data.get(
            "tech_passport_front_photo_id"
        ),
        tech_passport_back_photo_id=data.get(
            "tech_passport_back_photo_id"
        ),
        instructor_certificate_photo_id=data.get(
            "instructor_certificate_photo_id"
        ),
        profile_photo_id=data.get("profile_photo_id"),
        is_approved=data.get("is_approved", False),
        created_at=data.get("created_at") or datetime.now(),
    )


def _student_from_doc(doc) -> Optional[Student]:
    if doc is None or not doc.exists:
        return None

    data = doc.to_dict()

    return Student(
        id=data.get("id"),
        user_id=data.get("user_id"),
        instructor_id=data.get("instructor_id"),
        full_name=data.get("full_name", ""),
        phone=data.get("phone", ""),
        date_of_birth=data.get("date_of_birth"),
        address=data.get("address"),
        passport_id=data.get("passport_id"),
        profile_photo_id=data.get("profile_photo_id"),
        training_type=data.get("training_type", ""),
        desired_category=data.get("desired_category"),
        created_at=data.get("created_at") or datetime.now(),
    )


async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    db = get_firestore()

    query = (
        db.collection(_USERS)
        .where("telegram_id", "==", telegram_id)
        .limit(1)
    )

    docs = list(query.stream())

    if not docs:
        return None

    return _user_from_doc(docs[0])


async def get_or_create_user(telegram_id: int, role: str) -> User:
    db = get_firestore()

    existing = await get_user_by_telegram_id(telegram_id)

    if existing is not None:
        db.collection(_USERS).document(
            str(existing.id)
        ).update({"role": role})

        existing.role = role

        return existing

    new_id = _next_id(_USERS)
    user = User(id=new_id, telegram_id=telegram_id, role=role)

    db.collection(_USERS).document(str(new_id)).set({
        "id": user.id,
        "telegram_id": user.telegram_id,
        "role": user.role,
        "created_at": user.created_at,
    })

    return user


async def get_user_by_id(user_id: int):
    db = get_firestore()
    doc = db.collection(_USERS).document(str(user_id)).get()
    return _user_from_doc(doc)


async def get_instructor_by_id(
    instructor_id: int,
) -> Optional[Instructor]:
    db = get_firestore()
    doc = db.collection(_INSTRUCTORS).document(str(instructor_id)).get()
    return _instructor_from_doc(doc)


async def get_instructor_by_user_id(
    user_id: int,
) -> Optional[Instructor]:
    db = get_firestore()

    query = (
        db.collection(_INSTRUCTORS)
        .where("user_id", "==", user_id)
        .limit(1)
    )

    docs = list(query.stream())

    if not docs:
        return None

    return _instructor_from_doc(docs[0])


async def get_student_by_user_id(
    user_id: int,
) -> Optional[Student]:
    db = get_firestore()

    query = (
        db.collection(_STUDENTS)
        .where("user_id", "==", user_id)
        .limit(1)
    )

    docs = list(query.stream())

    if not docs:
        return None

    return _student_from_doc(docs[0])


async def get_telegram_id_for_instructor(
    instructor_id: int,
) -> Optional[int]:
    instructor = await get_instructor_by_id(instructor_id)

    if instructor is None:
        return None

    user = await get_user_by_id(instructor.user_id)

    if user is None:
        return None

    return user.telegram_id


def _parse_categories(categories: Optional[str]) -> list[str]:
    if not categories:
        return []

    try:
        parsed = json.loads(categories)

        if isinstance(parsed, list):
            return [
                str(item).strip().upper()
                for item in parsed
                if str(item).strip()
            ]
    except (json.JSONDecodeError, TypeError):
        pass

    return [
        item.strip().upper()
        for item in categories.split(",")
        if item.strip()
    ]


async def get_instructors_for_category(
    category: str,
) -> list[Instructor]:
    category = category.strip().upper()

    db = get_firestore()

    query = db.collection(_INSTRUCTORS).where(
        "is_approved", "==", True
    )

    result = []

    for doc in query.stream():
        instructor = _instructor_from_doc(doc)

        if instructor is None:
            continue

        categories = _parse_categories(instructor.categories)

        if category in categories:
            result.append(instructor)

    return result


async def save_instructor(
    user: User,
    data: dict,
) -> Instructor:

    db = get_firestore()

    existing = await get_instructor_by_user_id(user.id)

    if existing is None:
        instructor_id = _next_id(_INSTRUCTORS)
        instructor = Instructor(id=instructor_id, user_id=user.id)
    else:
        instructor = existing

    instructor.full_name = data.get(
        "instructor_name",
        data.get("full_name", ""),
    )

    instructor.phone = data.get(
        "instructor_phone",
        data.get("phone", ""),
    )

    instructor.date_of_birth = data.get("date_of_birth")

    instructor.experience_years = int(
        data.get("experience_years", 0) or 0
    )

    instructor.hourly_price = int(
        data.get("hourly_price", 0) or 0
    )

    instructor.gender = data.get("gender", "")

    instructor.driving_license_number = data.get(
        "driving_license_number"
    )

    instructor.driving_license_expiry = data.get(
        "driving_license_expiry"
    )

    instructor.driving_license_front_photo_id = data.get(
        "driving_license_front_photo_id"
    )

    instructor.driving_license_back_photo_id = data.get(
        "driving_license_back_photo_id"
    )

    categories = data.get("categories", [])

    if isinstance(categories, list):
        instructor.categories = json.dumps(categories)
    else:
        instructor.categories = str(categories)

    instructor.region = data.get("region")
    instructor.desired_category = data.get("desired_category")
    instructor.vehicle_info = data.get("vehicle_info")
    instructor.vehicle_photo_id = data.get("vehicle_photo_id")

    instructor.tech_passport_front_photo_id = data.get(
        "tech_passport_front_photo_id"
    )

    instructor.tech_passport_back_photo_id = data.get(
        "tech_passport_back_photo_id"
    )

    instructor.instructor_certificate_photo_id = data.get(
        "instructor_certificate_photo_id"
    )

    instructor.profile_photo_id = data.get("profile_photo_id")
    instructor.is_approved = False

    db.collection(_INSTRUCTORS).document(str(instructor.id)).set({
        "id": instructor.id,
        "user_id": instructor.user_id,
        "full_name": instructor.full_name,
        "phone": instructor.phone,
        "date_of_birth": instructor.date_of_birth,
        "experience_years": instructor.experience_years,
        "hourly_price": instructor.hourly_price,
        "gender": instructor.gender,
        "driving_license_number": instructor.driving_license_number,
        "driving_license_expiry": instructor.driving_license_expiry,
        "driving_license_front_photo_id": instructor.driving_license_front_photo_id,
        "driving_license_back_photo_id": instructor.driving_license_back_photo_id,
        "categories": instructor.categories,
        "region": instructor.region,
        "desired_category": instructor.desired_category,
        "rating": instructor.rating,
        "vehicle_info": instructor.vehicle_info,
        "vehicle_photo_id": instructor.vehicle_photo_id,
        "tech_passport_front_photo_id": instructor.tech_passport_front_photo_id,
        "tech_passport_back_photo_id": instructor.tech_passport_back_photo_id,
        "instructor_certificate_photo_id": instructor.instructor_certificate_photo_id,
        "profile_photo_id": instructor.profile_photo_id,
        "is_approved": instructor.is_approved,
        "created_at": instructor.created_at,
    })

    return instructor


async def save_student(
    user: User,
    data: dict,
    instructor_id: Optional[int] = None,
) -> Student:

    db = get_firestore()

    existing = await get_student_by_user_id(user.id)

    if existing is None:
        student_id = _next_id(_STUDENTS)
        student = Student(id=student_id, user_id=user.id)
    else:
        student = existing

    student.instructor_id = instructor_id
    student.full_name = data.get("full_name", "")
    student.phone = data.get("phone", "")
    student.date_of_birth = data.get("date_of_birth")
    student.address = data.get("address")
    student.passport_id = data.get("passport_id")
    student.profile_photo_id = data.get("profile_photo_id")
    student.training_type = data.get("training_type", "matching")
    student.desired_category = data.get("desired_category")

    db.collection(_STUDENTS).document(str(student.id)).set({
        "id": student.id,
        "user_id": student.user_id,
        "instructor_id": student.instructor_id,
        "full_name": student.full_name,
        "phone": student.phone,
        "date_of_birth": student.date_of_birth,
        "address": student.address,
        "passport_id": student.passport_id,
        "profile_photo_id": student.profile_photo_id,
        "training_type": student.training_type,
        "desired_category": student.desired_category,
        "created_at": student.created_at,
    })

    user.role = "student"

    db.collection(_USERS).document(str(user.id)).update(
        {"role": "student"}
    )

    return student


async def approve_instructor(
    instructor_id: int,
) -> Optional[Instructor]:

    instructor = await get_instructor_by_id(instructor_id)

    if instructor is None:
        return None

    db = get_firestore()

    db.collection(_INSTRUCTORS).document(
        str(instructor_id)
    ).update({"is_approved": True})

    instructor.is_approved = True

    return instructor


async def reject_instructor(
    instructor_id: int,
) -> Optional[Instructor]:

    instructor = await get_instructor_by_id(instructor_id)

    if instructor is None:
        return None

    db = get_firestore()

    db.collection(_INSTRUCTORS).document(
        str(instructor_id)
    ).update({"is_approved": False})

    instructor.is_approved = False

    return instructor


def get_all_instructors() -> list:
    db = get_firestore()
    return [
        _instructor_from_doc(doc)
        for doc in db.collection(_INSTRUCTORS).stream()
    ]


def get_all_students() -> list:
    db = get_firestore()
    return [
        _student_from_doc(doc)
        for doc in db.collection(_STUDENTS).stream()
    ]


def get_all_users() -> list:
    db = get_firestore()
    return [
        _user_from_doc(doc)
        for doc in db.collection(_USERS).stream()
    ]