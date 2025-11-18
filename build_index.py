import json
import pickle
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DATA_PATH = "firstaid.jsonl"
INDEX_PATH = "index.faiss"
META_PATH = "meta.pkl"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def safe_get(obj, key):
    """避免 None，避免缺字段，统一转成干净字符串"""
    val = obj.get(key, "")
    if val is None:
        return ""
    return str(val).strip()


def load_docs():
    docs = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"[WARN] Line {line_num} JSON 解析失败，跳过: {e}")
                continue

            q = safe_get(obj, "prompt")
            a = safe_get(obj, "response")

            # 如果两者都空，跳过
            if not q and not a:
                print(f"[WARN] Line {line_num} prompt 和 response 都为空，跳过")
                continue

            docs.append({
                "text": f"Q: {q}\nA: {a}",
                "q": q,
                "a": a
            })

    return docs


if __name__ == "__main__":
    docs = load_docs()
    print("Loaded", len(docs), "docs")

    if len(docs) == 0:
        raise ValueError("数据为空，无法构建索引。检查 firstaid.jsonl。")

    model = SentenceTransformer(MODEL_NAME)
    texts = [d["text"] for d in docs]

    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    embeddings = embeddings.astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(docs, f)

    print("Index saved.")
