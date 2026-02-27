import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv(override=True)

def rag_setup(pdf_path):
    print("\n--- [1/3] Reading PDF File ---")
    loader = PyPDFLoader(pdf_path)
    
    print("--- [2/3] Splitting text into chunks ---")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(loader.load())
    
    print("--- [3/3] Creating Vector Database (FAISS) ---")
    # This downloads the embedding model (only the first time)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print("--- Setup Complete! ---\n")
    return vectorstore

def ask_qn(vectorstore, q):
    # Initializes the Groq Llama 3 model
    api_key = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(model='llama-3.1-8b-instant', temperature=0.1)
    
    # Standard Retrieval Chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
    )
    return chain.invoke({"query": q})

if __name__ == "__main__":
    load_dotenv(override=True)
    
    # DEBUG: Check if the key is actually found
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("ERROR: GROQ_API_KEY not found in .env file!")
    else:
        print(f"Using API Key ending in: ...{key[-4:]}") # Only prints last 4 chars for safety
    pdf_file = r'E:/39 day RoadMap/day-11/srs document for se 26th feb.pdf'
    
    if not os.path.exists(pdf_file):
        print(f"ERROR: File not found at: {pdf_file}")
    else:
        # Build the DB
        db = rag_setup(pdf_file)
        
        while True:
            qn = input("Ask a question about your SRS (or 'quit'): ")
            if qn.lower() in ['quit', 'exit']:
                print("Closing...")
                break
            
            if qn.strip():
                try:
                    response = ask_qn(db, qn)
                    print(f"\nANSWER:\n{response['result']}\n")
                    print("-" * 50)
                except Exception as e:
                    print(f"An error occurred: {e}")
