from pathlib import Path

# 当前文件所在目录下的 prompts 文件夹
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    """
    读取prompts目录下 {name}.md 模板文件
    :param name: 模板文件名，不带 .md
    :return: 原始模板字符串，可以继续调用 .format(xxx=yyy)填充变量
    """
    file_path = PROMPTS_DIR / f"{name}.md"
    return file_path.read_text(encoding="utf-8")