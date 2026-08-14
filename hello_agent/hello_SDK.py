# hello_sdk.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一位表述简洁的 Python 老师。"},
        {"role": "user", "content": "什么是装饰器？"},
    ],
)

print(resp.choices[0].message.content)
print(f"消耗 Token：{resp.usage.total_tokens}")
