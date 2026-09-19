# code_analyzer.py
from pathlib import Path
from tool_agent import Agent
from tool_registry import ToolRegistry, Tool
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(".").resolve()


def safe_path(rel: str) -> Path:
    p = (ROOT / rel).resolve()
    if not str(p).startswith(str(ROOT)):
        raise ValueError("路径越界")
    return p


def list_python_files(directory: str = ".") -> list[str]:
    return [str(p.relative_to(ROOT)) for p in safe_path(directory).rglob("*.py")]


def read_file(path: str) -> str:
    content = safe_path(path).read_text(encoding="utf-8", errors="ignore")
    # 给 LLM 的内容截一下防止过长
    return content[:5000] + ("\n... (已截断)" if len(content) > 5000 else "")


def count_lines(path: str) -> int:
    return len(safe_path(path).read_text(encoding="utf-8", errors="ignore").splitlines())


def grep(keyword: str, directory: str = ".") -> list[str]:
    results = []
    for p in safe_path(directory).rglob("*.py"):
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if keyword in line:
                rel = p.relative_to(ROOT)
                results.append(f"{rel}:{i}: {line.strip()}")
                if len(results) >= 50:  # 防爆
                    return results
    return results


registry = ToolRegistry()
registry.register(Tool(
    name="list_python_files",
    description="列出目录下所有 .py 文件的相对路径",
    parameters={"type": "object", "properties": {"directory": {"type": "string"}}},
    func=list_python_files,
))
registry.register(Tool(
    name="read_file",
    description="读取文件内容，超过 5000 字符会被截断",
    parameters={
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
    func=read_file,
))
registry.register(Tool(
    name="count_lines",
    description="统计文件行数",
    parameters={
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
    func=count_lines,
))
registry.register(Tool(
    name="grep",
    description="在目录所有 .py 文件中搜索包含指定关键词的行",
    parameters={
        "type": "object",
        "properties": {
            "keyword": {"type": "string"},
            "directory": {"type": "string"},
        },
        "required": ["keyword"],
    },
    func=grep,
))


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

agent = Agent(
    client=client,
    registry=registry,
    system_prompt=(
        "你是一个代码分析助手。使用提供的工具回答关于当前项目的问题。"
        "回答要简洁，基于工具返回的真实数据，不要编造。"
    ),
    max_steps=8,
)

print(agent.run("这个项目有多少个 Python 文件？里面有多少处 TODO？给我列出来"))
