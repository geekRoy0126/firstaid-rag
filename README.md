## 🔧 Software Versions and Their Purposes

This project relies on a collection of modern machine learning, retrieval, and web technologies.  
Below are the core software components, their specific versions, and their roles in the system.

---

### **1. Python 3.10**
- **Role:** Primary development language  
- **Purpose:** Ensures compatibility with major ML libraries (FAISS, Transformers, FastAPI, Streamlit)

---

### **2. Sentence-Transformers 2.6.1**
- **Role:** Dense embedding generation  
- **Purpose:** Converts first-aid instructions and user queries into 768-d semantic vectors for retrieval.

---

### **3. FAISS 1.7.4**
- **Role:** Vector similarity search engine  
- **Purpose:** Performs fast top-k nearest neighbor retrieval over embedding space  
- Enables sub-millisecond search even with large corpora.

---

### **4. Qwen3 (8B, gguf version)**
- **Role:** Local Large Language Model  
- **Purpose:** Generates grounded responses using retrieved evidence  
- Runs locally for determinism, reproducibility, and safety-critical reliability.

---

### **5. FastAPI 0.110+**
- **Role:** Backend inference server  
- **Purpose:**  
  - Hosts the `/ask` endpoint  
  - Orchestrates embedding → retrieval → generation  
  - Enables stateless, reproducible pipeline execution.

---

### **6. Uvicorn 0.29+**
- **Role:** ASGI web server for FastAPI  
- **Purpose:** Provides high-performance async inference and API routing.

---

### **7. Streamlit 1.33+**
- **Role:** Front-end user interface  
- **Purpose:**  
  - Implements a real-time chat UI  
  - Displays retrieved evidence + model responses  
  - Supports local experimentation and demonstration.

---

### **8. Docker 24+**
- **Role:** Full containerization of the system  
- **Purpose:**  
  - Guarantees reproducible environments for TAs and instructors  
  - Automates dataset download, embedding, FAISS indexing, and model startup  
  - Makes the system deployable across any OS.

---

### **9. HuggingFace Datasets 2.18+**
- **Role:** Dataset loading & preprocessing  
- **Purpose:**  
  - Downloads the *FirstAidInstructionsDataset*  
  - Standardized interface for text datasets  
  - Ensures compatibility with vectorization pipeline.

---

### **10. Transformers 4.40+**
- **Role:** Model loading and tokenization  
- **Purpose:**  
  - Provides tokenizer + model utilities  
  - Ensures compatibility with Qwen3 local inference.

---

### **11. numpy 1.26+**
- **Role:** Embedding & vector operations  
- **Purpose:** Fundamental numerical operations for FAISS & preprocessing.

---

## 📌 Why These Versions Matter

- Ensures reproducibility across environments  
- Matches FAISS & Sentence-Transformers compatible versions  
- Prevents API incompatibilities with FastAPI / Streamlit  
- Guarantees stable local inference with Qwen3  
- Meets the course requirement for reliable, reproducible LLM systems  

---
