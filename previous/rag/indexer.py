# indexer.py
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from loader import load_docs
from chunker import chunk_text

# 用持久化模式，数据存在本地目录
client = chromadb.PersistentClient(path="./chroma_db")

# 用 sentence-transformers 的 bge-m3 做嵌入
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3",
    normalize_embeddings=True,
)

# 获取或创建集合（相当于一张表）
collection = client.get_or_create_collection(
    name="company_docs",
    embedding_function=embedder,
    metadata={"hnsw:space": "cosine"},  # 用余弦相似度
)


def index_directory(docs_dir: Path):
    raw_docs = load_docs(docs_dir)

    chunks, metadatas, ids = [], [], []
    counter = 0
    for doc in raw_docs:
        for i, chunk in enumerate(chunk_text(doc["text"])):
            chunks.append(chunk)
            metadatas.append({"source": doc["source"], "chunk_index": i})
            ids.append(f"chunk_{counter}")
            counter += 1

    # 批量写入，Chroma 会自动调 embedder 编码
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)
    print(f"已索引 {len(chunks)} 个块")


if __name__ == "__main__":
    index_directory(Path("./docs"))
