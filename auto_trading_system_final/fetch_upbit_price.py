
import requests
import pandas as pd
from datetime import datetime

def fetch_upbit_ohlcv(market='KRW-BTC', minutes=1, count=200):
    url = f"https://api.upbit.com/v1/candles/minutes/{minutes}"
    params = {
        'market': market,
        'count': count
    }
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    df = pd.DataFrame(data)
    df = df.rename(columns={
        'candle_date_time_kst': 'datetime',
        'opening_price': 'open',
        'high_price': 'high',
        'low_price': 'low',
        'trade_price': 'close',
        'candle_acc_trade_volume': 'volume'
    })
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df[['datetime', 'open', 'high', 'low', 'close', 'volume']].sort_values(by='datetime')

# 테스트 실행
if __name__ == '__main__':
    df = fetch_upbit_ohlcv()
    print(df.head())
