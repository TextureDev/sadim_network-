import fitz  # تأكد من تثبيت pip install pymupdf
import os

# أضف هذه الدالة في أعلى ملف admin.py أو في ملف utils
def apply_sadim_brand(pdf_path):
    doc = fitz.open(pdf_path)
    # نضع الشعار في الصفحة الأولى فقط كمثال
    page = doc[0]
    
    # نص العلامة المائية في الأسفل (شفاف قليلاً)
    watermark_text = "www.sadim.cloud | شبكة سديم"
    page.insert_text(fitz.Point(50, 800), watermark_text, fontsize=15, color=(0.7, 0.7, 0.7))
    
    doc.save(pdf_path, incremental=True, encryption=0)
    doc.close()

