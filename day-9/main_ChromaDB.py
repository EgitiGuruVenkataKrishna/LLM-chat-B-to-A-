#VectorDB:The storing of any data(text,images,video, and audios) respresenting in the form of numbers
#These numbers are stored as vectors with n dimentions (our choice) called Vector Embeddings

##ChromaDB:Is an Open Source vector db(why we are using: light weight,easy to handle)

import chromadb


client=chromadb.PersistentClient(path='./chromadb_books')

collection=client.get_or_create_collection(
    name="Books"
)
###Here, i got space to store the data

print("Collection created...",collection.name)
collection.add(
documents=[
    "Atomic Habits by James Clear for routine building",
    "The Mountain Is You by Brianna Wiest for overcoming self-sabotage",
    " How to Win Friends and Influence People by Dale Carnegie for communication"],

ids=['b1','b2','b3']
)

R=collection.query(query_texts=['the book that related to influencing or making friends '],n_results=2)

