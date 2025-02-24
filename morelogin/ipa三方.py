import logging

import openai

openai.api_key = "sk-zk23f2635a6fccedc7fe76c74f3b6326a9f67a9b9a2451b0"  # 替换成你的 API 密钥
openai.api_base = "https://api.zhizengzeng.com/v1/"
def generate_question():
    """
    调用 ChatGPT API 动态生成一个问题。
    你可以根据需要调整 prompt 和参数。
    """
    prompt = "请随机生成一个有趣的问题，内容可以涉及外貌、性格或者生活中的其他方面。"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 或者使用 "gpt-4" 如果有权限
            messages=[
                {"role": "system", "content": "你是一个创意无限的问答助手，每次需要生成一个独特且有趣的问题。"},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0,  # 温度越高生成内容越随机
            max_tokens=50     # 根据需要控制生成的长度
        )
        question = response.choices[0].message['content'].strip()
        # 确保问题以问号结尾，并添加换行符用于模拟回车
        if not question.endswith("？"):
            question += "？"
        return question + "\n"
    except Exception as e:
        logging.error(f"调用 ChatGPT API 生成问题失败：{e}")
        # 如果调用失败，可以返回一个默认问题
        return "你觉得我好看吗？\n"
print(generate_question())