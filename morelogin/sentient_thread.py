import base64
import hashlib
import json
import random
import string
import time
from time import sleep
import openai
import requests
from concurrent.futures import ThreadPoolExecutor
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


# -------------------------------
# 1. 获取所有环境信息
# -------------------------------
env_list_url = f"{BASEURL}/api/env/page"
env_list_data = {
    "pageNo": 1,
    "pageSize": 100
}
try:
    response = requests.post(env_list_url, headers=requestHeader(), json=env_list_data)
    response.raise_for_status()
    response_data = response.json()
except requests.exceptions.RequestException as e:
    print(f"获取环境列表请求错误: {e}")
    exit()
except json.JSONDecodeError:
    print("错误：环境列表接口返回的不是 JSON 格式")
    exit()

# 反转列表（如有需要）并构造环境列表
data_list = response_data["data"]["dataList"][::-1]
envs = []
for item in data_list:
    envs.append({
        "id": item["id"],
        "envName": item["envName"]
    })

# 打乱列表，方便后面多线程调用时是以随机顺序执行
random.shuffle(envs)

if not envs:
    print("没有获取到任何环境信息")
    exit()

print("总共获取到的环境数量：", len(envs))

# -------------------------------
# 2. 定义辅助函数
# -------------------------------
openai.api_key = "sk-zk23f2635a6fccedc7fe76c74f3b6326a9f67a9b9a2451b0"  # 替换成你的 API 密钥
openai.api_base = "https://api.zhizengzeng.com/v1/"


def generate_question():
    questions = [
        "你如何看待人工智能对未来生活的深远影响？",
        "你认为哪种品质最能定义一个人的成功？",
        "当代社会中，你觉得最需要改变的是什么？",
        "你人生中最难忘的一次经历是什么？",
        "你认为真正的友情应具备哪些特质？",
        "如果可以改变历史上的一个事件，你会选择哪个？",
        "你觉得人类最核心的价值观是什么？",
        "你如何看待科技进步与自然环境之间的平衡？",
        "当下社会面临的最大挑战是什么？",
        "你认为艺术在社会变革中起到了怎样的作用？",
        "在教育领域，你最希望看到哪些改进？",
        "你如何理解工作的意义与乐趣？",
        "你觉得如何才能更好地平衡生活与工作？",
        "如果有机会环游世界，你最想去哪个地方，为什么？",
        "你认为未来人类发展的主要方向是什么？",
        "你如何看待传统文化与现代文化的碰撞与融合？",
        "你觉得家庭在个人成长中扮演了怎样的重要角色？",
        "你认为怎样的领导风格更能激发团队的潜力？",
        "你如何看待人与人之间沟通中存在的障碍？",
        "在未来十年内，你认为哪些科技创新最有可能改变世界？"
    ]
    return random.choice(questions) + "\n"


def run_js_with_retry(sentient, js_code, env_name, retries=1, delay=5):
    """
    尝试执行 js_code，如执行失败则刷新页面重试一次。
    """
    try:
        sentient.run_js(js_code)
    except Exception as e:
        print(f"【{env_name}】执行 js_code 出错: {e}，等待 {delay} 秒后重试...")
        sleep(delay)
        sentient.refresh()
        sleep(delay)
        sentient.run_js(js_code)
        print(f"【{env_name}】刷新后 js_code 执行成功。")


def random_interaction(sentient):
    """
    针对传入的 sentient（标签页对象）执行一次提问与投票操作
    """
    text_area_selector = "tag:textarea@class=w-full resize-none rounded-2xl bg-background px-4 pt-3 pb-3 font-normal text-foreground outline-none focus:outline-none focus:ring-0 focus-visible:ring-0"
    text_area = sentient.ele(text_area_selector, timeout=10)
    re_text = generate_question()
    sleep(2)
    text_area.input(re_text)
    # 主用投票 xpath 列表
    primary_xpaths = [
        "(//div[contains(@class,'my-1 flex')]//button)[1]",
        "(//div[contains(@class,'my-1 flex')]//button)[2]",
        "(//div[contains(@class,'my-1 flex')]//button)[3]",
        "(//div[contains(@class,'my-1 flex')]//button)[4]"
    ]
    # 备用投票 xpath 列表（点击时不检测显示状态）
    alternative_xpaths = [
        "/html/body/div/main/div/div/div[3]/div/div[2]/div/div[1]/div[1]/div/div/div/button[1]/span[2]",
        "/html/body/div/main/div/div/div[3]/div/div[2]/div/div[1]/div[1]/div/div/div/button[2]/span[2]"
    ]

    selected_primary = random.choice(primary_xpaths)
    try:
        if sentient.wait.ele_displayed("xpath:" + selected_primary, timeout=50):
            sentient.ele("xpath:" + selected_primary).click()
            print("主用点击成功")
        else:
            raise Exception("主要元素未检测到")
    except Exception as e:
        selected_alternative = random.choice(alternative_xpaths)
        try:
            sentient.ele("xpath:" + selected_alternative).click()
            print("备用点击成功")
        except Exception as e_alt:
            print("备用点击也失败，错误信息：", e_alt)
            raise Exception("交互操作均失败")


