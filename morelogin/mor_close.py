import base64
import hashlib
import json
from time import sleep
import openai
import random
import string
import time
import requests
from DrissionPage import ChromiumPage

APPID = '1617723807467469'
SECRETKEY = 'c8dde24bddf9492db49edc3ea13528f3'
BASEURL = 'http://127.0.0.1:40000'

def generateRandom(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generateNonceId():
    return str(int(time.time() * 1000)) + generateRandom()

def md5Encode(nonceId):
    md5 = hashlib.md5()
    md5.update((APPID + nonceId + SECRETKEY).encode('utf-8'))
    return md5.hexdigest()

def requestHeader():
    nonceId = generateNonceId()
    md5Str = md5Encode(nonceId)
    return {
       'X-Api-Id': APPID,
       'Authorization': md5Str,
       'X-Nonce-Id': nonceId
    }

# -------------------------------
# 1. 获取所有环境信息并随机选取一个
# -------------------------------
env_list_url = f"{BASEURL}/api/env/close"
env_list_data = {
    "envId": "1883520053569724416"
}

response = requests.post(env_list_url, headers=requestHeader(), json=env_list_data)
#     response.raise_for_status()
#     response_data = response.json()
# except requests.exceptions.RequestException as e:
#     print(f"获取环境列表请求错误: {e}")
#     exit()
# except json.JSONDecodeError:
#     print("错误：环境列表接口返回的不是 JSON 格式")
#     exit()