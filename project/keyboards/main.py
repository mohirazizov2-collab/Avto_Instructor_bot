from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..admin import get_admin_role


def get_main_menu_kb(
    username: str | None = None,
) -> InlineKeyboardMarkup:

    buttons = [
        [
            InlineKeyboardButton(
                text="📋 Registratsiya",
                callback_data="register",
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 Profil",
                callback_data="profile",
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ Biz haqimizda",
                callback_data="about",
            ),
            InlineKeyboardButton(
                text="📞 Bog‘lanish",
                callback_data="contact",
            ),
        ],
    ]

    role = get_admin_role(username)

    if role is not None:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🛠 Admin panel",
                    callback_data="admin_panel",
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
