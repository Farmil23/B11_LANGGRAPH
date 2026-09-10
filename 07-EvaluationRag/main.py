import os
import json
import random
import operator
from typing import Annotated, List, Sequence, TypedDict, Union
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()

# --- KONFIGURASI API KEY ---
# Pastikan key ini ada di .env atau di-set manual di sini
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Konfigurasi LangSmith
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Evaluasi-RAG-HR-Fixed" # Ganti nama project jika mau
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")

# --- LIST FILE DOKUMEN ---
# Masukkan semua nama file PDF kamu di sini
PDF_FILES = [
    "Andi.pdf",
    "siti.pdf",
    "budi.pdf"
    # "cv_budi.pdf", 
]

# --- IMPORTS ---
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever 
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_community.tools.tavily_search import TavilySearchResults

# Import untuk Graph
from langgraph.graph import StateGraph, END

# Import untuk Evaluasi (FIXED VERSION)
from langsmith import Client
from langsmith.evaluation import evaluate
from langchain_classic.evaluation import load_evaluator # Kita pakai ini sebagai pengganti class yang error

# ==========================================
# BAGIAN 1: MEMBANGUN ARSITEKTUR GRAPH (RAG)
# ==========================================

print("--- 1. Memuat Dokumen & Setup Retriever ---")

docs = []
for file_path in PDF_FILES:
    if os.path.exists(file_path):
        print(f"📄 Memuat file: {file_path}...")
        loader = PyMuPDFLoader(file_path)
        docs.extend(loader.load())
    else:
        print(f"⚠️ Warning: File tidak ditemukan: {file_path}")

# Fallback data dummy jika tidak ada file
if not docs:
    print("⚠️ Tidak ada dokumen. Menggunakan data dummy.")
    from langchain_core.documents import Document
    docs = [Document(page_content="Andi adalah Senior DevOps Engineer yang ahli Kubernetes dan Docker.")]

# Split Text
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=50)
doc_splits = text_splitter.split_documents(docs)
print(f"✅ Total Chunks: {len(doc_splits)}")

# Setup Hybrid Retriever
embedding = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(doc_splits, embedding)
retriever = EnsembleRetriever(
    retrievers=[
        BM25Retriever.from_documents(doc_splits, k=3),
        vectorstore.as_retriever(search_kwargs={"k": 3})
    ], weights=[0.5, 0.5]
)

# Setup LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- DEFINISI GRAPH STATE ---
class GraphState(TypedDict):
    question: str
    generation: str
    documents: List[str]

# --- NODES & LOGIC ---

def retrieve(state):
    print("--- NODE: RETRIEVE ---")
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

def grade_documents(state):
    print("--- NODE: GRADE DOCUMENTS ---")
    question = state["question"]
    documents = state["documents"]
    
    class Grade(BaseModel):
        binary_score: str = Field(description="yes atau no")

    structured_llm_grader = llm.with_structured_output(Grade)
    system = "Kamu adalah penilai relevansi. Jika dokumen mengandung keyword terkait pertanyaan, nilai 'yes'."
    grade_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Doc: {document}\n\nQuestion: {question}")
    ])
    grader = grade_prompt | structured_llm_grader
    
    filtered_docs = []
    for d in documents:
        score = grader.invoke({"question": question, "document": d.page_content})
        if score.binary_score == "yes":
            filtered_docs.append(d)
    
    return {"documents": filtered_docs, "question": question}

def generate(state):
    print("--- NODE: GENERATE ---")
    question = state["question"]
    documents = state["documents"]
    
    # Gabung konteks
    context = "\n\n".join([d.page_content for d in documents])
    
    prompt = ChatPromptTemplate.from_template(
        "Jawab pertanyaan berdasarkan konteks berikut:\n\n{context}\n\nPertanyaan: {question}"
    )
    chain = prompt | llm
    prediction = chain.invoke({"context": context, "question": question})
    return {"generation": prediction.content}

def web_search(state):
    print("--- NODE: WEB SEARCH ---")
    question = state["question"]
    try:
        tool = TavilySearchResults(k=3)
        docs = tool.invoke({"query": question})
        web_results = "\n".join([d["content"] for d in docs])
    except:
        web_results = "Pencarian web gagal."
        
    from langchain_core.documents import Document
    return {"documents": [Document(page_content=web_results)], "question": question}

