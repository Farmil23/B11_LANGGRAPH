import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model

from typing import Annotated
from typing_extensions import TypedDict

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages] # reducers, artinya tidak akan mengganti list yang ada namun di append terus menerus
    


llm=ChatGroq(model="openai/gpt-oss-120b")

def chatbot(state:State):
    return {
        "messages": [llm.invoke(state["messages"])]
    }

graph_builder = StateGraph(State)
graph_builder.add_node("llmchatbot", chatbot)

graph_builder.add_edge(START, "llmchatbot")
graph_builder.add_edge("llmchatbot", END)

graph=graph_builder.compile()

response=graph.invoke({
    "messages":"Hi"
})

print(response)