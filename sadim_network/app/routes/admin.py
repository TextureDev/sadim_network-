# ملف لادارة الموقع هذه نسخة متواضعة
#_____  
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import psycopg2.extras
import pytz
import time # أضف هذا الاستيراد في الأعلى

#_________
from app.db.sadim_db import get_db_connection
from utlis.login_required import login_required
from utlis.permissions import admin_required
from datetime import datetime
import os
from models.user import User
from models.product import service
from app.utlis.apply_sadim_brand import apply_sadim_brand

admin_bp = Blueprint('admin', __name__, url_prefix='/dashboard', template_folder='../../templates')


UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#هنا يتأكد من وجود الملف و لا
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# إعدادات المجلدات (توحيد مسار الرفع)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================================
# قسم إدارة مكتبة أجاثا كريستي (الدمج الجديد)
# ==========================================

@admin_bp.route('/library/manage')
@login_required
@admin_required
def manage_library():
    """عرض الكتب في لوحة التحكم"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM books ORDER BY id DESC;")
    books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("dashboard/admin_dashboard.html", books=books)


@admin_bp.route('/library/add', methods=['POST'])
@login_required
@admin_required
def add_book_to_library():
    title = request.form.get('title')
    desc = request.form.get('desc')
    pdf = request.files.get('pdf_file')
    cover = request.files.get('cover_file')

    if not all([title, pdf, cover]):
        flash("❌ خطأ: جميع الحقول مطلوبة", "danger")
        return redirect(url_for('admin.manage_library'))

    if allowed_file(pdf.filename) and allowed_file(cover.filename):
        # استخراج الامتدادات
        pdf_ext = pdf.filename.rsplit('.', 1)[1].lower()
        cover_ext = cover.filename.rsplit('.', 1)[1].lower()

        # توليد اسم فريد للسيرفر (بصمة زمنية) لتجنب مشاكل العربي والملفات المتكررة
        timestamp = int(time.time())
        pdf_name = f"sadim_{timestamp}.{pdf_ext}"
        cover_name = f"cover_{timestamp}.{cover_ext}"

        pdf_full_path = os.path.join(UPLOAD_FOLDER, pdf_name)
        cover_full_path = os.path.join(UPLOAD_FOLDER, cover_name)

        # حفظ الملفات
        pdf.save(pdf_full_path)
        cover.save(cover_full_path)

        # إضافة شعار سديم
        try:
            apply_sadim_brand(pdf_full_path)
        except Exception as e:
            print(f"⚠️ فشل إضافة الشعار: {e}")

        # حفظ البيانات (العنوان العربي سيحفظ في خانة title)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO books (title, desc_text, pdf_path, cover_path) VALUES (%s, %s, %s, %s)",
            (title, desc, pdf_name, cover_name) # title هنا هو الاسم العربي الذي أدخلته في الفورم
        )
        conn.commit()
        cur.close()
        conn.close()
        
        flash("✅ تم رفع الرواية بنجاح!", "success")
    else:
        flash("❌ نوع ملف غير مسموح", "warning")

    return redirect(url_for('admin.manage_library'))


@admin_bp.route('/library/edit/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def edit_book_in_library(book_id):
    """تعديل كتاب في المكتبة مباشرة من لوحة الإدارة"""
    title = request.form.get(f"title-{book_id}")
    desc = request.form.get(f"desc-{book_id}")

    if not title:
        flash("❌ العنوان مطلوب", "danger")
        return redirect(url_for('admin.manage_library'))

    # الملفات المرفوعة (قد تكون None)
    cover = request.files.get(f"cover_file-{book_id}")
    pdf = request.files.get(f"pdf_file-{book_id}")

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # جلب الكتاب الحالي لتحديد الملفات القديمة
    cur.execute("SELECT cover_path, pdf_path FROM books WHERE id=%s", (book_id,))
    book = cur.fetchone()

    # تحديث الملفات إذا تم رفع جديدة
    cover_name = book['cover_path']
    pdf_name = book['pdf_path']

    timestamp = int(time.time())

    if cover and allowed_file(cover.filename):
        old_cover_path = os.path.join(UPLOAD_FOLDER, cover_name)
        if os.path.exists(old_cover_path):
            os.remove(old_cover_path)

        ext = cover.filename.rsplit('.', 1)[1].lower()
        cover_name = f"cover_{timestamp}.{ext}"
        cover.save(os.path.join(UPLOAD_FOLDER, cover_name))

    if pdf and allowed_file(pdf.filename):
        old_pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
        if os.path.exists(old_pdf_path):
            os.remove(old_pdf_path)

        ext = pdf.filename.rsplit('.', 1)[1].lower()
        pdf_name = f"sadim_{timestamp}.{ext}"
        pdf.save(os.path.join(UPLOAD_FOLDER, pdf_name))

        # إضافة شعار سديم للملف الجديد
        try:
            apply_sadim_brand(os.path.join(UPLOAD_FOLDER, pdf_name))
        except Exception as e:
            print(f"⚠️ فشل إضافة الشعار: {e}")

    # تحديث قاعدة البيانات
    cur.execute(
        "UPDATE books SET title=%s, desc_text=%s, cover_path=%s, pdf_path=%s WHERE id=%s",
        (title, desc, cover_name, pdf_name, book_id)
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("✅ تم تحديث بيانات الكتاب بنجاح", "success")
    return redirect(url_for('admin.manage_library'))



@admin_bp.route('/library/delete/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def delete_book_from_library(book_id):
    """حذف كتاب من المكتبة مع ملفاته"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("SELECT pdf_path, cover_path FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()

    if book:
        # حذف الملفات الفيزيائية
        for key in ['pdf_path', 'cover_path']:
            file_path = os.path.join(UPLOAD_FOLDER, book[key])
            if os.path.exists(file_path):
                os.remove(file_path)

        cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        flash("🗑️ تم حذف الكتاب وملفاته بنجاح", "danger")
    
    cur.close()
    conn.close()
    return redirect(url_for('admin.manage_library'))

