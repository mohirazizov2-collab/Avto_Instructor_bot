import logging
import json

from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
try:
    from ..memory_db import (
        get_instructor_by_id,
        get_instructors_for_category,
        get_telegram_id_for_instructor,
        get_user_by_telegram_id,
        save_student,
    )
    from ..keyboards.main import get_main_menu_kb
    from ..keyboards.registration import get_chat_kb, get_instructor_card_kb, get_instructor_selection_kb, get_single_category_kb
    from ..services.validation import normalize_phone, validate_name, validate_phone
    from ..states.registration import RegistrationState
except ImportError:
    from memory_db import (
        get_instructor_by_id,
        get_instructors_for_category,
        get_telegram_id_for_instructor,
        get_user_by_telegram_id,
        save_student,
    )
    from keyboards.main import get_main_menu_kb
    from keyboards.registration import get_chat_kb, get_instructor_card_kb, get_instructor_selection_kb, get_single_category_kb
    from services.validation import normalize_phone, validate_name, validate_phone
    from states.registration import RegistrationState

router = Router()
logger = logging.getLogger(__name__)


def instructor_card(instructor) -> str:
    try:
        categories = ', '.join(json.loads(instructor.categories or '[]'))
    except json.JSONDecodeError:
        categories = '—'
    return (f"<b>👨‍🏫 {instructor.full_name}</b>\n🚗 Kategoriyasi: {categories or '—'}\n"
            f"📍 Hududi: {instructor.region or 'Koʻrsatilmagan'}\n⭐ Reytingi: {instructor.rating:.1f}\n"
            f"📝 Tajribasi: {instructor.experience_years} yil")


@router.message(RegistrationState.student_name)
async def student_name(message: types.Message, state: FSMContext) -> None:
    full_name = (message.text or '').strip()
    if not validate_name(full_name):
        await message.answer("Ism-familiya notoʻgʻri. Toʻliq ism kiriting.")
        return
    await state.update_data(full_name=full_name)
    await state.set_state(RegistrationState.student_phone)
    await message.answer("Telefon raqamingizni kiriting yoki kontakt yuboring.", reply_markup=types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text='📱 Kontakt yuborish', request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))


@router.message(RegistrationState.student_phone)
async def student_phone(message: types.Message, state: FSMContext) -> None:
    phone = normalize_phone(str(message.contact.phone_number)) if message.contact else (message.text or '').strip()
    if not validate_phone(phone):
        await message.answer("Telefon raqami notoʻgʻri. Masalan: +998901234567")
        return
    await state.update_data(phone=normalize_phone(phone))
    await state.set_state(RegistrationState.student_category)
    await message.answer("Qaysi haydovchilik kategoriyasi kerak?", reply_markup=get_single_category_kb())


@router.callback_query(RegistrationState.student_category, lambda c: c.data.startswith('student_category_'))
async def student_category(callback: types.CallbackQuery, state: FSMContext) -> None:
    category = callback.data.removeprefix('student_category_').upper()
    instructors = await get_instructors_for_category(category)
    await state.update_data(desired_category=category)
    if not instructors:
        await callback.message.edit_text(f"{category} kategoriya uchun hozircha instruktor topilmadi.", reply_markup=get_single_category_kb())
    else:
        await state.set_state(RegistrationState.student_instructor)
        await callback.message.edit_text(f"{category} kategoriya uchun instruktorlar:", reply_markup=get_instructor_selection_kb(instructors))
    await callback.answer()


@router.callback_query(RegistrationState.student_instructor, lambda c: c.data.startswith('view_instructor_'))
async def view_instructor(callback: types.CallbackQuery) -> None:
    instructor = await get_instructor_by_id(int(callback.data.removeprefix('view_instructor_')))
    if not instructor or not instructor.is_approved:
        await callback.answer("Instruktor mavjud emas.", show_alert=True)
        return
    await callback.message.edit_text(instructor_card(instructor), reply_markup=get_instructor_card_kb(instructor.id))
    await callback.answer()


@router.callback_query(RegistrationState.student_instructor, lambda c: c.data == 'back_to_instructors')
async def back_to_instructors(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    instructors = await get_instructors_for_category(data['desired_category'])
    await callback.message.edit_text("Instruktorlardan birini tanlang:", reply_markup=get_instructor_selection_kb(instructors))
    await callback.answer()


@router.callback_query(RegistrationState.student_instructor, lambda c: c.data.startswith('choose_instructor_'))
async def choose_instructor(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    instructor = await get_instructor_by_id(int(callback.data.removeprefix('choose_instructor_')))
    data = await state.get_data()
    if not instructor or not instructor.is_approved:
        await callback.answer("Instruktor mavjud emas.", show_alert=True)
        return
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("/start orqali qayta urinib koʻring.", show_alert=True)
        return
    user.role = 'student'

    await save_student(
        user=user,
        data=data,
        instructor_id=instructor.id,
    )
    instructor_telegram_id = await get_telegram_id_for_instructor(instructor.id)
    if instructor_telegram_id:
        try:
            await bot.send_message(instructor_telegram_id, f"<b>Yangi o‘quvchi sizni tanladi</b>\n\n👤 {data['full_name']}\n🚗 {data['desired_category']} kategoriya", reply_markup=get_chat_kb(callback.from_user.id, '💬 O‘quvchiga yozish'))
        except Exception:
            logger.exception('Instruktorga xabar yuborilmadi')
    await state.clear()
    if instructor_telegram_id:
        await callback.message.edit_text(f"✅ <b>Instruktor tanlandi!</b>\n\n👨‍🏫 {instructor.full_name}\n🚗 {data['desired_category']} kategoriya", reply_markup=get_chat_kb(instructor_telegram_id, '💬 Lichkaga yozish'))
    else:
        await callback.message.edit_text("✅ Instruktor tanlandi.", reply_markup=get_main_menu_kb())
    await callback.answer()
