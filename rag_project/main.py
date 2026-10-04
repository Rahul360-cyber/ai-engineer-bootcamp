from pydantic import BaseModel
from rag import load_docs,chunk_text,retrieve,build_prompt,generate_answer,retrieve_faiss
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
import os
from google import genai
from vector_store import query_chunks,load_pdf,chunk_pdf_pages,create_embeddings,store_chunks,document_exists,meta_data_exists,delete_document_source,same_documents_version,collection
from pypdf import PdfReader
import hashlib


"""
path1 = "data/hyperspectral_project (2) (1).pdf"
text = load_pdf(path1)
print(text[0])
"""
"""
delete_document_source("hyperspectral project.pdf")
data = collection.get()
for metadata in data["metadatas"]:
    print(metadata)
"""
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

def get_file_hash(path):
        with open(path,"rb") as file:
            text = file.read()
            hash_object = hashlib.sha256(text)
            file_hash = hash_object.hexdigest()
        return file_hash


class QueryRequest(BaseModel):
    question:str


app = FastAPI()

def ingest_pdfs(pdf_filess,model):
    for i in pdf_filess:
        path = i
        source = os.path.basename(path)
        file_hash = get_file_hash(path)
        if same_documents_version(source,file_hash):
            print(f"{source} already exists.skipping")
            continue
        if document_exists(source):
            delete_document_source(source)
        text = load_pdf(path)
       
        for page in text:
            print(
                  "PAGE:", page["page"],
                  "TEXT LENGTH:", len(page["text"]) if page["text"] else 0
                 )
            print(
                 "PREVIEW:",
                 repr(page["text"][:100]) if page["text"] else "NO TEXT"
                 )
        print("source:",source)
        print("pages:", len(text))

        chunk = chunk_pdf_pages(text, source)
        print("chunks:",len(chunk))

        embeddings = create_embeddings(model,chunk)
        print("EMBEDDINGS SHAPE:", embeddings.shape)
        store_chunks(chunk,embeddings,file_hash)

model = SentenceTransformer("sentence-transformers/all-Minilm-l6-v2")
ingest_pdfs(pdf_filess,model)
client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])

"""
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
    context = "\n\n".join(context)
    sources =  []
    sources_info = {}
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