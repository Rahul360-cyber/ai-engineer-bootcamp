from langgraph.graph import StateGraph,START,END
from typing import TypedDict
from agent import search_documents
import json 
from google import genai
from google.genai import types
import os

MAX_TOOL_CALLS = 5

class AgentState(TypedDict):
    question:str
    messages : list[types.Content]
    answer:str
    pending_tool : dict | None
    tool_rounds : int 

def agent_node(state:AgentState) -> dict:
    client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(model = "gemini-2.5-flash",contents = state["messages"],config =types.GenerateContentConfig(tools=[search_documents],automatic_function_calling = (types.AutomaticFunctionCallingConfig(disable=True)),),)
    calls = response.function_calls or []

    if not calls:
        return {
            "answer": response.text or "",
            "pending_tool":None
        }
    if state["tool_rounds"] >= MAX_TOOL_CALLS:
        return {
            "answer":"Stopped: maximum tool_call limit reached.",
            "pending_tool":None
        }
    if len(calls) != 1:
        raise ValueError("this graph currently support one tool call per turn ")
    call = calls[0]

    if call.name!= "search_documents":
        raise ValueError(f"Unsupported tool:{call.name}")

    args = call.args or {}
    query = args.get("query")
    if not isinstance(query,str) or not query.strip():
        raise ValueError("invalid retrieval query")

    model_context =response.candidates[0].content

    return{
        "messages" : state["messages"] + [model_context],
        "pending_tool" : {"name":call.name,
                          "query":query,}

    }

def route_agent(state:AgentState) -> str : 
    if state["pending_tool"] is not None:
        return "tool"
    return "end"

def tool_node(state : AgentState) -> dict:
    tool = state["pending_tool"]

    if tool is None:
        raise ValueError("no pending tool call")

    if tool["name"] != "search_documents":
        raise ValueError("unsupported tool")
    result = search_documents(tool["query"])

    tool_response = types.Part.from_function_response(name = "search_documents", response = {"result" : result},)
    return {"messages" : state["messages"] + [types.Content (role="tool",parts=[tool_response],)], 
            "pending tool": None , "tool_rounds":state["tool_rounds"]+1}
"""
def retrieve_node(state: AgentState) -> dict:
    question = state["question"]
    answer = search_documents(question)
    return {"context": answer}

def answer_node(state: AgentState) -> dict:
    question = state["question"]
    context = state["context"]
    
    
    return {"answer":f"received: {question}"}
"""

builder = StateGraph(AgentState)
builder.add_node("agent" , agent_node)
builder.add_node("tool" , tool_node)
builder.add_edge(START,"agent")
builder.add_conditional_edges("agent",route_agent,{"tool":"tool",
                                                   "end":END},)
builder.add_edge("tool","agent")

graph = builder.compile()


if __name__ == "__main__":
    question = "what architecture does my thesis use?"

    initial_state = {"question":question,
                     "messages":[types.content(role = "user",parts = [types.part,from_text(text=question)],)],
                     "answer":"",
                     "pending _tool":None,
                     "tool_rounds":0,}
    result = graph.invoke(initial_state,config ={"recursion_limit":15},)
    print("\nFINAL ANSWER")
    print(result["answer"])

    
    print("\n TOOL ROUNDS")
    print(result["tool_rounds"])
