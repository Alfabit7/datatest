import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../config/secrets.env")

class CoinGeckoAPI:
    def __init__(self):
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.base_url = "https://api.coingecko.com/api/v3"

    def get_coin_data(self, coin_id="bitcoin"):
        headers = {"x-cg-demo-api-key": self.api_key} if self.api_key else {}
        try:
            response = requests.get(
                f"{self.base_url}/coins/{coin_id}",
                headers=headers,
                timeout=10
            )
            if response.status_code == 429:
                print("[CoinGecko] Rate limit exceeded!")
                return None
            return response.json()
        except Exception as e:
            print(f"[CoinGecko] Error: {str(e)}")
            return None