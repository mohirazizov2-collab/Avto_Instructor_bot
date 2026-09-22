from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ============================================================
# REGISTRATSIYA TURI
# ============================================================

def get_registration_type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👨‍🏫 Instruktor",
                    callback_data="role_instructor",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎓 O'quvchi",
                    callback_data="role_student",
                )
            ],
        ]
    )


# ============================================================
# JINS
# ============================================================

def get_gender_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👨 Erkak",
                    callback_data="gender_male",
                ),
                InlineKeyboardButton(
                    text="👩 Ayol",
                    callback_data="gender_female",
                ),
            ],
        ]
    )


# ============================================================
# BITTA KATEGORIYA TANLASH (o'quvchi uchun)
# ============================================================

def get_single_category_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚗 A", callback_data="student_category_A"),
                InlineKeyboardButton(text="🚗 B", callback_data="student_category_B"),
            ],
            [
                InlineKeyboardButton(text="🚛 C", callback_data="student_category_C"),
                InlineKeyboardButton(text="🚌 D", callback_data="student_category_D"),
            ],
            [
                InlineKeyboardButton(text="🚚 E", callback_data="student_category_E"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_student_category"),
            ],
        ]
    )


# ============================================================
# KO'P KATEGORIYA TANLASH (instruktor uchun)
# ============================================================

def get_categories_kb(selected: list[str] | None = None) -> InlineKeyboardMarkup:

    selected = selected or []

    def button_text(category: str) -> str:
        if category in selected:
            return f"✅ {category}"
        return category

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=button_text("A"), callback_data="category_A"),
                InlineKeyboardButton(text=button_text("B"), callback_data="category_B"),
                InlineKeyboardButton(text=button_text("C"), callback_data="category_C"),
            ],
            [
                InlineKeyboardButton(text=button_text("D"), callback_data="category_D"),
                InlineKeyboardButton(text=button_text("E"), callback_data="category_E"),
            ],
            [
                InlineKeyboardButton(text="✅ Tayyor", callback_data="categories_done"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_instructor_categories"),
            ],
        ]
    )


# ============================================================
# MASHG'ULOT TURI
# ============================================================

def get_training_type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏁 Avtodrom", callback_data="training_autodrome"),
            ],
            [
                InlineKeyboardButton(text="🛣 Ko'cha", callback_data="training_street"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_training_type"),
            ],
        ]
    )


# ============================================================
# TASDIQLASH (umumiy klaviatura, zaxira uchun)
# ============================================================

def get_confirmation_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_register"),
            ],
            [
                InlineKeyboardButton(text="✏️ Qayta kiritish", callback_data="edit_register"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_register"),
            ],
        ]
    )


# ============================================================
# INSTRUKTOR TANLASH RO'YXATI
# ============================================================

def get_instructor_selection_kb(instructors) -> InlineKeyboardMarkup:

    buttons = []

    for instructor in instructors:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"👨‍🏫 {instructor.full_name}",
                    callback_data=f"view_instructor_{instructor.id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Orqaga",
                callback_data="back_student_instructor",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# INSTRUKTOR KARTASI
# ============================================================

def get_instructor_card_kb(instructor_id: int) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tanlash", callback_data=f"choose_instructor_{instructor_id}"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_instructors"),
            ],
        ]
    )


# ============================================================
# CHAT
# ============================================================

def get_chat_kb(telegram_id: int, button_text: str) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=button_text, url=f"tg://user?id={telegram_id}"),
            ],
        ]
    )