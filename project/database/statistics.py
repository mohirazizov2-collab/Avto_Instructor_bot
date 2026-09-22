from datetime import datetime, timezone

from .firebase import get_firestore


def get_statistics() -> dict:
    db = get_firestore()

    users = list(db.collection("users").stream())
    instructors = list(db.collection("instructors").stream())
    students = list(db.collection("students").stream())

    approved = 0
    pending = 0

    for doc in instructors:
        data = doc.to_dict() or {}

        if data.get("is_approved") is True:
            approved += 1
        else:
            pending += 1

    today = datetime.now(timezone.utc).date()
    today_users = 0

    for doc in users:
        data = doc.to_dict() or {}
        created_at = data.get("created_at")

        if created_at is None:
            continue

        try:
            created_date = created_at.date()
        except AttributeError:
            continue

        if created_date == today:
            today_users += 1

    return {
        "users": len(users),
        "instructors": len(instructors),
        "students": len(students),
        "approved_instructors": approved,
        "pending_instructors": pending,
        "today_users": today_users,
    }

