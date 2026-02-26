import re
from sentence_transformers import SentenceTransformer, util

'''Chunking Strategies Deep Dive'''

'''
Strategy 1: Fixed Character Size
How it works: Split every N characters'''

text = "Python is great. " * 100
print(len(text)/100)

def chunk_by_chars(text, chunk_size=500):
    """Split text into fixed-size character chunks"""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks


"""Strategy 2: Fixed Character Size with Overlap
    How it works: Split every N characters, but overlap by M characters"""
def chunk_by_chars_with_overlap(text, chunk_size=500, overlap=50):
    """Split with overlap to preserve context at boundaries
    Chunk 1: [================]
    Chunk 2:          [================]
                  ↑ overlap ↑                                    """
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)  # Move forward with overlap iter-1:chunk have 500 char,
                                          #start starts from 450=>chunk2=450:950,start starts=900
    return chunks


import re

def chunk_by_sentences(text, max_chunk_size=500):
    """Split by sentences, combine into chunks up to size limit
       When to use: General documents, articles, books
                 Good default choice!"""
    # Split into sentences (simple regex)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence exceeds limit, save current chunk
        if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def chunk_by_sentences_with_overlap(text, max_chunk_size=500, overlap_sentences=1):
    """Split by sentences with sentence-level overlap
    When to use: High-quality RAG systems, when accuracy matters
                              - Best for most RAG applications!"""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    for i in range(0, len(sentences), 3): 
        
        chunk_sentences = sentences[max(0, i-overlap_sentences):i+3]
        chunk = " ".join(chunk_sentences)
        
        if len(chunk) <= max_chunk_size:
            chunks.append(chunk)
        else:
            
            chunks.extend(chunk_by_sentences(chunk, max_chunk_size))
    
    return chunks

def chunk_by_paragraphs(text, max_chunk_size=1000):
    """Split by paragraphs.When to use: Well-formatted documents (books, articles, reports)
                                         - Great for structured content!"""
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        if len(current_chunk) + len(para) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk += "\n\n" + para if current_chunk else para
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks



def chunk_by_semantic_similarity(text, similarity_threshold=0.7):
    """Split when semantic similarity drops (topic change).When to use: Research papers, technical docs with distinct topics
                                       Powerful but complex! Use only when needed."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Spliting into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Get embeddings
    embeddings = model.encode(sentences)
    
    chunks = []
    current_chunk = [sentences[0]]
    
    for i in range(1, len(sentences)):
        
        similarity = util.cos_sim(embeddings[i-1], embeddings[i])[0][0]
        
        if similarity < similarity_threshold:
            
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]
        else:
            current_chunk.append(sentences[i])
    
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


text1 = """
Machine learning is great. It enables computers to learn. 
Neural networks are powerful. They can recognize patterns. 
Deep learning is a subset. It uses many layers.
"""


 
print('fixed chunking....')
chunks = chunk_by_chars(text, chunk_size=50)
print(chunks[0])  

print("\nOverlapp chunking...")
chunks = chunk_by_chars_with_overlap(text, chunk_size=50, overlap=10)
print("Chunk 1:", chunks[0])
print("Chunk 2:", chunks[1]) 
print("Chunk 3:", chunks[2]) 

print("\nSentence based chunking")
chunks = chunk_by_sentences(text1, max_chunk_size=100)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: {chunk}\n")


print("\nSentence+Overlapping based chunking")
chunks = chunk_by_sentences_with_overlap(text1, max_chunk_size=100)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: {chunk}\n")


print("\nParagraph based chunking")
chunks = chunk_by_paragraphs(text1, max_chunk_size=100)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: {chunk}\n")


print("\nSematic(meaning) based chunking")
chunks = chunk_by_semantic_similarity(text1)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: {chunk}\n")