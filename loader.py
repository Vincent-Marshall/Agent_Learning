# loader.py
from pathlib import Path
from pypdf import PdfReader


def load_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def load_docs(directory: Path) -> list[dict]:
    """返回 [{source, text}, ...]"""
    docs = []
    for path in directory.rglob("*"):
        if path.suffix == ".md":
            docs.append({"source": str(path), "text": load_markdown(path)})
        elif path.suffix == ".pdf":
            docs.append({"source": str(path), "text": load_pdf(path)})
    return docs
