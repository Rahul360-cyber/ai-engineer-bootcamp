from pydantic import BaseModel
from rag import load_docs,chunk_text,create_embeddings,retrieve,build_prompt,generate_answer,retrieve_faiss
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
import os
from google import genai
from vector_store import store_chunks,query_chunks
class QueryRequest(BaseModel):
    question:str

app = FastAPI()
path ="data/sample.txt"

docs = load_docs(path)
chunk = chunk_text(docs)
model = SentenceTransformer("sentence-transformers/all-Minilm-l6-v2")
embeddings = create_embeddings(chunk,model)
client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])

storage = store_chunks(chunk,embeddings)
print(storage)

results = query_chunks("is Madonna an American singer",model,top_k=3)
""""
print(results["documents"])
print(results["distances"])
print(results["ids"])
"""
@app.post("/query")
async def query_rag(request:QueryRequest):
    ##t_chunks = retrieve(request.question,embeddings,chunk,top_k = 3)
    ##t_chunks = retrieve_faiss(embeddings,request.question,chunk)
    t_chunks = query_chunks(request.question,model,top_k=3)
    context = "\n\n".join(t_chunks)
    prompt = build_prompt(request.question,context)
    answer = generate_answer(prompt,client)
    return {"question" : request.question,
            "answer" : answer,
            "sources":t_chunks}