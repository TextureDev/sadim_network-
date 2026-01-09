#ملف البريد الإلكتروني
from datetime import datetime
from db import sadim_db

class Email:
    def __init__(self, id=None, user_id=None, token=None, expires_at=None, is_used=False, created_at=None): 
        self.id = id
        self.user_id = user_id
        self.token = token
        self.expires_at = expires_at
        self.is_used = is_used
        self.created_at = created_at
    
    # الحصول على اتصال قاعدة البيانات
    @staticmethod
    def get_db_connection():
        return sadim_db.get_db_connection()

    # إضافة رمز تحقق جديد
    @staticmethod
    def add_token(user_id, token, expires_at):
        conn =  sadim_db.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO email_verifications (user_id, token, expires_at, is_used)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """, (user_id, token, expires_at, False))
        token_id = cur.fetchone()[0] # الحصول على معرف الرمز الجديد
        conn.commit()
        cur.close()
        conn.close()
        return token_id
    # استرجاع رمز تحقق بواسطة الكود
    @staticmethod
    def get_by_code(token):
        conn = sadim_db.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, token, expires_at, is_used, created_at
            FROM email_verifications WHERE token = %s;""", (token,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return Email(*row) if row else None
    # تحديث حالة الرمز (مستخدم أو لا)
    def mark_as_used(self):
        conn = sadim_db.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE email_verifications
            SET is_used=TRUE
            WHERE id = %s;
            """, (self.id,))
        conn.commit()
        cur.close()
        conn.close()
    # حذف الرموز القديمة (منتهية الصلاحية أو المستخدمة)
    def delete_old_tokens(self):
        conn = sadim_db.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM email_verifications
            WHERE expires_at < %s OR is_used=TRUE;
            """, (datetime.now(),))
        conn.commit()
        cur.close()
        conn.close()
# نهاية ملف البريد الإلكتروني