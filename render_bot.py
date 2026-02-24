import os
import sys
import logging
import threading
import time
from dotenv import load_dotenv

# Загружаем переменные из admin.env если есть локально
if os.path.exists("admin.env"):
    load_dotenv("admin.env")

# Токен должен быть в переменных окружения на Render
BOT_TOKEN = os.environ.get("8696018423:AAG3XQw6wXSNhY4-qi7mgRQcaq-aFSoCWMc")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN не найден!")
    sys.exit(1)

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Запускаем бота в отдельном потоке
def run_bot():
    """Функция для запуска бота"""
    try:
        # Импортируем и запускаем оригинальный bot.py
        # Можно скопировать сюда весь код из bot.py,
        # но проще импортировать
        logger.info("🚀 Запуск BitPunch Casino бота...")
        
        # Здесь должен быть весь твой код из bot.py
        # Я не копирую его сюда, чтобы не загромождать,
        # но тебе нужно скопировать всё содержимое твоего bot.py
        # и вставить вместо этого комментария
        
        # Пример минимального бота для теста:
        import telebot
        from telebot import types
        
        bot = telebot.TeleBot("8696018423:AAG3XQw6wXSNhY4-qi7mgRQcaq-aFSoCWMc")
        
        @bot.message_handler(commands=['start'])
        def start(message):
            bot.reply_to(message, "🥊 BitPunch Casino запущен на Render!")
        
        @bot.message_handler(func=lambda message: True)
        def echo(message):
            bot.reply_to(message, f"🥊 {message.text}")
        
        logger.info("✅ Бот запущен и работает!")
        bot.infinity_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")
        sys.exit(1)

# Создаём простой веб-сервер для Render
try:
    from flask import Flask, jsonify
    import threading
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            "status": "running",
            "bot": "BitPunch Casino 🥊",
            "message": "Бот работает! Иди в Telegram и пиши /start"
        })
    
    @app.route('/health')
    def health():
        return "OK", 200
    
    def run_web():
        port = int(os.environ.get("PORT", 10000))
        app.run(host='0.0.0.0', port=port)
    
except ImportError:
    # Если Flask не установлен - создаём заглушку
    def run_web():
        port = int(os.environ.get("PORT", 10000))
        import http.server
        import socketserver
        
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
            httpd.serve_forever()

# Запускаем всё
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем веб-сервер в основном потоке
    logger.info(f"🌐 Запуск веб-сервера на порту {os.environ.get('PORT', 10000)}")
    run_web()