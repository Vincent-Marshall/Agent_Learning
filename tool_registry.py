# tool_registry.py
import json
from typing import Callable
from pydantic import BaseModel


class Tool(BaseModel):
    name: str
    description: str
    parameters: dict
    func: Callable

    class Config:
        arbitrary_types_allowed = True


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def as_openai_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]

    def call(self, name: str, args_json: str) -> str:
        tool = self._tools.get(name)
        if not tool:
            return json.dumps({"error": f"工具 {name} 不存在"})
        try:
            args = json.loads(args_json)
            result = tool.func(**args)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})


# ==========业务函数实现，写在注册前面==========
def get_weather(city: str):
    fake_data = {"北京": 8, "上海": 15, "广州": 22}
    temp = fake_data.get(city, 20)
    return {"city": city, "temperature": temp}


# 实例化注册表，注册工具
registry = ToolRegistry()

registry.register(Tool(
    name="get_weather",
    description="查询指定城市当前天气",
    parameters={
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
    func=get_weather,
))

registry.register(Tool(
    name="get_stock_price",
    description="查询指定股票代码的实时价格",
    parameters={
        "type": "object",
        "properties": {"symbol": {"type": "string"}},
        "required": ["symbol"],
    },
    func=lambda symbol: {"symbol": symbol, "price": 150.23},
))