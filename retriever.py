# retriever.py
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import CrossEncoder

client = chromadb.PersistentClient(path="./chroma_db")
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3",
    normalize_embeddings=True,
)
collection = client.get_collection(name="company_docs", embedding_function=embedder)

# 加载重排模型
reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    result = collection.query(query_texts=[query], n_results=top_k)
    return [
        {
            "text": doc,
            "source": meta["source"],
            "score": 1 - dist,  # Chroma 返回距离，转为相似度
        }
        for doc, meta, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]


def retrieve_with_rerank(query: str, top_k: int = 5, candidate_k: int = 20) -> list[dict]:
    # 先向量检索召回候选集
    candidates = retrieve(query, top_k=candidate_k)
    if not candidates:
        return []
    # 构造查询-片段配对
    pairs = [(query, c["text"]) for c in candidates]
    # 重排打分
    scores = reranker.predict(pairs)
    # 按重排分数降序，取top_k
    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return [item[0] for item in ranked[:top_k]]


if __name__ == "__main__":
    for hit in retrieve_with_rerank("如何对项目的风险进行评估和管理？", top_k=5):
        print(f"[{hit['score']:.3f}] {hit['source']}\n{hit['text'][:100]}...\n")