# main_agent.py
from openai import OpenAI   # 1. 大模型客户端
from tool_registry import registry  # 2. 导入我们写好的注册表实例
from function_call import client  # 3. 导入instructor增强客户端

def run(question: str):
    messages = [{"role": "user", "content": question}]

    while True:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=registry.as_openai_tools(),
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            return msg.content

        messages.append(msg)
        for tc in msg.tool_calls:
            result = registry.call(tc.function.name, tc.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

if __name__ == "__main__":
    answer = run("郑州天气怎么样")
    print(f"\n[最终回答] {answer}")