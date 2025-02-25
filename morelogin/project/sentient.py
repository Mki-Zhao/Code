import base64
import hashlib
import json
import random
import string
import time
from time import sleep
from loguru import logger
import requests
from DrissionPage import ChromiumPage
from concurrent.futures import ThreadPoolExecutor, as_completed

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

'''
获取所有环境ID
'''
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

# 反转列表并构造环境列表
data_list = response_data["data"]["dataList"][::-1]
envs = []
for item in data_list:
    envs.append({
        "id": item["id"],
        "envName": item["envName"]
    })
random.shuffle(envs)    #反转列表

if not envs:
    print("没有获取到任何环境信息")
    exit()

print("总共获取到的环境数量：", len(envs))

#提问
def generate_question():
    questions = [
        "What do you usually have for breakfast?",
        "What is your favorite home-cooked dish?",
        "How do you usually spend your weekends?",
        "Do you enjoy taking walks to relax?",
        "What type of music do you prefer for relaxation?",
        "Do you prefer cooking at home or dining out?",
        "Do you have any special hobbies?",
        "How do you maintain a regular exercise routine?",
        "Are you a morning person or a night owl?",
        "What is your favorite TV show or movie?",
        "What kind of books do you enjoy reading?",
        "How important is it for you to meet up with friends?",
        "How do you typically cope with stress?",
        "What is your dream travel destination?",
        "What is your ideal way to spend a vacation?",
        "Do you enjoy trying old_code restaurants?",
        "Are you fond of keeping pets, and why?",
        "How important is a tidy home to you?",
        "What is your favorite leisure activity?",
        "Do you prefer coffee or tea to wake you up?",
        "Which city do you find the most vibrant, and why?",
        "What do you think is the most interesting feature of urban life?",
        "How does city life differ from rural life in your opinion?",
        "What is your favorite landmark in your city?",
        "Do you think public transportation in your city is efficient?",
        "What improvements would you like to see in your city?",
        "How do you think urban planning affects your daily life?",
        "What is your favorite café or restaurant in your city?",
        "How safe do you feel in your city at night?",
        "What do you think makes a city livable?",
        "What is 2 + 2?",
        "What is 10 minus 3?",
        "What is 7 times 8?",
        "What is the square root of 16?",
        "What is 100 divided by 4?",
        "What is 15 plus 25?",
        "If you have 3 apples and buy 2 more, how many apples do you have?",
        "What is 12 times 12?",
        "What is 50 minus 15?",
        "What is the sum of 20 and 30?",
        "What is your favorite season, and why?",
        "Do you prefer mornings or evenings?",
        "What is your favorite color?",
        "If you could have any superpower, what would it be?",
        "What is one skill you wish to learn?",
        "Do you enjoy solving puzzles or riddles?",
        "What is the last movie you watched?",
        "What is your favorite dessert?",
        "Do you prefer the beach or the mountains?",
        "What is your favorite sport?",
        "What is 9 minus 4?",
        "What is 3 multiplied by 7?",
        "What is 81 divided by 9?",
        "What is the sum of 45 and 55?",
        "What is half of 100?",
        "What is 8 plus 6?",
        "What is 20 divided by 5?",
        "What is 14 times 2?",
        "What is the difference between 30 and 10?",
        "What is 6 squared?",
        "How do you deal with stress on busy days?",
        "What is one thing that makes you smile every day?",
        "Do you have a pet? Tell me about it.",
        "What is your favorite memory from childhood?",
        "What hobby would you like to pick up in the future?",
        "What is one goal you have for this year?",
        "What motivates you to get out of bed in the morning?",
        "How do you relax after a challenging day?",
        "What do you think is the key to a happy life?",
        "What small pleasure do you look forward to daily?",
        "How do you think technology has changed urban life?",
        "What do you think about the increasing cost of living in cities?",
        "How do you feel about the noise levels in urban areas?",
        "What is your opinion on public parks in cities?",
        "How important is cultural diversity in a city?",
        "Do you think cities should invest more in green spaces?",
        "How do you feel about the traffic congestion in your city?",
        "What role do you think art plays in urban environments?",
        "How do you think cities can become more sustainable?",
        "What is the most important quality of a modern city?",
        "If you could solve one world problem, what would it be?",
        "What do you think is the meaning of life?",
        "How do you define success?",
        "What does freedom mean to you?",
        "How do you balance ambition and contentment?",
        "What is one thing you believe is essential for progress?",
        "Do you think technology will ever surpass human intelligence?",
        "How important is creativity in everyday life?",
        "What role does education play in society?",
        "If you could visit any place in the world, where would you go?",
        "What is your favorite type of cuisine?",
        "Do you prefer winter or summer vacations?",
        "What is your favorite outdoor activity?",
        "If you could meet any historical figure, who would it be?",
        "What is your favorite form of art?",
        "How do you prefer to spend your free time on a rainy day?",
        "What is your favorite board game or card game?",
        "Do you enjoy cooking? What dish do you love making?",
        "What is one thing you can’t live without?",
        "How do you stay organized throughout the week?",
        "What is one habit you would like to break?",
        "Do you prefer reading fiction or non-fiction?",
        "What is your favorite way to exercise?",
        "How do you like to celebrate your achievements?",
        "What is your favorite quote or saying?",
        "If you had a day all to yourself, how would you spend it?",
        "What is one challenge you recently overcame?",
        "How do you feel about trying old_code things?",
        "What is one thing you are grateful for today?"
    ]

    return random.choice(questions) + "\n" #随机抽取一个问题

#关闭浏览器
def close_environment(env_id,env_name):
    close_env_url = f"{BASEURL}/api/env/close"
    close_env_data = {"envId": env_id}
    try:
        response = requests.post(close_env_url, headers=requestHeader(), json=close_env_data)
        response.raise_for_status()
        logger.info(f"环境【 {env_name}】 已关闭。")
    except Exception as e:
        logger.info(f"关闭环境 【{env_name}】 失败: {e}")

#对浏览器进行操作
def single_env_test(env):
    env_id = env["id"]
    env_name = env["envName"]
    print(f"【{env_name}】开始执行")
    start_env_url = f"{BASEURL}/api/env/start"
    start_env_data = {"envId": env_id}
    try:
        response = requests.post(start_env_url, headers=requestHeader(), json=start_env_data)
        response.raise_for_status()
        response_data = response.json()
    except Exception as e:
        logger.info(f"【{env_name}】启动环境请求错误: {e}")
        return

    debug_port = response_data.get("data", {}).get("debugPort")
    if not debug_port:
        logger.info(f"【{env_name}】没有获取到调试端口，无法继续操作。")
        return

    # 新建浏览器窗口并打开目标页面
    driver = ChromiumPage(f"127.0.0.1:{debug_port}")
    sentient = driver.new_tab("https://dobby-arena.sentient.xyz/")
    sleep(15)   #等待加载

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
        with open ("error_env.log", 'a') as f:
            f.write(env_name + "\n")
        logger.info(f"【{env_name}】任务过程中出现错误，提问超过上限/网络问题页面没有更新，已保存环境名称至error_env.log文件")
        close_environment(env_id, env_name)


'''
多线程入口：将所有环境放入线程池，每次执行4个环境
'''
if __name__ == "__main__":
    max_workers = 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(single_env_test, env) for env in envs]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("任务异常：", e)
    print("所有任务已完成。")
