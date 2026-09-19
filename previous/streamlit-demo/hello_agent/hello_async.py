# hello_async.py
import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

async def ask(question: str) -> str:
    resp = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": question}],
    )
    return resp.choices[0].message.content

async def main():
    questions = [
        "用一句话解释什么是 异步",
        "用一句话解释什么是 同步",
        "用一句话解释什么是 高并发",
    ]
    results = await asyncio.gather(*[ask(q) for q in questions])
    for q, r in zip(questions, results):
        print(f"Q: {q}\nA: {r}\n")

asyncio.run(main())
