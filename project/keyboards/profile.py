from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_profile_kb(
    show_edit: bool = True,
) -> InlineKeyboardMarkup:

    keyboard = []

    if show_edit:
        keyboard.append([
            InlineKeyboardButton(
                text="✏️ Tahrirlash",
                callback_data="edit_profile",
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_to_start",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )
