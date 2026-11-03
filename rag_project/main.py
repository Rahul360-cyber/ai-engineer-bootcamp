"""
from pydantic import BaseModel
from rag import load_docs,chunk_text,retrieve,build_prompt,generate_answer,retrieve_faiss
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
import os
from google import genai
from vector_store import query_chunks,load_pdf,chunk_pdf_pages,create_embeddings,store_chunks,document_exists,meta_data_exists,delete_document_source,same_documents_version,collection
from pypdf import PdfReader
from ingestion import ingest_pdfs
import hashlib
CHUNKER_VERSION = "semantic_v1"


path1 = "data/hyperspectral_project (2) (1).pdf"
text = load_pdf(path1)
print(text[0])


delete_document_source("hyperspectral project.pdf")
data = collection.get()
for metadata in data["metadatas"]:
    print(metadata)

def load_multiple_files(folders):
    pdf_files=[]

    files  = os.listdir(folders)
    for i in files:
         if i.endswith(".pdf"):
            path =  os.path.join(folders,i)
            pdf_files.append(path)
    return pdf_files


pdf_filess = load_multiple_files("data")

print(pdf_filess)



class QueryRequest(BaseModel):
    question:str


app = FastAPI()


model = SentenceTransformer("sentence-transformers/all-Minilm-l6-v2")
#ingest_pdfs(pdf_filess,model,CHUNKER_VERSION)
client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])


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
storage = stor
e_chunks(chunk,embeddings)
print(storage)
"""
""""
print(results["documents"])
print(results["distances"])
print(results["ids"])

results = query_chunks(
    "What is hyperspectral imaging?",
    model,
    top_k=3
)
print(results)
12
top_chunks = []
for i,j in zip(documents,distances):
    if j < 0.79:
    
        top_chunks.append(i)
print(top_chunks)
print(results["distances"][0])

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
    context = "\n\n".join(context)
    sources =  []
    sources_info = {}
    for i in t_chunks:
        source_info = {"sources":i["metadata"]["SOURCE"],
                       "pages": i["metadata"]["page"]}
        if source_info not in sources:
            sources.append(source_info)
    prompt = build_prompt(request.question,context)
    answer = generate_answer(prompt,client)
    return {"question" : request.question,
            "answer" : answer,
            "sources": sources}


@app.post("/retrieve")
async def retrieve_chunk(request: QueryRequest):
    t_chunks = query_chunks(request.question,model,top_k=3)
    if not t_chunks:
        return {"question" : request.question,
                "answer" : "i dont know based on the provided context ",
                "sources" : []}
    context = [ i["documents"] for i in t_chunks]
    context = "\n\n".join(context)
    sources =  []
    for i in t_chunks:
        source_info = {"sources":i["metadata"]["SOURCE"],
                       "pages": i["metadata"]["page"],
                       "distances":i["distances"]
                       }
        sources.append(sources_info)    

    return {"retrieved chunks": context,
            "source":sources,
    }

"""

 
from functools import lru_cache

from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from google import genai
import os

from rag import build_prompt, generate_answer
from vector_store import query_chunks
from agent import run_agent
from fastapi import HTTPException
from google.genai.errors import serverError

app = FastAPI(title="Document Intelligence RAG API")


class QueryRequest(BaseModel):
    question: str


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )


@lru_cache(maxsize=1)
def get_gemini_client():
    return genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )


@app.post("/retrieve")
async def retrieve_chunk(request: QueryRequest):
    model = get_embedding_model()

    t_chunks = query_chunks(
        request.question,
        model,
        top_k=3
    )

    if not t_chunks:
        return {
            "question": request.question,
            "answer": "I don't know based on the provided context.",
            "sources": []
        }

    context = "\n\n".join(
        item["documents"] for item in t_chunks
    )

    sources = []

    for item in t_chunks:
        sources.append({
            "sources": item["metadata"]["SOURCE"],
            "pages": item["metadata"]["page"],
            "distances": item["distances"]
        })

    return {
        "retrieved chunks": context,
        "source": sources
    }


@app.post("/query")
async def query_rag(request: QueryRequest):
    model = get_embedding_model()

    t_chunks = query_chunks(
        request.question,
        model,
        top_k=3
    )

    if not t_chunks:
        return {
            "question": request.question,
            "answer": "I don't know based on the provided context.",
            "sources": []
        }

    context = "\n\n".join(
        item["documents"] for item in t_chunks
    )

    sources = []

    for item in t_chunks:
        source_info = {
            "sources": item["metadata"]["SOURCE"],
            "pages": item["metadata"]["page"]
        }

        if source_info not in sources:
            sources.append(source_info)

    prompt = build_prompt(request.question, context)
    client = get_gemini_client()
    answer = generate_answer(prompt, client)

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources
    }
@app.post("/agent/query")
def agent_response(request : QueryRequest):
       try:
            response = run_agent(request.question)
       except serverError as exc:
            raise HTTPException(status_code=503,detail="the model is temporarily unavailable")

       return {"question": request.question,
                    "answer" : response}