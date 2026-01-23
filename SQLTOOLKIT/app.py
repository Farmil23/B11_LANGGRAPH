import streamlit as st
from pathlib import Path
from langchain.agents import create_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq
import os
from langgraph.checkpoint.memory import InMemorySaver


system_prompt = """
    You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct {dialect} query to run,
    then look at the results of the query and return the answer. Unless the user
    specifies a specific number of examples they wish to obtain, always limit your
    query to at most {top_k} results.

    You can order the results by a relevant column to return the most interesting
    examples in the database. Never query for all the columns from a specific table,
    only ask for the relevant columns given the question.

    You MUST double check your query before executing it. If you get an error while
    executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
    database.

    To start you should ALWAYS look at the tables in the database to see what you
    can query. Do NOT skip this step.

    Then you should query the schema of the most relevant tables.
""".format(
    dialect="sqlite",
    top_k=5,
)

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

st.set_page_config(page_title="Farmiledb: Chat with SQL With Agent")
st.title("Farmiledb: Chat with SQL With Agent")

radio_opt = ["Use SQLite3 Database - Student.db ( Local )", "Connect to your MySQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB Which you want to chat", options = radio_opt)

if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide MySQL Hostname")
    mysql_user = st.sidebar.text_input("MySQL Username")
    mysql_password = st.sidebar.text_input("MySQL Password")
    mysql_db = st.sidebar.text_input("Mysql Database")
else:
    db_uri = LOCALDB

api_key = st.sidebar.text_input(label="Groq API Key", type="password")

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please add the Groq API Key")

## LLM MODEL 
model = ChatGroq(model_name="openai/gpt-oss-120b", api_key=api_key, streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        dbfilepath= (Path(__file__).parent.parent/"student.db").absolute()
        print(dbfilepath)

        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri = True)
        return SQLDatabase(create_engine("sqlite:///", creator =creator))
 

    elif db_uri == MYSQL:
        if not (mysql_db and mysql_host and mysql_user):
            st.error("Please Provide all MySQL Connection Details.")
            st.stop()

        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

if db_uri == MYSQL:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_uri)

toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
    checkpointer = InMemorySaver()
)

if "messages" not in st.session_state or st.sidebar.button("Clear Message History"):
    st.session_state["messages"] = [{
        "role": "assistant", "content" : "How Can I Help You?"
    }]

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])


user_query = st.chat_input(placeholder="Ask Anything from the database")

if user_query:
    st.session_state.messages.append({"role" : "user", "content": user_query})
    st.chat_message("user").write(user_query)

    config = {"configurable": {"thread_id": "1"}}
    
    chat_history = []
    for msg in st.session_state.messages:
        chat_history.append((msg["role"], msg["content"]))

    with st.chat_message("assistant"):
        response = agent.invoke(
            {"messages": chat_history},
            config=config
        )

        response_final = response["messages"][-1].content

        st.session_state.messages.append({"role": "assistant", "content": response_final})
        st.write(response_final)

        