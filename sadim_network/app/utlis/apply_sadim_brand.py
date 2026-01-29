import fitz
import os
import arabic_reshaper
from bidi.algorithm import get_display

def apply_sadim_brand(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        page = doc.new_page(pno=0, width=595, height=842)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.normpath(os.path.join(current_dir, "..", "static", "fonts", "Amiri.ttf"))
        logo_path = os.path.normpath(os.path.join(current_dir, "..", "static", "images", "logo.png"))

        # 1. إضافة الشعار
        if os.path.exists(logo_path):
            logo_rect = fitz.Rect(237, 50, 357, 150) 
            page.insert_image(logo_rect, filename=logo_path)

        # 2. معالجة النص العربي ليظهر متصلاً وصحيحاً
        raw_text = (
            "🏛️ مكتبة سديم الملكية | SADEEM ROYAL LIBRARY\n\n"
            "\"الغموض ليس مجرد قصة، بل تجربة نعيشها بين السطور\"\n\n"
            "أهلاً بك أيها القارئ في رحاب شبكة سديم.\n\n"
            "بين يديك الآن نسخة فريدة من روائع سيدة الغموض \"أجاثا كريستي\".\n"
            "لقد تم اختيار هذا العمل بعناية، بعد البحث و التقصي عنه   \n"
            "لضمان تجربة قراءة تليق بذائقتك الرفيعة.\n\n"
            "حقوق النسخة: حصري لـ شبكة سديم.\n\n"
            "🔗 للمزيد من الروايات، انضم إلينا:\n"
            "الموقع الرسمي: sadim.cloud\n"
            "قناتنا على التليجرام: t.me/SADIM_NETWORK\n\n"
            "قراءة ممتعة.. ولا تنسَ أن اللغز دائماً يبدأ من هنا!"
        )

        # السحر هنا: تهيئة النص للعربية (ربط الحروف وتعديل الاتجاه)
        reshaped_text = arabic_reshaper.reshape(raw_text)
        bidi_text = get_display(reshaped_text)

        text_rect = fitz.Rect(50, 160, 545, 800)

        # 3. إدراج النص
        if os.path.exists(font_path):
            page.insert_font(fontname="Ar", fontfile=font_path)
            page.insert_textbox(
                text_rect, 
                bidi_text,  # نمرر النص المعالج هنا
                fontsize=14, 
                fontname="Ar", 
                align=fitz.TEXT_ALIGN_CENTER, 
                color=(0, 0, 0)
            )
        
        # 4. الحفظ (تنظيف الملف من أخطاء الـ xref تلقائياً)
        temp_path = pdf_path + "_temp.pdf"
        doc.save(temp_path, garbage=4, deflate=True, clean=True)
        doc.close()
        
        os.replace(temp_path, pdf_path)
        print("✨ تم إنشاء الصفحة الملكية بنص عربي سليم 100%")

    except Exception as e:
        print(f"⚠️ خطأ: {e}")