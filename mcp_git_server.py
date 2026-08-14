# mcp_git_server.py
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("git-inspector")


def _run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        return f"错误：{result.stderr.strip()}"
    return result.stdout.strip()


@mcp.tool()
def git_status(repo_path: str) -> str:
    """查看指定 Git 仓库的工作区状态。"""
    return _run_git(["status", "--short"], Path(repo_path))


@mcp.tool()
def git_log(repo_path: str, limit: int = 10) -> str:
    """查看最近的 N 条提交记录。"""
    return _run_git(["log", f"-{limit}", "--oneline"], Path(repo_path))


@mcp.tool()
def git_diff(repo_path: str) -> str:
    """查看当前未暂存的改动。"""
    return _run_git(["diff"], Path(repo_path))


@mcp.tool()
def current_branch(repo_path: str) -> str:
    """查看当前分支名。"""
    return _run_git(["branch", "--show-current"], Path(repo_path))


if __name__ == "__main__":
    mcp.run()
