import requests
from datetime import datetime
import time

class BybitAPI:
    @staticmethod
    def get_futures_data(symbol="BTCUSDT"):
        """Запрос публичных данных фьючерсов Bybit"""
        url = "https://api.bybit.com/v5/market/tickers"
        params = {
            "category": "linear",
            "symbol": symbol
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get("retCode") == 0 and data.get("result", {}).get("list"):
                return {
                    "symbol": symbol,
                    "price": float(data["result"]["list"][0]["lastPrice"]),
                    "volume": float(data["result"]["list"][0]["volume24h"]),
                    "funding_rate": float(data["result"]["list"][0]["fundingRate"])
                }
            return None
            
        except Exception as e:
            print(f"[Bybit] Error for {symbol}: {str(e)}")
            return None