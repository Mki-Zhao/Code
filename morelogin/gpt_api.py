import logging
import openai

api_key = "sk-b4901c5a74454dc0b1b925461034095b"
url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
def generate_question():
    """
    调用 ChatGPT API 动态生成一个问题。
    你可以根据需要调整 prompt 和参数。
    """
    prompt = "请随机生成一个有趣的问题，内容可以涉及外貌、性格或者生活中的其他方面。"
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-r1",  # 或者使用 "gpt-4" 如果有权限
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

