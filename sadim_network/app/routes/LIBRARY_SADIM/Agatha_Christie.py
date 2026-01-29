from flask import (
    Blueprint,
    render_template,
    url_for,
    session,
    redirect,
    send_from_directory,
    request,
    flash
)
from app.db.sadim_db import get_db_connection
import os
from psycopg2.extras import RealDictCursor
import psycopg2.extras

# إنشاء البلوبرينت مع تحديد مجلد الملفات الثابتة بشكل صريح
Library_Agatha_bp = Blueprint(
    'Library_Agatha',
    __name__,
    template_folder='templates',
    static_folder='static'
)
import os

# نحدد مكان الملف الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))

# نصعد مستويين فقط للوصول لمجلد app (من LIBRARY_SADIM إلى routes ثم إلى app)
# المستوى 1: .. (يخرج من LIBRARY_SADIM إلى routes)
# المستوى 2: .. (يخرج من routes إلى app)
BASE_DIR = os.path.abspath(os.path.join(current_dir, "..", ".."))

# الآن ندمج المسار مع static/uploads
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

print(f"🎯 CORRECT PATH: {UPLOAD_FOLDER}")
# =========================
# عرض المكتبة للجمهور
# =========================
@Library_Agatha_bp.route('/library/agatha_christie')
def agatha_christie():
    # التحقق من تسجيل الدخول (اختياري حسب رغبتك)
#    if 'user_id' not in session:
#        return redirect(url_for('loading_bp.login'))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # جلب جميع الكتب لعرضها
    cur.execute("SELECT * FROM books ORDER BY id DESC;")
    books = cur.fetchall()
    
    cur.close()
    conn.close()

    return render_template("Agatha Christie/Agatha.html", books=books)

# =========================
# 1. تحديث عداد التحميلات (تفاعل لحظي - JSON)
# =========================
@Library_Agatha_bp.route('/library/increment_download/<int:book_id>', methods=['POST'])
def increment_download(book_id):
    if 'user_id' not in session:
       flash("يجب تسجيل الدخول لتحميل الكتب.", "warning")
       return redirect(url_for('loading_bp.login'))
   
    conn = get_db_connection()
    cur = conn.cursor() # لا نحتاج RealDictCursor هنا لأننا سنعيد قيمة واحدة
    try:
        # نستخدم COALESCE لتفادي الخطأ إذا كانت القيمة NULL، ونعيد القيمة الجديدة فوراً
        cur.execute("""
            UPDATE books 
            SET download_count = COALESCE(download_count, 0) + 1 
            WHERE id = %s 
            RETURNING download_count
        """, (book_id,))
        
        new_count = cur.fetchone()[0]
        conn.commit()
        return {"success": True, "new_count": new_count}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}, 500
    finally:
        cur.close()
        conn.close()

# =========================
# 2. تحميل الملف الفعلي (بدون تحديث العداد هنا)
# =========================
@Library_Agatha_bp.route('/library/download/<int:book_id>')
def download_file(book_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # نجلب بيانات الكتاب فقط
    cur.execute("SELECT title, pdf_path FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    
    cur.close()
    conn.close()

    if book:
        file_path = os.path.join(UPLOAD_FOLDER, book['pdf_path'])
        if os.path.exists(file_path):
            return send_from_directory(
                UPLOAD_FOLDER, 
                book['pdf_path'], 
                as_attachment=True,
                download_name=f"{book['title']}.pdf"
            )
        return "الملف غير موجود على السيرفر", 404
            
    return "الكتاب غير موجود في قاعدة البيانات", 404

# =========================
# 3. البحث (تمت إضافة حقل download_count)
# =========================
@Library_Agatha_bp.route('/search')
def search():
    query = request.args.get('q', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # أضفنا id و cover_path و download_count لتعمل نتائج البحث بنفس كفاءة الصفحة الرئيسية
    cur.execute("""
        SELECT id, title, desc_text, pdf_path, cover_path, download_count
        FROM books
        WHERE title ILIKE %s
        ORDER BY id DESC
    """, (f"%{query}%",))

    books = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "Agatha Christie/search_results.html",
        query=query,
        books=books
    )