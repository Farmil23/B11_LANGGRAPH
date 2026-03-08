from flask import Flask, jsonify, request, Response, stream_with_context
from agent.graph import app_graph
import time
import threading
import json
from datetime import datetime

app = Flask(__name__)
from pymongo.mongo_client import MongoClient
uri = "mongodb://dbFarmil:test123@ac-qb2o5by-shard-00-00.7nrschk.mongodb.net:27017,ac-qb2o5by-shard-00-01.7nrschk.mongodb.net:27017,ac-qb2o5by-shard-00-02.7nrschk.mongodb.net:27017/?ssl=true&replicaSet=atlas-brhf89-shard-0&authSource=admin&appName=Cluster0"
client = MongoClient(uri)
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['TEST']
chat_collection = db["chat_history"]



def save_chat_to_mongodb(thread_id, user_input, ai_response):
    document = {
        "thread_id": thread_id,
        "timestamp": datetime.utcnow(),
        "messages": [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_response}
        ]
    }
    # Update atau Insert (Upsert) berdasarkan thread_id
    chat_collection.insert_one(document)
    print(f" Log: Chat {thread_id} berhasil disimpan ke MongoDB.")

@app.route('/chat', methods=["POST"])
def chat():
    thread_id = threading.get_ident()
    
    data = request.json
    user_input = data.get("message", "")

    initial_state = {"input" : user_input}
    last = time.time()
    
    user_id = data.get("user_id", "default_user")
    config = {"configurable": {"thread_id": user_id}}
    
    app = app_graph
    result = app.invoke(initial_state, config=config)
    now = time.time() - last
          
    return jsonify({
        "status" : "Success",
        "reply" : result["response"],
        "latency" :  now,
        "user" : thread_id
    })
    
@app.route('/chat-stream', methods=["POST"])
def chat_stream():
    data = request.json
    user_input = data.get("message", "")

    initial_state = {"input" : user_input}
    last = time.time()
    thread_id = threading.get_ident()
    config = {"configurable": {"thread_id": thread_id}}
    app = app_graph
    
    def generate():
        final_response = ""
        for event in app_graph.stream(initial_state, config, stream_mode="values"):
            final_response = event.get("response", "")
            yield f"data: {json.dumps(event)}\n\n"
        
        # SETELAH STREAM SELESAI: Simpan ke MongoDB
        if final_response:
            save_chat_to_mongodb(thread_id, user_input, final_response)   

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
        