# hello_raw.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

resp = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json",
    },
    json={
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "用一句话解释什么是闭包"}
        ],
    },
    timeout=30,
)

data = resp.json()
print(data["choices"][0]["message"]["content"])
