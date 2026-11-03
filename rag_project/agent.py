from vector_store import query_chunks
from sentence_transformers import SentenceTransformer
from functools import lru_cache
from google import genai
from google.genai import types
import os

def run_agent(question:str) -> str:
    client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(model="gemini-3.8-flash",contents = question,config = types.GenerateContentConfig(tools =[search_documents]))
    return response.text

@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

def search_documents(query : str) -> str:
    """search indesed pdf documents for information relevant to a query"""
    print(f"[TOOL CALLED] search_documents(query={query!r})")
    model = get_embedding_model()

    t_chunks = query_chunks(
        query,
        model,
        top_k=3
    )

    if not t_chunks:
        return "I don't know based on the provided context."
    sources = []

    for item in t_chunks:
        source_info = {
            "sources": item["metadata"]["SOURCE"],
            "pages": item["metadata"]["page"],
            "content":item["documents"]
        }

        if source_info not in sources:
            sources.append(source_info)
    return str(sources)

if __name__ =="__main__":
    answer = run_agent("what model architecture is described in  my hypercpectral thesis?")
    print("AGENT ANSWER", answer)