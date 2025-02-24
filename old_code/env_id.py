import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen

from loguru import logger
from DrissionPage import ChromiumPage
from time import sleep
import requests


class OKXWalletAutomator:
    def __init__(self, base_url, headers, max_concurrent_tasks, start, end, password):
        self.base_url = base_url
        self.headers = headers
        self.start = start
        self.end = end
        self.password = password
        self.environment_ids = self.get_environment_ids(start, end)
        self.max_concurrent_tasks = max_concurrent_tasks
        self.current_env_name = None  # 初始化 env_name 属性
        self.value= None


    def get_environment_ids(self, start, end):
        """获取所有环境ID"""
        json_data = {"page": 0, "pageSize": 100}
        try:
            resp = requests.post(f"{self.base_url}/browser/list", json=json_data, headers=self.headers)
            resp.raise_for_status()
            res = resp.json()
            idt = [item['id'] for item in res['data']['list']]
            idt.reverse()
            ids = idt[self.start:self.end]

            logger.info(f"成功获取环境ID: {ids}")
            return ids
        except Exception as e:
            logger.error(f"获取环境ID失败，错误: {e}")
            return []

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


    def unlock_wallet(self, browser_result):
        """在浏览器中解锁钱包，并使用当前的 env_name"""
        try:
            if not browser_result:
                logger.error("未收到有效的浏览器结果，跳过操作")
                return
            drive = ChromiumPage(self.value)
            okx_wallet = drive.new_tab("https://google.com")
            okx_wallet.get("chrome-extension://dkaonkcpflfhalioalibgpdiamnjcpbn/popup.html")
            sleep(1)

            # 输入钱包密码
            okx_wallet.ele("tag:input@data-testid=okd-input").input(self.password)
            sleep(1)
            okx_wallet.ele("tag:span@text():Unlock").click()
            sleep(1)
            logger.info(f"钱包已成功解锁，环境名称: {self.current_env_name}")
        except Exception as e:
            logger.info(f"钱包已解锁,无需操作")

    def bitlayer_check(self,var):
        pass


    def process_environment(self, environment_id):
        """处理单个环境ID的任务：打开浏览器并解锁钱包"""
        self.browser_result = self.open_browser(environment_id)
        self.value = self.browser_result['data']['http']

        logger.info(f"开始处理窗口ID: {self.current_env_name}")
        if self.browser_result:
            # 使用 self.current_env_name 进行一些操作
            logger.info(f"当前环境名称：{self.current_env_name}")
            self.unlock_wallet(self.browser_result)


        else:
            logger.error(f"跳过窗口ID: {self.current_env_name}，因为浏览器打开失败")

    def execute_tasks(self):
        """多线程统一执行打开浏览器和解锁钱包任务"""
        if not self.environment_ids:
            logger.error("没有环境ID可处理，程序退出。")
            return

        with ThreadPoolExecutor(max_workers=self.max_concurrent_tasks) as executor:
            # 提交所有任务
            future_to_env = {executor.submit(self.process_environment, env_id): env_id for env_id in self.environment_ids}

            # 处理完成的任务
            for future in as_completed(future_to_env):
                env_id = future_to_env[future]
                try:
                    future.result()
                    logger.info(f"完成窗口ID: {self.current_env_name} 的任务")
                except Exception as e:
                    logger.error(f"窗口ID: {self.current_env_name} 的任务执行失败，错误: {e}")


def main():
    # 配置
    password = input("请输入钱包密码：")
    start = int(input("请输入要执行的窗口起始点："))
    end = int(input("请输入要执行的窗口结束点："))
    base_url = "http://127.0.0.1:54345"
    headers = {'Content-Type': 'application/json'}
    max_concurrent_tasks = 5

    # 初始化任务管理器
    okx_bot = OKXWalletAutomator(base_url, headers, max_concurrent_tasks,start,end,password)
    # 执行多线程任务
    okx_bot.execute_tasks()


if __name__ == "__main__":
    main()


