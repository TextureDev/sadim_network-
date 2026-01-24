import telebot
import os
import threading
import glob
import time
from flask import Blueprint, request, jsonify
from yt_dlp import YoutubeDL

bot_bp = Blueprint('bot_api', __name__)

DOWNLOAD_DIR = "downloads"
SADIM_URL = "https://sadim.cloud/"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def text_to_binary(text):
    return ' '.join(format(byte, '08b') for byte in text.encode('utf-8'))

# --- قالب الترويسة الموحد لشبكة سديم ---
def sdm_header(title):
    return f"✨ **شبكة سديم | {title}**\n" + "—" * 22

def start_bot_worker(bot_token, user_id):
    try:
        bot = telebot.TeleBot(bot_token, threaded=True)

        # 1. رسالة ترحيب تعكس فخامة الشبكة
        @bot.message_handler(commands=['start'])
        def start(message):
            welcome = (
                f"{sdm_header('المنصة الذكية')}\n\n"
                "🚀 **أهلاً بك في نظام سديم المتكامل**\n"
                "الخيار الأفضل لتحميل وإدارة الوسائط.\n\n"
                "📌 **الخدمات المتاحة:**\n"
                "• 📥 **التحميل:** أرسل رابط تيك توك أو إنستغرام.\n"
                "• 👤 **المعلومات:** `/info` + اسم المستخدم.\n"
                "• 🔢 **التحويل:** `/binary` + النص.\n\n"
                f"🌐 [زيارة موقعنا الرسمي]({SADIM_URL})\n"
                "🛡 _Powered by Sadim Cloud_"
            )
            bot.reply_to(message, welcome, parse_mode="Markdown", disable_web_page_preview=True)

        # 2. جلب معلومات الحساب بتنسيق احترافي
        @bot.message_handler(commands=['info'])
        def get_account_info(msg):
            username = msg.text.replace('/info', '').strip().replace('@', '')
            if not username:
                bot.reply_to(msg, "⚠️ **تنبيه:** يرجى إدخال اليوزر.\nمثال: `/info username`", parse_mode="Markdown")
                return
            
            status = bot.reply_to(msg, "🔍 **جاري فحص البيانات...**", parse_mode="Markdown")
            
            ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"https://instagram.com/{username}/", download=False)
                    res = (
                        f"{sdm_header('معلومات الحساب')}\n\n"
                        f"👤 **الاسم:** `{info.get('uploader', 'غير معروف')}`\n"
                        f"📊 **المتابعين:** `{info.get('follower_count', 'N/A')}`\n"
                        f"✅ **التوثيق:** `{'موثق ★' if info.get('is_verified') else 'حساب عادي'}`\n\n"
                        f"🌐 [انتقل للموقع لمزيد من الأدوات]({SADIM_URL})"
                    )
                    bot.edit_message_text(res, msg.chat.id, status.message_id, parse_mode="Markdown", disable_web_page_preview=True)
            except:
                bot.edit_message_text("❌ **خطأ:** تعذر الوصول للحساب أو أنه خاص.", msg.chat.id, status.message_id, parse_mode="Markdown")

        # 3. التحويل الثنائي
        @bot.message_handler(commands=['binary'])
        def convert_to_binary(msg):
            text = msg.text.replace('/binary', '').strip()
            if text:
                res = (
                    f"{sdm_header('نتائج التحويل')}\n\n"
                    f"✅ **النص الأصلي:** `{text}`\n"
                    f"🔢 **الناتج الثنائي:**\n`{text_to_binary(text)}`\n\n"
                    f"🔗 {SADIM_URL}"
                )
                bot.reply_to(msg, res, parse_mode="Markdown")

        # 4. دالة التحميل مع إضافة رابط الموقع تحت المحتوى المرسل
        @bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
        def handle_download(msg):
            url = msg.text.strip()
            if not any(d in url for d in ["tiktok.com", "instagram.com", "reels"]):
                return

            prog_msg = bot.reply_to(msg, "⚙️ **جاري سحب المحتوى من خوادم سديم...**", parse_mode="Markdown")

            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(id)s_{msg.chat.id}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'writethumbnail': True,
                'ignoreerrors': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }

            if os.path.exists('cookies.txt'):
                ydl_opts['cookiefile'] = 'cookies.txt'

            try:
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    files = glob.glob(os.path.join(DOWNLOAD_DIR, f"*{msg.chat.id}.*"))
                    
                    if not files:
                        bot.edit_message_text("❌ **فشل:** المحتوى غير متاح أو محمي.", msg.chat.id, prog_msg.message_id)
                        return

                    # إضافة رابط الموقع في الوصف أسفل الفيديو/الصورة
                    caption = (
                        f"✅ **تم استخراج المحتوى بنجاح**\n"
                        f"👤 **الناشر:** {info.get('uploader', 'N/A')}\n"
                        f"📁 **المصدر:** {info.get('extractor_key', 'Sadim Cloud')}\n\n"
                        f"🔗 **عبر سديم:** {SADIM_URL}"
                    )

                    for file_path in files:
                        with open(file_path, 'rb') as f:
                            if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                bot.send_photo(msg.chat.id, f, caption=caption, parse_mode="Markdown")
                            else:
                                bot.send_video(msg.chat.id, f, caption=caption, parse_mode="Markdown", timeout=120)
                        os.remove(file_path)
                    
                    bot.delete_message(msg.chat.id, prog_msg.message_id)

            except Exception:
                bot.edit_message_text("⚠️ **تنبيه:** حدث ضغط على النظام، حاول مرة أخرى لاحقاً.", msg.chat.id, prog_msg.message_id)

        # تشغيل البوت
        bot.send_message(user_id, f"✅ **نظام سديم:** تم تفعيل البوت وربطه بـ {SADIM_URL}", parse_mode="Markdown")
        bot.infinity_polling(timeout=60, long_polling_timeout=30)

    except Exception as e:
        print(f"Sadim System Error: {e}")

@bot_bp.route('/api/add_bots', methods=['POST'])
def add_bots():
    data = request.get_json()
    bot_token, user_id, admin_token = data.get('bot_token'), data.get('user_id'), data.get('admin_token')

    if admin_token != "123456":
        return jsonify({"error": "Unauthorized"}), 401
    
    threading.Thread(target=start_bot_worker, args=(bot_token, user_id), daemon=True).start()
    return jsonify({"message": "Sadim Bot Activated", "status": "success", "site": SADIM_URL}), 200