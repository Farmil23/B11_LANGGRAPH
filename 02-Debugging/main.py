from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import AnyMessage
import os
from dotenv import load_dotenv
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGSMITH_API_KEY')
os.environ['LANGSMITH_ENDPOINT'] = os.getenv('LANGSMITH_ENDPOINT')
os.environ['LANGSMITH_TRACING'] = os.getenv('LANGSMITH_TRACING')
os.environ['LANGSMITH_PROJECT'] = "ReAct Agents by Farmil"

os.environ['LANGCHAIN_TRACING_V2'] = "true" 
os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY') 
os.environ['LANGCHAIN_PROJECT'] = "ReAct Agents by Farmil"


def tools_setup(top_k_results=2, doc_content_chars_max=500):
    wiki_wrapper = WikipediaAPIWrapper(top_k_results=top_k_results, doc_content_chars_max=doc_content_chars_max)
    wiki = WikipediaQueryRun(api_wrapper=wiki_wrapper)
    
    arxiv_wrapper = ArxivAPIWrapper(top_k_results=top_k_results, doc_content_chars_max=doc_content_chars_max)
    arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)
    
    tavily = TavilySearch()
    
    return [wiki, arxiv, tavily]

def llm_with_tools(tools, model_name="gpt-5-nano-2025-08-07"):
    model = ChatOpenAI(model_name=model_name, streaming=True)
    llm_with_tools = model.bind_tools(tools)
    
    return llm_with_tools

def graph_builder(llm_with_tools, tools):
    
    class State(TypedDict):
        messages : Annotated[list[AnyMessage], add_messages]
        
    def tool_calling_llm(state:State) -> State:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages" : [response]}
    
    builder = StateGraph(State)
    
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_node("tools", ToolNode(tools))
    
    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges("tool_calling_llm", tools_condition)
    builder.add_edge("tools", "tool_calling_llm")
    
    memory = MemorySaver()
    
    builder_graph = builder.compile(checkpointer=memory)
    return builder_graph

def setting_config(thread_id = 1):
    config = {"configurable" : {"thread_id" : thread_id}}
    return config



if __name__ == '__main__':
    tools = tools_setup()
    llm_with_tools = llm_with_tools(tools)
    agent = graph_builder(llm_with_tools=llm_with_tools, tools=tools)
    config = setting_config()

    while True:
        query = input("Masukkan pertanyaan kamu: ")
        
        if query == "exit":
            break
        
        response = agent.invoke({"messages" : query}, config = config)
        
        result = response["messages"][-1].content
        
        print(result)
    