# ------------------ صفحة عرض جميع الخدمات ------------------
@admin_bp.route('/services')

def show_services():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        # جلب الكتب
        cur.execute("""
            SELECT id, image_url, name, category, description, title, type, price, download_url, delivery_time
            FROM services
            WHERE category = 'books'
            ORDER BY created_at DESC
        """)
        books = cur.fetchall()
        
        # جلب الأدوات التقنية
        cur.execute("""
            SELECT id, image_url, name, category, description, title, type, price, download_url, delivery_time
            FROM services
            WHERE category = 'tech'
            ORDER BY created_at DESC
        """)
        tech_tools = cur.fetchall()
    
    finally:
        cur.close()
        conn.close()
    
    # اسم المستخدم من session
    username = session.get('username', 'ضيف')

    # الوقت الحالي حسب منطقتك
    tz = pytz.timezone("Africa/Tripoli")
    now = datetime.now(tz)
    current_time = now.strftime("%Y-%m-%d")

    # تحديد التحية حسب الوقت
    hour = now.hour
    if 5 <= hour < 12:
        greeting = "صباح الخير"
    elif 12 <= hour < 17:
        greeting = "مساء النور"
    else:
        greeting = "مساء الخير"

    return render_template('dashboard/services.html', books=books, tech_tools=tech_tools,
                           username=username, greeting=greeting, current_time=current_time)

# ------------------ صفحة إضافة خدمة جديدة ------------------

