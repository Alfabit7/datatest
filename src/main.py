import os
import time
import json
import requests
from datetime import datetime
from github import Github, GithubException
from dotenv import load_dotenv

# Конфигурация
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'secrets.env')
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'combined.json')
SYMBOLS = ["BTCUSDT", "SOLUSDT"]
COIN_IDS = ["bitcoin", "solana"]
INTERVAL = 60
GITHUB_REPO = "Alfabit7/datatest"

# Инициализация
load_dotenv(dotenv_path=CONFIG_PATH)
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

class DataCollector:
    @staticmethod
    def safe_request(url, params=None, headers=None, timeout=10):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[API Error] {str(e)}")
            return None

    def get_binance_data(self, symbol):
        data = self.safe_request(
            "https://fapi.binance.com/fapi/v1/ticker/24hr",
            params={"symbol": symbol}
        )
        return {
            "price": float(data["lastPrice"]),
            "volume": float(data["volume"]),
            "funding_rate": float(data.get("lastFundingRate", 0))
        } if data else None

    def get_bybit_data(self, symbol):
        data = self.safe_request(
            "https://api.bybit.com/v5/market/tickers",
            params={"category": "linear", "symbol": symbol}
        )
        if data and data.get("retCode") == 0:
            item = data["result"]["list"][0]
            return {
                "price": float(item["lastPrice"]),
                "volume": float(item["volume24h"]),
                "funding_rate": float(item["fundingRate"])
            }
        return None

    def get_coingecko_data(self, coin_id):
        headers = {"x-cg-demo-api-key": os.getenv("COINGECKO_API_KEY")} if os.getenv("COINGECKO_API_KEY") else {}
        data = self.safe_request(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}",
            headers=headers,
            timeout=15
        )
        return {
            "price": data["market_data"]["current_price"]["usd"],
            "market_cap": data["market_data"]["market_cap"]["usd"]
        } if data else None

    def collect(self):
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "binance": {},
            "bybit": {},
            "coingecko": {}
        }
        
        for symbol in SYMBOLS:
            if data := self.get_binance_data(symbol):
                result["binance"][symbol] = data
            time.sleep(0.5)
            
            if data := self.get_bybit_data(symbol):
                result["bybit"][symbol] = data
            time.sleep(0.5)
        
        for coin_id in COIN_IDS:
            if data := self.get_coingecko_data(coin_id):
                result["coingecko"][coin_id] = data
            time.sleep(1.5)
        
        return result

class DataManager:
    @staticmethod
    def load_existing_data():
        if not os.path.exists(DATA_PATH):
            return []
        
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                if os.path.getsize(DATA_PATH) > 0:
                    return json.load(f)
                return []
        except (json.JSONDecodeError, IOError) as e:
            print(f"[DataManager] Ошибка загрузки файла: {str(e)}")
            backup_path = f"{DATA_PATH}.bak"
            os.rename(DATA_PATH, backup_path)
            print(f"Создана резервная копия: {backup_path}")
            return []

    @staticmethod
    def save_to_file(data):
        try:
            existing = DataManager.load_existing_data()
            existing.append(data)
            
            temp_path = f"{DATA_PATH}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(DATA_PATH):
                os.replace(temp_path, DATA_PATH)
            else:
                os.rename(temp_path, DATA_PATH)
            
            return True
        except Exception as e:
            print(f"[DataManager] Ошибка сохранения: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False

    @staticmethod
    def upload_to_github():
        try:
            if not os.path.exists(DATA_PATH):
                print("[GitHub] Файл данных не найден")
                return None
                
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            g = Github(os.getenv("GITHUB_TOKEN"))
            repo = g.get_repo(GITHUB_REPO)
            
            try:
                # Пробуем получить текущий файл
                file = repo.get_contents("combined.json", ref="main")
                
                # Обновляем файл
                repo.update_file(
                    path=file.path,
                    message=f"Update {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    content=content,
                    sha=file.sha,
                    branch="main"
                )
            except GithubException as e:
                if e.status == 404:
                    # Создаем новый файл
                    repo.create_file(
                        path="combined.json",
                        message="Initial commit",
                        content=content,
                        branch="main"
                    )
                else:
                    raise
            
            return f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/combined.json"
        except Exception as e:
            print(f"[GitHub] Критическая ошибка: {str(e)}")
            return None

def check_config():
    required = ['GITHUB_TOKEN']
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        print(f"❌ Отсутствуют переменные: {', '.join(missing)}")
        return False
    
    try:
        g = Github(os.getenv("GITHUB_TOKEN"))
        repo = g.get_repo(GITHUB_REPO)
        # Проверка записи
        try:
            repo.get_contents("test_access.txt")
        except GithubException:
            pass
        return True
    except Exception as e:
        print(f"❌ GitHub: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Крипто-сборщик данных ===")
    print(f"Будут использованы пары: {', '.join(SYMBOLS)}")
    
    if not check_config():
        exit(1)

    collector = DataCollector()
    manager = DataManager()

    try:
        while True:
            print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Сбор данных...")
            
            data = collector.collect()
            
            if manager.save_to_file(data):
                print("✅ Данные сохранены локально")
                
                if raw_url := manager.upload_to_github():
                    print(f"✅ Данные обновлены в GitHub:\n{raw_url}")
                else:
                    print("⚠️ Не удалось обновить GitHub")
            else:
                print("❌ Ошибка сохранения данных")
            
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 Работа завершена")