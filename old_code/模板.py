import asyncio
from log import logger
from curl_cffi import requests
from eth_utils import to_checksum_address

proxys = "7F575C2EEE3C6030-residential-country_ANY-r_0m-s_SxYlqFAxFW:Lgxlygrk@gate.nstproxy.io:24125"

proxy = {
    "http": proxys,
    "https": proxys,
}

async def make_request(address=None, token=None, max_retries=10):
    checksum_address = to_checksum_address(address)
    url = f'https://bartiofaucet.berachain.com/api/claim?address={checksum_address}'

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

    data = {"address": checksum_address}

    try:
        req_ip = await asyncio.to_thread(requests.get, "https://ipinfo.io/", proxies=proxy, verify=False)
        ip_info = req_ip.json()
        ip = f"当前ip: {ip_info['ip']} \t  当前地区: {ip_info['region']}"
        logger.info(ip)
    except Exception as e:
        logger.info(f"无法获取IP信息: {e}")

    logger.info("开始领水")
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                requests.post, url, headers=headers, json=data, proxies=proxy, verify=False
            )
            if "Added" in response.text:
                logger.info(f"地址{address}水成功领取，返回信息:", response.text)
            else:
                logger.info(f"地址{address}水领取失败，错误信息: {response.text}")
            break
        except Exception as e:
            logger.info(f"请求失败: {e}，重试中... (尝试 {attempt + 1}/{max_retries})")
            await asyncio.sleep(2)

async def sign_request(address: str):
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

    for attempt in range(5):
        try:
            task_response = await asyncio.to_thread(
                requests.post, create_task_url, json=body, proxies=proxy, verify=False
            )
            task_data = task_response.json()
            task_id = task_data["taskId"]
            break
        except Exception as e:
            logger.info(f"创建任务失败: {e}，重试中... (尝试 {attempt + 1}/5)")
            await asyncio.sleep(2)
    else:
        logger.error("创建任务失败，退出。")
        return

    get_token_url = "https://api.yescaptcha.com/getTaskResult"
    token_body = {"clientKey": key, "taskId": task_id}

    for i in range(10):
        try:
            token_response = await asyncio.to_thread(
                requests.post, get_token_url, json=token_body, proxies=proxy, verify=False
            )
            token_data = token_response.json()
            status = token_data["status"]
            if status == "processing":
                logger.info(f"等待CloudflareTurnstile返回第{i + 1}次")
                await asyncio.sleep(3)
            else:
                logger.info("CloudflareTurnstile返回成功")
                token = token_data["solution"]["token"]
                await make_request(address, token)
                break
        except Exception as e:
            logger.info(f"获取Token失败: {e}，重试中...")
            await asyncio.sleep(2)

async def process_address(semaphore, address):
    async with semaphore:
        await sign_request(address)

async def main():
    tasks = []
    semaphore = asyncio.Semaphore(5)
    with open("evm_address.txt", "r", encoding="utf-8") as f:
        for line in f:
            address = line.strip()
            tasks.append(process_address(semaphore,address))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())