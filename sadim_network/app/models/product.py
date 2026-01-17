from unicodedata import category
from db.sadim_db import get_db_connection
from datetime import datetime, timedelta


class service:
    @staticmethod
    def add_service(image_url, name, category, description, title, type):
        """إضافة خدمة جديدة إلى قاعدة البيانات"""
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO services (image_url, name, category, description, title, type, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (image_url, name, category, description, title, type, datetime.now(), datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        return True
    
    @staticmethod
    def get_all_services():
        """جلب جميع الخدمات من قاعدة البيانات"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM services;")
        services = cur.fetchall()
        cur.close()
        conn.close()
        return services
    
    @staticmethod
    def get_service_by_id(service_id):
        """جلب خدمة بواسطة معرفها"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM services WHERE id=%s;", (service_id,))
        service = cur.fetchone()
        cur.close()
        conn.close()
        return service
    
    @staticmethod
    def delete_service(service_id):
        """حذف خدمة من قاعدة البيانات"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM services WHERE id=%s;", (service_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    
    @staticmethod
    def update_service(service_id, image_url, name, description, title, type):
        """تحديث بيانات خدمة في قاعدة البيانات"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE services
            SET image_url=%s, name=%s, category=%s, description=%s, title=%s, type=%s, updated_at=%s
            WHERE id=%s;
        """, (image_url, name, category, description, title, type, datetime.now(), service_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    
    @staticmethod
    def search_services(keyword):
        """البحث عن خدمات بواسطة كلمة مفتاحية في الاسم أو الوصف"""
        conn = get_db_connection()
        cur = conn.cursor()
        search_pattern = f"%{keyword}%"
        cur.execute("""
            SELECT * FROM services
            WHERE name ILIKE %s OR description ILIKE %s;
        """, (search_pattern, search_pattern))
        services = cur.fetchall()
        cur.close()
        conn.close()
        return services
    @staticmethod
    def get_services_by_type(service_type):
        """جلب خدمات بواسطة النوع"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM services WHERE type=%s;", (service_type,))
        services = cur.fetchall()
        cur.close()
        conn.close()
        return services
    
    @staticmethod
    def count_services():
        """عد عدد الخدمات في قاعدة البيانات"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM services;")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    