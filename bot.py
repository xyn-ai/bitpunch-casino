import telebot
from telebot import types
import threading
import time
import random
from config import *
from database import Database
from games import SlotGame, DiceGame, MinesGame, RocketGame
from payments import CryptoPay, WalletGenerator

# Инициализация
bot = telebot.TeleBot(8696018423:AAG3XQw6wXSNhY4-qi7mgRQcaq-aFSoCWMc)
db = Database()
crypto = CryptoPay(CRYPTO_TOKEN) if CRYPTO_TOKEN else None

# Хранилища
user_states = {}      # Состояния пользователей
active_games = {}     # Активные краш-игры

# ========== КЛАВИАТУРЫ ==========
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        '🥊 BitPunch Слоты',
        '🎲 BitPunch Кости',
        '💣 BitPunch Mines',
        '🚀 BitPunch Rocket',
        '💰 Мой баланс',
        '₿ Пополнить',
        '📊 Статистика',
        '🎮 Демо-режим',
        '🏆 Топ игроков'
    ]
    
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    return markup

def crypto_currency_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for currency in ACCEPTED_CRYPTO:
        markup.add(types.InlineKeyboardButton(currency, callback_data=f"crypto_{currency}"))
    return markup

def back_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("◀ Назад", callback_data="back_to_main"))
    return markup

