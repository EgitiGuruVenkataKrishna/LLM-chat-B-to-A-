# 📄 Production RAG API (FastAPI + ChromaDB + Groq)

A lightweight, production-ready Retrieval-Augmented Generation (RAG) API for querying information from uploaded PDFs.

This API lets you upload documents, store embeddings in a persistent vector database, and ask questions grounded in those documents.

---

## 🚀 Features

* PDF upload and processing
* Persistent vector storage using ChromaDB
* Fast semantic search using sentence-transformer embeddings
* LLM answer generation via Groq
* Edge-case safe:

  * File size validation
  * File type validation
  * Corrupted PDF handling
  * Empty-text detection
  * Missing API key handling
  * Empty collection protection
* Retrieval logic optimized to avoid false “no answer” cases

---

## 📦 Tech Stack

* FastAPI
* ChromaDB (persistent vector DB)
* SentenceTransformers (embeddings)
* Groq LLM API
* LangChain loaders + text splitters

---

## 📂 Project Structure

```
project/
│
├── main.py                # FastAPI RAG service
├── chroma_data/           # Persistent vector store
├── uploaded_files/        # Temporary file storage
├── .env                   # Environment variables
└── README.md
```

---

## ⚙️ Setup

### 1️⃣ Create virtual environment

```bash
python -m venv venv
```

Activate:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / Mac**

```bash
source venv/bin/activate
```

---

### 2️⃣ Install dependencies

```bash
pip install fastapi uvicorn chromadb sentence-transformers langchain-community langchain-text-splitters langchain-groq python-dotenv
```

---

### 3️⃣ Configure environment variables

Create `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

---

### 4️⃣ Run the API

```bash
uvicorn main:app --reload
```

API runs at:

```
http://localhost:8000
```

Docs:

```
http://localhost:8000/docs
```

---

## 📥 Upload a PDF

**POST** `/upload-pdf`

Form-data:

* file: PDF file
* collection_name (optional)

Returns chunk count and collection info.

---

## ❓ Ask a Question

**POST** `/ask`

```json
{
  "question": "What is SRS?",
  "collection_name": "documents"
}
```

Returns:

* AI answer
* source chunks used
* similarity score

---

## 🩺 Health Check

**GET** `/health`

Returns system status and vector store info.

---

## 🧠 How Retrieval Works

1. PDF text is extracted and chunked
2. Each chunk is embedded and stored
3. Question is embedded
4. Top matching chunks are retrieved
5. LLM answers strictly using retrieved context

The system avoids over-filtering so valid answers are not blocked.

---

## ⚠️ Limitations

* Image-only PDFs require OCR preprocessing
* Very large documents should be split before upload
* Answer quality depends on document clarity

---

## 📌 Future Improvements

* OCR support for scanned PDFs
* Multi-file semantic routing
* Streaming answers
* Citation highlighting
* Auth + rate limiting

---

## 📜 License

MIT — free to use and modify.

---

## 👨‍💻 Author

Built as a production-style RAG backend for document question answering.
