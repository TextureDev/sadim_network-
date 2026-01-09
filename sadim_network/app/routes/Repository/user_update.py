# ملف لتحديث بيانات المستخدم في قاعدة البيانات
from db import sadim_db
from models.user import User
from datetime import datetime

def update_user(user: User):  
        """تحديث بيانات المستخدم في قاعدة البيانات"""
        conn = sadim_db.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE users
            SET name=%s, username=%s, user_agent=%s, ip=%s, email=%s, password_hash=%s, role=%s, is_verified=%s, updated_at=%s
            WHERE id=%s;
                    """, (user.name, user.username, user.user_agent, user.ip, user.email, user.password_hash, user.role, user.is_verified, datetime.now(), user.id))
        conn.commit()
        cur.close()
        conn.close()
        return True