# ========== СТАРТ ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "NoName"
    
    user = db.get_user(user_id, username)
    
    welcome_text = f"""
🥊 **ДОБРО ПОЖАЛОВАТЬ В BITPUNCH CASINO!** 🥊

🎰 Первое крипто-казино с мощным ударом!
₿ Играй на BTC, ETH, USDT, TON

💰 **Твой демо-баланс:** {user[6]} монет
💎 **Реальный баланс:** {user[3]} USDT

🔥 Заряжай и выигрывай! 🔥
    """
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ========== БАЛАНС ==========
@bot.message_handler(func=lambda message: message.text == '💰 Мой баланс')
def show_balance(message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    text = f"""
🥊 **BITPUNCH CASINO - ТВОЙ БАЛАНС** 🥊

🎮 **Демо-счёт:** `{user[6]}` монет

💰 **Крипто-счёт:**
₿ BTC: `{user[2]:.6f}`
💵 USDT: `{user[3]:.2f}`
Ξ ETH: `{user[4]:.4f}`
💎 TON: `{user[5]:.2f}`

📊 **Статистика:**
🎲 Всего игр: {user[7] or 0}
🏆 Побед: {user[8] or 0}
💸 Выиграно: {user[9] or 0} USDT
    """
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ========== ПОПОЛНЕНИЕ ==========
@bot.message_handler(func=lambda message: message.text == '₿ Пополнить')
def deposit(message):
    text = f"""
🥊 **BITPUNCH CASINO - ПОПОЛНЕНИЕ** 🥊

Выбери криптовалюту:

₿ **BTC** - Биткоин
💵 **USDT** - Стабильная монета
Ξ **ETH** - Эфириум
💎 **TON** - Telegram Open Network

Минимальный депозит: 5 USDT (или эквивалент)
Комиссия: 0%
    """
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=crypto_currency_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('crypto_'))
def select_crypto(call):
    currency = call.data.replace('crypto_', '')
    
    # Для USDT используем CryptoBot
    if currency == "USDT" and crypto:
        # Создаём инвойс на 10 USDT (для примера)
        pay_url, invoice_id = crypto.create_invoice(10, currency, call.from_user.id)
        
        if pay_url:
            user_states[call.from_user.id] = {'invoice_id': invoice_id, 'currency': currency}
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💳 Оплатить", url=pay_url))
            markup.add(types.InlineKeyboardButton("✅ Проверить оплату", callback_data="check_payment"))
            
            bot.edit_message_text(
                f"💵 **Оплата {currency}**\n\n"
                f"Сумма: 10 {currency}\n"
                f"💰 Ты получишь: 1000 монет\n\n"
                f"1. Нажми 'Оплатить'\n"
                f"2. Подтверди платёж\n"
                f"3. Нажми 'Проверить оплату'",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
        else:
            bot.edit_message_text(
                "❌ Ошибка создания счёта. Попробуй позже.",
                call.message.chat.id,
                call.message.message_id
            )
    else:
        # Для других валют показываем адрес
        address = WalletGenerator.get_address(currency)
        
        text = f"""
💳 **Адрес для перевода {currency}:**

`{address}`

❗️ **ВАЖНО:**
• Отправь **любую сумму** на этот адрес
• После подтверждения сети баланс обновится
• Транзакция занимает 5-30 минут
        """
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_payment")
def check_payment(call):
    user_id = call.from_user.id
    
    if user_id not in user_states or 'invoice_id' not in user_states[user_id]:
        bot.answer_callback_query(call.id, "Нет ожидающих платежей")
        return
    
    invoice_id = user_states[user_id]['invoice_id']
    
    if crypto and crypto.check_invoice(invoice_id):
        # Начисляем монеты
        db.update_balance(user_id, "usdt", 10)
        db.add_transaction(user_id, "USDT", 10, "", "deposit", "completed")
        
        bot.edit_message_text(
            "✅ **Платёж получен!**\n\n"
            "💰 Начислено 1000 монет на реальный счёт.\n"
            "Удачной игры! 🥊",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        
        del user_states[user_id]
    else:
        bot.answer_callback_query(call.id, "⏳ Платёж ещё не получен", show_alert=True)

# ========== ИГРЫ ==========
@bot.message_handler(func=lambda message: message.text == '🥊 BitPunch Слоты')
def slots_game(message):
    user_id = message.from_user.id
    mode = user_states.get(user_id, {}).get('mode', 'demo')
    
    user = db.get_user(user_id)
    balance = user[6] if mode == 'demo' else user[3] * 100
    
    msg = bot.send_message(
        message.chat.id,
        f"🥊 **BitPunch Слоты**\n\n"
        f"💰 Твой баланс: {balance} {'монет' if mode == 'demo' else 'USDT'}\n"
        f"🎮 Режим: {'ДЕМО' if mode == 'demo' else 'РЕАЛ'}\n\n"
        f"Введи ставку (10-{min(1000, balance)}):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_slots, user_id, mode)

def process_slots(message, user_id, mode):
    try:
        bet = int(message.text)
        
        if bet < 10:
            bot.send_message(message.chat.id, "❌ Минимальная ставка 10!", reply_markup=main_menu())
            return
        
        user = db.get_user(user_id)
        
        if mode == 'demo':
            if bet > user[6]:
                bot.send_message(message.chat.id, f"❌ Недостаточно монет! У тебя {user[6]}", reply_markup=main_menu())
                return
        else:
            if bet/100 > user[3]:
                bot.send_message(message.chat.id, f"❌ Недостаточно USDT! У тебя {user[3]} USDT", reply_markup=main_menu())
                return
        
        # Играем
        win, result_msg, symbols = SlotGame.spin(bet)
        
        # Обновляем баланс
        if mode == 'demo':
            db.update_balance(user_id, "demo", win)
            new_balance = user[6] + win
        else:
            win_usdt = win / 100
            db.update_balance(user_id, "usdt", win_usdt)
            new_balance = user[3] + win_usdt
        
        # Сохраняем статистику
        db.add_game_stat(user_id, "slots", bet, win if win > 0 else 0, win/bet if win > 0 else 0)
        
        # Отправляем результат
        text = f"""
🥊 **BitPunch Слоты**

{' '.join(symbols)}

{result_msg}

💰 Новый баланс: {new_balance} {'монет' if mode == 'demo' else 'USDT'}
        """
        
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '🎲 BitPunch Кости')
def dice_game(message):
    user_id = message.from_user.id
    mode = user_states.get(user_id, {}).get('mode', 'demo')
    
    user = db.get_user(user_id)
    balance = user[6] if mode == 'demo' else user[3] * 100
    
    msg = bot.send_message(
        message.chat.id,
        f"🎲 **BitPunch Кости**\n\n"
        f"💰 Твой баланс: {balance} {'монет' if mode == 'demo' else 'USDT'}\n"
        f"🎮 Режим: {'ДЕМО' if mode == 'demo' else 'РЕАЛ'}\n\n"
        f"Введи ставку (10-{min(1000, balance)}):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_dice, user_id, mode)

def process_dice(message, user_id, mode):
    try:
        bet = int(message.text)
        
        if bet < 10:
            bot.send_message(message.chat.id, "❌ Минимальная ставка 10!", reply_markup=main_menu())
            return
        
        user = db.get_user(user_id)
        
        if mode == 'demo':
            if bet > user[6]:
                bot.send_message(message.chat.id, f"❌ Недостаточно монет! У тебя {user[6]}", reply_markup=main_menu())
                return
        else:
            if bet/100 > user[3]:
                bot.send_message(message.chat.id, f"❌ Недостаточно USDT! У тебя {user[3]} USDT", reply_markup=main_menu())
                return
        
        # Играем
        win, result_msg, (player, casino) = DiceGame.roll(bet)
        
        # Обновляем баланс
        if mode == 'demo':
            db.update_balance(user_id, "demo", win)
            new_balance = user[6] + win
        else:
            win_usdt = win / 100
            db.update_balance(user_id, "usdt", win_usdt)
            new_balance = user[3] + win_usdt
        
        # Сохраняем статистику
        db.add_game_stat(user_id, "dice", bet, win if win > 0 else 0, win/bet if win > 0 else 0)
        
        # Отправляем результат
        text = f"""
🎲 **BitPunch Кости**

{result_msg}

💰 Новый баланс: {new_balance} {'монет' if mode == 'demo' else 'USDT'}
        """
        
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '💣 BitPunch Mines')
def mines_game(message):
    user_id = message.from_user.id
    mode = user_states.get(user_id, {}).get('mode', 'demo')
    
    user = db.get_user(user_id)
    balance = user[6] if mode == 'demo' else user[3] * 100
    
    text = f"""
💣 **BitPunch Mines** 💣

Правила:
• Поле 5x5 (25 клеток)
• 3 мины
• Чем больше клеток открыл - тем выше множитель

💰 Твой баланс: {balance} {'монет' if mode == 'demo' else 'USDT'}

🎮 Игра в разработке, но скоро будет!
Следи за обновлениями.
    """
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())

# ========== ROCKET (LUCKY JET) ==========
@bot.message_handler(func=lambda message: message.text == '🚀 BitPunch Rocket')
def rocket_game(message):
    user_id = message.from_user.id
    mode = user_states.get(user_id, {}).get('mode', 'demo')
    
    user = db.get_user(user_id)
    balance = user[6] if mode == 'demo' else user[3] * 100
    
    text = f"""
🚀 **BITPUNCH ROCKET** 🚀

Правила как в Lucky Jet:
1. Делаешь ставку
2. Ракета взлетает, множитель растёт
3. Жми /cashout чтобы забрать деньги
4. Успел до взрыва - выиграл

💰 Твой баланс: {balance} {'монет' if mode == 'demo' else 'USDT'}

Введи ставку (10-{min(1000, balance)}):
    """
    
    msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_rocket_bet, user_id, mode)

