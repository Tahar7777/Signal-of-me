import requests
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from datetime import datetime
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

BASE_URL = "https://api.bybit.com"
TICKERS_URL = f"{BASE_URL}/v5/market/tickers?category=linear"
KLINE_URL = f"{BASE_URL}/v5/market/kline?category=linear&symbol={{}}&interval=15&limit=20"

def fetch_pairs():
    resp = requests.get(TICKERS_URL)
    resp.raise_for_status()
    data = resp.json()['result']['list']
    return [x['symbol'] for x in data if x['symbol'].endswith('USDT')]

def fetch_klines(symbol):
    url = KLINE_URL.format(symbol)
    resp = requests.get(url)
    resp.raise_for_status()
    klines = resp.json()['result']['list']
    df = pd.DataFrame(klines, columns=["timestamp","open","high","low","close","volume","turnover"])
    df = df.astype({"open":float,"high":float,"low":float,"close":float,"volume":float,"close":float})
    df = df.sort_values("timestamp")
    return df

def analyze(df):
    ema9 = EMAIndicator(df['close'], window=9).ema_indicator()
    ema21 = EMAIndicator(df['close'], window=21).ema_indicator()
    rsi = RSIIndicator(df['close'], window=14).rsi()
    macd = MACD(df['close'])
    macd_line = macd.macd()
    macd_signal = macd.macd_signal()
    bb = BollingerBands(df['close'], window=20, window_dev=2)
    bb_high = bb.bollinger_hband()
    bb_low = bb.bollinger_lband()
    adx = ADXIndicator(df['high'], df['low'], df['close'], window=14).adx()

    last = -1
    signals = {'long': False, 'short': False, 'confidence': 'ضعيفة'}

    # شروط LONG
    bullish_ema = ema9[last] > ema21[last]
    bullish_rsi = rsi[last] < 30 and rsi[last] > rsi[last-2]
    bullish_macd = macd_line[last] > macd_signal[last] and macd_line[last-1] < macd_signal[last-1]
    bb_break = df['close'][last] > bb_high[last]
    adx_good = adx[last] > 20

    # شروط SHORT
    bearish_ema = ema9[last] < ema21[last]
    bearish_rsi = rsi[last] > 70 and rsi[last] < rsi[last-2]
    bearish_macd = macd_line[last] < macd_signal[last] and macd_line[last-1] > macd_signal[last-1]
    bb_break_dn = df['close'][last] < bb_low[last]

    bullish_count = sum([bullish_ema, bullish_rsi, bullish_macd, bb_break, adx_good])
    bearish_count = sum([bearish_ema, bearish_rsi, bearish_macd, bb_break_dn, adx_good])

    if bullish_count >= 4:
        signals['long'] = True
        signals['confidence'] = 'عالية' if bullish_count == 5 else 'متوسطة'
    elif bearish_count >= 4:
        signals['short'] = True
        signals['confidence'] = 'عالية' if bearish_count == 5 else 'متوسطة'

    return signals

def generate_signals():
    pairs = fetch_pairs()
    signals = []
    for symbol in pairs:
        try:
            df = fetch_klines(symbol)
            if len(df) < 20:
                continue
            signal = analyze(df)
            price = df['close'].iloc[-1]
            now = datetime.utcnow()
            if signal['long']:
                target = price * 1.015
                signals.append({
                    "direction": "شراء",
                    "symbol": symbol,
                    "price": f"{price:.2f}",
                    "target": f"{target:.2f}",
                    "target_pct": "+1.5%",
                    "time": now.strftime("%H:%M"),
                    "type": "شراء (LONG)",
                    "leverage": "x3",
                    "confidence": signal["confidence"]
                })
            elif signal['short']:
                target = price * 0.985
                signals.append({
                    "direction": "بيع",
                    "symbol": symbol,
                    "price": f"{price:.2f}",
                    "target": f"{target:.2f}",
                    "target_pct": "-1.5%",
                    "time": now.strftime("%H:%M"),
                    "type": "بيع (SHORT)",
                    "leverage": "x3",
                    "confidence": signal["confidence"]
                })
        except Exception as e:
            print(f"خطأ في الزوج {symbol}: {e}")
    return signals

@app.route('/')
def index():
    signals = generate_signals()
    return render_template("signals.html", signals=signals)

@app.route('/refresh')
def refresh():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)
