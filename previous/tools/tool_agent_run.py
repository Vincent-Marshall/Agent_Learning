# tool_agent_run.py
from tool_agent import Agent
from tool_registry import registry
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)
# 这里注册你的工具函数，比如get_weather

agent = Agent(client=client, registry=registry, max_steps=8)
answer = agent.run("查询北京天气")
print(answer)