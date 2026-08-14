# tool_registry.py
import json
import logging
import threading
from typing import Callable, Optional, Any
from pydantic import BaseModel, ValidationError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


class Tool(BaseModel):
    name: str
    description: str
    parameters: dict
    func: Callable
    args_model: Optional[type[BaseModel]] = None
    # 新增：工具超时时间，单位秒；None代表不设置超时
    timeout: Optional[float] = None

    class Config:
        arbitrary_types_allowed = True


def _run_func_in_thread(func: Callable, kwargs: dict, result_box: dict):
    """线程包装，用来实现同步函数超时"""
    try:
        result_box["result"] = func(**kwargs)
    except Exception as e:
        result_box["exception"] = e


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
            err_msg = f"工具 {name} 不存在"
            logger.error(err_msg)
            return json.dumps({"error": err_msg}, ensure_ascii=False)

        # 日志：记录工具调用原始输入
        logger.info(f"[工具调用] name={name}, raw_args={args_json}")

        # 1、解析JSON参数
        try:
            args = json.loads(args_json)
        except json.JSONDecodeError as e:
            err_msg = f"参数JSON解析失败: {str(e)}"
            logger.error(err_msg)
            return json.dumps({"error": err_msg}, ensure_ascii=False)

        # 2、Pydantic参数校验
        if tool.args_model is not None:
            try:
                validated_args = tool.args_model(**args)
                args = validated_args.model_dump()
            except ValidationError as e:
                err_msg = f"参数校验失败: {str(e)}"
                logger.warning(err_msg)
                return json.dumps({"error": err_msg}, ensure_ascii=False)

        # 3、执行工具，带超时控制
        try:
            if tool.timeout is not None:
                # 开启线程执行业务函数，实现超时
                res_box: dict[str, Any] = {}
                t = threading.Thread(
                    target=_run_func_in_thread,
                    args=(tool.func, args, res_box)
                )
                t.start()
                t.join(timeout=tool.timeout)
                if t.is_alive():
                    # 超时！线程还在跑
                    err_msg = f"工具执行超时({tool.timeout}s)"
                    logger.error(err_msg)
                    return json.dumps({"error": err_msg}, ensure_ascii=False)
                if "exception" in res_box:
                    raise res_box["exception"]
                result = res_box["result"]
            else:
                # 不设置超时，直接执行
                result = tool.func(**args)

            ret_json = json.dumps(result, ensure_ascii=False, default=str)
            logger.info(f"[工具返回] name={name}, output={ret_json}")
            return ret_json

        except Exception as e:
            err_msg = f"工具执行异常: {str(e)}"
            logger.exception(err_msg)
            return json.dumps({"error": err_msg}, ensure_ascii=False)


# ====================参数模型====================
class WeatherArgs(BaseModel):
    city: str


class StockArgs(BaseModel):
    symbol: str


# ==========业务函数==========
def get_weather(city: str):
    fake_data = {"北京": 8, "上海": 15, "广州": 22}
    temp = fake_data.get(city, 20)
    return {"city": city, "temperature": temp}


def get_stock_price(symbol: str):
    return {"symbol": symbol, "price": 150.23}


# 模拟卡死的坏工具，用来测试超时效果
def slow_bad_tool():
    import time
    time.sleep(10)  # 休眠10秒模拟接口卡死
    return {"ok": True}


registry = ToolRegistry()

# 注册工具，设置timeout秒
registry.register(Tool(
    name="get_weather",
    description="查询指定城市当前天气",
    parameters={
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
    func=get_weather,
    args_model=WeatherArgs,
    timeout=5.0  # 5秒超时
))

registry.register(Tool(
    name="get_stock_price",
    description="查询指定股票代码的实时价格",
    parameters={
        "type": "object",
        "properties": {"symbol": {"type": "string"}},
        "required": ["symbol"],
    },
    func=get_stock_price,
    args_model=StockArgs,
    timeout=3.0
))

# 测试超时工具，设置2秒超时，函数sleep10秒，会触发超时
registry.register(Tool(
    name="slow_bad_tool",
    description="测试超时",
    parameters={"type": "object", "properties": {}, "required": []},
    func=slow_bad_tool,
    timeout=2.0
))


if __name__ == "__main__":
    print("===正常调用天气===")
    print(registry.call("get_weather", json.dumps({"city": "北京"})))

    print("\n===测试超时工具===")
    print(registry.call("slow_bad_tool", json.dumps({})))