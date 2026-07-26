import os
import requests
from telegram import Bot
from datetime import datetime

BASE_URL = "https://api.toobit.com"

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def get_symbols():
    url = BASE_URL + "/api/v1/futures/public/symbols"   # ← خط 12 اصلاح شد
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return [s["symbol"] for s in r.json()["data"]]


def get_daily_candles(symbol):
    url = BASE_URL + f"/api/v1/futures/klines?symbol={symbol}&interval=1d&limit=6"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()["data"]


def check_pattern(candles):
    if len(candles) < 6:
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

    body_prev = abs(prev_close - prev_open)

    avg_body = sum(
        abs(float(c[4]) - float(c[1]))
        for c in candles[-6:-2]
    ) / 4

    cond1 = body_prev > avg_body

    upper_shadow = prev_high - max(prev_open, prev_close)
    lower_shadow = min(prev_open, prev_close) - prev_low

    if max(upper_shadow, lower_shadow) == 0:
        cond2 = False
    else:
        cond2 = abs(upper_shadow - lower_shadow) <= max(
            upper_shadow,
            lower_shadow
        ) * 0.10

    body_last = abs(last_close - last_open)
    cond3 = body_last <= (last_high - last_low) * 0.10

    if prev_close > prev_open:

        cond4 = last_close < last_open
        cond5 = (
            last_open < prev_high
            and last_close < prev_high
        )
        cond6 = last_high > prev_high

    else:

        cond4 = last_close > last_open
        cond5 = (
            last_open > prev_low
            and last_close > prev_low
        )
        cond6 = last_low < prev_low

    return (
        cond1
        and cond2
        and cond3
        and cond4
        and cond5
        and cond6
    )


def send_message(text):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=text)


def scan():
    symbols = get_symbols()

    for symbol in symbols:
        try:
            candles = get_daily_candles(symbol)

            if check_pattern(candles):
                ts = datetime.fromtimestamp(
                    int(candles[-1][0]) / 1000
                )

                send_message(
                    f"✅ CRT پیدا شد\n\n"
                    f"نماد: {symbol}\n"
                    f"تاریخ: {ts.strftime('%Y-%m-%d')}"
                )

        except Exception as e:
            print(symbol, e)


if __name__ == "__main__":
    scan()
