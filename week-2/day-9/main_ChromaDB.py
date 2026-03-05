import chromadb

client=chromadb.Client()

collection=client.create_collection(name='Brand')

collection.add(
    documents=["Rolex watch is Costly but royal","Titan watch is a modern watch",'i want to buy a Meteor Bike'],
    metadatas=[{'source':"MySrc",'page':1},{'source':"MySrc",'page':2},{'source':"MySrc",'page':3}],
    ids=['page-1','page-2','page-3']
)

quary='i want to buy a watch should look royal and modern'

res=collection.query(
    query_texts=[quary],
    n_results=3,
    include=['metadatas','distances','embeddings','documents']
)

print(res)