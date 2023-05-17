import sys
import uuid
import requests
import wave
import base64
import hashlib

import time


def connect():
    YOUDAO_URL = 'https://openapi.youdao.com/asrapi'
    APP_KEY = '337af8c31d798a2c'
    APP_SECRET = 't17A2QK4mt81JGWOEhWXjoPOeoU34oub'
    
    def truncate(q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size-10:size]

    def encrypt(signStr):
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(signStr.encode('utf-8'))
        return hash_algorithm.hexdigest()

    def do_request(data):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(YOUDAO_URL, data=data, headers=headers)

    
    data = {}
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['signType'] = "v2"
    data['langType'] = 'zh-CHS'
    data['rate'] = 16000
    data['format'] = 'wav'
    data['channel'] = 1
    data['type'] = 1

    response = do_request(data)
    print(response.content.decode())

if __name__ == '__main__':
    connect()