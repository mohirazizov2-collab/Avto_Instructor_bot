# Avtomaktab Telegram Bot

Telegram bot loyihasi uchun modular Python arxitekturasi. Bu loyiha quyidagi funksiyalarni o'z ichiga oladi:

- /start menyusi
- Registratsiya: instruktor yoki o'quvchi
- FSM-based bosqichma-bosqich ma'lumot yig'ish
- Kiritilgan ma'lumotlar validatsiyasi
- SQLite / SQLAlchemy modeli
- Profil ko'rish
- /cancel va ortga qaytish imkoniyatlari

## Strukturasi

```text
project/
├── bot.py
├── config.py
├── database/
│   ├── __init__.py
│   ├── database.py
│   └── models.py
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   ├── registration.py
│   ├── instructor.py
│   ├── student.py
│   └── profile.py
├── keyboards/
│   ├── __init__.py
│   ├── main.py
│   ├── registration.py
│   └── profile.py
├── states/
│   ├── __init__.py
│   └── registration.py
├── services/
│   ├── __init__.py
│   └── validation.py
├── __init__.py
└── requirements.txt
```

## Ishga tushirish

1. Virtual environment yarating:

```bash
python -m venv .venv
```

2. Activate qiling:

- Windows:

```powershell
.venv\Scripts\Activate.ps1
```

- Linux/macOS:

```bash
source .venv/bin/activate
```

3. Dependencylarni o'rnating:

```bash
pip install -r project/requirements.txt
```

4. `.env` faylini to'ldiring:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
DATABASE_URL=sqlite+aiosqlite:///./avtomaktab.db
APP_NAME=Avtomaktab Bot
LOG_LEVEL=INFO
```

5. Botni ishga tushiring:

```bash
python -m project.bot
```

## Qo'shimcha

- Bot uchun Telegram token kerak.
- SQLite default database sifatida ishlaydi.
- Kelajakda admin panel, dars bron qilish, to'lov va boshqa modullar uchun arxitektura kengaytirilishi mumkin.
