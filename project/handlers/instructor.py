import json
import logging
from datetime import date

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

try:
    from ..database.database import (
        AsyncSessionLocal,
        get_user_by_telegram_id,
    )
    from ..database.models import Instructor, User
    from ..keyboards.main import get_main_menu_kb
    from ..keyboards.registration import (
        get_confirmation_kb,
        get_gender_kb,
        get_categories_kb,
    )
    from ..services.validation import (
        normalize_phone,
        validate_name,
        validate_phone,
        validate_positive_int,
        validate_positive_money,
        validate_date,
        validate_age,
        validate_driving_license_number,
        validate_vehicle_brand_model,
        parse_date,
    )
    from ..states.registration import RegistrationState

except ImportError:
    from database.database import (
        AsyncSessionLocal,
        get_user_by_telegram_id,
    )
    from database.models import Instructor, User
    from keyboards.main import get_main_menu_kb
    from keyboards.registration import (
        get_confirmation_kb,
        get_gender_kb,
        get_categories_kb,
    )
    from services.validation import (
        normalize_phone,
        validate_name,
        validate_phone,
        validate_positive_int,
        validate_positive_money,
        validate_date,
        validate_age,
        validate_driving_license_number,
        validate_vehicle_brand_model,
        parse_date,
    )
    from states.registration import RegistrationState


router = Router()


# ============================================================
# 1. ISM
# ============================================================

