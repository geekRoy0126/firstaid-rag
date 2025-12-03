# 🚑 First Aid RAG Assistant
A lightweight Retrieval-Augmented Generation (RAG) system that provides **reliable, evidence-grounded first-aid guidance**.  
The system integrates **Sentence-Transformers, FAISS, Qwen3, FastAPI, Streamlit**, and **Docker** for full local reproducibility.

---

## 📌 Features
- 🔍 Dense Retrieval (FAISS + Embeddings)
- 🤖 Local Qwen3 LLM generation
- 🧩 PAL-style grounded reasoning
- ⚙️ Automated dataset download, embedding, and index construction
- 💬 Streamlit-based chat UI
- 📦 Full Docker containerization

---

## 🧱 Tech Stack (with Versions)
| Component | Version | Purpose |
|----------|---------|---------|
| Python | 3.10 | Core development language |
| Sentence-Transformers | 2.6.1 | Embedding of documents & queries |
| FAISS | 1.7.4 | Vector similarity search |
| Qwen3 (8B gguf) | — | Local LLM inference |
| FastAPI | 0.110+ | Backend inference server |
| Uvicorn | 0.29+ | ASGI server |
| Streamlit | 1.33+ | Front-end chat UI |
| HuggingFace Datasets | 2.18+ | Dataset loading & preprocessing |

---

## 📚 Dataset
Uses the **FirstAidInstructionsDataset** (~120k procedural units):  
https://huggingface.co/datasets/lextale/FirstAidInstructionsDataset

---

## 🚀 Quick Start

### 1. Clone
```bash
git clone https://github.com/geekRoy0126/firstaid-rag
cd firstaid-rag
```

### 2. Run with Docker (recommended)
```bash
docker build -t firstaid-rag .
docker run -p 8000:8000 firstaid-rag
```

API available at:
```
http://localhost:8000
```

### 3. Start Streamlit UI
```bash
streamlit run streamlit/app.py
```

UI loads at:
```
http://localhost:8501
```

---

## 📡 API Usage

### POST `/ask`
**Request**
```json
{
  "question": "What should I do for a minor burn?"
}
```

**Response**
```json
{
  "answer": "... grounded instructions ...",
  "retrieved_docs": [...]
}
```

---

## 📁 Project Structure
```
firstaid-rag/
│ app.py                # FastAPI backend
│ build_index.py        # Build FAISS index + embed corpus
│ Dockerfile
│ requirements.txt
│ data/                 # Auto-generated corpus + FAISS index
└ streamlit/
  └ app.py              # Chat UI
```

---

## 🔧 Notes on Reproducibility
- Fully containerized via Docker
- Startup script handles:
  - dataset download
  - embedding generation
  - FAISS index construction
- Ensures deterministic execution across environments

---

## 🧭 Future Improvements
- Add multimodal input (image-based wound analysis)
- Integrate cross-encoder re-ranking (ColBERT)
- Add uncertainty estimation / confidence scores
- Expand to multilingual first-aid datasets
- Optional fine-tuning of Qwen3 for medical reasoning

---
