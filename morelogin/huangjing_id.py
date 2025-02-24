import base64
import hashlib
import json
import logging
import random
import string
import time
from tkinter.messagebox import QUESTION

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

if __name__ == '__main__':
    import requests

    # 请求 URL 和数据
    url = "http://127.0.0.1:40000/api/env/page"
    data = {
        "pageNo": 1,
        "pageSize": 100
    }

    # 发起请求
    response = requests.post(url, headers=requestHeader(), json=data)
    response.raise_for_status()
    response_data = response.json()

    data_list = response_data["data"]["dataList"][::-1]  # 反转列表
    # 打开两个文件，一个用来存储id，一个用来存储envName
    with open("project/env_id.txt", "w", encoding="utf-8") as id_file, \
            open("project/env_name.txt", "w", encoding="utf-8") as name_file:

        # 遍历dataList中的所有元素
        for item in data_list:
            env_id = item["id"]
            env_name = item["envName"]

            # 写入文件，每个id和envName占一行
            id_file.write(env_id + "\n")
            name_file.write(env_name + "\n")

    print("所有id和envName已分别写入env_id.txt和env_name.txt文件中。")



    #
    #     print(response_data)
    # except requests.exceptions.RequestException as e:
    #     print(f"Request Error: {e}")
    #     exit()
    # except json.JSONDecodeError:
    #     print("Error: Response is not in JSON format")
    #     exit()
