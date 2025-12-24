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
from exchanges.models import Exchange

API_KEY = "CG-tpMDjB6SNKH7F3QWuRpsUrXY"
COINGECKO_API_OHLC = "https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
COINGECKO_API_MARKET_CHART = "https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
COINGECKO_API_COINS_LIST = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_API_EXCHANGES = "https://api.coingecko.com/api/v3/exchanges"
COINGECKO_API_EXCHANGE_DETAIL = "https://api.coingecko.com/api/v3/exchanges/{exchange_id}"

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


@rate_limiter(10)
def get_btc_price():
    """Получает актуальный курс BTC к USD"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            headers=HEADERS
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("bitcoin", {}).get("usd", 60000)
        return 60000
    except:
        return 60000


@rate_limiter(10)
def get_exchange_details(exchange_id):
    """Получает детальную информацию о бирже"""
    try:
        response = requests.get(
            COINGECKO_API_EXCHANGE_DETAIL.format(exchange_id=exchange_id),
            headers=HEADERS
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching details for {exchange_id}: {e}")
        return None


@rate_limiter(10)
def fill_exchanges_table_if_empty(limit=50):
    """Заполняет таблицу бирж, если она пуста"""
    if Exchange.objects.exists():
        print("exchanges table is already filled")
        return

    btc_price = get_btc_price()
    print(f"BTC price: ${btc_price:,.2f}")

    params = {
        "per_page": limit,
        "page": 1
    }

    response = requests.get(COINGECKO_API_EXCHANGES, params=params, headers=HEADERS)
    if response.status_code != 200:
        print(f"request error CoinGecko exchanges list: {response.status_code}")
        print(f"response text: {response.text}")
        return

    exchanges_list = response.json()
    print(f"Received {len(exchanges_list)} exchanges from API")

    saved_count = 0
    for exchange_data in exchanges_list:
        try:
            exchange_id = exchange_data.get("id", "")
            name = exchange_data.get("name", "")

            trading_volume_24h_btc = exchange_data.get("trade_volume_24h_btc", 0)
            trading_volume_24h_btc_normalized = exchange_data.get("trade_volume_24h_btc_normalized", 0)

            volume_btc = float(trading_volume_24h_btc_normalized or trading_volume_24h_btc or 0)
            trading_volume_usd = volume_btc * btc_price

            detail_data = get_exchange_details(exchange_id)
            
            coins_listed = 0
            rating = 0
            
            if detail_data:

                tickers = detail_data.get("tickers", [])
                if tickers:
                    unique_coins = set()
                    for ticker in tickers:
                        base = ticker.get("base", "")
                        if base:
                            unique_coins.add(base.upper())
                    coins_listed = len(unique_coins)

                trust_score = detail_data.get("trust_score", None)
                if trust_score is not None:
                    try:
                        rating = float(trust_score)
                    except (ValueError, TypeError):
                        rating = 0
                else:
                    rating = 0
            else:
                print(f"Warning: Could not get details for {name}")

            if name:
                Exchange.objects.create(
                    name=name,
                    trading_volume=trading_volume_usd,
                    coins_listed=coins_listed,
                    rating=rating
                )
                saved_count += 1
                print(f"added exchange: {name} (volume: ${trading_volume_usd:,.2f}, coins: {coins_listed}, rating: {rating:.2f})")
            else:
                print(f"Warning: Skipping exchange with no name (id: {exchange_id})")
            
        except Exception as e:
            print(f"Error processing exchange {exchange_data.get('name', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"successfully added {saved_count} exchanges")


def main():
    fill_crypto_table_if_empty()
    fill_exchanges_table_if_empty()

    coins = CryptoCoin.objects.all()
    print(f"Loading OHLCV for {coins.count()} coins")

    for coin in coins:
        print(f"fetching {coin.name} ({coin.pair})")
        ohlcv = fetch_ohlcv(coin.name, "1")
        if ohlcv:
            save_ohlcv(coin, ohlcv, "1")


if __name__ == "__main__":
    main()
