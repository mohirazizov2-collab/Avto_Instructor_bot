path = "project/handlers/student.py"

with open(path, encoding="utf-8") as f:
    content = f.read()

old = "instructor_telegram_id = await get_telegram_id_for_instructor(instructor)"
new = "instructor_telegram_id = await get_telegram_id_for_instructor(instructor.id)"

if old in content:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Muvaffaqiyatli tuzatildi!")
else:
    print("Mos matn topilmadi.")