@router.message(RegistrationState.instructor_name)
async def instructor_name(
    message: types.Message,
    state: FSMContext,
) -> None:

    text = (message.text or "").strip()

    if not validate_name(text):
        await message.answer(
            "❌ Ism noto'g'ri.\n\n"
            "Iltimos, to'liq ism-familiyangizni kiriting."
        )
        return

    await state.update_data(
        full_name=text
    )

    await state.set_state(
        RegistrationState.instructor_phone
    )

    await message.answer(
        "2. 📱 Telefon raqami\n\n"
        "Telefon raqamingizni yozing yoki kontakt yuboring.",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(
                        text="📲 Kontakt yuborish",
                        request_contact=True,
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


# ============================================================
# 2. TELEFON
# ============================================================

@router.message(RegistrationState.instructor_phone)
async def instructor_phone(
    message: types.Message,
    state: FSMContext,
) -> None:

    if message.contact:
        phone = normalize_phone(
            str(message.contact.phone_number)
        )
    else:
        phone = (message.text or "").strip()

    if not validate_phone(phone):
        await message.answer(
            "❌ Telefon raqami noto'g'ri formatda.\n\n"
            "Masalan: +998901234567"
        )
        return

    await state.update_data(
        phone=normalize_phone(phone)
    )

    await state.set_state(
        RegistrationState.instructor_date_of_birth
    )

    await message.answer(
        "3. 🎂 Tug'ilgan sana\n\n"
        "Sanani DD.MM.YYYY formatida kiriting.\n"
        "Masalan: 15.05.1990",
        reply_markup=None,
    )


# ============================================================
# 3. TUG'ILGAN SANA
# ============================================================

@router.message(
    RegistrationState.instructor_date_of_birth
)
async def instructor_date_of_birth(
    message: types.Message,
    state: FSMContext,
) -> None:

    text = (message.text or "").strip()

    try:

        if not validate_date(text):
            await message.answer(
                "❌ Sana noto'g'ri formatda.\n\n"
                "DD.MM.YYYY ko'rinishida kiriting.\n"
                "Masalan: 15.05.1990"
            )
            return

        birth_date = parse_date(text)

        if not birth_date:
            await message.answer(
                "❌ Sana noto'g'ri.\n"
                "Iltimos, qayta kiriting."
            )
            return

        if not validate_age(
            birth_date,
            min_age=18,
        ):
            await message.answer(
                "❌ Instruktor kamida 18 yoshda bo'lishi kerak."
            )
            return

        await state.update_data(
            date_of_birth=birth_date.isoformat()
        )

        await state.set_state(
            RegistrationState.instructor_experience
        )

        await message.answer(
            "4. 🚗 Haydovchilik / instruktorlik staji\n\n"
            "Necha yil tajribaga egasiz?\n"
            "Masalan: 5"
        )

    except Exception as e:

        logging.error(
            f"Date parsing error: {e}"
        )

        await message.answer(
            "❌ Xatolik yuz berdi.\n\n"
            "DD.MM.YYYY formatida sana kiriting."
        )


# ============================================================
# 4. STAJ
# ============================================================

@router.message(
    RegistrationState.instructor_experience
)
async def instructor_experience(
    message: types.Message,
    state: FSMContext,
) -> None:

    text = (message.text or "").strip()

    if not validate_positive_int(text):
        await message.answer(
            "❌ Staj faqat musbat son bo'lishi kerak.\n\n"
            "Misol: 5"
        )
        return

    await state.update_data(
        experience_years=int(text)
    )

    await state.set_state(
        RegistrationState.instructor_hourly_price
    )

    await message.answer(
        "5. 💰 1 soatlik dars narxi\n\n"
        "Narxni kiriting.\n"
        "Masalan: 80000"
    )


# ============================================================
# 5. NARX
# ============================================================

@router.message(
    RegistrationState.instructor_hourly_price
)
async def instructor_hourly_price(
    message: types.Message,
    state: FSMContext,
) -> None:

    text = (message.text or "").strip()

    if not validate_positive_money(text):
        await message.answer(
            "❌ Narx faqat musbat son bo'lishi kerak.\n\n"
            "Misol: 80000"
        )
        return

    await state.update_data(
        hourly_price=int(
            text.replace(" ", "")
        )
    )

    await state.set_state(
        RegistrationState.instructor_gender
    )

    await message.answer(
        "6. ⚧ Jinsi",
        reply_markup=get_gender_kb(),
    )


# ============================================================
# 6. JINSI - ORQAGA
# ============================================================

@router.callback_query(
    RegistrationState.instructor_gender,
    lambda c: c.data == "back_instructor_gender",
)
async def instructor_gender_back(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:

    await state.set_state(
        RegistrationState.instructor_hourly_price
    )

    await callback.message.edit_text(
        "5. 💰 1 soatlik dars narxi\n\n"
        "Narxni kiriting.\n"
        "Masalan: 80000"
    )

    await callback.answer()


# ============================================================
# 6. JINSI
# ============================================================

@router.callback_query(
    RegistrationState.instructor_gender,
    lambda c: c.data in {
        "gender_male",
        "gender_female",
    },
)
async def instructor_gender(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:

    gender = (
        "male"
        if callback.data == "gender_male"
        else "female"
    )

    await state.update_data(
        gender=gender
    )

    await state.set_state(
        RegistrationState.instructor_driving_license
    )

    await callback.message.edit_text(
        "7. 🪪 Haydovchilik guvohnomasi\n\n"
        "Haydovchilik guvohnomasi raqamini kiriting.\n"
        "Masalan: AB123456"
    )

    await callback.answer()


# ============================================================
# 7. GUVOHNOMA RAQAMI
# ============================================================

@router.message(
    RegistrationState.instructor_driving_license
)
async def instructor_driving_license(
    message: types.Message,
    state: FSMContext,
) -> None:

    text = (
        message.text or ""
    ).strip().upper()

    if not validate_driving_license_number(text):
        await message.answer(
            "❌ Guvohnoma raqami noto'g'ri formatda.\n\n"
            "Masalan: AB123456"
        )
        return

    await state.update_data(
        driving_license_number=text
    )

    await state.set_state(
        RegistrationState.instructor_driving_license_expiry
    )

    await message.answer(
        "8. 📅 Guvohnomaning amal qilish muddati\n\n"
        "Sanani DD.MM.YYYY formatida kiriting.\n"
        "Masalan: 25.12.2030"
    )


# ============================================================
# 8. GUVOHNOMA MUDDATI
# ============================================================

@router.message(
    RegistrationState.instructor_driving_license_expiry
)
async def instructor_driving_license_expiry(
    message: types.Message,
    state: FSMContext,
) -> None:

    text = (message.text or "").strip()

    if not validate_date(text):
        await message.answer(
            "❌ Sana noto'g'ri formatda.\n\n"
            "DD.MM.YYYY ko'rinishida kiriting."
        )
        return

    expiry_date = parse_date(text)
    today = date.today()

    if expiry_date and expiry_date <= today:
        await message.answer(
            "❌ Guvohnomaning muddati o'tib ketgan.\n\n"
            "Amal qiluvchi guvohnoma kiriting."
        )
        return

    await state.update_data(
        driving_license_expiry=(
            expiry_date.isoformat()
            if expiry_date
            else None
        )
    )

    await state.set_state(
        RegistrationState.instructor_categories
    )

    await message.answer(
        "9. 📚 Qaysi kategoriyalarda dars beradi?\n\n"
        "Kerakli kategoriyalarni tanlang:",
        reply_markup=get_categories_kb(),
    )


# ============================================================
# 9. KATEGORIYALAR
# ============================================================

@router.callback_query(
    RegistrationState.instructor_categories,
    lambda c: c.data.startswith("category_"),
)
async def instructor_categories(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:

    data = await state.get_data()

    categories = data.get(
        "categories",
        [],
    )

    category = (
        callback.data
        .replace("category_", "")
        .upper()
    )

    if category in categories:
        categories.remove(category)
    else:
        categories.append(category)

    await state.update_data(
        categories=categories
    )

    selected = (
        ", ".join(sorted(categories))
        if categories
        else "Hech qaysisi tanlanmadi"
    )

    await callback.message.edit_text(
        "9. 📚 Qaysi kategoriyalarda dars beradi?\n\n"
        f"Tanlanganlar: {selected}\n\n"
        "Kerakli kategoriyalarni tanlang:",
        reply_markup=get_categories_kb(),
    )

    await callback.answer()


# ============================================================
# 9. KATEGORIYALAR - TAYYOR
# ============================================================

@router.callback_query(
    RegistrationState.instructor_categories,
    lambda c: c.data == "categories_done",
)
async def categories_done(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:

    data = await state.get_data()

    categories = data.get(
        "categories",
        [],
    )

    if not categories:
        await callback.answer(
            "❌ Kamida bir kategoriya tanlang.",
            show_alert=True,
        )
        return

    await state.update_data(
        categories=json.dumps(
            sorted(categories)
        )
    )

    await state.set_state(
        RegistrationState.instructor_region
    )

    await callback.message.edit_text(
        "10. 📍 Hududingizni kiriting.\n\n"
        "Masalan: Chilonzor"
    )

    await callback.answer()


# ============================================================
# 9. ORQAGA
# ============================================================

@router.callback_query(
    RegistrationState.instructor_categories,
    lambda c: c.data == "back_instructor_categories",
)
async def back_instructor_categories(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:

    await state.set_state(
        RegistrationState.instructor_driving_license_expiry
    )

    await callback.message.edit_text(
        "8. 📅 Guvohnomaning amal qilish muddati\n\n"
        "Sanani DD.MM.YYYY formatida kiriting.\n"
        "Masalan: 25.12.2030"
    )

    await callback.answer()


# ============================================================
# 10. HUDUD
# ============================================================

@router.message(
    RegistrationState.instructor_region
)
async def instructor_region(
    message: types.Message,
    state: FSMContext,
) -> None:

    region = (
        message.text or ""
    ).strip()

    if len(region) < 2 or len(region) > 128:
        await message.answer(
            "❌ Hudud nomini to'g'ri kiriting.\n\n"
            "Masalan: Chilonzor"
        )
        return

    await state.update_data(
        region=region
    )

    await state.set_state(
        RegistrationState.instructor_vehicle_info
    )

    await message.answer(
        "11. 🚗 Avtomobil ma'lumotlari\n\n"
        "Brand va modelini kiriting.\n"
        "Masalan: Toyota Camry"
    )


# ============================================================
# 11. AVTOMOBIL MA'LUMOTI
# ============================================================

@router.message(
    RegistrationState.instructor_vehicle_info
)
async def instructor_vehicle_info(
    message: types.Message,
    state: FSMContext,
) -> None:

    text = (
        message.text or ""
    ).strip()

    if not validate_vehicle_brand_model(text):
        await message.answer(
            "❌ Avtomobil ma'lumotlari noto'g'ri.\n\n"
            "Masalan: Toyota Camry"
        )
        return

    await state.update_data(
        vehicle_info=text
    )

    await state.set_state(
        RegistrationState.instructor_vehicle_photo
    )

    await message.answer(
        "12. 📸 Avtomobil rasmi\n\n"
        "Avtomobilingizning rasmini yuboring."
    )


# ============================================================
# 12. AVTOMOBIL RASMI
# ============================================================

@router.message(
    RegistrationState.instructor_vehicle_photo
)
async def instructor_vehicle_photo(
    message: types.Message,
    state: FSMContext,
) -> None:

    if not message.photo:
        await message.answer(
            "❌ Iltimos, avtomobil rasmini yuboring."
        )
        return

    photo = message.photo[-1]

    await state.update_data(
        vehicle_photo_id=photo.file_id
    )

    # ========================================================
    # TEXNIK PASPORTGA O'TISH
    # ========================================================

    await state.set_state(
        RegistrationState.instructor_tech_passport_front_photo
    )

    await message.answer(
        "13. 🪪 Texnik pasport\n\n"
        "Avtomobilingizning texnik pasportini "
        "rasm qilib yuboring.\n\n"
        "⚠️ Bu hujjat faqat administrator tekshiruvi "
        "uchun ishlatiladi va o'quvchilarga ko'rsatilmaydi."
    )


# ============================================================
# 13. TEXNIK PASPORT
# ============================================================

@router.message(
    RegistrationState.instructor_tech_passport_front_photo
)
async def instructor_tech_passport_front_photo(
    message: types.Message,
    state: FSMContext,
) -> None:

    if not message.photo:
        await message.answer(
            "❌ Iltimos, texnik pasport rasmini yuboring."
        )
        return

    photo = message.photo[-1]

    await state.update_data(
    )

    await state.set_state(
        RegistrationState.instructor_certificate_photo
    )

    await message.answer(
        "14. 📜 Instruktorlik hujjati\n\n"
        "Instruktor ekanligingizni tasdiqlovchi "
        "hujjat rasmini yuboring.\n\n"
        "⚠️ Bu hujjat faqat administrator tekshiruvi "
        "uchun ishlatiladi va o'quvchilarga ko'rsatilmaydi."
    )


# ============================================================
# 14. INSTRUKTORLIK HUJJATI
# ============================================================

@router.message(
    RegistrationState.instructor_certificate_photo
)
async def instructor_certificate_photo(
    message: types.Message,
    state: FSMContext,
) -> None:

    if not message.photo:
        await message.answer(
            "❌ Iltimos, instruktorlik hujjati "
            "rasmini yuboring."
        )
        return

    photo = message.photo[-1]

    await state.update_data(
        instructor_certificate_photo_id=photo.file_id
    )

    await state.set_state(
        RegistrationState.instructor_profile_photo
    )

    await message.answer(
        "15. 👤 Profil rasmi\n\n"
        "O'zingizning aniq va sifatli rasmingizni yuboring."
    )


# ============================================================
# 15. PROFIL RASMI
# ============================================================

@router.message(
    RegistrationState.instructor_profile_photo
)
async def instructor_profile_photo(
    message: types.Message,
    state: FSMContext,
) -> None:

    if not message.photo:
        await message.answer(
            "❌ Iltimos, profil rasmini yuboring."
        )
        return

    photo = message.photo[-1]

    await state.update_data(
        profile_photo_id=photo.file_id
    )

    data = await state.get_data()

    try:
        categories_list = json.loads(
            data.get(
                "categories",
                "[]",
            )
        )
    except json.JSONDecodeError:
        categories_list = []

    categories_text = (
        ", ".join(categories_list)
        if categories_list
        else "Belgilanmagan"
    )

    confirmation_text = (
        "📋 <b>Registratsiyani tasdiqlang:</b>\n\n"

        f"👤 <b>Ism:</b> {data['full_name']}\n"
        f"📞 <b>Telefon:</b> {data['phone']}\n"
        f"🎂 <b>Tug'ilgan sana:</b> "
        f"{data['date_of_birth']}\n"

        f"🚗 <b>Staj:</b> "
        f"{data['experience_years']} yil\n"

        f"💰 <b>1 soatlik narx:</b> "
        f"{data['hourly_price']:,} so'm\n"

        f"⚧ <b>Jinsi:</b> "
        f"{'Erkak' if data['gender'] == 'male' else 'Ayol'}\n"

        f"🪪 <b>Guvohnoma:</b> "
        f"{data['driving_license_number']}\n"

        f"📅 <b>Muddati:</b> "
        f"{data['driving_license_expiry']}\n"

        f"📚 <b>Kategoriyalar:</b> "
        f"{categories_text}\n"

        f"📍 <b>Hudud:</b> "
        f"{data['region']}\n"

        f"🚗 <b>Avtomobil:</b> "
        f"{data['vehicle_info']}\n\n"

        "🔐 <b>Maxfiy hujjatlar:</b>\n"
        "🪪 Texnik pasport — qabul qilindi\n"
        "📜 Instruktorlik hujjati — qabul qilindi\n\n"

        "⚠️ Hujjatlar o'quvchilarga ko'rsatilmaydi."
    )

    await state.set_state(
        RegistrationState.instructor_confirm
    )

    await message.answer(
        confirmation_text,
        reply_markup=get_confirmation_kb(),
    )




