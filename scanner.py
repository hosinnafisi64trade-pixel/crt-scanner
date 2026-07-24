import requests
import time

print("CRT Scanner Started")

BASE_URL = "https://api.toobit.com"

def get_symbols():
    url = BASE_URL + "/api/v1/futures/market/tickers"
    r = requests.get(url, timeout=10)
    data = r.json()

    symbols = []
    for item in data["data"]:
        symbols.append(item["symbol"])

    return symbols

symbols = get_symbols()

print(f"Found {len(symbols)} symbols")

for symbol in symbols:
    print(symbol)
