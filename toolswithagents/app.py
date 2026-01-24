
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.agents import create_agent
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from langchain_community.callbacks import StreamlitCallbackHandler
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()


api_key_groq = os.getenv("GROQ_API_KEY")
api_key_openai = os.getenv("OPENAI_API_KEY")

# Arxiv dan wiki api wrapper
arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=300)
wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=300)

# Arxiv dan Wiki Tools
wiki = WikipediaQueryRun(api_wrapper=wiki_wrapper)
arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)

# Search Tools
search = DuckDuckGoSearchRun(name="Search")

# =============================
# ======= Streamlit App =======
# =============================

st.title(" Aplikasi agent dengan search engine")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": " Hi, aku adalah chatbot yang bisa mencari dan search ke google, ada yang bisa aku bantu?"}
    ]

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg['content'])

if prompt:= st.chat_input(placeholder = "Apa itu machine learning?"):
    st.session_state.messages.append({"role": "user", "content" : prompt})
    st.chat_message("user").write(prompt)

    # LLM Model
    model = ChatGroq(model_name="openai/gpt-oss-120b", api_key=api_key_groq, streaming=True)
    embedding = OpenAIEmbeddings()
    tools = [wiki, arxiv, search]

    agent = create_agent(
        tools=tools,
        model=model,

    )

    chat_history = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = agent.invoke(
            {"messages": chat_history},
            {"callbacks" : [st_cb]}
        )

        # Ambil respon terakhir dari agent
        pesan_terakhir_content = response["messages"][-1].content
        
        # Simpan ke session state agar tidak hilang saat rerun berikutnya
        st.session_state.messages.append({"role": 'assistant', "content": pesan_terakhir_content})
        st.write(pesan_terakhir_content)
         
 

