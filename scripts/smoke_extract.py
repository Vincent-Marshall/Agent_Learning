"""结构化提取冒烟:直连聊天上游验证 function_calling 路径。

回归测试:修复「DeepSeek 不支持 json_schema 响应格式(400)」后,
用当初报错的那条售后描述跑一遍,确认链路正常。
运行:PYTHONPATH=. ~/mewhelp/.venv/bin/python scripts/smoke_extract.py
"""
import asyncio

from app.api.extract import get_extractor


async def main() -> None:
    ex = get_extractor()
    r = await ex.ainvoke({"text": "我上周买的猫爬架，订单号 MH20260701123，到货就散架了，我要退款"})
    print("订单号:", r.order_id)
    print("诉求:", r.request_type.value)
    print("期望:", r.expected_solution)


if __name__ == "__main__":
    asyncio.run(main())
