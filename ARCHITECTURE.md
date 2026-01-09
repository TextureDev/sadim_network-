**ملخص معماري لمشروع Sadim Network**

**الهدف:** وصف بنية التطبيق، مكوناته، تدفق البيانات، ومتطلبات النشر دون تعديل أي شفرة موجودة.

**نوع التطبيق:** تطبيق ويب مبني بـ `Flask` يقدم صفحات HTML وعمليات تسجيل/تسجيل دخول ولوحة إدارة.

**المكوّنات الرئيسية:**
- **تطبيق Flask:** تعريف التطبيق في `app/__init__.py` مع تسجيل بلوبرنتات: `main_bp`, `register_bp`, `loading_bp`, `admin_bp`, `errors_bp`.
- **قوالب وستايتك:** مجلد `app/templates` لواجهات HTML و`app/static` للملفات الثابتة والرفع في `static/uploads`.
- **نُهج التوجيه (Routes):** بلورنتات مفصولة داخل `app/routess` (Pages, Auth, Admin).
- **طبقة النماذج/البيانات:** `app/models` يحوي `User`, `service` (products/services), و`Email` (رموز التحقق) مع دوال CRUD.
- **طبقة Repository/Services:** `routess/Repository` لعزل منطق الوصول إلى البيانات (مثال: `auth_service.py`).
- **قاعدة البيانات:** PostgreSQL عبر `psycopg2`، تعريف الجداول في `app/db/sadim_db.py` (`users`, `services`, `email_verifications`, `visitor_logs`, `user_logs`).
- **الجلسات/كاش:** Redis مذكور في `app/config/settings.py` لاستخدامه مع جلسات التطبيق و`flask_limiter`.
- **حدود الطلبات:** `flask_limiter` مهيأ في `app/pppp.py` ومطبق على نقاط الدخول الحساسة.
- **خدمات خارجية:** SMTP لإرسال بريد التحقق (تُستخدم دوال في `app/utlis/email_utils.py`).

**نماذج البيانات الأساسية:**
- `users`: `id, username, email, password_hash, role, is_verified, profile_image, last_login, status, created_at, updated_at`.
- `services`: `id, title, description, price, image_url, download_url, delivery_time, category, created_at, updated_at`.
- `email_verifications`: `id, user_id, token, expires_at, is_used, created_at`.
- `visitor_logs` و `user_logs` لسجلات الزوار ونشاط المستخدمين.

**تدفق البيانات (عالي المستوى):**
- المستخدم يرسل طلبات عبر المتصفح → Nginx (اختياري) → WSGI (gunicorn/uwsgi) → تطبيق Flask.
- نقاط الإدخال (Routes) تتعامل مع النماذج وتستدعي Repository/Model التي تتصل بـ Postgres.
- الجلسات مخزنة في Redis، وملفات الوسائط تُخزن محلياً في `static/uploads` أو يمكن نقلها إلى S3.
- إرسال بريد التحقق يتم عبر SMTP المكوّن في `email_utils.py`.

**أمن وممارسات موصى بها:**
- تفعيل HTTPS عبر Nginx وتهيئة `SESSION_COOKIE_SECURE`, `HTTPONLY` و `SAMESITE` (مختلفة حسب الحاجة).
- استخدام كلمات مرور تطبيق للبريد، وعدم تخزين بيانات حساسة في الكود — استخدم `.env` (المفاتيح موجودة في `app/config/settings.py`).
- حماية نقاط الدخول الحيوية باستخدام `login_required`, دور `admin_required`، و`flask_limiter`.

**نشر مقترح:**
- واجهة ثابتة عبر Nginx، وخادم تطبيق خلفه باستخدام `gunicorn` مع عدد مناسب من workers.
- Postgres كخدمة منفصلة (managed أو container)، وRedis للجلسات والlimiting.
- تخزين الوسائط: البدء بمحلي ثم الانتقال إلى S3 عند الحاجة للتوسع.
- إضافة عمليات CI/CD للتدقيق واختبارات الراوبط الحرجة (auth, register, upload).

**مخطط مقترح للرسم:**
- صناديق: `Browser` → `Nginx (static)` → `Gunicorn/Flask` → داخلياً: `Blueprints`, `Repository/Models` → قواعد خارجية: `Postgres`, `Redis`, `SMTP`, `Uploads(S3)`.
- ضع أسهم توضح: طلبات المستخدم → بلوبرنت → Repository → DB/Redis/SMTP.

**خطوات مقبلة مقترحة:**
1. توليد رسم بياني (PNG/SVG) للمخطط أعلاه.
2. مراجعة إعدادات `.env` والتأكد من `REDIS_URL`, `DB_*`, `EMAIL_USER`, `EMAIL_PASS` قبل الإنتاج.
3. إعداد `gunicorn` وNginx وكتابة ملف `docker-compose` أو manifests للنشر إن رغبت.

إذا تريد، أكتب ملف رسم (Graphviz `.dot`) أو أنشئ PNG/SVG للمخطط الآن.

***انتهى***
