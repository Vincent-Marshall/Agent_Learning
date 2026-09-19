import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_git_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            for t in tools.tools:
                print(f"- {t.name}: {t.description}")

            # 增加超时保护，最多12秒，避免永久卡死
            try:
                result = await asyncio.wait_for(
                    session.call_tool(
                        "git_status",
                        {"repo_path": r"D:\\Python_Learning\\first_course"},
                    ),
                    timeout=12
                )
                print("\n====工具返回结果====")
                print(result.content[0].text)
            except asyncio.TimeoutError:
                print("\n!!!调用工具超时！MCP服务端没有返回响应")


asyncio.run(main())