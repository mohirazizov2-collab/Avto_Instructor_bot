path = "project/keyboards/main.py"

with open(path, encoding="utf-8") as f:
    content = f.read()

old = """            [
                InlineKeyboardButton(
                    text="📝 Registratsiya",
                    callback_data="register",
                )
            ],"""

new = """            [
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
            ],"""

if old in content:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Muvaffaqiyatli tuzatildi!")
else:
    print("Mos matn topilmadi.")
