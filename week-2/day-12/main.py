from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import shutil
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import RetrievalQA
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv

load_dotenv(override=True)

# Initialize FastAPI
app = FastAPI(
    title="RAG API for SRS",
    summary="FastAPI-wrapped RAG model with document Q&A",
    description="Upload PDFs, ask questions, get AI-powered answers using RAG"
)

# Global ChromaDB client (persistent storage)
CHROMA_PATH = "./chroma_data"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Create uploads directory
UPLOAD_DIR = Path("./uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    collection_name: str = "documents"  # Default collection

class QueryResponse(BaseModel):
    answer: str
    source_documents: list

# ==================== ENDPOINTS ====================

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    collection_name: str = "documents"
):
    """
    Upload a PDF file and store it in ChromaDB
    
    Args:
        file: PDF file to upload
        collection_name: Name of the collection to store in
    
    Returns:
        Success message with document count
    """
    try:
        # 1. Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # 2. Save uploaded file temporarily
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"\n--- [1/4] PDF uploaded: {file.filename} ---")
        
        # 3. Load and extract text
        loader = PyPDFLoader(str(file_path))
        documents = loader.load()
        print(f"--- [2/4] Extracted {len(documents)} pages ---")
        
        # 4. Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(documents)
        print(f"--- [3/4] Created {len(chunks)} chunks ---")
        
        # 5. Create embeddings and store in ChromaDB
        texts = [chunk.page_content for chunk in chunks]
        embeddings = embedding_model.encode(texts, normalize_embeddings=True)
        
        # Get or create collection
        try:
            collection = chroma_client.get_collection(collection_name)
        except:
            collection = chroma_client.create_collection(collection_name)
        
        # Add to ChromaDB
        ids = [f"{file.filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": file.filename,
                "page": chunk.metadata.get("page", 0),
                "chunk_id": i
            }
            for i, chunk in enumerate(chunks)
        ]
        
        collection.add(
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"--- [4/4] Stored in ChromaDB collection: {collection_name} ---")
        
        # 6. Clean up uploaded file (optional)
        # file_path.unlink()  # Uncomment to delete after processing
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "PDF uploaded and processed successfully",
                "filename": file.filename,
                "chunks_created": len(chunks),
                "collection": collection_name,
                "total_documents_in_collection": collection.count()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a question about uploaded documents
    
    Args:
        request: QueryRequest with question and collection_name
    
    Returns:
        AI-generated answer with source documents
    """
    try:
        # 1. Get collection
        try:
            collection = chroma_client.get_collection(request.collection_name)
        except:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{request.collection_name}' not found. Upload a PDF first!"
            )
        
        if collection.count() == 0:
            raise HTTPException(
                status_code=400,
                detail="Collection is empty. Upload a PDF first!"
            )
        
        print(f"\n--- Answering question: {request.question} ---")
        
        # 2. Generate query embedding
        query_embedding = embedding_model.encode(
            request.question,
            normalize_embeddings=True
        )
        
        # 3. Retrieve relevant chunks
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=3,  # Top 3 relevant chunks
            include=["documents", "metadatas", "distances"]
        )
        
        # 4. Build context from retrieved chunks
        context = "\n\n".join(results['documents'][0])
        
        print(f"--- Retrieved {len(results['documents'][0])} relevant chunks ---")
        
        # 5. Generate answer with LLM
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GROQ_API_KEY not found in .env file"
            )
        
        llm = ChatGroq(
            model='llama-3.1-8b-instant',
            temperature=0.1,
            api_key=api_key
        )
        
        # Create prompt
        prompt = f"""Use the following context to answer the question. If you cannot answer based on the context, say "I don't have enough information in the provided documents to answer this question."

Context:
{context}

Question: {request.question}

Answer:"""
        
        # Get answer
        answer = llm.invoke(prompt)
        
        print(f"--- Answer generated ---\n")
        
        # 6. Format response
        source_docs = [
            {
                "text": doc,
                "source": meta["source"],
                "page": meta["page"],
                "similarity": 1 - (dist / 2)  # Convert distance to similarity
            }
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]
        
        return QueryResponse(
            answer=answer.content,
            source_documents=source_docs
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "chroma_path": CHROMA_PATH,
        "collections": len(chroma_client.list_collections())
    }


# ==================== RUN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)