from openai import OpenAI
import httpx

# 关键：trust_env=False，禁止读取系统代理
transport = httpx.HTTPTransport(trust_env=False)

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    timeout=15,
    http_client=httpx.Client(transport=transport)
)

try:
    resp = client.chat.completions.create(
        model="qwen2.5:7b",
        messages=[{"role": "user", "content": "你是谁？"}]
    )
    print(resp.choices[0].message.content)
except Exception as e:
    print("请求出错：", e)
