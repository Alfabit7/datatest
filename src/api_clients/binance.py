import requests

class BinanceAPI:
    @staticmethod
    def get_futures_data(symbol="BTCUSDT"):
        """Запрос публичных данных фьючерсов Binance"""
        url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
        params = {"symbol": symbol}
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            return {
                "symbol": symbol,
                "price": float(data["lastPrice"]),
                "volume": float(data["volume"]),
                "funding_rate": float(data["lastFundingRate"])
            }
        except Exception as e:
            print(f"[Binance] Error for {symbol}: {str(e)}")
            return None