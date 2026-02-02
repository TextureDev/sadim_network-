
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# إضافة المسار لجلب الإعدادات
from config import settings

def send_verification_email(to_email, token):
    """
    إرسال بريد التحقق باستخدام منطق الإرسال الناجح مع قالب سديم الاحترافي
    """
    if not all([settings.EMAIL_USER, settings.EMAIL_PASS, settings.APP_URL]):
        raise RuntimeError('Missing configuration: EMAIL_USER, EMAIL_PASS, or APP_URL')

    subject = 'تأكيد البريد الإلكتروني - شبكة سديم'
    verify_link = f"{settings.APP_URL}/verify_email/{token}"

    # 1. إنشاء الرسالة وتجهيز الـ Headers بنفس الطريقة الناجحة
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_USER  # استخدمنا البريد مباشرة كما في الكود الناجح
    msg['To'] = to_email

    # 2. قالب الـ HTML الاحترافي
    html = f"""
    <html lang="ar" dir="rtl">
      <body style="margin:0; padding:0; background-color: #1a1a2e; font-family: sans-serif;">
        <table align="center" width="100%" style="max-width:600px; margin:40px auto; background:#ffffff; border-radius:16px; overflow:hidden; border: 1px solid #2b124c;">
          <tr>
            <td style="background: linear-gradient(135deg, #2b124c 0%, #522b5b 100%); padding:40px; text-align:center;">
              <h1 style="color:#dfb6b2; margin:0; font-size:28px;">SADEEM NETWORK</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:40px; text-align: right; color:#2b124c;">
              <h2 style="color:#854f6c;">تفعيل الحساب ✨</h2>
              <p>مرحباً بك، خطوة واحدة تفصلك عن الانضمام لشبكة سديم التقنية. يرجى الضغط على الزر أدناه:</p>
              <div style="text-align:center; margin:30px 0;">
                <a href="{verify_link}" style="background:#854f6c; color:#ffffff; padding:15px 35px; text-decoration:none; border-radius:10px; display:inline-block; font-weight:bold;">تفعيل حسابي الآن</a>
              </div>
              <p style="font-size:12px; color:#666; border-top:1px solid #eee; padding-top:20px;">
                إذا واجهت مشكلة، انسخ الرابط: <br> {verify_link}
              </p>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    # 3. إرفاق المحتوى (UTF-8)
    part = MIMEText(html, 'html', 'utf-8')
    msg.attach(part)

    # 4. عملية الإرسال باستخدام المنطق الناجح (send_message)
    try:
        print(f"🔌 محاولة الاتصال بـ {settings.EMAIL_HOST} عبر المنفذ {settings.EMAIL_PORT}...")
        
        # اختيار بروتوكول الاتصال بناءً على الإعدادات
        if settings.EMAIL_USE_SSL:
            with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=15) as server:
                server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=15) as server:
                if settings.EMAIL_USE_TLS:
                    server.starttls()
                server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
                server.send_message(msg)

        print(f"✅ تم إرسال بريد التأكيد بنجاح إلى: {to_email}")
        return True

    except Exception as e:
        print(f"❌ فشل الإرسال: {e}")
        return False
    

# لم اكتبه بنفسي بل كتبه ai 