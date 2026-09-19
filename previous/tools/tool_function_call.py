# function_call.py
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


# 真正的业务函数
def get_weather(city: str, unit: str = "celsius") -> dict:
    # 实际项目里这里会调气象 API
    fake_data = {"北京": 8, "上海": 15, "广州": 22}
    temp = fake_data.get(city, 20)
    if unit == "fahrenheit":
        temp = temp * 9 / 5 + 32
    return {"city": city, "temperature": temp, "unit": unit, "condition": "晴"}


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市当前的天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["city"],
            },
        },
    }
]


def ask(question: str):
    messages = [{"role": "user", "content": question}]

    # 第一次调用
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
    )
    msg = resp.choices[0].message

    # 如果模型决定调用工具
    if msg.tool_calls:
        # 把模型的工具调用意图加入 messages
        messages.append(msg)

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            if tc.function.name == "get_weather":
                result = get_weather(**args)
            else:
                result = {"error": f"未知函数 {tc.function.name}"}

            # 把工具执行结果以 tool 角色塞回
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

        # 第二次调用：基于工具结果生成最终回答
        final = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
        )
        return final.choices[0].message.content
    else:
        # 模型直接回答，没有调用工具
        return msg.content


if __name__ == "__main__":
    print(ask("你好啊"))  # 这种不会触发工具
    print(ask("北京今天天气怎么样？"))
    print(ask("郑州今天天气怎么样？")) # fake_data里没有郑州，会返回默认20度
    
