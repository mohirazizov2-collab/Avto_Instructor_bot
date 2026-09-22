from __future__ import annotations


SUPER_ADMIN_USERNAMES: set[str] = {
    "z707fz",
}

PARTIAL_ADMIN_USERNAMES: set[str] = {
    "khab1bullayev_007",
}


def _normalize_username(username: str | None) -> str:
    if not username:
        return ""

    return username.lstrip("@").strip().lower()


def get_admin_role(username: str | None) -> str | None:

    normalized = _normalize_username(username)

    if not normalized:
        return None

    if normalized in {
        item.lower()
        for item in SUPER_ADMIN_USERNAMES
    }:
        return "super"

    if normalized in {
        item.lower()
        for item in PARTIAL_ADMIN_USERNAMES
    }:
        return "partial"

    return None


def is_admin(username: str | None) -> bool:
    return get_admin_role(username) is not None


def is_super_admin(username: str | None) -> bool:
    return get_admin_role(username) == "super"
