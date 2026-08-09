# retriever.py
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi
from ai import chat

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

# 相似度阈值配置
RERANK_SCORE_THRESHOLD = 0.4


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


def expand_query(origin_query: str) -> list[str]:
    """查询改写：大模型生成多条同义、多角度衍生查询"""
    prompt = f"""
你是查询优化助手，针对用户原始问题，生成3条不同表述、同义、多角度的衍生查询，仅输出每行一条问句，不要多余解释、序号、标点备注。
原始问题：{origin_query}
"""
    resp = chat(messages=[{"role": "user", "content": prompt}], temperature=0.1)
    query_list = [q.strip() for q in resp.splitlines() if q.strip()]
    # 追加原始问句，避免改写跑偏丢失原意
    query_list.insert(0, origin_query)
    return query_list


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
    result_items = [item[0] for item in ranked[:top_k]]
    # 阈值校验：top1分数低于阈值直接返回空结果
    if result_items and ranked[0][1] < RERANK_SCORE_THRESHOLD:
        return []
    return result_items


def retrieve_with_query_expand(origin_query: str, top_k: int = 5, candidate_k: int = 20) -> list[dict]:
    """查询改写入口：多问句分别检索，合并去重后统一重排筛选"""
    # 生成多组查询
    query_list = expand_query(origin_query)
    total_candidates = []
    # 逐个问句执行混合检索
    for q in query_list:
        q_candidates = hybrid_retrieve(q, candidate_k=candidate_k)
        total_candidates.extend(q_candidates)
    # 全局文本去重
    seen_text = set()
    unique_candidates = []
    for item in total_candidates:
        if item["text"] not in seen_text:
            seen_text.add(item["text"])
            unique_candidates.append(item)
    if not unique_candidates:
        return []
    # 统一对原始问题做重排打分
    pairs = [(origin_query, c["text"]) for c in unique_candidates]
    rerank_scores = reranker.predict(pairs)
    ranked_result = sorted(zip(unique_candidates, rerank_scores), key=lambda x: -x[1])
    final_items = [i[0] for i in ranked_result[:top_k]]
    # 相似度阈值兜底判断
    if final_items and ranked_result[0][1] < RERANK_SCORE_THRESHOLD:
        return []
    return final_items


if __name__ == "__main__":
    hits = retrieve_with_query_expand("如何对项目的风险进行评估和管理？", top_k=5)
    for hit in hits:
        print(f"[{hit['score']:.3f}] {hit['source']}\n{hit['text'][:100]}...\n")