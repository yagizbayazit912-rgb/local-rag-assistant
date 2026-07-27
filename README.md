# 📚 Local RAG Assistant (Offline & Privacy-First)

A fully local, offline Retrieval-Augmented Generation (RAG) assistant built with Python. This project demonstrates a privacy-first AI architecture where all document processing, vector embeddings, and LLM text generation occur strictly on the local machine without relying on external APIs.

## 🚀 Key Features
* **100% Offline & Private:** No data is sent to external servers. Ideal for sensitive document analysis.
* **Local Vector Database:** Utilizes SQLite and cosine similarity for lightweight, dependency-free vector search.
* **Hallucination Control:** Strict prompt engineering ensures the model only answers based on the provided context, preventing AI hallucinations.
* **Modern UI:** Built with Streamlit for a clean, chat-based user experience.

## 🛠️ Tech Stack
* **Language:** Python
* **LLM Engine:** Qwen/Qwen2.5-3B-Instruct (via Hugging Face `transformers` pipeline)
* **Embedding Model:** `paraphrase-multilingual-MiniLM-L12-v2` (Sentence-Transformers)
* **Database:** SQLite (Custom JSON Vector Storage)
* **Frontend:** Streamlit

## ⚙️ Installation & Usage

**Step 1: Clone the repository**
```bash
git clone https://github.com/yagizbayazit912-rgb/local-rag-assistant.git
cd local-rag-assistant
