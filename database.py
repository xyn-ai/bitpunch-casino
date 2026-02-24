import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_file="bitpunch.db"):
        self.db_file = db_file
        self.init_db()
    
    def init_db(self):
        """Создаёт таблицы при первом запуске"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Пользователи
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    balance_btc REAL DEFAULT 0,
                    balance_usdt REAL DEFAULT 0,
                    balance_eth REAL DEFAULT 0,
                    balance_ton REAL DEFAULT 0,
                    balance_demo INTEGER DEFAULT 1000,
                    total_bets INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    total_win_amount REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Транзакции
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    currency TEXT,
                    amount REAL,
                    tx_hash TEXT,
                    type TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Игровая статистика
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    game TEXT,
                    bet REAL,
                    win REAL,
                    multiplier REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def get_user(self, user_id, username=None):
        """Получает или создаёт пользователя"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                cursor.execute("""
                    INSERT INTO users (user_id, username, balance_demo)
                    VALUES (?, ?, 1000)
                """, (user_id, username))
                conn.commit()
                
                # Получаем созданного пользователя
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                user = cursor.fetchone()
            
            return user
    
    def update_balance(self, user_id, currency, amount):
        """Обновляет баланс пользователя"""
        field = f"balance_{currency.lower()}"
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE users SET {field} = {field} + ? WHERE user_id = ?", (amount, user_id))
            conn.commit()
    
    def add_transaction(self, user_id, currency, amount, tx_hash, type_, status):
        """Добавляет запись о транзакции"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, currency, amount, tx_hash, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, currency, amount, tx_hash, type_, status))
            conn.commit()
    
    def add_game_stat(self, user_id, game, bet, win, multiplier):
        """Добавляет статистику игры"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO game_stats (user_id, game, bet, win, multiplier)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, game, bet, win, multiplier))
            
            # Обновляем тоталы пользователя
            cursor.execute("""
                UPDATE users 
                SET total_bets = total_bets + 1,
                    total_wins = total_wins + ?,
                    total_win_amount = total_win_amount + ?
                WHERE user_id = ?
            """, (1 if win > 0 else 0, win if win > 0 else 0, user_id))
            
            conn.commit()
    
    def get_top_players(self, limit=10):
        """Возвращает топ игроков по выигрышам"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, total_win_amount, total_bets
                FROM users
                WHERE total_win_amount > 0
                ORDER BY total_win_amount DESC
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()