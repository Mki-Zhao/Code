import json
import os
from asyncio import timeout
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen
from loguru import logger
from DrissionPage import ChromiumPage
from time import sleep
import requests


class OKXWalletAutomator:
    def __init__(self, base_url, headers):
        self.browser_result = None
        self.base_url = base_url
        self.headers = headers
        self.current_env_name = None  # 初始化 env_name 属性
        self.value= None
        self.browser_result = self.open_browser(environment_id='6f6ce698e068412c9aeb6e55e4554a95')
        self.drive = None

    def open_browser(self, environment_id):
        """打开指定环境ID的浏览器"""
        json_data = {"id": f"{environment_id}"}
        try:
            resp = requests.post(f"{self.base_url}/browser/open", json=json_data, headers=self.headers)
            resp.raise_for_status()
            result = resp.json()
            self.current_env_name = result['data']['name']  # 设置 env_name
            logger.info(f"浏览器打开成功，当前执行窗口名称：{self.current_env_name}")
            return result
        except Exception as e:
            logger.error(f"打开浏览器失败，环境ID: {environment_id}，错误: {e}")
            return None

    def bitlayer_check(self):
        var = self.browser_result['data']['http']
        web = ChromiumPage(var)  # 接管浏览器
        bitlayer = web.new_tab("https://www.bitlayer.org/btcfi")
        sleep(2)

        # 使用原始字符串（r""）避免反斜杠转义问题,
        js_code = r'''
        document.querySelector("body > main > div > div > div.bl-mt-\\[70px\\].sm\\:bl-mt-0.bl-bg-white.bl-pb-12 > div.bl-relative.bl-container.bl-flex-center.bl-mt-7.sm\\:bl-mt-\\[-120px\\].lg\\:bl-mt-\\[-168px\\].bl-z-10 > div > div.md\\:bl-pb-10.bl-pb-\\[28px\\] > div.bl-grid.bl-grid-cols-4.bl-gap-\\[10px\\].md\\:bl-gap-6.bl-flex-wrap.bl-pt-5.md\\:bl-pt-9 > div:nth-child(2) > button").click();
        '''
        bitlayer.run_js(js_code)

        sleep(2)
        okxtab = web.wait.new_tab(timeout=20)
        okx = web.get_tab(okxtab)
        okx.ele("tag:div@text():Confirm").click()



def main():
    base_url = "http://127.0.0.1:54345"
    headers = {'Content-Type': 'application/json'}

    # 初始化任务管理器
    okx_bot = OKXWalletAutomator(base_url, headers)
    # 执行多线程任务
    okx_bot.open_browser('6f6ce698e068412c9aeb6e55e4554a95')
    okx_bot.bitlayer_check()

if __name__ == "__main__":
    main()


