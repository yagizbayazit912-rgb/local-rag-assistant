# 📚 Local RAG Assistant (Offline & Privacy-First)

A fully local, offline Retrieval-Augmented Generation (RAG) assistant built with Python and **Microsoft Foundry Local**. This project demonstrates a privacy-first AI architecture where all document processing, vector embeddings, and LLM text generation occur strictly on the local machine, with zero internet dependency and zero external API calls.

This project was built as part of a one-month summer program plan inspired by the Microsoft Tech Community blog post *["Building Your First Local RAG Application with Foundry Local"](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968)*.

## 🚀 Key Features
* **100% Offline & Private:** No data is sent to external servers. Ideal for sensitive document analysis.
* **On-device inference via Foundry Local:** Both the embedding model and the chat model run locally through the Foundry Local SDK — no cloud account, no API key, no GPU required.
* **Local Vector Database:** Utilizes SQLite and cosine similarity for lightweight, dependency-free vector search.
* **Hallucination Control:** Strict prompt engineering ensures the model only answers based on the provided context, and explicitly says "I don't know" when the context is insufficient.
* **Modern UI:** Built with Streamlit for a clean, chat-based user experience.

## 🛠️ Tech Stack
* **Language:** Python
* **LLM Engine:** `qwen2.5-7b` (via Microsoft Foundry Local SDK — on-device chat completion)
* **Embedding Model:** `qwen3-embedding-0.6b` (via Microsoft Foundry Local SDK — on-device embeddings)
* **PDF Parsing:** PyMuPDF (`fitz`) — chosen over PyPDF2 for more reliable Unicode/ligature handling
* **Database:** SQLite (custom JSON vector storage, cosine similarity search)
* **Frontend:** Streamlit

## 🏗️ Architecture

```
User question
     │
     ▼
[Streamlit UI] ──▶ [Foundry Local: embedding client] ──▶ query vector
     │                                                        │
     │                                                        ▼
     │                                     [SQLite: cosine similarity search]
     │                                                        │
     │                                          top matching chunks (context)
     │                                                        │
     ▼                                                        ▼
[Foundry Local: chat client]  ◀── system prompt + context + question
     │
     ▼
Answer (grounded in retrieved context) + cited source chunks
```

## ⚙️ Installation & Usage

**Step 1: Install Foundry Local (one-time, OS-level)**

Windows:
```bash

winget install --id Microsoft.FoundryLocal -e
```
macOS:
```bash
brew tap microsoft/foundrylocal
brew install foundrylocal
```
Verify installation:
```bash
foundry model list
```

**Step 2: Clone the repository**
```bash
git clone https://github.com/yagizbayazit912-rgb/local-rag-assistant.git
cd local-rag-assistant
```

**Step 3: Install Python dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Add your documents**

Place your PDF files inside the `belgeler/` folder.

**Step 5: Build the knowledge base**
```bash
python veri_yukle.py
```
This reads every PDF in `belgeler/`, splits it into chunks, generates embeddings via Foundry Local's `qwen3-embedding-0.6b` model, and stores everything in `rag_veritabani.db`. The first run downloads the embedding model (a few hundred MB).

**Step 6: Run the app**
```bash
streamlit run app.py
```
The first run also downloads the chat model (`qwen2.5-7b`, ~6 GB) and loads it into memory, which can take a minute or two on CPU-only machines. A CLI version is also available: `python main.py`.

## ✅ Testing & Evaluation

A set of manual test queries was used to validate the assistant's behavior, covering both answerable and unanswerable questions (per the project plan's Week 5 testing phase):

| # | Question | Expected behavior | Result |
|---|---|---|---|
| 1 | "Python nedir?" (in-document topic) | Should return a grounded answer citing `ders_notu.pdf` | ✅ Pass — relevant answer with correct source citation |
| 2 | "Paul kimdir?" (not in the document) | Should reply "Elimdeki belgelerde bu bilgiye sahip değilim." instead of fabricating an answer | ✅ Pass — correctly refused to hallucinate |
| 3 | "Merhaba" (casual greeting) | Should be blocked by the chit-chat filter, not sent to the LLM | ✅ Pass — showed "günlük sohbet edemem" warning |
| 4 | Another in-document topic question | Should return a grounded, on-topic answer | ✅ Pass — answered correctly using document content |
| 5 | "Türkiye'nin başkenti neresi?" (clearly unrelated to the document) | Should reply that the information isn't in the documents, not answer from general knowledge | ✅ Pass — replied "bu bilgiler belgede bulunamadı" |
| 6 | Empty input (pressing Enter with no text) | Should not crash the app or send an empty query | ✅ Pass — no action taken |

All six test cases were run manually against the live Streamlit app and passed as expected.

**Known limitations:**
* Response time is CPU-bound (~10–30 seconds per answer on a laptop without GPU acceleration); switching to a smaller alias like `phi-3.5-mini` or `qwen2.5-1.5b` trades some answer quality for speed.
* Answers can occasionally be verbose or loosely structured, since the chat model is a small, quantized, CPU-optimized model rather than a large cloud-hosted one.

## 📌 Notes on the project plan

The original one-month plan specified using Microsoft Foundry Local's SDK for both the chat and embedding components. An earlier iteration of this project used Hugging Face `transformers` and `sentence-transformers` instead; it has since been migrated to use the Foundry Local SDK end-to-end (see `foundry_client.py`) to align with the plan's core requirement of an on-device Foundry Local runtime.
