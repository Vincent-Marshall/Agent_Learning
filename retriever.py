# retriever.py
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_db")
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3",
    normalize_embeddings=True,
)
collection = client.get_collection(name="company_docs", embedding_function=embedder)


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


if __name__ == "__main__":
    for hit in retrieve("年假可以累计到明年吗"):
        print(f"[{hit['score']:.3f}] {hit['source']}\n{hit['text'][:100]}...\n")
