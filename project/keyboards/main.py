from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_kb(
    username: str | None = None,
) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Registratsiya",
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
    )