def close_environment(env_id):
    close_env_url = f"{BASEURL}/api/env/close"
    close_env_data = {"envId": env_id}
    try:
        response = requests.post(close_env_url, headers=requestHeader(), json=close_env_data)
        response.raise_for_status()
        print(f"环境 {env_id} 已关闭。")
    except Exception as e:
        print(f"关闭环境 {env_id} 失败: {e}")


def browser_worker(env):
    env_id = env["id"]
    env_name = env["envName"]
    print(f"【{env_name}】开始启动……")
    start_env_url = f"{BASEURL}/api/env/start"
    start_env_data = {"envId": env_id}
    driver = None
    try:
        response = requests.post(start_env_url, headers=requestHeader(), json=start_env_data)
        response.raise_for_status()
        response_data = response.json()
    except Exception as e:
        print(f"【{env_name}】启动环境请求错误: {e}")
        return

    debug_port = response_data.get("data", {}).get("debugPort")
    if not debug_port:
        print(f"【{env_name}】没有获取到调试端口，无法继续操作。")
        return

    try:
        driver = ChromiumPage(f"127.0.0.1:{debug_port}")
        sentient = driver.new_tab("https://dobby-arena.sentient.xyz/")
        sleep(10)
        # 钱包链接操作：先执行 js_code，如失败则刷新页面重试
        js_code = '''
                  document.querySelector("body > div > div > div > button").click();
                  '''
        run_js_with_retry(sentient, js_code, env_name)

        # 接着执行钱包链接操作
        try:
            sentient.ele("tag:button@text():Continue with a wallet").click()
            sentient.ele(
                "tag:button@class=t-btn t-btn-tertiary w3a--rounded-full size-md w3a--w-full w3a--rounded-xl w3a--size-xl !w3a--justify-between w3a--items-center wallet-btn").click()
        except Exception:
            print(f"【{env_name}】钱包已链接，无需再次操作。")
        try:
            wallet = driver.wait.new_tab(timeout=10)
            okx_wallet = driver.get_tab(wallet)
            okx_wallet.ele("tag:input@class=okui-input-input _input_11p2x_8").input("zm960810")
            okx_wallet.ele("tag:span@text():Unlock").click()
            okx_wallet.ele('xpath://*[@id="app"]/div/div/div/div/div[5]/div[2]/button[2]').click()
        except Exception:
            print(f"【{env_name}】钱包已链接或弹窗不存在，无需处理。")
        num_times = random.randint(5, 10)
        print(f"【{env_name}】窗口开始随机执行 {num_times} 次交互操作。")
        for i in range(num_times):
            print(f"【{env_name}】执行第 {i + 1} 次")
            random_interaction(sentient)
            sleep(random.uniform(1, 3))
    except Exception as e:
        print(f"【{env_name}】窗口内操作发生错误: {e}")
        with open("project/error_env.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 环境ID: {env_id}，环境名称: {env_name} 出现错误: {e}\n")
    # finally:
    #     if driver:
    #         try:
    #             driver.quit()  # 或者 driver.close()，根据 DrissionPage 实现选择
    #             print(f"【{env_name}】浏览器窗口已关闭。")
    #         except Exception as e_close:
    #             print(f"【{env_name}】关闭浏览器窗口时发生错误: {e_close}")
    #     # 关闭整个环境
        close_environment(env_id)


# -------------------------------
# 3. 分批并发运行所有环境，每批 4 个
# -------------------------------
def process_all_envs(env_list, batch_size=4):
    total = len(env_list)
    for i in range(0, total, batch_size):
        batch = env_list[i:i + batch_size]
        print(f"正在处理第 {i + 1} 到 {i + len(batch)} 个环境...")
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [executor.submit(browser_worker, env) for env in batch]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print("批次中某个环境执行出错:", e)
        print(f"第 {i + 1} 到 {i + len(batch)} 个环境处理完毕。\n")
    print("所有环境操作均已完成。")


if __name__ == "__main__":
    process_all_envs(envs, batch_size=4)
