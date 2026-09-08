from pydantic import BaseModel
from rag import load_docs,chunk_text,retrieve,build_prompt,generate_answer,retrieve_faiss
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
import os
from google import genai
from vector_store import query_chunks,load_pdf,chunk_pdf_pages,create_embeddings,store_chunks
from pypdf import PdfReader

path1 = "data/hyperspectral_project (2) (1).pdf"
text = load_pdf(path1)
print(text[0])


class QueryRequest(BaseModel):
    question:str

app = FastAPI()

#path ="data/sample.txt"
#docs = load_docs(path)
path1 = "data/hyperspectral_project (2) (1).pdf"
text = load_pdf(path1)
#chunk = chunk_text(docs)
chunk = chunk_pdf_pages(text,"hyperspectral project.pdf")
model = SentenceTransformer("sentence-transformers/all-Minilm-l6-v2")
print(type(chunk[0]))
print(type(chunk[0]["text"]))
embeddings = create_embeddings(model,chunk)
client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])
storage = store_chunks(chunk,embeddings)
"""
storage = stor
e_chunks(chunk,embeddings)
print(storage)
"""
""""
print(results["documents"])
print(results["distances"])
print(results["ids"])
"""
results = query_chunks(
    "What is hyperspectral imaging?",
    model,
    top_k=3
)
print(results)
"""
top_chunks = []
for i,j in zip(documents,distances):
    if j < 0.79:
        top_chunks.append(i)
print(top_chunks)
print(results["distances"][0])
"""
@app.post("/query")
async def query_rag(request:QueryRequest):
    ##t_chunks = retrieve(request.question,embeddings,chunk,top_k = 3)
    ##t_chunks = retrieve_faiss(embeddings,request.question,chunk)
    t_chunks = query_chunks(request.question,model,top_k=3)
    if not t_chunks:
        return {"question" : request.question,
                "answer" : "i dont know based on the provided context ",
                "sources" : []}
    context = [ i["documents"] for i in t_chunks]
    context = "\n\n".join(t_chunks)
    sources =  []
    for i in t_chunks:
        source_info = {"sources":i["metadata"]["SOURCE"],
                       "pages": i["metadata"]["page"]}
        if source_info not in sources:
            sources.append(sources_info)
    prompt = build_prompt(request.question,context)
    answer = generate_answer(prompt,client)
    return {"question" : request.question,
            "answer" : answer,
            "sources": sources}