def process_rocket_bet(message, user_id, mode):
    try:
        bet = int(message.text)
        
        if bet < 10:
            bot.send_message(message.chat.id, "❌ Минимальная ставка 10!", reply_markup=main_menu())
            return
        
        user = db.get_user(user_id)
        
        if mode == 'demo':
            if bet > user[6]:
                bot.send_message(message.chat.id, f"❌ Недостаточно монет! У тебя {user[6]}", reply_markup=main_menu())
                return
            # Списываем ставку сразу
            db.update_balance(user_id, "demo", -bet)
        else:
            bet_usdt = bet / 100
            if bet_usdt > user[3]:
                bot.send_message(message.chat.id, f"❌ Недостаточно USDT! У тебя {user[3]} USDT", reply_markup=main_menu())
                return
            # Списываем ставку сразу
            db.update_balance(user_id, "usdt", -bet_usdt)
        
        # Генерируем раунд
        round_data = RocketGame.simulate_round()
        
        # Сохраняем игру
        active_games[user_id] = {
            'bet': bet,
            'mode': mode,
            'round_id': round_data['round_id'],
            'crash_point': round_data['crash_point'],
            'active': True,
            'cashout': None,
            'chat_id': message.chat.id
        }
        
        # Информация о раунде
        text = f"""
🚀 **РАУНД #{round_data['round_id'][:4]}**

💰 Ставка: {bet} {'монет' if mode == 'demo' else 'USDT'}

Ракета взлетает через 3 секунды!
⚡️ Множитель растёт...
⚡️ Жми /cashout чтобы забрать деньги

Хеш раунда: `{round_data['hash'][:16]}...`
        """
        
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        
        # Запускаем полёт в отдельном потоке
        threading.Thread(target=rocket_flight, args=(user_id, round_data['crash_point'])).start()
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!", reply_markup=main_menu())

