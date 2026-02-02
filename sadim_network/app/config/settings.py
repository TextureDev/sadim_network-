
# settings.py
import os
from dotenv import load_dotenv
import redis

# تحميل المتغيرات من ملف .env
load_dotenv()

# ====== إعدادات Flask الأساسية ======
SECRET_KEY = os.getenv("SECRET_KEY")  # مفتاح قوي للجلسة
SESSION_TYPE = os.getenv("SESSION_TYPE", "redis")  # استخدام Redis للجلسات
SESSION_REDIS = redis.from_url(os.getenv("REDIS_URL"))

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"

# ====== إعدادات قاعدة البيانات ======
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))

APP_URL = os.getenv("APP_URL")

# ====== إعدادات البريد ======
EMAIL_USER = os.getenv("EMAIL_USER")       # البريد الرسمي: 
EMAIL_PASS = os.getenv("EMAIL_PASS")       
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.hostinger.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False") == "True"
EMAIL_DEFAULT_SENDER = EMAIL_USER
