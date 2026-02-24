import requests
import time

class CryptoPay:
    """Интеграция с @CryptoBot API"""
    
    def __init__(self, token):
        self.token = token
        self.base_url = "https://pay.crypt.bot/api"
    
    def create_invoice(self, amount, currency, user_id):
        """Создаёт счёт в CryptoBot"""
        url = f"{self.base_url}/createInvoice"
        payload = {
            "asset": currency,
            "amount": str(amount),
            "description": f"BitPunch Casino - пополнение #{user_id}",
            "paid_btn_name": "openBot",
            "paid_btn_url": "https://t.me/YourBitPunchBot"  # Замени на своего бота
        }
        
        headers = {"Crypto-Pay-API-Token": self.token}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return data["result"]["pay_url"], data["result"]["invoice_id"]
        except Exception as e:
            print(f"CryptoPay error: {e}")
        
        return None, None
    
    def check_invoice(self, invoice_id):
        """Проверяет статус оплаты"""
        url = f"{self.base_url}/getInvoices"
        headers = {"Crypto-Pay-API-Token": self.token}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    for invoice in data["result"]["items"]:
                        if invoice["invoice_id"] == invoice_id:
                            return invoice["status"] == "paid"
        except:
            pass
        return False

class WalletGenerator:
    """Заглушка для генерации крипто-адресов"""
    
    @staticmethod
    def get_address(currency):
        addresses = {
            "BTC": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "ETH": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
            "USDT": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F (ERC-20)",
            "TON": "UQA5_7c2JxQqQqQqQqQqQqQqQqQqQqQqQqQqQqQqQq"
        }
        return addresses.get(currency, "Адрес временно недоступен")