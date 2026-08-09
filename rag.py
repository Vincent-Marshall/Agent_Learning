# rag.py
from ai import chat  # 沿用 02 篇的 chat 封装，指向 DeepSeek
from retriever import retrieve_with_query_expand


SYSTEM_PROMPT = """\
你是一个企业内部知识库助手。严格按以下规则回答：

1. 只能基于给定的「参考资料」回答
2. 如果参考资料里没有相关信息，直接说"在现有资料中未找到相关信息"，不要编造
3. 回答末尾用 [来源：文件名] 的格式标出每条信息的出处
4. 回答要简洁，优先使用要点列举
"""


def answer(question: str, top_k: int = 5) -> str:
    # 替换为带查询改写的检索方法
    hits = retrieve_with_query_expand(question, top_k=top_k)

    if not hits:
        return "在现有资料中未找到相关信息"

    context = "\n\n---\n\n".join(
        f"[来源：{h['source']}]\n{h['text']}" for h in hits
    )

    user_prompt = f"""\
参考资料：
{context}

问题：{question}
"""

    return chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )


if __name__ == "__main__":
    q = "如何对项目的风险进行评估和管理？"
    print(f"问：{q}\n答：{answer(q)}")