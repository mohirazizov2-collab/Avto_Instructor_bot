from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..database.database import (
    get_user_by_telegram_id,
    AsyncSessionLocal,
)
from ..database.models import User
from ..keyboards.registration import get_registration_type_kb
from ..keyboards.main import get_main_menu_kb
from ..states.registration import RegistrationState


router = Router()


# ============================================================
# START
# ============================================================

@router.message(Command("start"))
async def start_handler(
    message: types.Message,
    state: FSMContext,
) -> None:

    await state.clear()

    await message.answer(
        "🚗 <b>Avtomaktab botiga xush kelibsiz!</b>\n\n"
        "Registratsiyadan o'tish uchun "
        "quyidagi tugmadan foydalaning.",
        reply_markup=get_main_menu_kb(
            message.from_user.username
        ),
        parse_mode="HTML",
    )


# ============================================================
# REGISTRATION BUTTON
# ============================================================

@router.callback_query(
    lambda callback: callback.data == "register"
)
async def register_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:

    await state.clear()

    await callback.message.edit_text(
        "📋 <b>Registratsiya turini tanlang:</b>",
        reply_markup=get_registration_type_kb(),
        parse_mode="HTML",
    )

    await callback.answer()


# ============================================================
# ROLE SELECT
# ============================================================

@router.callback_query(
    lambda callback: callback.data in {
        "role_instructor",
        "role_student",
    }
)
async def role_selected(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:

    role = (
        "instructor"
        if callback.data == "role_instructor"
        else "student"
    )

    user = await get_user_by_telegram_id(
        callback.from_user.id
    )

    # ========================================================
    # YANGI USER
    # ========================================================

    if user is None:

        async with AsyncSessionLocal() as session:

            session.add(
                User(
                    telegram_id=callback.from_user.id,
                    role=role,
                )
            )

            await session.commit()

    # ========================================================
    # MAVJUD USER
    # ========================================================

    else:

        async with AsyncSessionLocal() as session:

            db_user = await session.get(
                User,
                user.id,
            )

            if db_user is not None:
                db_user.role = role
                await session.commit()

    # ========================================================
    # INSTRUCTOR
    # ========================================================

    if role == "instructor":

        await state.set_state(
            RegistrationState.instructor_name
        )

        await callback.message.edit_text(
            "👨‍🏫 <b>Instruktor registratsiyasi</b>\n\n"
            "1️⃣ <b>Ism-familiya</b>\n\n"
            "To'liq ism-familiyangizni kiriting:",
            parse_mode="HTML",
        )

    # ========================================================
    # STUDENT
    # ========================================================

    else:

        await state.set_state(
            RegistrationState.student_name
        )

        await callback.message.edit_text(
            "🎓 <b>O'quvchi registratsiyasi</b>\n\n"
            "1️⃣ <b>Ism-familiya</b>\n\n"
            "To'liq ism-familiyangizni kiriting:",
            parse_mode="HTML",
        )

    await callback.answer()


# ============================================================
# CANCEL
# ============================================================

@router.message(Command("cancel"))
async def cancel_registration(
    message: types.Message,
    state: FSMContext,
) -> None:

    await state.clear()

    await message.answer(
        "❌ Registratsiya bekor qilindi.",
        reply_markup=get_main_menu_kb(
            message.from_user.username
        ),
    )


# ============================================================
# CONTACT
# ============================================================

@router.callback_query(
    lambda callback: callback.data == "contact"
)
async def contact_handler(
    callback: types.CallbackQuery,
) -> None:

    await callback.message.edit_text(
        "📞 <b>Bog‘lanish</b>\n\n"
        "☎️ Telefon: <b>+998 55 588 07 17</b>\n"
        "📢 Telegram: <b>@avtomaktab_dreamm</b>\n"
        "📸 Instagram: <b>@avtomaktab_dream</b>",
        parse_mode="HTML",
    )

    await callback.answer()
