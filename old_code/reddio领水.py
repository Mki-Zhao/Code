import asyncio
import time
import json
import random
from idlelib.window import add_windows_to_menu

import requests
from log import logger  # 确保 logger 已正确导入

class ReddioWater:
    def __init__(self):
        # 读取 evm_address 文件并获取地址列表
        with open("evm_address.txt", "r") as f:
            words = f.read()
            self.address = words.split("\n")  # 将地址按行分割
            self.sui = len(self.address)

    # 随机字符串
    def random_string(self, length):
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(length))

    # 随机代理
    def generate_random_proxy(self):
        random_proxy_str = self.random_string(10)
        proxy_url = f"7F575C2EEE3C6030-residential-country_ANY-r_0m-s_{random_proxy_str}:Lgxlygrk@gate.nstproxy.io:24125"
        logger.info(f"Using proxy: {proxy_url}")
        return proxy_url


    async def request(self, recipient):

        random_proxy = self.generate_random_proxy()
        proxy = {
            "http": random_proxy,
            "https": random_proxy,
        }

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36"
        ]

        # 随机选择一个 User-Agent
        selected_user_agent = random.choice(user_agents)
        logger.info(f"当前user：{selected_user_agent}")


        url = "https://testnet-faucet.reddio.com/api/claim/new"

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-HK,zh;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://testnet-faucet.reddio.com',
            'priority': 'u=1, i',
            'referer': 'https://testnet-faucet.reddio.com/',
            'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': selected_user_agent

        }

        payload = json.dumps({
            "address": recipient,
            "others": False
        })

        try:
            req_ip = await asyncio.to_thread(requests.get,"https://ipinfo.io/", proxies=proxy)
            await asyncio.sleep(2)
            ip_info = req_ip.json()
            ip = f"当前ip: {ip_info['ip']} \t  当前地区: {ip_info['region']}"
            logger.info(ip)
        except Exception as e:
            logger.error(f"无法获取IP信息: {e}")

        # 发送POST请求
        response = await asyncio.to_thread(requests.post,url,headers=headers, data=payload, proxies=proxy, timeout=30)

        # 检查响应状态码
        if response.status_code == 200:
            print(f"请求成功，地址: {recipient}，等待10秒到账...")
        else:
            print(f"请求失败，地址: {recipient}，状态码: {response.status_code}")
            print("错误信息：", response.text)

    # def run(self):
    #     # 循环遍历所有地址并调用 request 方法
    #     for address in self.address:
    #         if address.strip():  # 排除空行
    #             print(f"正在请求地址: {address.strip()}")
    #             self.request(address.strip())  # 传递当前地址到 recipient

    async def process_address(self,semaphore,address):
        async with semaphore:
            await self.request(address)

    async def main(self):
        tasks = []
        semaphore = asyncio.Semaphore(5)
        with open("evm_address.txt","r") as f:
            for i in f:
                address = i.split()
                tasks.append(self.process_address(semaphore,address))

        await asyncio.gather(*tasks)

if __name__ == '__main__':
    Water = ReddioWater()
    asyncio.run(Water.main())
