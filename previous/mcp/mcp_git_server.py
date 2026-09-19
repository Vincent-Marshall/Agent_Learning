import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("git-inspector")


def _run_git(args: list[str], cwd: Path) -> str:
    try:
        if not cwd.exists():
            return f"【错误】路径不存在：{cwd}"
        if not (cwd / ".git").exists():
            return f"【错误】不是Git仓库，无.git目录：{cwd}"

        startupinfo = None
        if subprocess.os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            stdin=subprocess.DEVNULL,   # 核心！切断继承过来的stdin，防止git等待输入卡死
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW,
            startupinfo=startupinfo
        )
        if result.returncode != 0:
            return f"【Git错误】{result.stderr.strip()}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "【错误】git命令执行超时(10s)"
    except Exception as e:
        return f"【异常】{str(e)}"


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