# --- في دالة add_service ---
@admin_bp.route('/services/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_service():
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        delivery_time = request.form['delivery_time']
        category = request.form.get('category', 'tech')  # استلام التصنيف الجديد

        # التعامل مع الصورة (نفس كودك الحالي)
        image_file = request.files.get('image')

        if image_file and image_file.filename != '':

            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_url = f'uploads/{filename}'
        else:
            image_url = 'uploads/default.jpg'
 
        # إدخال البيانات مع التصنيف
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO services (image_url, name, category, description, title, price, delivery_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (image_url, title, category, description, title, price, delivery_time))
        conn.commit()
        cur.close()
        conn.close()

        
        flash('✅ تمت إضافة الخدمة بنجاح!', 'success')
        return redirect(url_for('admin.add_service'))

    return render_template('dashboard/service_form.html', service=None)

# ------------------ صفحة تعديل خدمة ------------------
@admin_bp.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
@admin_required

def edit_service(service_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form.get('image_url')
        delivery_time = request.form['delivery_time']
        category = request.form.get('category') # الخطوة 1: استلام النوع

        cur.execute("""
            UPDATE services
            SET title=%s, description=%s, price=%s, image_url=%s, delivery_time=%s, category=%s
            WHERE id=%s
        """, (title, description, price, image_url, delivery_time, category, service_id)) # الخطوة 2: التحديث
        conn.commit()

        cur.close()
        conn.close()
        flash('تم تحديث الخدمة بنجاح!', 'success')
        return redirect(url_for('admin.show_services'))

    # عرض البيانات في النموذج للتعديل
    cur.execute("SELECT id, title, description, price, image_url, delivery_time FROM services WHERE id=%s", (service_id,))
    service = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('dashboard/service_form.html', service=service)

# ------------------ حذف خدمة ------------------
@admin_bp.route('/services/delete/<int:service_id>')
@login_required
@admin_required

def delete_service(service_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM services WHERE id=%s", (service_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('تم حذف الخدمة بنجاح!', 'danger')
    return redirect(url_for('admin.add_service'))

# ------------------ صفحة لوحة التحكم الرئيسية ------------------
@admin_bp.before_request
@login_required

def log_visitors():
    if request.path.startswith("/dashboard"):
        return  # تجاهل زيارات لوحة التحكم

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    path = request.path

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO visitor_logs (ip, user_agent, path) VALUES (%s, %s, %s)",
        (ip, user_agent, path)
    )
    conn.commit()
    cur.close()
    conn.close()


@admin_bp.route('/')
@login_required
@admin_required


def dashboard_home():
    conn = get_db_connection()
    cur = conn.cursor()

    # عدد الزوار
    cur.execute("SELECT COUNT(*) FROM visitor_logs")
    total_visits = cur.fetchone()[0] 

    # آخر 20 زيارة
    cur.execute("SELECT ip, user_agent, path, timestamp FROM visitor_logs ORDER BY timestamp DESC LIMIT 1000")
    visits = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('dashboard/dashboard_home.html', total_visits=total_visits, visits=visits)
# ------------------ صفحة عرض المستخدمين ------------------
@admin_bp.route('/users')
@login_required
@admin_required

def dashboard_users():
    conn = get_db_connection()
    cur = conn.cursor()

    # المتصلين الآن – آخر 5 دقائق
    cur.execute("""
        SELECT email, username, ip, user_agent, created_at 
        FROM user_logs 
        WHERE created_at >= NOW() - INTERVAL '5 minutes'
        ORDER BY created_at DESC
    """)
    online_users = cur.fetchall()

    # غير المتصلين
    cur.execute("""
        SELECT email, username, ip, user_agent, created_at 
        FROM user_logs 
        WHERE created_at < NOW() - INTERVAL '5 minutes'
        ORDER BY created_at DESC
    """)
    offline_users = cur.fetchall()

    # إحصائيات آخر ظهور
    stats = {}

    cur.execute("SELECT COUNT(*) FROM user_logs WHERE created_at >= NOW() - INTERVAL '1 day'")
    stats["day"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM user_logs WHERE created_at >= NOW() - INTERVAL '7 days'")
    stats["week"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM user_logs WHERE created_at >= NOW() - INTERVAL '30 days'")
    stats["month"] = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        'dashboard/users_dashboard.html',
        online_users=online_users,
        offline_users=offline_users,
        stats=stats
    )

# ------------------ حذف جميع الزيارات ------------------
@admin_bp.route('/delete_visits', methods=['POST'])
@login_required
@admin_required

def delete_visits():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM visitor_logs")
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('admin.dashboard_home'))

@admin_bp.route("/serverss")
@login_required
@admin_required
def services_dashboard():
    username = session.get('username', 'ضيف')

    # الوقت الحالي حسب منطقتك
    tz = pytz.timezone("Africa/Tripoli")
    now = datetime.now(tz)
    current_time = now.strftime("%Y-%m-%d")

    # تحديد التحية حسب الوقت
    hour = now.hour
    if 5 <= hour < 12:
        greeting = "صباح الخير"
    elif 12 <= hour < 17:
        greeting = "مساء النور"
    else:
        greeting = "مساء الخير"
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT * FROM services ORDER BY created_at DESC")
        services = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    # اختبار ما تم جلبه
    print("Services:", services)

    return render_template("dashboard/services_dashboard.html", services=services, username=username, greeting=greeting, current_time=current_time)


@admin_bp.route('/dashboard/userss')
@login_required
@admin_required
def admin_users_list():
    users = User.get_all()
    return render_template('dashboard/users.html', users=users)

@admin_bp.route('/view_user/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    user = User.get_by_id(user_id)
    if user is None:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for('admin.admin_users_list'))
    

    return render_template('dashboard/view_user.html', user=user)

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.get_by_id(user_id)

    if not user:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for('admin.admin_users_list'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        status = request.form['status']
        password = request.form.get('password')
        verified = request.form.get('is_verified') == 'on'
        user.name = name
        user.email = email
        user.role = role
        user.status = status
        if password and password.strip():
            user.password_hash = password  # تأكد من أن setter الخاص بك يقوم بالتجزئة
        user.is_verified = verified
        user.update_user()

        flash('تم تحديث المستخدم بنجاح', 'success')
        return redirect(url_for('admin.admin_users_list'))

    return render_template('dashboard/edit_user.html', user=user)





@admin_bp.route('/soft_delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def soft_delete_user(user_id):
    user = User.delete(user_id)
    flash('تم تعطيل المستخدم', 'warning')
    return redirect(url_for('admin.admin_users_list'))


@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        user = User(name=name, username=username, email=email, password=password, role=role)
        user.add_to_db()

        flash('تم إضافة المستخدم بنجاح', 'success')
        return redirect(url_for('admin.admin_users_list'))

    return render_template('dashboard/add_user.html')