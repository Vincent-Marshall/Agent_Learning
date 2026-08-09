# retriever.py
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi

client = chromadb.PersistentClient(path="./chroma_db")
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3",
    normalize_embeddings=True,
)
collection = client.get_collection(name="company_docs", embedding_function=embedder)

# 加载重排模型
reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")

# 全局缓存全部文档，用于BM25
_all_chunks: list[dict] = []
_bm25: BM25Okapi | None = None


def build_bm25_index():
    """读取chroma全部文档，构建BM25索引，只执行一次"""
    global _all_chunks, _bm25
    if _bm25 is not None:
        return
    res = collection.get(include=["documents", "metadatas"])
    docs = res["documents"]
    metas = res["metadatas"]
    _all_chunks = [{"text": d, "source": m["source"]} for d, m in zip(docs, metas)]
    tokenized_corpus = [item["text"].split() for item in _all_chunks]
    _bm25 = BM25Okapi(tokenized_corpus)


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


def bm25_retrieve(query: str, top_k: int = 5) -> list[dict]:
    build_bm25_index()
    tokenized_query = query.split()
    bm25_scores = _bm25.get_scores(tokenized_query)
    scored = list(zip(_all_chunks, bm25_scores))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [{"text": c["text"], "source": c["source"], "score": s} for c, s in scored[:top_k]]


def hybrid_retrieve(query: str, top_k: int = 5, candidate_k: int = 20) -> list[dict]:
    """混合检索：向量 + BM25，做简单去重，输出候选"""
    vec_candidates = retrieve(query, top_k=candidate_k)
    bm25_candidates = bm25_retrieve(query, top_k=candidate_k)

    # 简单去重，用text做key
    seen = set()
    all_candidates = []
    for item in vec_candidates + bm25_candidates:
        t = item["text"]
        if t not in seen:
            seen.add(t)
            all_candidates.append(item)
    return all_candidates


def retrieve_with_rerank(query: str, top_k: int = 5, candidate_k: int = 20) -> list[dict]:
    # 混合检索召回候选集
    candidates = hybrid_retrieve(query, candidate_k=candidate_k)
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