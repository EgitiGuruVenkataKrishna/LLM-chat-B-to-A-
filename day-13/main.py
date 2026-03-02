from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv(override=True)

# ================= CONFIG =================

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".pdf"]
MIN_TEXT_LENGTH = 100

app = FastAPI(
    title="Production RAG API",
    description="Upload PDFs and ask questions using retrieval-augmented generation"
)

# Persistent vector store
CHROMA_PATH = "./chroma_data"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

UPLOAD_DIR = Path("./uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)

# ================= MODELS =================

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    collection_name: str = "documents"

class QueryResponse(BaseModel):
    answer: str
    source_documents: list
    similarity: float

# ================= UPLOAD =================

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), collection_name: str = "documents"):
    try:
        # Validate extension
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, "Only PDF files are allowed")

        # Read file
        contents = await file.read()
        size = len(contents)

        # Validate size
        if size == 0:
            raise HTTPException(400, "Uploaded file is empty")

        if size > MAX_FILE_SIZE:
            raise HTTPException(
                400,
                f"File too large. Maximum: 10MB. Your file: {round(size/(1024*1024),1)}MB"
            )

        # Save temp file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(contents)

        # Load PDF
        try:
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
        except Exception:
            file_path.unlink(missing_ok=True)
            raise HTTPException(400, "PDF could not be read. It may be corrupted or image-based.")

        # Extract text
        full_text = " ".join([d.page_content for d in documents])
        if len(full_text.strip()) < MIN_TEXT_LENGTH:
            file_path.unlink(missing_ok=True)
            raise HTTPException(400, "PDF contains too little readable text.")

        # Chunk text (same logic as your working version)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = splitter.split_documents(documents)

        texts = [c.page_content for c in chunks]
        embeddings = embedding_model.encode(texts, normalize_embeddings=True)

        # Get/create collection
        try:
            collection = chroma_client.get_collection(collection_name)
        except:
            collection = chroma_client.create_collection(collection_name)

        ids = [f"{file.filename}_{i}" for i in range(len(chunks))]
        metas = [
            {"source": file.filename, "page": c.metadata.get("page", 0)}
            for c in chunks
        ]

        collection.add(
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metas,
            ids=ids
        )

        return {
            "message": "PDF processed successfully",
            "chunks": len(chunks),
            "collection": collection_name,
            "total_docs": collection.count()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")

# ================= ASK =================

@app.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    try:
        # Check collection
        try:
            collection = chroma_client.get_collection(request.collection_name)
        except:
            raise HTTPException(404, "Collection not found. Upload a PDF first.")

        if collection.count() == 0:
            raise HTTPException(400, "Collection is empty.")

        # Embed query
        query_emb = embedding_model.encode(request.question, normalize_embeddings=True)

        # Retrieve chunks (same as your working logic)
        results = collection.query(
            query_embeddings=[query_emb.tolist()],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )

        if not results["documents"][0]:
            return QueryResponse(
                answer="No relevant information found in the uploaded documents.",
                source_documents=[],
                similarity=0.0
            )

        # Use BEST similarity only (not average!)
        best_similarity = max([1 - (d/2) for d in results["distances"][0]])

        # Only reject if extremely low
        if best_similarity < 0.18:
            return QueryResponse(
                answer="I could not find relevant information in the uploaded documents.",
                source_documents=[],
                similarity=round(best_similarity,3)
            )

        # Build context
        context = "\n\n".join(results["documents"][0])

        # LLM
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(500, "GROQ_API_KEY missing in .env")

        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.1,
            api_key=api_key
        )

        prompt = f"""
Answer the question using ONLY the context below.
If context truly lacks info, say you cannot find it.

Context:
{context}

Question: {request.question}

Answer:
"""

        answer = llm.invoke(prompt).content

        sources = [
            {
                "text": d[:300] + "...",
                "source": m["source"],
                "page": m["page"]
            }
            for d, m in zip(
                results["documents"][0],
                results["metadatas"][0]
            )
        ]

        return QueryResponse(
            answer=answer,
            source_documents=sources,
            similarity=round(best_similarity,3)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Query error: {str(e)}")

@app.get("/collections")
async def list_collections():
    """List all available collections"""
    collections = chroma_client.list_collections()
    return {
        "collections": [
            {
                "name": col.name,
                "document_count": col.count()
            }
            for col in collections
        ]
    }

@app.delete("/collection/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a collection"""
    try:
        chroma_client.delete_collection(collection_name)
        return {"message": f"Collection '{collection_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Collection not found: {str(e)}")

# ================= HEALTH =================

@app.get("/health")
async def health():
    try:
        cols = chroma_client.list_collections()
        return {
            "status": "healthy",
            "collections": len(cols),
            "embedding_model": "all-MiniLM-L6-v2",
            "max_file_size_mb": 10
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    

# ==================== RUN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)