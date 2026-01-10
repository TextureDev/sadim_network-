#ملف بس انشئ الادمن و سيحذف بالسيرفر
from models.user import User

def create_admin():
    email = "saaadqutub@gmail.com"
    password = ""  # كلمة المرور الأصلية
    admin = User.get_by_email(email)

    if admin:
        print("⚠️ الأدمن موجود مسبقًا:", email)
        return

    new_admin = User(
        username="admin",
        name="salah",
        email=email,
        role="admin",
        password=password,
        is_verified=True
    )
    
    # تشفير كلمة المرور وإضافة المستخدم
    new_admin.add_to_db()
    print("✅ تم إنشاء الأدمن بنجاح:", email)

if __name__ == "__main__":
    create_admin()
