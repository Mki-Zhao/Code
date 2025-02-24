import asyncio
import random
import aiohttp
from log import logger

class BeraWater:
    def __init__(self):
        self.proxys = self.generate_random_proxy()

    def random_string(self, length):
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(length))

    # 随机代理
    def generate_random_proxy(self):
        random_proxy_str = self.random_string(10)
        proxy_url = f"7F575C2EEE3C6030-residential-country_ANY-r_0m-s_{random_proxy_str}:Lgxlygrk@gate.nstproxy.io:24125"
        logger.info(f"Using proxy: {proxy_url}")
        return proxy_url

    async def make_request(self, address, token, max_retries=10):
        proxy = {
            "http": self.proxys,
            "https": self.proxys,
        }

        url = f'https://bartiofaucet.berachain.com/api/claim?address={address}'

        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            "Authorization": "Bearer " + token,
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://bartio.faucet.berachain.com',
            'pragma': 'no-cache',
            'referer': 'https://bartio.faucet.berachain.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }

        data = {"address": address}

        # 使用 aiohttp 异步请求
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://ipinfo.io/", proxy=self.proxys) as req_ip:
                    ip_info = await req_ip.json()
                    ip = f"当前ip: {ip_info['ip']} \t  当前地区: {ip_info['region']} 当前地址为：{address}"
                    logger.info(ip)
            except Exception as e:
                logger.info(f"无法获取IP信息: {e}")

            logger.info("开始领水")
            for attempt in range(max_retries):
                try:
                    async with session.post(url, headers=headers, json=data, proxy=self.proxys) as response:
                        logger.info(await response.json())
                        return await response.json()
                except Exception as e:
                    logger.info(f"请求失败: {e}，重试中... (尝试 {attempt + 1}/{max_retries})")
                    await asyncio.sleep(2)

            logger.error("所有重试已用尽，无法完成请求。")
        return None

    async def sign_request(self, address):
        key = "c597e5bbd47f0ca0565a2665f3592819293db2fb39892"
        create_task_url = "https://api.yescaptcha.com/createTask"
        body = {
            "clientKey": key,
            "task": {
                "type": "TurnstileTaskProxylessM1",
                "websiteURL": "https://artio.faucet.berachain.com/",
                "websiteKey": "0x4AAAAAAARdAuciFArKhVwt"
            }
        }

        # 使用 aiohttp 进行异步请求
        async with aiohttp.ClientSession() as session:
            for attempt in range(5):
                try:
                    async with session.post(create_task_url, json=body, proxy=self.proxys) as task_response:
                        task_data = await task_response.json()
                        task_id = task_data["taskId"]
                        break
                except Exception as e:
                    logger.info(f"创建任务失败: {e}，重试中... (尝试 {attempt + 1}/5)")
                    await asyncio.sleep(3)
            else:
                logger.error("创建任务失败，退出。")
                return

            get_token_url = "https://api.yescaptcha.com/getTaskResult"
            token_body = {"clientKey": key, "taskId": task_id}

            for i in range(10):
                try:
                    async with session.post(get_token_url, json=token_body, proxy=self.proxys) as token_response:
                        token_data = await token_response.json()
                        status = token_data["status"]
                        if status == "processing":
                            logger.info(f"等待CloudflareTurnstile返回第{i + 1}次")
                            await asyncio.sleep(3)
                        else:
                            logger.info("CloudflareTurnstile返回成功")
                            token = token_data["solution"]["token"]
                            await self.make_request(address, token)
                            break
                except Exception as e:
                    logger.info(f"获取Token失败: {e}，重试中...")
                    await asyncio.sleep(2)

    async def process_address(self, semaphore, address):
        async with semaphore:
            await self.sign_request(address)

    async def main(self):
        tasks = []
        semaphore = asyncio.Semaphore(5)  # 限制最大并发数为 5
        with open("evm_address.txt", "r", encoding="utf-8") as f:
            for line in f:
                address = line.strip()
                tasks.append(self.process_address(semaphore, address))

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    bera = BeraWater()
    asyncio.run(bera.main())
