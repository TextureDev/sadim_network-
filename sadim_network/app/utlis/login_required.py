from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs): # هنا بنشيك إذا المستخدم مسجل دخول
        if 'user_id' not in session: # الشرط لو المستخدم مش مسجل دخول
         return redirect(url_for('loading_bp.login'))

        return f(*args, **kwargs) # لو مسجل دخول بننفذ الدالة الأصلية
    return decorated_function # بنرجع الديكوريتور