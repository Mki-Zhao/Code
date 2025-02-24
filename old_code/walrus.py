import logging
from csv import excel
from turtledemo.penrose import start

import requests
import json
from loguru import logger
from DrissionPage import ChromiumPage
from time import sleep
import threading

from lxml.html import open_in_browser
from openpyxl.worksheet.print_settings import PrintArea
from toolz import excepts
from concurrent.futures import ThreadPoolExecutor


class Walrus:
    def __init__(self, url,headers,password,start,end):
        self.password = password
        self.url = url
        self.headers = headers
        self.drive = None
        self.claim_page = None
        self.value = self.openbrowser(start,end)
        self.j = 0
        with open("evm_address.txt", "r") as f:     #address 替换为自己的sui地址
            words = f.read()
            self.address = words.split("\n")
        self.number = len(self.address)
        #self.balance = self.get_sui_balance()
        #self.balance = int(self.balance)

    def get_id(self):
        """
        批量获取bit浏览器环境ID
        :return:
        """
        json_data = {
            "page": 0,  # 第0页
            "pageSize": 100,  # 每页10条记录
        }
        res = requests.post(f"{self.url}/browser/list",data=json.dumps(json_data), headers=self.headers).json()

        #pretty_output = json.dumps(res, indent=4, ensure_ascii=False)    #美化json文件

        id_list = [item['id'] for item in res['data']['list']]
        id_list.reverse()  # 或者 id_list = id_list[::-1]

        # 写入倒序后的内容
        with open('id_list.txt', 'w') as file:
            [file.write(f"{id}\n") for id in id_list]

        logger.info("ID列表已写入文件 id_list.txt")
        #寻找key为id的值，这里遍历的是data里面的list字典，并且从list字典中找id的key

        with open ('id_list.txt','w') as file:
            [file.write(f"{id}\n") for id in id_list]

        logger.info("ID列表已成功写入文件 id_list.txt")


    def openbrowser(self,start,end):  # 直接指定ID打开窗口，也可以使用 createBrowser 方法返回的ID
        """
        打开指定环境ID的浏览器
        :return:
        """

        with open("id_list.txt", "r") as h:
            huanjing = h.read().strip()
            huanjingid = huanjing.split('\n')   #\n将huanjing转成了数组
            id_list = huanjingid[start:end]

            for user_id in id_list:    #再从数组里取值，传递给json_data
                json_data = {"id": f'{user_id}'}
                res = requests.post(f"{self.url}/browser/open",
                                data=json.dumps(json_data), headers=self.headers).json()
                return res


    def sui_wallet(self):
        """
        对SUI的钱包操作：导入、输入密码等
        :return:
        """
        result = self.value
        var = result['data']['http']  # 获取浏览器的控制IP:端口
        self.drive = ChromiumPage(var)  # 使用DP接管浏览器
        sleep(1)
        sui_page = self.drive.new_tab("chrome-extension://cmnogdnidnbojfcknhacgkdboifdpdcg/ui.html?type=popup")
        sleep(1)
        try:
            sui_page.ele("tag:div@text():More Options").click()
            sui_page.ele("tag:div@text():Import Passphrase").click()
            """
            exiszhujici替换为自己的助记词文件
            """
            with open("zhujici","r") as  f:
                 mnemonic_array = f.read()

            words= mnemonic_array.split()
            mnemonic_array = [words[i:i + 12] for i in range(0, len(words), 12)]    #得到一个12位助记词的数组


            for i in range(12):  # 遍历每个子数组
                    word = mnemonic_array[self.j][i]  # 获取词
                    sui_page.ele(f"tag:input@id=recoveryPhrase.{i}").input(word)

            sui_page.ele("tag:div@text():Add Account").click()
            sui_page.ele("tag:input@name=password.input").input(self.password)
            sui_page.ele("tag:input@name=password.confirmation").input(self.password)
            sui_page.ele("tag:div@class=text-bodySmall whitespace-nowrap").click()
            sui_page.ele("tag:div@text():Create Wallet").click()
            sui_page.ele("tag:svg@d=M5.5.75A1.75 1.75 0 0 0 3.75 2.5h1.5a.25.25 0 0 1 .25-.25h3c.69 0 1.25.56 1.25 1.25v3a.25.25 0 0 1-.25.25v1.5a1.75 1.75 0 0 0 1.75-1.75v-3A2.75 2.75 0 0 0 8.5.75h-3ZM2.5 5h4a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-.5.5h-4a.5.5 0 0 1-.5-.5v-4a.5.5 0 0 1 .5-.5Zm-2 .5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-4Z")
            sui_page.ele("tag:path@d=M11.112 21.05c-.677 0-1.195-.413-1.353-1.064l-.387-1.643-.281-.097-1.424.879c-.571.36-1.24.273-1.723-.21l-1.221-1.223c-.484-.483-.58-1.151-.211-1.713l.887-1.424-.096-.264-1.644-.387a1.359 1.359 0 0 1-1.063-1.353v-1.74a1.35 1.35 0 0 1 1.063-1.354l1.626-.395.106-.282-.888-1.424c-.37-.562-.273-1.221.21-1.713l1.223-1.23c.474-.476 1.142-.563 1.713-.212l1.424.88.3-.115.386-1.644c.158-.65.676-1.063 1.353-1.063h1.776c.677 0 1.195.413 1.353 1.063l.378 1.644.299.114 1.433-.879c.57-.351 1.23-.263 1.705.211l1.23 1.23c.483.493.571 1.152.211 1.714l-.896 1.424.114.282 1.626.395a1.35 1.35 0 0 1 1.063 1.353v1.74c0 .669-.422 1.196-1.063 1.354l-1.644.387-.105.264.896 1.424c.36.562.273 1.23-.21 1.713l-1.231 1.222c-.483.483-1.143.571-1.714.211l-1.433-.879-.28.097-.379 1.643c-.158.65-.676 1.064-1.353 1.064h-1.776Zm.14-1.371h1.495c.15 0 .229-.062.246-.202l.536-2.18a4.905 4.905 0 0 0 1.406-.58l1.917 1.178c.114.079.22.061.334-.044l1.028-1.037c.105-.097.105-.203.035-.326l-1.178-1.898a6 6 0 0 0 .572-1.406l2.188-.519c.132-.026.202-.105.202-.255v-1.468c0-.158-.061-.228-.202-.255l-2.18-.527c-.14-.571-.395-1.09-.562-1.415l1.169-1.898c.079-.132.079-.238-.027-.343l-1.037-1.02c-.114-.105-.202-.123-.342-.044L14.944 6.6a6.41 6.41 0 0 0-1.415-.57l-.536-2.198c-.017-.14-.097-.202-.246-.202h-1.494c-.15 0-.229.061-.255.202l-.518 2.18c-.528.15-1.064.369-1.442.58L7.14 5.44c-.132-.079-.229-.061-.334.044L5.76 6.504c-.097.105-.106.21-.027.343l1.17 1.898c-.159.325-.423.844-.563 1.415l-2.171.527c-.15.027-.202.097-.202.255v1.468c0 .15.061.229.202.255l2.18.519c.14.536.369 1.037.57 1.406l-1.177 1.898c-.07.123-.061.229.035.326l1.037 1.037c.106.105.22.123.326.044l1.916-1.178c.378.237.879.448 1.415.58l.527 2.18c.026.14.106.202.255.202ZM12 15.012a3.374 3.374 0 0 1-3.357-3.358c0-1.828 1.52-3.34 3.357-3.34 1.837 0 3.349 1.512 3.349 3.34 0 1.846-1.512 3.358-3.349 3.358Zm0-1.363c1.072 0 1.969-.905 1.969-1.995A1.99 1.99 0 0 0 12 9.677c-1.09 0-1.986.896-1.986 1.977 0 1.099.896 1.995 1.986 1.995Z").click()
            sui_page.ele("tag:div@text():Mainnet").click()
            network = sui_page.ele("tag:button@text():Testnet").click()
            logger.info(network)

        except Exception:
            logger.info("钱包已导入，继续执行")


    def data_page(self):
        """
        刷新钱包页面用于解锁钱包功能
        :return:
        """
        print("更新钱包页面，解锁钱包")
        result = self.value
        var = result['data']['http']  # 获取浏览器的控制IP:端口
        self.drive = ChromiumPage(var)  # 使用DP接管浏览器
        sleep(1)
        updatapage = self.drive.new_tab("chrome-extension://cmnogdnidnbojfcknhacgkdboifdpdcg/ui.html")
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
            updatapage.ele("tag:svg@d=M5.5.75A1.75 1.75 0 0 0 3.75 2.5h1.5a.25.25 0 0 1 .25-.25h3c.69 0 1.25.56 1.25 1.25v3a.25.25 0 0 1-.25.25v1.5a1.75 1.75 0 0 0 1.75-1.75v-3A2.75 2.75 0 0 0 8.5.75h-3ZM2.5 5h4a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-.5.5h-4a.5.5 0 0 1-.5-.5v-4a.5.5 0 0 1 .5-.5Zm-2 .5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-4Z")
            updatapage.ele("tag:path@d=M11.112 21.05c-.677 0-1.195-.413-1.353-1.064l-.387-1.643-.281-.097-1.424.879c-.571.36-1.24.273-1.723-.21l-1.221-1.223c-.484-.483-.58-1.151-.211-1.713l.887-1.424-.096-.264-1.644-.387a1.359 1.359 0 0 1-1.063-1.353v-1.74a1.35 1.35 0 0 1 1.063-1.354l1.626-.395.106-.282-.888-1.424c-.37-.562-.273-1.221.21-1.713l1.223-1.23c.474-.476 1.142-.563 1.713-.212l1.424.88.3-.115.386-1.644c.158-.65.676-1.063 1.353-1.063h1.776c.677 0 1.195.413 1.353 1.063l.378 1.644.299.114 1.433-.879c.57-.351 1.23-.263 1.705.211l1.23 1.23c.483.493.571 1.152.211 1.714l-.896 1.424.114.282 1.626.395a1.35 1.35 0 0 1 1.063 1.353v1.74c0 .669-.422 1.196-1.063 1.354l-1.644.387-.105.264.896 1.424c.36.562.273 1.23-.21 1.713l-1.231 1.222c-.483.483-1.143.571-1.714.211l-1.433-.879-.28.097-.379 1.643c-.158.65-.676 1.064-1.353 1.064h-1.776Zm.14-1.371h1.495c.15 0 .229-.062.246-.202l.536-2.18a4.905 4.905 0 0 0 1.406-.58l1.917 1.178c.114.079.22.061.334-.044l1.028-1.037c.105-.097.105-.203.035-.326l-1.178-1.898a6 6 0 0 0 .572-1.406l2.188-.519c.132-.026.202-.105.202-.255v-1.468c0-.158-.061-.228-.202-.255l-2.18-.527c-.14-.571-.395-1.09-.562-1.415l1.169-1.898c.079-.132.079-.238-.027-.343l-1.037-1.02c-.114-.105-.202-.123-.342-.044L14.944 6.6a6.41 6.41 0 0 0-1.415-.57l-.536-2.198c-.017-.14-.097-.202-.246-.202h-1.494c-.15 0-.229.061-.255.202l-.518 2.18c-.528.15-1.064.369-1.442.58L7.14 5.44c-.132-.079-.229-.061-.334.044L5.76 6.504c-.097.105-.106.21-.027.343l1.17 1.898c-.159.325-.423.844-.563 1.415l-2.171.527c-.15.027-.202.097-.202.255v1.468c0 .15.061.229.202.255l2.18.519c.14.536.369 1.037.57 1.406l-1.177 1.898c-.07.123-.061.229.035.326l1.037 1.037c.106.105.22.123.326.044l1.916-1.178c.378.237.879.448 1.415.58l.527 2.18c.026.14.106.202.255.202ZM12 15.012a3.374 3.374 0 0 1-3.357-3.358c0-1.828 1.52-3.34 3.357-3.34 1.837 0 3.349 1.512 3.349 3.34 0 1.846-1.512 3.358-3.349 3.358Zm0-1.363c1.072 0 1.969-.905 1.969-1.995A1.99 1.99 0 0 0 12 9.677c-1.09 0-1.986.896-1.986 1.977 0 1.099.896 1.995 1.986 1.995Z").click()
        try:
            updatapage.ele("tag:div@text():Mainnet").click()
            updatapage.ele("tag:button@text():Testnet").click()
            logger.info("网络修改为Testnet")
        except Exception:
            logger.info("钱包当前网络为测试网，无需更改")



    # def GiveSui(self):
    #     result = self.value()
    #     var = result['data']['http']  # 获取浏览器的控制IP:端口
    #     self.drive = ChromiumPage(var)  #接管浏览器
    #     givesui = self.drive.new_tab("https://faucet.blockbolt.io/")
    #
    #     try:
    #         givesui.ele("tag:input@name=sui_address").input(self.address[self.j])
    #
    #     except Exception:
    #         givesui.get("https://faucet.blockbolt.io/")
    #         givesui.ele("tag:input@name=sui_address").input(self.address[self.j])
    #         givesui.ele("tag:button@text():Give me sui!").click()# 点击输入框
    #         sleep(10)
    #         givesui.get("https://faucet.blockbolt.io/")
    #         print(f"领水次完成，继续执行任务...")

    def stakesui(self):
        result = self.value
        var = result['data']['http']  # 获取浏览器的控制IP:端口
        connect = self.drive = ChromiumPage(var)  #接管浏览器
        stake_page = self.drive.new_tab("https://stake.walrus.site/")
        try:
            stake_page.ele("tag:button@text():Connect Wallet").click()
            suitab = self.drive.wait.new_tab(timeout=10)
            suiwindow = self.drive.get_tab(suitab)
            suiwindow.ele("tag:div@text():Sui Wallet").click()
            sleep(1)

            suitab2 = self.drive.wait.new_tab(timeout=10)
            suiwindow2 = self.drive.get_tab(suitab2)
            sleep(2)
            suiwindow2.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
            try:
                suiwindow2.ele("tag:button@class=appearance-none p-0 bg-transparent border-none cursor-pointer text-steel hover:text-hero-dark ml-auto flex items-center justify-center")
            except Exception:
                logger.info("钱包已解锁无需操作")
        except Exception:
            logger.info("钱包已连接到当前网站，继续执行...")

        """
        触发兑换按钮get wal,并兑换成wal
        """
        stake_page.ele("tag:button@class=justify-center whitespace-nowrap font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950 disabled:pointer-events-none disabled:opacity-50 bg-primaryDark text-primary shadow-sm hover:bg-primaryDark/80 border border-primary/50 hover:border-primary h-8 rounded-md px-3 text-xs flex items-center gap-2").click()
        stake_page.ele("tag:input@class=border-primary/30 focus-visible:ring-secondary flex h-9 w-full rounded-md border bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-neutral-950 placeholder:text-neutral-500 focus-visible:outline-none focus-visible:ring-1 disabled:cursor-not-allowed disabled:opacity-50").input(1)
        sleep(2)
        stake_page.ele("tag:button@text():Exchange").click()

        """
        捕捉弹兑换wal的弹窗，点击确认
        """
        suitab3 = self.drive.wait.new_tab(timeout=8)
        approve = self.drive.get_tab(suitab3)
        try:
             approve.ele("tag:div@text():Unlock Account")
             approve.ele("tag:input@name=password").input(self.password)
        except Exception:
             logger.info("钱包已解锁无需操作")

        try:
            approve.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
            approve.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
        except Exception:
            logger.info("钱包此次无需授权")
        sleep(2)
        """
        查找元素stake质押
        """
        stake_page.get("https://stake.walrus.site")
        stake_page.ele("tag:button@text():Stake").click()
        stake_page.ele("tag:input@type=text").input(1)

        sleep(1)
        try:
            stake_page.ele("tag:button@class=inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-950 disabled:pointer-events-none disabled:opacity-50 bg-secondary/90 text-primaryDark shadow hover:bg-secondary h-9 px-4 py-2").click()
            sleep(2)
            """
            捕捉弹窗，确认质押
            """
            suitab4 = self.drive.wait.new_tab(timeout=5)
            approve2 = self.drive.get_tab(suitab4)
            approve2.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
            print("质押完成!")
        except Exception:
            logger.error("GWL余额不足...")

    def claimnft(self):
        try:
            result = self.value
            var = result['data']['http']  # 获取浏览器的控制IP:端口
            mint = self.drive = ChromiumPage(var)  # 接管浏览器
            self.claim_page = mint.new_tab("https://flatland.walrus.site")
            self.claim_page.ele("tag:button@text():Connect Wallet").click()
            self.claim_page.ele("tag:div@text():Sui Wallet").click()

            suitab5 = self.drive.wait.new_tab(timeout=8)
            suiwindow4 = self.drive.get_tab(suitab5)
            suiwindow4.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
            try:
                self.claim_page.ele(
                "tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
            except Exception:
                logger.info("未找到授权按钮，跳过")
        except Exception as f:
            logger.info("钱包已连接，执行Mint...")

            self.claim_page.ele("tag:button@class=rt-reset rt-BaseButton rt-Button rt-r-size-2 rt-variant-surface").click()
            suitab6 = self.drive.wait.new_tab(timeout=8)
            approve = self.drive.get_tab(suitab6)
            re = approve.ele("tag:button@class=cursor-pointer transition no-underline outline-none group flex flex-row flex-nowrap items-center justify-center gap-2 cursor-pointer text-body font-semibold max-w-full min-w-0 w-full bg-hero-dark text-white border-none hover:bg-hero focus:bg-hero visited:text-white active:text-white/70 disabled:bg-hero-darkest disabled:text-white disabled:opacity-40 h-10 px-5 rounded-xl").click()
            sleep(5)
            if re:
                logger.info("领取成功")
            else:
                logger.info("未领取成功")

    def get_sui_balance(self):
        url = "https://fullnode.testnet.sui.io"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "suix_getAllBalances",
            "params": [self.address[self.j]]  # 确保传递的是当前地址
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            balances = response.json().get("result", [])
            for balance in balances:
                if balance.get("coinType") == "0x2::sui::SUI":
                    total_balance = balance.get("totalBalance")
                    #if total_balance is not None:  # 增加检查
                    total_balance = int(total_balance)
                    adjusted_balance = total_balance / 1000000000
                    #print(f"SUI Adjusted Balance: {adjusted_balance}")
                    return adjusted_balance

                else:
                    print("没找到")
                    return 0

        else:
            logger.error(f"API请求失败: {response.status_code}")

    # def main(self):
        # while self.j < self.number:
        #     self.balance = self.get_sui_balance()
        #     if self.balance > 1:
        #         print("sui余额大于1，可以执行任务..")
        #         print("当前余额为：", self.balance)
        #         self.openbrowser(start,end)
        #         self.sui_wallet()
        #         self.data_page()
        #         #self.GiveSui()
        #         self.stakesui()
        #         self.claimnft()
        #         self.j += 1
        #     else:
        #         self.get_sui_balance()
        #         print("余额不足，前往领水,未完成账号的EVM地址已重新保存至文件:balance_no")
        #         print("当前余额为：",self.balance)
        #         with open("balance_no","a") as  f:
        #             f.write(self.address[self.j]+ "\n")
        #             #self.GiveSui()
        #             self.j += 1
        #             continue


    def main(self):
            #self.openbrowser(start,end)
            #self.sui_wallet()
            #self.data_page()
            #self.GiveSui()
            #self.stakesui()
            self.claimnft()



if __name__ == '__main__':
    password = input("请输入钱包密码：")
    start = int(input("请输入要执行的窗口起始点："))
    end = int(input("请输入要执行的窗口结束点："))
    walrus = Walrus(url="http://127.0.0.1:54345", headers={'Content-Type': 'application/json'}, start = start, end = end,password=password)
    walrus.main()





























