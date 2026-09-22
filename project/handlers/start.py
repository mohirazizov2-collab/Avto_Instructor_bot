from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..keyboards.main import get_main_menu_kb
from ..keyboards.registration import get_registration_type_kb
from ..states.registration import RegistrationState
from ..memory_db import get_or_create_user


router = Router()


# ============================================================
# START
# ============================================================

@router.message(Command("start"))
async def start_handler(
    message: types.Message,
    state: FSMContext,
) -> None:
    try:
        await state.clear()

        username = (
            message.from_user.username
            if message.from_user
            else None
        )

        await message.answer(
            "🚗 <b>Avtomaktab botiga xush kelibsiz!</b>\n\n"
            "Registratsiyadan o'tish uchun "
            "quyidagi tugmadan foydalaning.",
            reply_markup=get_main_menu_kb(username),
        )

        print("START_OK", flush=True)

    except Exception as e:
        print(
            f"START_ERROR|{type(e).__name__}|{str(e)[:300]}",
            flush=True,
        )


# ============================================================
# REGISTRATION BUTTON
# ============================================================

@router.callback_query(F.data == "register")
async def register_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    try:
        await state.clear()

        await callback.message.edit_text(
            "📋 <b>Registratsiya turini tanlang:</b>",
            reply_markup=get_registration_type_kb(),
        )

        await callback.answer()

        print(
            "REGISTER_BUTTON_OK",
            flush=True,
        )

    except Exception as e:
        print(
            f"REGISTER_ERROR|{type(e).__name__}|{str(e)[:300]}",
            flush=True,
        )


# ============================================================
# ROLE SELECT
# ============================================================

@router.callback_query(
    F.data.in_(
        {
            "role_instructor",
            "role_student",
        }
    )
)
async def role_selected(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:

    try:
        role = (
            "instructor"
            if callback.data == "role_instructor"
            else "student"
        )

        # ====================================================
        # FIRESTORE USER
        # ====================================================

        user = await get_or_create_user(
            callback.from_user.id,
            role,
        )

        print(
            f"ROLE_SELECTED_OK|"
            f"telegram_id={callback.from_user.id}|"
            f"user_id={user.id}|"
            f"role={role}",
            flush=True,
        )

        # ====================================================
        # INSTRUCTOR
        # ====================================================

        if role == "instructor":

            await state.set_state(
                RegistrationState.instructor_name
            )

            await callback.message.edit_text(
                "👨‍🏫 <b>Instruktor registratsiyasi</b>\n\n"
                "1️⃣ <b>Ism-familiya</b>\n\n"
                "To'liq ism-familiyangizni kiriting:"
            )

        # ====================================================
        # STUDENT
        # ====================================================

        else:

            await state.set_state(
                RegistrationState.student_name
            )

            await callback.message.edit_text(
                "🎓 <b>O'quvchi registratsiyasi</b>\n\n"
                "1️⃣ <b>Ism-familiya</b>\n\n"
                "To'liq ism-familiyangizni kiriting:"
            )

        await callback.answer()

    except Exception as e:

        print(
            f"ROLE_SELECTED_ERROR|"
            f"{type(e).__name__}|"
            f"{str(e)[:500]}",
            flush=True,
        )

        try:
            await callback.answer(
                "❌ Ma'lumotlarni saqlashda xatolik yuz berdi.",
                show_alert=True,
            )
        except Exception:
            pass


# ============================================================
# CONTACT
# ============================================================

@router.callback_query(F.data == "contact")
async def contact_handler(
    callback: types.CallbackQuery,
) -> None:

    try:

        await callback.message.edit_text(
            "📞 <b>Bog‘lanish</b>\n\n"
            "☎️ Telefon: <b>+998 55 588 07 17</b>\n"
            "📢 Telegram: <b>@avtomaktab_dreamm</b>\n"
            "📸 Instagram: <b>@avtomaktab_dream</b>",
        )

        await callback.answer()

        print(
            "CONTACT_OK",
            flush=True,
        )

    except Exception as e:

        print(
            f"CONTACT_ERROR|{type(e).__name__}|{str(e)[:300]}",
            flush=True,
        )


# ============================================================
# ABOUT
# ============================================================

@router.callback_query(F.data == "about")
async def about_handler(
    callback: types.CallbackQuery,
) -> None:

    try:

        await callback.message.edit_text(
            "ℹ️ <b>Biz haqimizda</b>\n\n"
            "🚗 <b>Avtomaktab</b> — haydovchilik "
            "ta'limi uchun qulay platforma.\n\n"
            "👨‍🏫 Instruktorlarni topish va tanlash\n"
            "🎓 O‘quvchilar uchun qulay ro‘yxatdan o‘tish\n"
            "📚 Haydovchilik bo‘yicha ta'lim xizmatlari\n\n"
            "Sizga qulay instruktorni topishingizga yordam beramiz."
        )

        await callback.answer()

        print(
            "ABOUT_OK",
            flush=True,
        )

    except Exception as e:

        print(
            f"ABOUT_ERROR|{type(e).__name__}|{str(e)[:300]}",
            flush=True,
        )


# ============================================================
# CANCEL
# ============================================================

@router.message(Command("cancel"))
async def cancel_registration(
    message: types.Message,
    state: FSMContext,
) -> None:

    try:

        await state.clear()

        await message.answer(
            "❌ Registratsiya bekor qilindi.",
            reply_markup=get_main_menu_kb(
                message.from_user.username
                if message.from_user
                else None
            ),
        )

        print(
            "CANCEL_OK",
            flush=True,
        )

    except Exception as e:

        print(
            f"CANCEL_ERROR|{type(e).__name__}|{str(e)[:300]}",
            flush=True,
        )