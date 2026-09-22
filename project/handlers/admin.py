from aiogram import F, Router, types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from aiogram.filters import Command

from ..admin import get_admin_role
from ..config import settings
from ..database.statistics import get_statistics
from ..memory_db import (
    Instructor,
    get_instructor_by_id,
    get_user_by_id,
    approve_instructor,
    reject_instructor,
)


router = Router()


# ============================================================
# ADMIN PANEL
# ============================================================

@router.callback_query(
    lambda c: c.data == "admin_panel"
)
async def admin_panel_handler(
    callback: types.CallbackQuery,
) -> None:

    role = get_admin_role(
        callback.from_user.username
    )

    if role is None:

        await callback.answer(
            "❌ Sizda admin huquqi yo'q.",
            show_alert=True,
        )

        return

    if role == "super":

        text = (
            "👑 <b>SUPER ADMIN PANEL</b>\n\n"
            "🔑 Siz Super Adminsiz.\n\n"
            "Kerakli boshqaruv bo'limini tanlang:"
        )

    else:

        text = (
            "🛠 <b>ADMIN PANEL</b>\n\n"
            "🔑 Siz qisman admin huquqiga egasiz.\n\n"
            "Sizga ruxsat berilgan bo'limni tanlang:"
        )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data="admin_statistics",
                )
            ]
        ]
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    await callback.answer()


# ============================================================
# ADMIN STATISTIKA
# ============================================================

@router.callback_query(
    F.data == "admin_statistics"
)
async def admin_statistics_handler(
    callback: types.CallbackQuery,
) -> None:

    role = get_admin_role(
        callback.from_user.username
    )

    if role is None:

        await callback.answer(
            "❌ Sizda admin huquqi yo'q.",
            show_alert=True,
        )

        return

    try:

        stats = get_statistics()

        text = (
            "📊 <b>AVTOMAKTAB STATISTIKASI</b>\n\n"

            f"👥 <b>Jami foydalanuvchilar:</b> "
            f"{stats['users']}\n"

            f"🎓 <b>Jami o'quvchilar:</b> "
            f"{stats['students']}\n"

            f"🚗 <b>Jami instruktorlar:</b> "
            f"{stats['instructors']}\n"

            f"✅ <b>Tasdiqlangan instruktorlar:</b> "
            f"{stats['approved_instructors']}\n"

            f"⏳ <b>Kutilayotgan instruktorlar:</b> "
            f"{stats['pending_instructors']}\n"

            f"🆕 <b>Bugun ro'yxatdan o'tganlar:</b> "
            f"{stats['today_users']}\n"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Yangilash",
                        callback_data="admin_statistics",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 Admin panel",
                        callback_data="admin_panel",
                    )
                ],
            ]
        )

        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

        await callback.answer(
            "📊 Statistika yangilandi."
        )

    except Exception as e:

        print(
            "ADMIN STATISTICS ERROR:",
            repr(e),
            flush=True,
        )

        await callback.answer(
            f"⚠️ Xatolik: {type(e).__name__}",
            show_alert=True,
        )


# ============================================================
# INSTRUKTOR ARIZASINI ADMINLAR GURUHIGA YUBORISH
# ============================================================

