import chromadb
from rag import retrieve_faiss
import chromadb
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="rag_documents")

def store_chunks(chunk,embeddings):
   ids = [f"chunk_{i}" for i in range(len(chunk))]

   metadatas= [{"SOURCE" :"SAMPLE.TXT"}
               for i in range(len(chunk))]

   collection.add (ids = ids,
                documents = chunk,
                embeddings = embeddings.tolist(),
                metadatas = metadatas)
   print(collection.count())

def query_chunks(question,model,top_k=3):
   q_embeddings = model.encode([question])

   results = collection.query(query_embeddings=q_embeddings.tolist(),n_results = top_k)
   return results["documents"][0]