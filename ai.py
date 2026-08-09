# ai.py
import os
from typing import Iterable
from openai import OpenAI
from dotenv import load_dotenv
import instructor
from pydantic import BaseModel

load_dotenv()

# 原生DeepSeek客户端
raw_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)
# 用instructor增强客户端，支持response_model结构化输出
client = instructor.from_openai(raw_client)

DEFAULT_MODEL = "deepseek-chat"

# 原有普通非流式对话（保留兼容旧业务）
def chat(messages: list[dict], model: str = DEFAULT_MODEL,** kwargs) -> str:
    resp = raw_client.chat.completions.create(model=model, messages=messages, **kwargs)
    return resp.choices[0].message.content

# 原有流式对话（保留前端打字预览能力）
def chat_stream(messages: list[dict], model: str = DEFAULT_MODEL, **kwargs) -> Iterable:
    stream = raw_client.chat.completions.create(
        model=model, messages=messages, stream=True,** kwargs
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

# 新增：instructor结构化专用非流式方法（核心改造点）
def chat_struct(
    messages: list[dict],
    response_model: type[BaseModel],
    model: str = DEFAULT_MODEL,
    max_retries: int = 3,
    **kwargs
):
    """
    结构化输出专用方法
    :param response_model: 自定义Pydantic模型
    :param max_retries: 校验失败自动重试次数
    :return: Pydantic实例对象
    """
    result = client.chat.completions.create(
        model=model,
        messages=messages,
        response_model=response_model,
        max_retries=max_retries,
        **kwargs
    )
    return result