def decide_to_generate(state):
    print("--- EDGE: DECISION ---")
    if not state["documents"]:
        return "web_search"
    return "generate"

# --- BUILD GRAPH ---
workflow = StateGraph(GraphState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_node("web_search", web_search)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {"web_search": "web_search", "generate": "generate"},
)
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()

# ==========================================
# BAGIAN 2: EVALUASI (MANUAL WRAPPER FIX)
# ==========================================

def run_evaluation():
    print("\n\n=== MEMULAI EVALUASI ===\n")
    client = Client()
    dataset_name = "HR_RAG_Fixed_Dataset"

    # A. GENERATE DATASET OTOMATIS
    if not client.has_dataset(dataset_name=dataset_name):
        print("Dataset baru sedang dibuat...")
        qa_llm = ChatOpenAI(model="gpt-4o", temperature=0)
        prompt = ChatPromptTemplate.from_template(
            "Buat JSON 1 pasang 'question' dan 'answer' dari teks: {context}"
        )
        chain = prompt | qa_llm
        
        inputs, outputs = [], []
        # Ambil sampel acak
        sample_chunks = random.sample(doc_splits, min(len(doc_splits), 5))
        
        for chunk in sample_chunks:
            try:
                res = chain.invoke({"context": chunk.page_content})
                clean = res.content.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean)
                inputs.append({"question": data["question"]})
                outputs.append({"answer": data["answer"]})
                print(f"Generated: {data['question']}")
            except: continue
        
        if inputs:
            dataset = client.create_dataset(dataset_name=dataset_name)
            client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)

    # B. TARGET FUNCTION (Wrapper Graph)
    def target(inputs: dict) -> dict:
        response = app.invoke({"question": inputs["question"]})
        
        # Format dokumen untuk evaluator
        retrieved = []
        if response.get("documents"):
            for d in response["documents"]:
                content = d.page_content if hasattr(d, "page_content") else str(d)
                retrieved.append(content)
                
        return {
            "answer": response["generation"],
            "retrieved_docs": retrieved # List of strings
        }

    # C. DEFINISI EVALUATOR MANUAL (SOLUSI ERROR IMPORT)
    # --------------------------------------------------
    # Kita buat fungsi wrapper sendiri menggunakan load_evaluator dari langchain
    
    eval_llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # 1. QA Correctness Evaluator Wrapper
    qa_eval_chain = load_evaluator("qa", llm=eval_llm)

    def qa_evaluator_wrapper(run, example):
        """Menilai apakah jawaban benar sesuai referensi"""
        # Ambil data dari run (hasil prediksi) dan example (kunci jawaban)
        prediction = run.outputs.get("answer")
        reference = example.outputs.get("answer")
        input_question = example.inputs.get("question")
        
        # Jalankan evaluasi
        res = qa_eval_chain.evaluate_strings(
            prediction=prediction,
            reference=reference,
            input=input_question
        )
        # Return format skor (0.0 - 1.0)
        score = res.get("score", 0)
        # Normalisasi skor jika outputnya bukan angka (kadang string 'CORRECT')
        return {"key": "correctness", "score": score}

    # 2. Context Faithfulness Evaluator Wrapper
    context_eval_chain = load_evaluator("context_qa", llm=eval_llm)

    def context_evaluator_wrapper(run, example):
        """Menilai apakah jawaban berdasarkan konteks dokumen (anti-halusinasi)"""
        prediction = run.outputs.get("answer")
        input_question = example.inputs.get("question")
        retrieved_docs = run.outputs.get("retrieved_docs")
        
        # Gabung list dokumen jadi satu string panjang untuk evaluator
        context_str = "\n\n".join(retrieved_docs) if isinstance(retrieved_docs, list) else str(retrieved_docs)

        res = context_eval_chain.evaluate_strings(
            prediction=prediction,
            input=input_question,
            reference=context_str
        )
        score = res.get("score", 0)
        return {"key": "faithfulness", "score": score}

    # D. JALANKAN EVALUASI
    print("Menjalankan Evaluasi di LangSmith...")
    
    results = evaluate(
        target,
        data=dataset_name,
        evaluators=[qa_evaluator_wrapper, context_evaluator_wrapper],
        experiment_prefix="RAG-Run-Fixed",
    )
    
if __name__ == "__main__":
    run_evaluation()