
import jwt
import uuid
import hashlib
import os
import requests
from urllib.parse import urlencode

def get_upbit_balance():
    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")

    payload = {
        'access_key': ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, SECRET_KEY)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get("https://api.upbit.com/v1/accounts", headers=headers)
    result = res.json()
    for item in result:
        if item['currency'] == 'KRW':
            return float(item['balance'])
    return 0.0

def calculate_quantity(price, ratio=0.95):
    balance = get_upbit_balance()
    krw_available = balance * ratio
    quantity = krw_available / price
    return round(quantity, 6)  # 6자리 소수점까지 BTC 가능

# 예시: 현재가 50,000,000원일 때 주문 수량 계산
# print(calculate_quantity(50000000))
