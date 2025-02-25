import random
import time
import hmac
import hashlib
import base64
import requests
import json
from urllib.parse import urlencode


"""
这是一个查询链ID的函数
"""
class CheckChainID:
    def __init__(self, ccy, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.ccy = ccy

    def generate_signature(self, method, request_path, body=""):
        """ 生成 API 请求签名 """
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime()) + '.000Z'

        if isinstance(body, dict):
            body = json.dumps(body)

        message = timestamp + method + request_path + body
        signature = base64.b64encode(
            hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()

        return timestamp, signature

    def check(self):
        """ 查询币种信息 """
        method = "GET"
        params = {"ccy": self.ccy}
        query_string = urlencode(params)
        request_path = "/api/v5/asset/currencies" + "?" + query_string

        body = ""  # GET请求没有请求体
        timestamp, signature = self.generate_signature(method, request_path, body)

        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }

        base_url = "https://www.okx.com"
        url = base_url + "/api/v5/asset/currencies"

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # 如果返回的状态码不是 200，则抛出异常

            data = response.json()

            # 构造链列表
            chain_list = [item["chain"] for item in data["data"] if "chain" in item]

            num_items = len(data["data"])

            if not chain_list:
                print(f"币种 {self.ccy} 没有找到相关链ID")
            else:
                print(f"{self.ccy} 的可用提币链 ID：")
                for idx, chain in enumerate(chain_list, 1):
                    print(f"{idx}. {chain}")

                # 保存到 JSON 文件
                with open("chain.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            return chain_list


        except requests.exceptions.RequestException as e:
            print("请求失败：", e)
        except json.JSONDecodeError:
            print("返回的 JSON 数据格式错误")
        except KeyError:
            print("API 返回数据缺失 'data' 字段")
        return []

class WithdrawCoin:
    def __init__(self, api_key, secret_key, passphrase,coin,SelectedChain,start,end):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.coin = coin
        self.SelectedChain = SelectedChain
        self.start = start
        self.end = end

    def generate_signature(self,request_path,body=""):
        # 请求方法和路径
        method = "POST"
        #request_path = "/api/v5/asset/withdrawal"
        # 获取当前UTC时间戳，ISO 8601格式
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime()) + '.000Z'
        # 如果 body 是字典，则转换为JSON字符串
        if isinstance(body, dict):
            body = json.dumps(body)
        # 拼接字符串：timestamp + method + requestPath + body
        message = timestamp + method + request_path + body
        # 使用HMAC-SHA256加密，并进行Base64编码
        signature = base64.b64encode(
            hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()
        return timestamp, signature

    def withdraw(self):
        with open("okx_evm_address.txt","r") as f:
            lines = [line.strip() for line in f if line.strip()]    #for循环遍历f文件,去掉两端的空白字符，查看每行是否有值，有则把值加入到lines列表
            random.shuffle(lines)
            num_lines  = len(lines)
        # 使用最终需要发送的请求数据生成签名

        for address in range(num_lines):
            random_amt = random.uniform(self.start,self.end)

            data = {
                "ccy": self.coin,
                "amt": random_amt,
                "dest": 4,
                "toAddr": lines[address],
                "chain": self.SelectedChain,  # 注意参数名称调整为 chain
                "walletType": "private"
            }

            print(f"提币地址：{lines[address]}")

            # 请求方法和路径
            request_path = "/api/v5/asset/withdrawal"

            # 生成请求体字符串
            body = json.dumps(data)

            # 生成签名
            timestamp, signature = self.generate_signature(request_path,body)

            # 构造请求头
            headers = {
                "OK-ACCESS-KEY": self.api_key,
                "OK-ACCESS-SIGN": signature,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": self.passphrase,
                "Content-Type": "application/json"
            }

            # 构建完整URL
            base_url = "https://www.okx.com"
            url = base_url + request_path

            # 发送POST请求
            response = requests.post(url, headers=headers, json=data)

            # 打印响应
            if response.status_code == 200:
                resp_json = response.json()
                print("提币详情：", resp_json)
                #print("提币状态：", resp_json.get("msg", "无消息"))
                print(f"随机提币数量：{random_amt}")
                RadomTime = random.uniform(30, 60)
                status = resp_json.get("msg")
                if status:
                    print("\033[1;31m提币失败，自行检查余额/ip是否加入白名单,提币详情有报错信息\033[0m")

                else:
                    print("\033[1;32m============================")
                    print("     提币成功!!")
                    print("============================\033[0m")

                    print(f"等待{RadomTime}秒继续")
                    time.sleep(RadomTime)

            else:
                print("请求失败，状态码：", response.status_code)
                print("错误信息：", response.text)


if __name__ == "__main__":
    # 用户输入币种（例如 USDT）
    coin = input("输入提币币种（例如 USDT）：").strip()
    api_key = "填自己的api_key"
    secret_key = "填自己的secret_key"
    passphrase = "填自己的passphrase"
    print("脚本默认打乱了address地址的排列顺序，如需按顺序执行,注销第118行代码：random.shuffle(lines)")
    input("按任意键继续...")

    #查询可用的链ID
    check_chain = CheckChainID(coin, api_key, secret_key, passphrase)
    chain_options = check_chain.check()

    if not chain_options:
        print("未查询到可用的提币链，请检查币种是否正确或者稍后重试。")

    else:
        #提示用户选择链
        choice = input("请选择你要使用的链（输入序号）：").strip()

        try:
            choice_idx = int(choice)-1
            selected_chain = chain_options[choice_idx]
        except (ValueError,IndexError):
            print("输入错误，默认选择第一个")
            selected_chain = chain_options[0]

        print(f"你选择的链为：{selected_chain}")

        start = float(input(f"输入你要提币的{coin}数量起始值： "))
        end = float(input(f"输入你要提币的{coin}数量结束值： "))

        withdraws = WithdrawCoin(api_key, secret_key, passphrase, coin,selected_chain,start,end)
        withdraws.withdraw()

        print("\033[1;32m任务已全部完成。\033[0m")

