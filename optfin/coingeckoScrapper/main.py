import os, sys
import django
import requests
from datetime import datetime
import time
import threading
from functools import wraps

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MainProject.settings")
django.setup()

from modelsMark.models import OHLCV
from cryptocurrencies.models import CryptoCoin

API_KEY = "CG-tpMDjB6SNKH7F3QWuRpsUrXY"
COINGECKO_API_OHLC = "https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
COINGECKO_API_MARKET_CHART = "https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
COINGECKO_API_COINS_LIST = "https://api.coingecko.com/api/v3/coins/markets"

HEADERS = {
    "accept": "application/json",
    "x-cg-pro-api-key": API_KEY
}

def rate_limiter(calls_per_minute):
    interval = 60 / calls_per_minute
    lock = threading.Lock()
    last_time = [0.0]  

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                elapsed = time.time() - last_time[0]
                wait = interval - elapsed
                if wait > 0:
                    time.sleep(wait)
                result = func(*args, **kwargs)
                last_time[0] = time.time()
                return result
        return wrapper
    return decorator

@rate_limiter(20)
def fill_crypto_table_if_empty(limit=30):
    if CryptoCoin.objects.exists():
        print("table is already filled")
        return

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1
    }

    response = requests.get(COINGECKO_API_COINS_LIST, params=params, headers=HEADERS)
    if response.status_code != 200:
        print(f"request error CoinGecko: {response.status_code}")
        return

    coins = response.json()
    for coin in coins:
        CryptoCoin.objects.create(
            name=coin["id"],
            pair=coin["symbol"].upper() + "/USDT",
        )
        print(f"added: {coin['id']} ({coin['symbol'].upper()}/USDT)")

    print(f"successfully added {len(coins)} coins")

def match_volume_to_ohlc(ohlc_data, volumes):
    """
    ohlc_data: [[ts, open, high, low, close], ...]
    volumes: [[ts, vol], ...]
    returns [ts, open, high, low, close, volume]
    """
    volumes.sort(key=lambda x: x[0])

    result = []

    for candle in ohlc_data:
        ts, open_p, high_p, low_p, close_p = candle

        closest_vol = min(volumes, key=lambda x: abs(x[0] - ts))[1]

        result.append([ts, open_p, high_p, low_p, close_p, closest_vol])

    return result

@rate_limiter(10)
def fetch_ohlcv(coin_id: str, interval: str = "1"):
    response_ohlc = requests.get(COINGECKO_API_OHLC.format(coin_id=coin_id),
                                 params={"vs_currency": "usd", "days": interval})
    if response_ohlc.status_code != 200:
        print(f"request error: {response_ohlc.text}")
        return []

    ohlc_data = response_ohlc.json()  

    response_vol = requests.get(COINGECKO_API_MARKET_CHART.format(coin_id=coin_id),
                                params={"vs_currency": "usd", "days": interval})
    if response_vol.status_code != 200:
        print(f"request error: {response_vol.text}")
        return []

    market_data = response_vol.json()
    volumes = market_data.get("total_volumes", []) 

    ohlcv_list = match_volume_to_ohlc(ohlc_data, volumes)

    return ohlcv_list

def save_ohlcv(coin: CryptoCoin, ohlcv_data: list, interval: str):
    """
    OHLCV format: [timestamp, open, high, low, close, volume]
    """
    for candle in ohlcv_data:
        ts, open_p, high_p, low_p, close_p, vol = candle
        OHLCV.objects.update_or_create(
            trading_pair=coin,
            interval=interval,
            open_time=datetime.fromtimestamp(ts / 1000.0),
            defaults={
                "open_price": open_p,
                "high_price": high_p,
                "low_price": low_p,
                "close_price": close_p,
                "volume": vol,
            }
        )

    print(f"Saved {len(ohlcv_data)} candles for {coin.pair}")


def main():
    fill_crypto_table_if_empty()

    coins = CryptoCoin.objects.all()
    print(f"Loading OHLCV for {coins.count()} coins")

    for coin in coins:
        print(f"fetching {coin.name} ({coin.pair})")
        ohlcv = fetch_ohlcv(coin.name, "1")
        if ohlcv:
            save_ohlcv(coin, ohlcv, "1")


if __name__ == "__main__":
    main()
