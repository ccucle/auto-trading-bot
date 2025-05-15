
import requests
from dotenv import load_dotenv
import os
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

import pandas as pd
from fetch_upbit_price import fetch_upbit_ohlcv

import numpy as np
from datetime import datetime

# 텔레그램 설정
TELEGRAM_TOKEN = '여기에_봇_토큰'
CHAT_ID = '여기에_챗_ID'


from upbit_trade_api import send_order
from balance_utils import calculate_quantity

def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"[텔레그램 오류] {e}")

# RSI 계산
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ADX 계산
def compute_adx(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    return dx.rolling(window=period).mean()

def run_strategy(df):
    df['rsi'] = compute_rsi(df['close'])
    df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
    df['pct_change'] = df['close'].pct_change()
    df['avg_return_3'] = df['pct_change'].rolling(window=3).mean()
    df['adx'] = compute_adx(df)

    ma20 = df['close'].rolling(window=20).mean()
    std20 = df['close'].rolling(window=20).std()
    df['bb_upper'] = ma20 + 2 * std20
    df['bb_lower'] = ma20 - 2 * std20

    position = 0
    capital = 1000
    entry_price = 0
    max_price = 0
    trade_log = []

    for i in range(26, len(df)):
        row = df.iloc[i]
        price = row['close']
        rsi = row['rsi']
        avg_return_3 = row['avg_return_3']
        bb_lower = row['bb_lower']
        adx = row['adx']
        time = row['datetime']

        signal = False
        strategy = ""

        if position == 0:
            if adx < 20 and rsi < 40 and price < bb_lower:
                signal = True
                strategy = "반전_RSI40"
            elif adx >= 20 and avg_return_3 > 0 and rsi > 45:
                signal = True
                strategy = "추세_상승3봉"

            if signal:
                entry_price = price
                max_price = price
                position = 1
                capital *= 0.999  # 수수료
                
                send_telegram(f"📈 진입: {strategy}\n가격: {entry_price}\n시간: {time}")
                
                quantity = calculate_quantity(entry_price)
                order_result = send_order('bid', volume=quantity, price=entry_price)
                send_telegram(f"📈 진입: {strategy}\n가격: {entry_price}\n시간: {time}")
                send_telegram(f"🧾 매수 결과: {order_result.get('uuid', '실패')} / 상태: {order_result.get('state', '에러')}")



        elif position == 1:
            max_price = max(max_price, price)
            profit_pct = (price - entry_price) / entry_price
            if profit_pct >= 0.02 or price < max_price * (1 - 0.01) or profit_pct <= -0.015:
                capital *= (1 + profit_pct) * 0.999
                position = 0
                
                
                quantity = calculate_quantity(price)
                order_result = send_order('ask', volume=quantity, price=price)
                send_telegram(f"📉 청산: {strategy}\n수익률: {round(profit_pct*100,2)}%\n가격: {price}\n시간: {time}")
                send_telegram(f"🧾 매도 결과: {order_result.get('uuid', '실패')} / 상태: {order_result.get('state', '에러')}")

                send_telegram(f"📉 청산: {strategy}\n수익률: {round(profit_pct*100,2)}%\n가격: {price}\n시간: {time}")

                trade_log.append({
                    '진입가': round(entry_price, 2),
                    '청산가': round(price, 2),
                    '수익률': round(profit_pct * 100, 2),
                    '전략': strategy,
                    '시간': time,
                    '자산': round(capital, 2)
                })

    
    result_df = pd.DataFrame(trade_log)
    result_df.to_csv('trade_log_result.csv', index=False, encoding='utf-8-sig')

    return result_df

# 예시용 CSV 로딩
if __name__ == '__main__':
    df = fetch_upbit_ohlcv('KRW-BTC', minutes=1, count=200)  # 열: datetime, open, high, low, close, volume
    df['datetime'] = pd.to_datetime(df['datetime'])
    result = run_strategy(df)
    print(result)
