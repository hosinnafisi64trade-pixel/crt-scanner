import requests

BASE_URL = "https://api.toobit.com"


def get_symbols():
    url = BASE_URL + "/api/v1/futures/market/contracts"
    r = requests.get(url, timeout=10)
    data = r.json()

    symbols = []
    if "data" in data:
        for item in data["data"]:
            symbols.append(item["symbol"])

    return symbols


def scan():
    symbols = get_symbols()

    print(f"Found {len(symbols)} symbols")

    for symbol in symbols:
        print("Scanning:", symbol)

    print("Scan Finished")


if __name__ == "__main__":
    scan()
