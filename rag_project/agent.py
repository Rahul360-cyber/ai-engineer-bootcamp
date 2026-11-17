from vector_store import query_chunks
from sentence_transformers import SentenceTransformer
from functools import lru_cache
from google import genai
from google.genai import types
import os
import json 

def run_agent(question:str) -> str:
    client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(model="gemini-3.8-flash",contents = question,config = types.GenerateContentConfig(tools =[search_documents]))
    return response.text
    
def run_agent_manually(question: str) -> str:
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    config = types.GenerateContentConfig(
        tools=[search_documents],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        )
    )
    max_iterations = 5
    tool_rounds = 1
    

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
        config=config)
    
    history =[]
    history = [types.Content(role = "user",parts = [types.part.from_text(text=question)])]
    while tool_rounds < max_iterations : 

                response = client.models.generate_content(
                           model="gemini-2.5-flash",
                           contents= history,
                           config=config
                            )
                if not response.function_calls:
                    return response.text or ""
                function_call = response.function_calls[0]
                if function_call.name != "search_documents":
                    raise ValueError("unsupported tool request")
                args = function_call.args or {}
                query = args.get("query")
                if not isinstance(query,str) or not query.strip():
                    raise ValueError("Invalid search query")

                tool_result = search_documents(query)
                tool_response = types.Part.from_function_response(
                name="search_documents",
                response={"result": tool_result}
                )
                history.append(response.candidates[0].content)
                history.append(types.Content(role = "tool",parts = [tool_response]))
                
                tool_rounds = tool_rounds + 1
                
    contents = [types.Content(role = "user", parts = [types.Part.from_text(text=question)]),
                response.candidates[0].content,
                types.Content(role="tool",parts = [tool_response])]
    
    tool_rounds =  tool_rounds + 1
    
    next_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=config
    )

    print("FUNCTION CALLS:", response.function_calls)

    if not next_response.function_calls:
        return next_response.text or ""

    return "Tool call requested; loop not implemented yet."
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
    return json.dumps(sources)





if __name__ =="__main__":
    answer = run_agent("what model architecture is described in  my hypercpectral thesis?")
    print("AGENT ANSWER", answer)