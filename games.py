import random
import hashlib
import time

class SlotGame:
    """Слоты"""
    
    @staticmethod
    def spin(bet):
        symbols = ['🥊', '₿', 'Ξ', '♠️', '🍒', '7️⃣']
        result = [random.choice(symbols) for _ in range(3)]
        
        # Проверяем комбинации
        if result[0] == result[1] == result[2]:
            if result[0] == '🥊':
                win = bet * 15
                msg = f"🥊 BITPUNCH JACKPOT! x15"
            elif result[0] == '7️⃣':
                win = bet * 10
                msg = f"🎰 ДЖЕКПОТ! x10"
            else:
                win = bet * 5
                msg = f"🎰 ТРИ! x5"
        elif result[0] == result[1] or result[1] == result[2]:
            win = bet * 2
            msg = f"🎰 ДВА! x2"
        else:
            win = -bet
            msg = f"🎰 ПРОИГРЫШ"
        
        return win, msg, result

class DiceGame:
    """Кости"""
    
    @staticmethod
    def roll(bet):
        player = random.randint(1, 6)
        casino = random.randint(1, 6)
        
        if player > casino:
            win = bet
            msg = f"🎲 Ты: {player}, Казино: {casino} - ПОБЕДА!"
        elif player < casino:
            win = -bet
            msg = f"🎲 Ты: {player}, Казино: {casino} - ПРОИГРЫШ"
        else:
            win = 0
            msg = f"🎲 Ничья! {player}:{casino}"
        
        return win, msg, (player, casino)

class MinesGame:
    """Мины (упрощённая версия)"""
    
    @staticmethod
    def generate_field(size=5, mines=3):
        total_cells = size * size
        mines_positions = random.sample(range(total_cells), mines)
        return mines_positions
    
    @staticmethod
    def calculate_multiplier(opens, total_cells, mines):
        # Чем больше открыто клеток, тем выше множитель
        risk = opens / (total_cells - mines)
        multiplier = 1 + risk * 3
        return round(multiplier, 2)

class RocketGame:
    """Краш-игра (Lucky Jet / Rocket Queen)"""
    
    @staticmethod
    def generate_round_id():
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    
    @staticmethod
    def generate_crash_point(house_edge=0.03):
        """
        Генерирует точку краша по алгоритму краш-игр
        house_edge - преимущество казино (3%)
        """
        # Экспоненциальное распределение
        r = random.random()
        crash_point = 0.99 / (1 - r) + 1.0
        
        # Добавляем преимущество казино
        crash_point = crash_point * (1 - house_edge)
        
        return round(crash_point, 2)
    
    @staticmethod
    def simulate_round():
        round_id = RocketGame.generate_round_id()
        crash_point = RocketGame.generate_crash_point()
        
        # Создаём хеш для provably fair
        server_seed = hashlib.md5(str(random.getrandbits(256)).encode()).hexdigest()
        client_seed = hashlib.md5(str(random.getrandbits(256)).encode()).hexdigest()
        
        combined = f"{server_seed}:{client_seed}:{round_id}"
        hash_value = hashlib.sha256(combined.encode()).hexdigest()
        
        return {
            'round_id': round_id,
            'crash_point': crash_point,
            'hash': hash_value,
            'server_seed': server_seed
        }