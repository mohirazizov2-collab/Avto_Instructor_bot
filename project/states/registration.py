from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):

    # ============================================================
    # UMUMIY
    # ============================================================

    choosing_role = State()


    # ============================================================
    # STUDENT
    # ============================================================

    student_name = State()
    student_phone = State()
    student_category = State()
    student_instructor = State()
    student_training_type = State()
    student_confirm = State()


    # ============================================================
    # INSTRUCTOR
    # ============================================================

    instructor_name = State()
    instructor_phone = State()
    instructor_date_of_birth = State()
    instructor_experience = State()
    instructor_hourly_price = State()
    instructor_gender = State()

    # Prava
    instructor_driving_license = State()
    instructor_driving_license_expiry = State()
    instructor_driving_license_front_photo = State()
    instructor_driving_license_back_photo = State()

    # Kategoriya
    instructor_categories = State()

    # Hudud
    instructor_region = State()

    # Avtomobil
    instructor_vehicle_info = State()
    instructor_vehicle_photo = State()

    # Texnik pasport
    instructor_tech_passport_front_photo = State()
    instructor_tech_passport_back_photo = State()

    # Sertifikat
    instructor_certificate_photo = State()

    # Profil
    instructor_profile_photo = State()

    # Tasdiqlash
    instructor_confirm = State()
