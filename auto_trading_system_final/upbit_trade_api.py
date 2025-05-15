
import requests
import uuid
import jwt
import hashlib
import time
from urllib.parse import urlencode

# 이 파일을 사용하려면 아래 값을 자신의 것으로 교체하거나 .env 처리 필요
ACCESS_KEY = '여기에_접근키'
SECRET_KEY = '여기에_비밀키'
SERVER_URL = 'https://api.upbit.com'

def send_order(side, volume, price, market="KRW-BTC", ord_type="limit"):
    query = {
        'market': market,
        'side': side,          # 'bid' = 매수, 'ask' = 매도
        'volume': str(volume),
        'price': str(price),
        'ord_type': ord_type,  # 시장가 = 'market', 지정가 = 'limit'
    }

    query_string = urlencode(query).encode()
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, SECRET_KEY)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(SERVER_URL + "/v1/orders", params=query, headers=headers)
    return res.json()

# 매수 예시
# print(send_order('bid', volume=0.0005, price=50000000))

# 매도 예시
# print(send_order('ask', volume=0.0005, price=51000000))
