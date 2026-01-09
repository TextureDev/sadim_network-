# settings.py
import os
from dotenv import load_dotenv
import redis
# تحميل المتغيرات من ملف .env
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")  # غيّرها لأي مفتاح قوي
SESSION_TYPE = os.getenv("SESSION_TYPE", "redis")  # القيمة الافتراضية 
SECRET_REDIS_URL = redis.from_url(os.getenv("REDIS_URL"))  # إعداد Redis للجلسات
# إعدادات البريد
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")  # استخدم كلمة مرور التطبيق من Gmail

    # القيمة الافتراضية 5432
DB_NAME =  os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = 5432 

APP_URL = os.getenv("APP_URL")  
# إعدادات أخرى يمكن إضافتها هنا حسب الحاجة
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"