async def send_instructor_application(
    bot,
    instructor: Instructor,
    telegram_id: int,
) -> None:

    group_id = settings.ADMIN_GROUP_ID

    if not group_id:
        raise RuntimeError(
            "ADMIN_GROUP_ID sozlanmagan"
        )

    categories = instructor.categories or "-"

    caption = (
        "📩 <b>YANGI INSTRUKTOR ARIZASI</b>\n\n"

        f"👤 <b>Ism:</b> "
        f"{instructor.full_name}\n"

        f"📞 <b>Telefon:</b> "
        f"{instructor.phone}\n"

        f"🎂 <b>Tug'ilgan sana:</b> "
        f"{instructor.date_of_birth or '-'}\n"

        f"⏳ <b>Tajriba:</b> "
        f"{instructor.experience_years} yil\n"

        f"💰 <b>1 soat narxi:</b> "
        f"{instructor.hourly_price:,} so'm\n"

        f"🚻 <b>Jins:</b> "
        f"{instructor.gender}\n"

        f"🚗 <b>Kategoriyalar:</b> "
        f"{categories}\n"

        f"📍 <b>Hudud:</b> "
        f"{instructor.region or '-'}\n"

        f"🚙 <b>Avtomobil:</b> "
        f"{instructor.vehicle_info or '-'}\n\n"

        "🔒 <b>Maxfiy hujjatlar:</b>\n"
        "🪪 Prava oldi/orqasi\n"
        "📄 Tex pasport oldi/orqasi\n"
        "📜 Instruktorlik sertifikati\n"
        "🖼 Profil rasmi\n\n"

        "⏳ <b>Admin tekshiruvini kutmoqda.</b>"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"admin_approve_{instructor.id}",
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"admin_reject_{instructor.id}",
                ),
            ]
        ]
    )

    await bot.send_message(
        chat_id=group_id,
        text=caption,
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    photos = []

    photo_fields = [
        (
            instructor.vehicle_photo_id,
            "🚗 Avtomobil rasmi",
        ),
        (
            instructor.driving_license_front_photo_id,
            "🪪 Prava — oldi",
        ),
        (
            instructor.driving_license_back_photo_id,
            "🪪 Prava — orqasi",
        ),
        (
            instructor.tech_passport_front_photo_id,
            "📄 Tex pasport — oldi",
        ),
        (
            instructor.tech_passport_back_photo_id,
            "📄 Tex pasport — orqasi",
        ),
        (
            instructor.instructor_certificate_photo_id,
            "📜 Sertifikat",
        ),
        (
            instructor.profile_photo_id,
            "🖼 Profil rasmi",
        ),
    ]

    for photo_id, label in photo_fields:

        if photo_id:
            photos.append(
                InputMediaPhoto(
                    media=photo_id,
                    caption=label,
                )
            )

    if photos:

        await bot.send_media_group(
            chat_id=group_id,
            media=photos[:10],
        )


# ============================================================
# ADMIN HUQUQINI TEKSHIRISH
# ============================================================

async def is_real_group_admin(
    callback: types.CallbackQuery,
) -> bool:

    if not callback.message:
        return False

    if callback.message.chat.id != settings.ADMIN_GROUP_ID:
        return False

    try:

        member = await callback.bot.get_chat_member(
            settings.ADMIN_GROUP_ID,
            callback.from_user.id,
        )

        return member.status in {
            "administrator",
            "creator",
        }

    except Exception as e:

        print(
            "ADMIN CHECK ERROR:",
            repr(e),
            flush=True,
        )

        return False


# ============================================================
# INSTRUKTORNI TASDIQLASH
# ============================================================

@router.callback_query(
    F.data.startswith("admin_approve_")
)
async def handle_approve_instructor(
    callback: types.CallbackQuery,
) -> None:

    if not await is_real_group_admin(callback):

        await callback.answer(
            "❌ Faqat guruh administratorlari tasdiqlashi mumkin.",
            show_alert=True,
        )

        return

    try:

        instructor_id = int(
            callback.data.replace(
                "admin_approve_",
                "",
                1,
            )
        )

        instructor = await get_instructor_by_id(
            instructor_id
        )

        if instructor is None:

            await callback.answer(
                "❌ Instruktor topilmadi.",
                show_alert=True,
            )

            return

        instructor = await approve_instructor(
            instructor_id
        )

        if instructor is None:

            await callback.answer(
                "❌ Instruktorni tasdiqlab bo'lmadi.",
                show_alert=True,
            )

            return

        user = await get_user_by_id(
            instructor.user_id
        )

        if user:

            await callback.bot.send_message(
                chat_id=user.telegram_id,
                text=(
                    "🎉 <b>Tabriklaymiz!</b>\n\n"
                    "✅ Sizning instruktor profilingiz "
                    "administrator tomonidan tasdiqlandi.\n\n"
                    "👀 Endi profilingiz o'quvchilarga "
                    "ko'rinadi.\n"
                    "📩 O'quvchilar sizga murojaat "
                    "qilishi mumkin.\n\n"
                    "Omad tilaymiz! 🚗"
                ),
            )

        await callback.message.edit_reply_markup(
            reply_markup=None
        )

        await callback.message.answer(
            "✅ <b>Instruktor tasdiqlandi.</b>\n\n"
            f"👤 {instructor.full_name}\n"
            "👀 Profil o'quvchilarga ko'rinadigan bo'ldi.",
            parse_mode="HTML",
        )

        await callback.answer(
            "✅ Tasdiqlandi."
        )

    except Exception as e:

        print(
            "APPROVE INSTRUCTOR ERROR:",
            repr(e),
            flush=True,
        )

        await callback.answer(
            f"⚠️ Xatolik: {type(e).__name__}",
            show_alert=True,
        )


# ============================================================
# INSTRUKTORNI RAD ETISH
# ============================================================

@router.callback_query(
    F.data.startswith("admin_reject_")
)
async def handle_reject_instructor(
    callback: types.CallbackQuery,
) -> None:

    if not await is_real_group_admin(callback):

        await callback.answer(
            "❌ Faqat guruh administratorlari "
            "rad etishi mumkin.",
            show_alert=True,
        )

        return

    try:

        instructor_id = int(
            callback.data.replace(
                "admin_reject_",
                "",
                1,
            )
        )

        instructor = await get_instructor_by_id(
            instructor_id
        )

        if instructor is None:

            await callback.answer(
                "❌ Instruktor topilmadi.",
                show_alert=True,
            )

            return

        instructor = await reject_instructor(
            instructor_id
        )

        if instructor is None:

            await callback.answer(
                "❌ Instruktorni rad etib bo'lmadi.",
                show_alert=True,
            )

            return

        user = await get_user_by_id(
            instructor.user_id
        )

        if user:

            await callback.bot.send_message(
                chat_id=user.telegram_id,
                text=(
                    "❌ <b>Registratsiyangiz rad etildi.</b>\n\n"
                    "Administrator hujjatlaringizni ko'rib chiqdi "
                    "va hozircha profilingizni tasdiqlamadi.\n\n"
                    "ℹ️ Qo'shimcha ma'lumot uchun "
                    "avtomaktab administratoriga murojaat qiling."
                ),
            )

        await callback.message.edit_reply_markup(
            reply_markup=None
        )

        await callback.message.answer(
            "❌ <b>Instruktor arizasi rad etildi.</b>\n\n"
            f"👤 {instructor.full_name}",
            parse_mode="HTML",
        )

        await callback.answer(
            "❌ Rad etildi."
        )

    except Exception as e:

        print(
            "REJECT INSTRUCTOR ERROR:",
            repr(e),
            flush=True,
        )

        await callback.answer(
            f"⚠️ Xatolik: {type(e).__name__}",
            show_alert=True,
        )


# ============================================================
# TEMP: GROUP ID ANIQLASH
# ============================================================

@router.message(Command("groupid"))
async def group_id_handler(
    message: types.Message,
) -> None:

    await message.answer(
        f"🆔 <b>Chat ID:</b> <code>{message.chat.id}</code>\n"
        f"📋 <b>Chat type:</b> <code>{message.chat.type}</code>"
    )
