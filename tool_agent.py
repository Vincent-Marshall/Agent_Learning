# agent.py
import json
import logging
from openai import OpenAI
from pydantic import BaseModel
from tool_registry import ToolRegistry  # 沿用上一篇的注册表

logging.basicConfig(level=logging.INFO, format="%(message)s")


class Agent:
    def __init__(
        self,
        client: OpenAI,
        registry: ToolRegistry,
        model: str = "deepseek-chat",
        system_prompt: str = "你是一个智能助手，必要时调用工具完成任务。",
        max_steps: int = 10,
    ):
        self.client = client
        self.registry = registry
        self.model = model
        self.system_prompt = system_prompt
        self.max_steps = max_steps

    def run(self, question: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question},
        ]

        for step in range(self.max_steps):
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.registry.as_openai_tools(),
            )
            msg = resp.choices[0].message

            if not msg.tool_calls:
                logging.info(f"[step {step}] 最终回答：{msg.content}")
                return msg.content

            messages.append(msg)
            for tc in msg.tool_calls:
                logging.info(f"[step {step}] 调用 {tc.function.name}({tc.function.arguments})")
                result = self.registry.call(tc.function.name, tc.function.arguments)
                logging.info(f"[step {step}] 结果：{result[:120]}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        return f"超出最大步数 {self.max_steps}，未能完成任务"
