import pickle
import faiss
import numpy as np
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

INDEX_PATH = "index.faiss"
META_PATH = "meta.pkl"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"   # Windows/Mac Docker 必用


class AskRequest(BaseModel):
    question: str
    top_k: int = 3


app = FastAPI()


# Load on startup
faiss_index = faiss.read_index(INDEX_PATH)
with open(META_PATH, "rb") as f:
    docs = pickle.load(f)

embed = SentenceTransformer(MODEL_NAME)


def retrieve(q, k):
    vec = embed.encode([q]).astype("float32")
    dist, idx = faiss_index.search(vec, k)
    idx = idx[0]
    dist = dist[0]

    results = []
    for i, d in zip(idx, dist):
        doc = docs[i]
        results.append({
            "q": doc["q"],
            "a": doc["a"],
            "score": float(d)
        })
    return results


def call_ollama(question, context_docs):
    context_text = "\n\n".join([
        f"Document {i+1}:\nQuestion: {d['q']}\nAnswer: {d['a']}"
        for i, d in enumerate(context_docs)
    ])

    prompt = f"""
You are a first-aid assistant. Use ONLY the documents to answer.

Documents:
{context_text}

User question: {question}

Your helpful answer:
"""

    # ✔ 修复点：改用 /api/chat + messages
    payload = {
        "model": "qwen3:8b",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    # ✔ Ollama chat API endpoint
    url = "http://host.docker.internal:11434/api/chat"

    r = requests.post(url, json=payload)
    data = r.json()

    # ✔ 返回生成的内容
    return data["message"]["content"]


@app.post("/ask")
def ask(req: AskRequest):
    retrieved = retrieve(req.question, req.top_k)
    answer = call_ollama(req.question, retrieved)
    return {
        "question": req.question,
        "retrieved_docs": retrieved,
        "answer": answer
    }


@app.get("/")
def root():
    return {"msg": "RAG server running. Use POST /ask"}
