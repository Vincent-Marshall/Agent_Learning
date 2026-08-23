from openai import OpenAI
from tool_registry import registry
import logging
import httpx

logging.basicConfig(level=logging.INFO, format="%(message)s")


def ollama_agent_run(question: str, max_steps: int = 8):
    # trust_env=False：不读取系统代理环境变量，解决本地127.0.0.1被代理劫持
    http_client = httpx.Client(trust_env=False)
    client = OpenAI(
        base_url="http://127.0.0.1:11434/v1",
        api_key="dummy",
        http_client=http_client
    )
    model_name = "football-coach"

    # 不传入system，复用Modelfile内置system prompt
    messages = [
        {"role": "user", "content": question}
    ]

    tools = registry.as_openai_tools()

    for step in range(max_steps):
        logging.info(f"\n----- step {step+1} -----")
        resp = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.3,
            stream=False
        )
        msg = resp.choices[0].message

        # 无工具调用，返回最终回答
        if not msg.tool_calls:
            logging.info(f"[最终输出] {msg.content}")
            return msg.content

        messages.append(msg.model_dump())

        for tc in msg.tool_calls:
            logging.info(f"调用工具：{tc.function.name}")
            logging.info(f"工具参数：{tc.function.arguments}")

            tool_out = registry.call(tc.function.name, tc.function.arguments)
            logging.info(f"工具返回：{tool_out}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_out
            })

    return f"达到最大轮次 {max_steps}，任务未完成"


if __name__ == "__main__":
    res = ollama_agent_run("帮我查询北京的气温")
    print("\n==== Answer ====")
    print(res)