def rocket_flight(user_id, crash_point):
    """Симулятор полёта ракеты"""
    time.sleep(3)  # Задержка перед взлётом
    
    multiplier = 1.0
    step = 0.05  # Шаг увеличения
    
    game = active_games.get(user_id)
    if not game:
        return
    
    chat_id = game['chat_id']
    
    # Отправляем стартовое сообщение
    bot.send_message(chat_id, f"🚀 **ПОЕХАЛИ!** x{multiplier:.2f}")
    
    while multiplier < crash_point and active_games.get(user_id, {}).get('active', False):
        time.sleep(0.3)
        multiplier += step
        
        # Отправляем обновления на ключевых множителях
        if abs(multiplier - round(multiplier)) < 0.01 and multiplier > 1:
            bot.send_message(chat_id, f"⚡️ **x{multiplier:.2f}**")
    
    # Проверяем, не кэшаутнул ли игрок
    game = active_games.get(user_id)
    if game and game.get('cashout'):
        return
    
    if multiplier >= crash_point:
        # Взрыв
        bot.send_message(chat_id, f"💥 **ВЗРЫВ!** Ракета упала на x{crash_point:.2f}")
        
        # Очищаем игру (ставка уже списана)
        if user_id in active_games:
            del active_games[user_id]

@bot.message_handler(commands=['cashout'])
def cashout(message):
    user_id = message.from_user.id
    
    if user_id not in active_games:
        bot.send_message(message.chat.id, "❌ У тебя нет активной игры!")
        return
    
    game = active_games[user_id]
    
    if not game['active']:
        bot.send_message(message.chat.id, "❌ Игра уже завершена")
        return
    
    if game['cashout']:
        bot.send_message(message.chat.id, "❌ Ты уже забрал выигрыш")
        return
    
    # Рассчитываем текущий множитель (упрощённо)
    # В реальности нужно синхронизировать с потоком
    current_multiplier = game['crash_point'] * 0.7  # Заглушка
    
    # Рассчитываем выигрыш
    win_amount = game['bet'] * current_multiplier
    
    # Начисляем выигрыш
    if game['mode'] == 'demo':
        db.update_balance(user_id, "demo", win_amount)
    else:
        win_usdt = win_amount / 100
        db.update_balance(user_id, "usdt", win_usdt)
    
    # Сохраняем статистику
    db.add_game_stat(user_id, "rocket", game['bet'], win_amount, current_multiplier)
    
    # Помечаем кэшаут
    game['cashout'] = current_multiplier
    game['active'] = False
    
    text = f"""
✅ **КЭШАУТ!** ✅

💰 Выигрыш: {win_amount:.2f} {'монет' if game['mode'] == 'demo' else 'USDT'}
📈 Множитель: x{current_multiplier:.2f}

💥 Ракета у