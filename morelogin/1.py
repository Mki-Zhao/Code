import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from DrissionPage import ChromiumPage
from time import sleep
import requests

base_url = "http://127.0.0.1:54345"
headers = {'Content-Type': 'application/json'}
max_concurrent_tasks = 5

def get_environment_ids():
    """获取所有环境ID"""
    json_data = {"page": 0, "pageSize": 100}
    try:
        resp = requests.post(f"{base_url}/browser/list", json=json_data, headers=headers)
        resp.raise_for_status()
        res = resp.json()
        idt = [item['id'] for item in res['data']['list']]
        random.shuffle(idt)
        return idt
    except Exception as e:
        logger.error(f"获取环境ID失败，错误: {e}")
        return []

env_id = get_environment_ids()

def open_browser(environment_id):
    """打开指定环境ID的浏览器，并返回独立的浏览器实例和环境名称"""
    env_id = get_environment_ids()
    json_data = {"id": f"136ba288fae54180a36fe61da246a725"}
    try:
        resp = requests.post(f"{base_url}/browser/open", json=json_data, headers=headers)
        resp.raise_for_status()
        result = resp.json()
        env_name = result['data']['name']  # 当前环境名称
        logger.info(f"浏览器打开成功，环境名称：{env_name}")
        return result, env_name
    except Exception as e:
        logger.error(f"打开浏览器失败，环境ID: {environment_id}，错误: {e}")
        return None, None

    driver = ChromiumPage(f"127.0.0.1:{debug_port}")
    sentient = driver.new_tab("https://dobby-arena.sentient.xyz/")
    sleep(12)   #等待加载

    # 钱包链接操作
    try:
        js_code = '''
                  document.querySelector("body > div > div > div > button").click();
                  '''   #页面链接钱包按钮
        sentient.run_js(js_code)
        sentient.ele("tag:button@text():Continue with a wallet").click()
        sentient.ele("tag:button@class=t-btn t-btn-tertiary w3a--rounded-full size-md w3a--w-full w3a--rounded-xl w3a--size-xl !w3a--justify-between w3a--items-center wallet-btn").click()
    except Exception:
        logger.info(f"【{env_name}】钱包已链接。")
    try:
        wallet = driver.wait.new_tab(timeout=10)
        okx_wallet = driver.get_tab(wallet)
        okx_wallet.ele("tag:input@class=okui-input-input _input_11p2x_8").input("zm960810")
        okx_wallet.ele("tag:span@text():Unlock").click()
        okx_wallet.ele('xpath://*[@id="app"]/div/div/div/div/div[5]/div[2]/button[2]').click()  #链接按钮connet
    except Exception:
        logger.info(f"【{env_name}】登陆成功。")

    # 执行多次随机交互（输入问题）
    try:
        # 随机决定执行次数（1～7 次）
        num_times = random.randint(1, 6)
        print(f"【{env_name}】本次任务将执行 {num_times} 次随机交互。")
        for i in range(num_times):
            # 定位输入框并输入随机问题
            text_area_selector = "tag:textarea@class=w-full resize-none rounded-2xl bg-background px-4 pt-3 pb-3 font-normal text-foreground outline-none focus:outline-none focus:ring-0 focus-visible:ring-0"
            text_area = sentient.ele(text_area_selector, timeout=10)
            re_text = generate_question()
            sleep(2)
            text_area.input(re_text)
            logger.info(f"【{env_name}】第 {i + 1} 次已输入问题：{re_text.strip()}")

            # 随机选择一个按钮 xpath 并执行点击操作
            primary_xpaths = [
                "(//div[contains(@class,'my-1 flex')]//button)[1]",
                "(//div[contains(@class,'my-1 flex')]//button)[2]",
                "(//div[contains(@class,'my-1 flex')]//button)[3]",
                "(//div[contains(@class,'my-1 flex')]//button)[4]"
            ]
            selected_primary = random.choice(primary_xpaths)
            sleep(3)
            if sentient.wait.ele_displayed("xpath:" + selected_primary):
                wait_time = random.uniform(40, 50)  # 随机等待40-50秒（浮点数）
                time.sleep(wait_time)
                sentient.ele("xpath:" + selected_primary).click()
                print(f"【{env_name}】第 {i + 1} 次任务执行完成。")
            else:
                print(f"【{env_name}】第 {i + 1} 次任务未检测到按钮。")
            sleep(2)
        logger.info(f"【{env_name}】所有任务执行完成，关闭窗口")
        close_environment(env_id, env_name)
    except Exception:
        with open ("project/error_env.log", 'a') as f:
            f.write(env_name + "\n")
        logger.info(f"【{env_name}】任务过程中出现错误，提问超过上限/网络问题页面没有更新，已保存环境名称至error_env.log文件")
        close_environment(env_id, env_name)


'''
多线程入口：将所有环境放入线程池，每次执行4个环境
'''
if __name__ == "__main__":
    max_workers = 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(open_browser, env) for env in env_id]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("任务异常：", e)
    print("所有任务已完成。")

