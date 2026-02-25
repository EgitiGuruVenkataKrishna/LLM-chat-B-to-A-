import chromadb

client= chromadb.PersistentClient(path='./chromadb_books')
old_collection= client.get_collection(name='Books')

try:
    old_collection = client.get_collection(name="Books")
    
   
    print("Collection found! Current data:")
    print(old_collection.get())
    
except Exception as e:
    print(f"Error: {e}")
    print("Available collections:", client.list_collections())