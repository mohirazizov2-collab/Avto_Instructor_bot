import re
from datetime import datetime, date


def validate_name(value: str) -> bool:
    value = value.strip()
    if not value or len(value) < 2:
        return False
    if value.isdigit():
        return False
    return True


def validate_phone(value: str) -> bool:
    cleaned = re.sub(r'\s+|[-()]+', '', value.strip())
    pattern = r'^\+?998\d{9}$'
    return bool(re.fullmatch(pattern, cleaned))


def validate_positive_int(value: str) -> bool:
    try:
        number = int(value.strip())
    except ValueError:
        return False
    return number > 0


def validate_positive_money(value: str) -> bool:
    try:
        number = int(value.strip().replace(' ', ''))
    except ValueError:
        return False
    return number > 0


def normalize_phone(value: str) -> str:
    cleaned = re.sub(r'\s+|[-()]+', '', value.strip())
    if cleaned.startswith('998'):
        return '+' + cleaned
    if cleaned.startswith('+998'):
        return cleaned
    return '+998' + cleaned.lstrip('0') if cleaned.isdigit() else cleaned


def validate_date(value: str) -> bool:
    """Validate date format: DD.MM.YYYY or DD/MM/YYYY"""
    try:
        if '.' in value:
            datetime.strptime(value.strip(), '%d.%m.%Y')
        elif '/' in value:
            datetime.strptime(value.strip(), '%d/%m/%Y')
        else:
            return False
        return True
    except ValueError:
        return False


def parse_date(value: str) -> date | None:
    """Parse date from DD.MM.YYYY or DD/MM/YYYY format"""
    try:
        if '.' in value:
            dt = datetime.strptime(value.strip(), '%d.%m.%Y')
        elif '/' in value:
            dt = datetime.strptime(value.strip(), '%d/%m/%Y')
        else:
            return None
        return dt.date()
    except ValueError:
        return None


def validate_age(birth_date: date, min_age: int = 18) -> bool:
    """Validate if person is at least min_age years old"""
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age >= min_age


def validate_driving_license_number(value: str) -> bool:
    """Validate driving license number format"""
    value = value.strip().upper()
    # Simple validation: should be at least 5 characters alphanumeric
    return len(value) >= 5 and value.replace(' ', '').isalnum()


def validate_vehicle_brand_model(value: str) -> bool:
    """Validate vehicle brand and model"""
    value = value.strip()
    return len(value) >= 3 and len(value) <= 200
