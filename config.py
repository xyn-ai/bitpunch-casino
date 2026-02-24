import os
from dotenv import load_dotenv

load_dotenv("admin.env")

# Бренд
CASINO_NAME = "BITPUNCH"
CASINO_EMOJI = "🥊"

# Telegram Bot
BOT_TOKEN = os.getenv("8696018423:AAG3XQw6wXSNhY4-qi7mgRQcaq-aFSoCWMc")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле!")

# CryptoBot API (опционально)
CRYPTO_TOKEN = os.getenv("CRYPTO_TOKEN", "")

# ID админа
ADMIN_ID = os.getenv("319370809", "")

# Настройки игр
MIN_BET = 10
MAX_BET_DEMO = 1000
STARS_RATE = 0.016  # 1 звезда = 0.016 USDT

# Крипто-валюты
ACCEPTED_CRYPTO = ["USDT", "BTC", "ETH", "TON"]
