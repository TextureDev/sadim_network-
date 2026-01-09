import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import EMAIL_USER, EMAIL_PASS, APP_URL


def send_verification_email(to_email, token):
    """
    إرسال بريد التحقق من البريد الإلكتروني
    """
    if not EMAIL_USER or not EMAIL_PASS or not APP_URL:
        raise RuntimeError('Email credentials or APP_URL not configured in environment')

    subject = 'تأكيد البريد الإلكتروني - شبكة سديم'
    verify_link = f"{APP_URL}/verify_email/{token}"

    html = f"""
<html lang="ar" dir="rtl">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>
  <body style="margin:0; padding:0; background-color: #1a1a2e; font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <table align="center" width="100%" cellpadding="0" cellspacing="0" 
           style="max-width:600px; margin:40px auto; background-color:#ffffff; 
                  border-radius:16px; overflow:hidden; box-shadow:0 15px 50px rgba(0,0,0,0.4);
                  border: 1px solid #2b124c;">
      
      <tr>
        <td style="background: linear-gradient(135deg, #2b124c 0%, #522b5b 100%); 
                   padding:50px 20px; text-align:center;">
          <h1 style="color:#dfb6b2; margin:0; font-size:32px; font-weight:900; 
                     letter-spacing: 2px; text-transform: uppercase;">
            SADEEM NETWORK
          </h1>
          <p style="color:#f5f1eb; margin:10px 0 0 0; font-size:16px; opacity: 0.8;">
            بوابتك نحو المعرفة والتقنية
          </p>
        </td>
      </tr>
      
      <tr>
        <td style="padding:40px 35px; color:#2b124c; font-size:16px; line-height:1.8; text-align: right;">
          <h2 style="color:#854f6c; font-size:24px; margin-bottom:20px; text-align:center;">
            تفعيل الحساب في سديم ✨
          </h2>
          
          <p style="margin-bottom:20px;">
            مرحباً بك،
          </p>
          
          <p style="margin-bottom:20px;">
            يسعدنا انضمامك إلى <strong>شبكة سديم</strong>. خطوة واحدة تفصلك عن الوصول إلى مكتبة الكتب التقنية وأدوات المختبر السيبراني. يرجى تأكيد هويتك بالضغط على الزر أدناه:
          </p>
          
          <table width="100%" cellpadding="0" cellspacing="0" style="margin:40px 0;">
            <tr>
              <td align="center">
                <a href="{verify_link}" 
                   style="background-color: #854f6c; 
                          color:#ffffff; text-decoration:none; 
                          padding:18px 45px; border-radius:12px; 
                          display:inline-block; font-weight:bold; font-size:18px;
                          box-shadow: 0 8px 20px rgba(133, 79, 108, 0.3);">
                  تفعيل حسابي الآن
                </a>
              </td>
            </tr>
          </table>
          
          <div style="background-color:#f8f9fa; padding:20px; border-radius:12px; 
                      margin:30px 0; border-right: 4px solid #dfb6b2;">
            <p style="margin:0; font-size:13px; color:#666;">
              <strong>إذا واجهت مشكلة في الزر، انسخ الرابط التالي:</strong>
            </p>
            <p style="margin:10px 0 0 0; word-break:break-all; direction:ltr; text-align:left; font-size: 13px;">
              <a href="{verify_link}" style="color:#854f6c; text-decoration:none;">
                {verify_link}
              </a>
            </p>
          </div>
          
          <p style="color:#666; font-size:14px; margin-top:30px; border-top: 1px solid #eee; padding-top: 20px;">
            إذا لم تقم بالتسجيل في شبكتنا، يمكنك تجاهل هذا البريد بأمان.
          </p>
        </td>
      </tr>
      
      <tr>
        <td style="background-color: #fcf8f7; padding:30px 20px; text-align:center; color:#2b124c;">
          <p style="margin:0 0 10px 0; font-size:13px; font-weight: bold;">
            © 2026 <span style="color:#854f6c;">SADEEM NETWORK</span>
          </p>
          <p style="margin:0; font-size:11px; color:#999; line-height: 1.5;">
            تصلك هذه الرسالة لأنك قمت بإنشاء حساب في منصتنا.<br>
            المملكة العربية السعودية، جدة.
          </p>
        </td>
      </tr>
    </table>
    
    <div style="height:40px;"></div>
  </body>
</html>
"""

    # إنشاء الرسالة
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"شبكة سديم <{EMAIL_USER}>"
    msg['To'] = to_email

    part = MIMEText(html, 'html', 'utf-8')
    msg.attach(part)

    # إعدادات SMTP الخاصة بـ Gmail
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    
    print(f"📧 محاولة إرسال البريد...")
    print(f"   من: {EMAIL_USER}")
    print(f"   إلى: {to_email}")
    print(f"   SMTP Host: {smtp_host}:{smtp_port}")
    
    # إرسال البريد مع معالجة أخطاء محسّنة
    try:
        print(f"🔌 جاري الاتصال بـ SMTP...")
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            print(f"✅ تم الاتصال بـ SMTP")
            
            print(f"🔐 جاري تفعيل TLS...")
            server.ehlo()
            server.starttls()
            server.ehlo()
            print(f"✅ تم تفعيل TLS")
            
            print(f"🔑 جاري تسجيل الدخول...")
            print(f"   البريد: {EMAIL_USER}")
            server.login(EMAIL_USER, EMAIL_PASS)
            print(f"✅ تم تسجيل الدخول بنجاح")
            
            print(f"📬 جاري إرسال البريد...")
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
            print(f"✅ تم إرسال بريد التأكيد بنجاح إلى: {to_email}")
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ خطأ في المصادقة (بيانات البريد/كلمة المرور غير صحيحة): {str(e)}")
        print(f"   تأكد من أن كلمة المرور هي App Password من Gmail")
        print(f"   أو فعّل 'السماح بالتطبيقات الأقل أماناً'")
        raise RuntimeError(f"Email authentication failed: {str(e)}")
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ خطأ في الاتصال بـ SMTP: {str(e)}")
        print(f"   تحقق من الإنترنت وإعدادات المضيف")
        raise RuntimeError(f"SMTP connection failed: {str(e)}")
        
    except smtplib.SMTPException as e:
        print(f"❌ خطأ SMTP: {str(e)}")
        raise RuntimeError(f"Failed to send email: {str(e)}")
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")
        raise RuntimeError(f"Unexpected error sending email: {str(e)}")

