
import numpy as np
from sentence_transformers import SentenceTransformer

# # 第一次跑会下载约 2 GB 的模型权重，需要等几分钟
# model = SentenceTransformer("BAAI/bge-m3")

# texts = [
#     "如何重置密码",
#     "忘记密码怎么办",
#     "今天的午饭吃什么",
# ]

# # 把文字变成向量（一段 1024 维的浮点数数组）
# vectors = model.encode(texts, normalize_embeddings=True)
# print("向量形状:", vectors.shape)

# # 算两两相似度（归一化向量的点积 = 余弦相似度）
# similarity = vectors @ vectors.T
# print("相似度矩阵:")
# print(similarity.round(3))




model = SentenceTransformer("BAAI/bge-m3")

# 假装这是你的"知识库"
docs = [
    "Python 的列表推导式让代码更简洁",
    "如何在 macOS 上安装 Homebrew",
    "FastAPI 是一个现代的 Python Web 框架",
    "煮意大利面要在水里加盐",
    "用 Pandas 处理 CSV 文件的最佳实践",
    "今天去爬山看到了一只松鼠",
    "asyncio 提供了 Python 的异步编程模型",
    "good night",
    "have a nice day"
]

# 启动时把所有文档编码一次，存在内存里
doc_vecs = model.encode(docs, normalize_embeddings=True)


def search(query: str, top_k: int = 3):
    q_vec = model.encode([query], normalize_embeddings=True)[0]
    sims = doc_vecs @ q_vec        # 一次性算 query 和所有文档的相似度
    idx = np.argsort(-sims)[:top_k]  # 按相似度从高到低取前 k 个
    return [(docs[i], float(sims[i])) for i in idx]


for q in ["Python 异步怎么写", "做饭技巧", "farewell my friend"]:
    print(f"\n查询：{q}")
    for text, score in search(q):
        print(f"  [{score:.3f}] {text}")
