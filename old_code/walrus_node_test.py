import logging
import requests
import json
from loguru import logger
from DrissionPage import ChromiumPage
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed

class Walrus:
    def __init__(self, url, headers, password):
        self.password = password
        self.url = url
        self.headers = headers

    def get_id(self):
        """
        批量获取 bit 浏览器环境 ID
        :return: list of IDs
        """
        json_data = {
            "page": 0,  # 第0页
            "pageSize": 100,  # 每页100条记录
        }
        try:
            res = requests.post(f"{self.url}/browser/list", data=json.dumps(json_data), headers=self.headers).json()
            id_list = [item['id'] for item in res['data']['list']]
            id_list.reverse()  # 倒序

            # 写入倒序后的内容到文件
            with open('id_list.txt', 'w') as file:
                for id in id_list:
                    file.write(f"{id}\n")

            logger.info("ID列表已成功写入文件 id_list.txt")
            return id_list
        except Exception as e:
            logger.error(f"获取 ID 列表失败: {e}")
            return []

    def openbrowser(self, user_id):
        """
        打开指定环境 ID 的浏览器
        :param user_id: 环境 ID
        :return: response json
        """
        try:
            json_data = {"id": f'{user_id}'}
            res = requests.post(f"{self.url}/browser/open", data=json.dumps(json_data), headers=self.headers).json()
            logger.info(f"成功打开浏览器环境 ID: {user_id}")
            return res
        except Exception as e:
            logger.error(f"打开浏览器环境 ID {user_id} 失败: {e}")
            return None

    def sui_wallet(self, res):
        """
        对 SUI 钱包操作：导入、输入密码等
        :param res: openbrowser 的响应
        """
        if not res:
            logger.error("无效的浏览器响应，跳过钱包操作")
            return
        try:
            var = res['data']['http']  # 获取浏览器的控制 IP:端口
            drive = ChromiumPage(var)  # 使用 DP 接管浏览器
            sleep(1)
            sui_page = drive.new_tab("chrome-extension://cmnogdnidnbojfcknhacgkdboifdpdcg/ui.html?type=popup")
            sleep(1)
            try:
                sui_page.ele("tag:div@text():More Options").click()
                sui_page.ele("tag:div@text():Import Passphrase").click()

                # 读取助记词文件
                with open("zhujici", "r") as f:
                    mnemonic_array = f.read()

                words = mnemonic_array.split()
                mnemonic_chunks = [words[i:i + 12] for i in range(0, len(words), 12)]  # 12位助记词的数组

                # 假设处理第一个助记词组
                for i in range(12):
                    word = mnemonic_chunks[0][i]
                    sui_page.ele(f"tag:input@id=recoveryPhrase.{i}").input(word)

                sui_page.ele("tag:div@text():Add Account").click()
                sui_page.ele("tag:input@name=password.input").input(self.password)
                sui_page.ele("tag:input@name=password.confirmation").input(self.password)
                sui_page.ele("tag:div@class=text-bodySmall whitespace-nowrap").click()
                sui_page.ele("tag:div@text():Create Wallet").click()
                # 请替换为实际的 SVG 路径或其他元素选择器
                sui_page.ele("tag:svg@d=M5.5.75A1.75 ...").click()  # SVG路径省略
                logger.info("钱包导入成功")
            except Exception as e:
                logger.error(f"SUI钱包操作失败: {e}")
        except Exception as e:
            logger.error(f"处理SUI钱包时出错: {e}")

    def data_page(self, res):
        """
        刷新钱包页面用于解锁钱包功能
        :param res: openbrowser 的响应
        """
        if not res:
            logger.error("无效的浏览器响应，跳过数据页面操作")
            return
        try:
            var = res['data']['http']  # 获取浏览器的控制 IP:端口
            drive = ChromiumPage(var)  # 使用 DP 接管浏览器
            sleep(1)
            updatapage = drive.new_tab("chrome-extension://cmnogdnidnbojfcknhacgkdboifdpdcg/ui.html")
            try:
                updatapage.ele("tag:button@class=appearance-none bg-transparent border-none cursor-pointer w-full").click()
            except Exception:
                logger.info("广告已删除")
            try:
                updatapage.ele("tag:div@text():Unlock Account").input("zm960810.")
                sleep(1)
                updatapage.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
            except Exception:
                logger.info("无需解锁钱包,修改网络为testnet")
                updatapage.ele("tag:svg@d=M5.5.75A1.75 ...").click()  # SVG路径省略
                updatapage.ele("tag:path@d=M11.112 ...").click()  # SVG路径省略
                logger.info("网络修改为Testnet")
        except Exception as e:
            logger.error(f"数据页面处理失败: {e}")

    def stakesui(self, res):
        """
        stake SUI 操作
        :param res: openbrowser 的响应
        """
        if not res:
            logger.error("无效的浏览器响应，跳过staking操作")
            return
        try:
            var = res['data']['http']  # 获取浏览器的控制 IP:端口
            drive = ChromiumPage(var)  # 接管浏览器
            stake_page = drive.new_tab("https://stake.walrus.site/")
            try:
                stake_page.ele("tag:button@text():Connect Wallet").click()
                suitab = drive.wait.new_tab(timeout=10)
                suiwindow = drive.get_tab(suitab)
                suiwindow.ele("tag:div@text():Sui Wallet").click()
                sleep(1)

                suitab2 = drive.wait.new_tab(timeout=10)
                suiwindow2 = drive.get_tab(suitab2)
                sleep(2)
                suiwindow2.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
                try:
                    suiwindow2.ele("tag:button@class=appearance-none p-0 bg-transparent border-none cursor-pointer text-steel hover:text-hero-dark ml-auto flex items-center justify-center").click()
                except Exception:
                    logger.info("钱包已解锁无需操作")
            except Exception:
                logger.info("钱包已连接到当前网站，继续执行...")

            # 触发兑换按钮并进行兑换操作
            stake_page.ele("tag:button@class=justify-center whitespace-nowrap font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950 disabled:pointer-events-none disabled:opacity-50 bg-primaryDark text-primary shadow-sm hover:bg-primaryDark/80 border border-primary/50 hover:border-primary h-8 rounded-md px-3 text-xs flex items-center gap-2").click()
            stake_page.ele("tag:input@class=border-primary/30 focus-visible:ring-secondary flex h-9 w-full rounded-md border bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-neutral-950 placeholder:text-neutral-500 focus-visible:outline-none focus-visible:ring-1 disabled:cursor-not-allowed disabled:opacity-50").input(1)
            sleep(2)
            stake_page.ele("tag:button@text():Exchange").click()

            # 捕捉弹窗，点击确认
            suitab3 = drive.wait.new_tab(timeout=8)
            approve = drive.get_tab(suitab3)
            try:
                approve.ele("tag:div@text():Unlock Account").click()
                approve.ele("tag:input@name=password").input(self.password)
            except Exception:
                logger.info("钱包已解锁无需操作")

            try:
                approve.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
                approve.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
                logger.info("兑换成功")
            except Exception:
                logger.info("钱包此次无需授权")
            sleep(2)

            # 查找并执行质押操作
            stake_page.get("https://stake.walrus.site")
            stake_page.ele("tag:button@text():Stake").click()
            stake_page.ele("tag:input@type=text").input(1)

            sleep(1)
            try:
                stake_page.ele("tag:button@class=inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950 disabled:pointer-events-none disabled:opacity-50 bg-secondary/90 text-primaryDark shadow hover:bg-secondary h-9 px-4 py-2").click()
                sleep(2)
                # 捕捉弹窗，确认质押
                suitab4 = drive.wait.new_tab(timeout=5)
                approve2 = drive.get_tab(suitab4)
                approve2.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
                logger.info("质押完成!")
            except Exception:
                logger.error("GWL余额不足...")
        except Exception:
            logger.error("未找到浏览器接口")

    def claimnft(self, res):
        """
        claim NFT 过程：连接钱包并点击领取按钮
        :param res: openbrowser 的响应
        """
        if not res:
            logger.error("无效的浏览器响应，跳过claimnft操作")
            return
        try:
            var = res['data']['http']  # 获取浏览器的控制IP:端口
            drive = ChromiumPage(var)  # 接管浏览器
            claim_page = drive.new_tab("https://flatland.walrus.site")
            claim_page.ele("tag:button@text():Connect Wallet").click()
            claim_page.ele("tag:div@text():Sui Wallet").click()

            suitab5 = drive.wait.new_tab(timeout=8)
            suiwindow4 = drive.get_tab(suitab5)
            suiwindow4.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
            try:
                claim_page.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
                logger.info("授权按钮点击成功")
            except Exception:
                logger.info("未找到授权按钮，跳过")

        except Exception:
            logger.error("未找到浏览器接口")
        # except Exception as e:
        #     logger.error(f"claimnft操作失败: {e}")
        #     try:
        #         drive = ChromiumPage(res['data']['http'])  # 确保drive被初始化
        #         claim_page = drive.new_tab("https://flatland.walrus.site")
        #         claim_page.ele("tag:button@class=rt-reset rt-BaseButton rt-Button rt-r-size-2 rt-variant-surface").click()
        #         suitab6 = drive.wait.new_tab(timeout=8)
        #         approve = drive.get_tab(suitab6)
        #         re = approve.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
        #         sleep(5)
        #         if re:
        #             logger.info("领取成功")
        #         else:
        #             logger.info("未领取成功")
        #     except Exception as ex:
        #         logger.error(f"领取NFT时出错: {ex}")

    def execute_task(self, user_id):
        """
        处理单个钱包任务
        """
        try:
            res = self.openbrowser(user_id)
            self.sui_wallet(res)
            self.data_page(res)
            self.stakesui(res)
            self.claimnft(res)
        except Exception as e:
            logger.error(f"处理钱包 {user_id} 时出错: {e}")

def main():
    password = input("请输入钱包密码：")
    start = int(input("请输入要执行的窗口起始点："))
    end = int(input("请输入要执行的窗口结束点："))

    walrus = Walrus(url="http://127.0.0.1:54345", headers={'Content-Type': 'application/json'}, password=password)
    id_list = walrus.get_id()
    id_list = id_list[start:end]

    if not id_list:
        logger.error("没有找到任何环境ID，程序退出。")
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(walrus.execute_task, user_id)
            for user_id in id_list
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"任务执行失败: {e}")

if __name__ == '__main__':
    main()
