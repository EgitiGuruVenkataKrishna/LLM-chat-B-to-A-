from sentence_transformers import SentenceTransformer as st,util

model = st('all-MiniLM-L6-v2') 

query="where is the cat?"
sentences = [
    "The cat sits outside", 
    "A man is playing guitar", 
    "The feline is resting outdoors"
]

Q_embeddings = model.encode(query)
s_embeddings=model.encode(sentences)


scores=util.cos_sim(Q_embeddings,s_embeddings)[0]

for i,score in enumerate(scores):
    print(f"Score: {score:.4f} and Sentence:{sentences[i]}")