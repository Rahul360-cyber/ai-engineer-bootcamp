import chromadb
from rag import retrieve_faiss
import chromadb
from pypdf import PdfReader
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="rag_documents")
"""
def store_chunks(chunk,embeddings):
   ids = [f"chunk_{i}" for i in range(len(chunk))]

   metadatas= [{"SOURCE" :"SAMPLE.TXT"}
               for i in range(len(chunk))]

   collection.add (ids = ids,
                documents = chunk,
                embeddings = embeddings.tolist(),
                metadatas = metadatas)
   print(collection.count())
"""
print (collection.count())

def query_chunks(question,model,top_k=3):
   q_embeddings = model.encode([question])

   results = collection.query(query_embeddings=q_embeddings.tolist(),n_results = top_k)
   final_result =[]
   for documents,metadata,distances in zip (results["documents"][0],results["metadatas"][0],results["distances"][0]):
        if distances < 0.79:
            result = {"documents": documents,
                        "metadata":metadata,
                        "distances": distances}
            final_result.append(result)
   return final_result


##results["documents"][0]

def load_pdf(path):
   complete_text = []
   reader = PdfReader(path)
   for page_number ,page in enumerate(reader.pages):
      text = page.extract_text()
      page_data = {
         "page" : page_number,
         "text" : text
      }
      complete_text.append(page_data)
   return complete_text

def chunk_pdf_pages(pages,source,chunk_size = 500,overlap = 50):
         start = 0
         end = start + chunk_size
         final_chunk=[]
         for page in pages:
            start = 0
            text = page["text"]
            page_number = page["page"]
            while start < len(text):
              end = start + chunk_size
              chunks = text[start:end]
              start = end-overlap
              chunk_data ={
                "text" : chunks,
                "page" : page_number,
                "source" : source
                        }
              
              final_chunk.append(chunk_data)
         return final_chunk

def create_embeddings(model,text):
           text = [item["text"] for item in text]
           text_embeddings = model.encode(text)
           return text_embeddings
         
def store_chunks(chunk,embeddings):
   documents = [item["text"] for item in chunk]
   ids = [f"chunk_{i}" for i in range(len(chunk))]

   metadatas= [{"SOURCE" :item["source"],
                "page" : item["page"]}
               for item in chunk]

   collection.add (ids =ids,
                documents = documents,
                embeddings = embeddings.tolist(),
                metadatas = metadatas)
   print(collection.count())
