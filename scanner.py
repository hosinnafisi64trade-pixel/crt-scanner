import os
import requests
from datetime import datetime
from telegram import Bot

BASE_URL = "https://api.toobit.com"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram Secrets not found")
        return

    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=text)


def get_symbols():
    url = BASE_URL + "/api/v1/futures/public/symbols"

    r = requests.get(url, timeout=20)
    r.raise_for_status()

    data = r.json()

    symbols = []

    if "result" in data:
        for s in data["result"]:
            if (
                s.get("quoteCoin") == "USDT"
                and s.get("status") == "TRADING"
            ):
                symbols.append(s["symbol"])

    return symbols


def get_daily_candles(symbol):
    url = BASE_URL + "/api/v1/futures/market/kline"

    params = {
        "symbol": symbol,
        "interval": "1day",
        "limit": 10
    }

    r = requests.get(
        url,
        params=params,
        timeout=20
    )

    r.raise_for_status()

    data = r.json()

    if "result" in data:
        return data["result"]

    return []def check_pattern(candles):
    if len(candles) < 3:
        return False

    prev = candles[-2]
    last = candles[-1]

    prev_open = float(prev[1])
    prev_high = float(prev[2])
    prev_low = float(prev[3])
    prev_close = float(prev[4])

    last_open = float(last[1])
    last_high = float(last[2])
    last_low = float(last[3])
    last_close = float(last[4])

    total_range = prev_high - prev_low

    if total_range <= 0:
        return False

    body = abs(prev_close - prev_open)
    body_ratio = body / total_range

    if body_ratio < 0.84:
        return False

    upper_shadow = prev_high - max(prev_open, prev_close)
    lower_shadow = min(prev_open, prev_close) - prev_low

    if max(upper_shadow, lower_shadow) > 0:
        diff = abs(upper_shadow - lower_shadow)
        if diff > max(upper_shadow, lower_shadow) * 0.10:
            return False

    total_range2 = last_high - last_low

    if total_range2 <= 0:
        return False

    body2 = abs(last_close - last_open)
    body2_percent = (body2 / last_open) * 100

    if body2_percent < 1.5:
        return False

    body2_ratio = body2 / total_range2

    if body2_ratio < 0.20 or body2_ratio > 0.30:
        return False

    upper2 = last_high - max(last_open, last_close)
    lower2 = min(last_open, last_close) - last_low

    if prev_close > prev_open:

        if last_close >= last_open:
            return False

        if upper2 <= lower2:
            return False

        if last_high <= prev_high:
            return False

        shadow_start = max(prev_open, prev_close)
        shadow_end = prev_high

        if not (
            shadow_start <= last_open <= shadow_end
            and shadow_start <= last_close <= shadow_end
        ):
            return False

    else:

        if last_close <= last_open:
            return False

        if lower2 <= upper2:
            return False

        if last_low >= prev_low:
            return False

        shadow_start = prev_low
        shadow_end = min(prev_open, prev_close)

        if not (
            shadow_start <= last_open <= shadow_end
            and shadow_start <= last_close <= shadow_end
        ):
            return False

    return Truedef scan():

    symbols = get_symbols()

    print(f"Scanning {len(symbols)} symbols...")

    for symbol in symbols:

        try:

            candles = get_daily_candles(symbol)

            if not candles:
                continue

            if check_pattern(candles):

                last = candles[-1]

                signal_time = datetime.utcfromtimestamp(
                    int(last[0]) / 1000
                ).strftime("%Y-%m-%d")

                message = (
                    "✅ CRT Pattern Found\n\n"
                    f"Exchange : Toobit Futures\n"
                    f"Pair : {symbol}\n"
                    f"Date : {signal_time}"
                )

                print(message)

                send_message(message)

        except Exception as e:

            print(f"{symbol} -> {e}")


if __name__ == "__main__":

    print("====================================")
    print(" Toobit CRT Scanner Started")
    print("====================================")

    scan()

    print("Finished.")
