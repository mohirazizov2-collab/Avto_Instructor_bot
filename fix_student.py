path = "project/handlers/student.py"

with open(path, encoding="utf-8") as f:
    content = f.read()

old = """    await save_student(
        user_id=user.id,
        instructor_id=instructor.id,
        full_name=data['full_name'],
        phone=data['phone'],
        training_type='matching',
        desired_category=data['desired_category'],
    )"""

new = """    await save_student(
        user=user,
        data=data,
        instructor_id=instructor.id,
    )"""

if old in content:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Muvaffaqiyatli tuzatildi!")
else:
    print("Mos matn topilmadi - qolda tuzatish kerak bolishi mumkin.")
    print("Faylni ochib, save_student( sozini qidiring.")
