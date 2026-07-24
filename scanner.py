import requests
from telegram import Bot
from datetime import datetime

BASE_URL = "https://api.toobit.com"
TELEGRAM_TOKEN = "8654570303:AAHPSBcwQHjQUnHy8WPbk2MKf6vZlxPsQCY"
CHAT_ID = "8654570303"

def get_symbols():
    url = BASE_URL + "/api/v1/futures/market"
    r = requests.get(url, timeout=10)
    return [s["symbol"] for s in r.json()["data"]]

def get_daily_candles(symbol):
    url = BASE_URL + f"/api/v1/futures/klines?symbol={symbol}&interval=1d&limit=6"
    r = requests.get(url, timeout=10)
    return r.json()["data"]

def check_pattern(candles):
    prev = candles[-2]  # کندل اول (بزرگ)
    last = candles[-1]  # کندل دوم (دوجی)

    prev_open, prev_high, prev_low, prev_close = map(float, prev[1:5])
    last_open, last_high, last_low, last_close = map(float, last[1:5])

    # شرط 1: کندل بزرگ با بدنه بزرگ‌تر از میانگین 3 تا 5 کندل قبل
    body_prev = abs(prev_close - prev_open)
    avg_body = sum(abs(float(c[4]) - float(c[1])) for c in candles[-6:-2]) / 4
    cond1 = body_prev > avg_body

    # شرط 2: شادوهای بالا و پایین کندل بزرگ تقریباً مساوی
    upper_shadow = prev_high - max(prev_open, prev_close)
    lower_shadow = min(prev_open, prev_close) - prev_low
    cond2 = abs(upper_shadow - lower_shadow) <= (max(upper_shadow, lower_shadow) * 0.1)

    # شرط 3: کندل دوم دوجی (بدنه کوچک)
    body_last = abs(last_close - last_open)
    cond3 = body_last <= (last_high - last_low) * 0.1

    # شرط 4 تا 6: بسته به جهت کندل اول
    if prev_close > prev_open:  # کندل اول صعودی
        cond4 = last_close < last_open  # دوجی نزولی
        cond5 = last_open < prev_high and last_close < prev_high  # بدنه دوجی داخل شادوی کندل صعودی
        cond6 = last_high > prev_high  # شادوی بالای دوجی بالاتر از سقف کندل صعودی
    else:  # کندل اول نزولی
        cond4 = last_close > last_open  # دوجی صعودی
        cond5 = last_open > prev_low and last_close > prev_low  # بدنه دوجی داخل شادوی کندل نزولی
        cond6 = last_low < prev_low  # شادوی پایین دوجی پایین‌تر از کف کندل نزولی

    return cond1 and cond2 and cond3 and cond4 and cond5 and cond6

def send_message(text):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=text)

def scan():
    symbols = get_symbols()
    for symbol in symbols:
        candles = get_daily_candles(symbol)
        if check_pattern(candles):
            ts = datetime.fromtimestamp(int(candles[-1][0]) / 1000)
            send_message(f"{symbol} الگوی CRT تشکیل شد در {ts}")

if __name__ == "__main__":
    scan()
