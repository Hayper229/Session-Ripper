import telebot
import sqlite3
import os
import librosa
import numpy as np
from scipy.spatial.distance import cosine
import matplotlib.pyplot as plt
from datetime import datetime

# --- [КОНФИГУРАЦИЯ] ---
TOKEN = 'YOUR_BOT_TOKEN'
ADMIN_ID = 123456789  # Твой ID

bot = telebot.TeleBot(TOKEN)
db = {} # Оперативная память для сравнения голосов и текстов

# --- [1. ГЛУБОКИЙ РИППЕР СЕССИЙ] ---
def advanced_session_rip(path):
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        
        # Вытягиваем не только контакты, но и данные о входах
        cur.execute("SELECT id, username, phone, name FROM entities")
        entities = cur.fetchall()
        
        cur.execute("SELECT dc_id, auth_key FROM sessions")
        auth = cur.fetchone()
        
        report = [f"📂 Анализ сессии: {os.path.basename(path)}"]
        if auth:
            report.append(f"🔑 Auth Key Found! DC: {auth[0]} | Key_Hash: {hash(auth[1])}")
        
        report.append("\n--- КЭШ СУЩНОСТЕЙ ---")
        for e in entities:
            report.append(f"ID: {e[0]} | @{e[1] or 'unknown'} | {e[2] or 'no_phone'} | {e[3] or ''}")
            
        conn.close()
        return "\n".join(report)
    except Exception as e:
        return f"❌ Ошибка парсинга: {e}"

# --- [2. БИОМЕТРИЧЕСКИЙ АНАЛИЗАТОР ГОЛОСА] ---
def get_voice_signature(path):
    y, sr = librosa.load(path, sr=None)
    # Используем 20 коэффициентов для максимальной точности
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    return np.mean(mfcc.T, axis=0)

# --- [3. ОБРАБОТЧИКИ СООБЩЕНИЙ] ---

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID: return
    help_text = (
        "🚀 **ShadowSuite Ultimate v3.0 Activated**\n\n"
        "📎 **Документы:** Кидай `.session` для полного рипа базы и ключей.\n"
        "🎙 **Голос:** Перешли два ГС подряд, чтобы сравнить их биометрию.\n"
        "📸 **Фото:** Пришли фото 'Файлом', чтобы вытащить GPS и EXIF.\n"
        "⚙️ **TWA:** Используй `/gen_trap` для создания ссылки-ловушки."
    )
    bot.send_message(ADMIN_ID, help_text, parse_mode="Markdown")

# Сравнение голосов
@bot.message_handler(content_types=['voice'])
def voice_comparator(message):
    if message.from_user.id != ADMIN_ID: return
    
    file_info = bot.get_file(message.voice.file_id)
    downloaded = bot.download_file(file_info.file_path)
    path = f"voice_{message.voice.file_id}.ogg"
    
    with open(path, 'wb') as f:
        f.write(downloaded)
    
    if message.chat.id not in db: db[message.chat.id] = []
    db[message.chat.id].append(path)
    
    if len(db[message.chat.id]) >= 2:
        v1 = db[message.chat.id].pop(0)
        v2 = db[message.chat.id].pop(0)
        
        bot.send_message(ADMIN_ID, "🧬 Сравниваю биометрические сигналы...")
        try:
            sig1 = get_voice_signature(v1)
            sig2 = get_voice_signature(v2)
            similarity = 1 - cosine(sig1, sig2)
            
            verdict = "✅ ИДЕНТИЧНЫ" if similarity > 0.85 else "🧐 ПОХОЖИ" if similarity > 0.7 else "❌ РАЗНЫЕ"
            bot.send_message(ADMIN_ID, f"📊 Результат: **{similarity:.2%}**\nВердикт: **{verdict}**", parse_mode="Markdown")
        finally:
            os.remove(v1); os.remove(v2)
    else:
        bot.send_message(ADMIN_ID, "📥 Первый образец принят. Жду второй...")

# Риппер сессий
@bot.message_handler(content_types=['document'])
def doc_handler(message):
    if message.from_user.id != ADMIN_ID: return
    
    if message.document.file_name.endswith('.session'):
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        path = f"analyze_{message.document.file_name}"
        
        with open(path, 'wb') as f: f.write(downloaded)
        
        report = advanced_session_rip(path)
        
        if len(report) > 4000:
            with open("full_rip.txt", "w", encoding="utf-8") as f: f.write(report)
            bot.send_document(ADMIN_ID, open("full_rip.txt", "rb"), caption="📄 Полный дамп сессии")
            os.remove("full_rip.txt")
        else:
            bot.send_message(ADMIN_ID, f"```\n{report}\n```", parse_mode="Markdown")
        
        os.remove(path)

bot.polling(none_stop=True)
