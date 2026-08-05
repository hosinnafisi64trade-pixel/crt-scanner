import os
import requests
from datetime import datetime
from telegram import Bot

BASE_URL = "https://api.toobit.com"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN or CHAT_ID not found")
        return

    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=text)


def get_symbols():

    url = BASE_URL + "/api/v1/futures/public/symbols"

    r = requests.get(url, timeout=20)
    r.raise_for_status()

    data = r.json()

    symbols = []

    for s in data["data"]:

        symbol = s["symbol"]

        if symbol.endswith("USDT"):
            symbols.append(symbol)

    return symbols


def get_daily_candles(symbol):

    url = BASE_URL + "/api/v1/futures/klines"

    params = {
        "symbol": symbol,
        "interval": "1d",
        "limit": 10
    }

    r = requests.get(
        url,
        params=params,
        timeout=20
    )

    r.raise_for_status()

    return r.json()["data"]
    def check_pattern(candles):

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


    # -------------------------
    # کندل اول
    # رشد بالای 10 درصد
    # بدنه بزرگ
    # شادوهای تقریباً مساوی
    # -------------------------

    first_range = prev_high - prev_low

    if first_range <= 0:
        return False


    first_percent = (
        (prev_high - prev_low)
        / prev_open
    ) * 100


    if first_percent < 10:
        return False


    first_body = abs(
        prev_close - prev_open
    )


    first_body_ratio = (
        first_body / first_range
    )


    if first_body_ratio < 0.84:
        return False


    upper_shadow = (
        prev_high -
        max(prev_open, prev_close)
    )


    lower_shadow = (
        min(prev_open, prev_close)
        - prev_low
    )


    if max(upper_shadow, lower_shadow) > 0:

        shadow_diff = abs(
            upper_shadow - lower_shadow
        )

        if shadow_diff > max(
            upper_shadow,
            lower_shadow
        ) * 0.01:

            return False



    # -------------------------
    # کندل دوم (دوجی)
    # بدنه 20 تا 30 درصد
    # حداقل 1.5 درصد
    # -------------------------


    second_range = last_high - last_low

    if second_range <= 0:
        return False


    second_body = abs(
        last_close - last_open
    )


    second_body_percent = (
        second_body / last_open
    ) * 100


    if second_body_percent < 1.5:
        return False


    second_body_ratio = (
        second_body / second_range
    )


    if (
        second_body_ratio < 0.20
        or
        second_body_ratio > 0.30
    ):
        return False
        
