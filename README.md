
# 🦜🕸️ From Chains to Graphs: AI Agents Bootcamp Journey

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-v0.1-green?style=for-the-badge&logo=chainlink&logoColor=white)](https://python.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-orange?style=for-the-badge&logo=diagram&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Status](https://img.shields.io/badge/Status-Learning_Process-yellow?style=for-the-badge)]()

> **"Dokumentasi perjalanan teknis saya dalam menguasai Arsitektur Kognitif AI: Dimulai dari Chain linier sederhana hingga Multi-Agent Systems yang kompleks menggunakan LangGraph."**

Repositori ini bukan sekadar kumpulan kode, melainkan jejak langkah pembelajaran intensif (Bootcamp Mandiri) untuk memahami bagaimana *Large Language Models* (LLM) dapat diorkestrasi untuk menyelesaikan tugas dunia nyata.

---

## 🗺️ Peta Perjalanan (Roadmap)

Perjalanan ini dibagi menjadi beberapa fase evolusi kode:

### 🟢 Fase 1: The Foundation (LangChain Basics)
Memahami blok bangunan dasar: *Prompt Templates*, *Models*, dan *Output Parsers*.
* 📂 `LangChain/`: Eksperimen dasar koneksi ke OpenAI dan manipulasi prompt.
* 📂 `LangChain/3.2-DataIngestion`: Teknik memuat data dari PDF, TXT, dan XML.

### 🟡 Fase 2: Memory & Retrieval (RAG Systems)
Memberikan "ingatan" jangka panjang dan konteks khusus pada AI.
* 📂 `LangChain/faiss`: Implementasi Vector Database lokal untuk pencarian semantik cepat.
* 📂 `vectorretriever`: Eksperimen mendalam tentang *retrieval strategies*.
* **Proyek Utama**: Sistem RAG untuk "chat" dengan dokumen PDF.

### 🔴 Fase 3: Chains & Chatbots
Menggabungkan ingatan dan logika dalam percakapan.
* 📂 `ConverChatbotQA`: Membangun chatbot yang memiliki *Conversational Memory* (mengingat percakapan sebelumnya).

### 🟣 Fase 4: Agentic Workflow (LangGraph) 🚧 *Current Focus*
Transisi dari DAG (Directed Acyclic Graph) ke siklus (Cycles).
* Membangun agen yang bisa *reasoning*, *acting*, dan melakukan *self-correction*.
* Implementasi `StateGraph` dan `Nodes`.
* *Coming soon: Multi-Agent Collaboration projects.*

---

## 🛠️ Proyek Unggulan

Berikut adalah implementasi nyata yang telah dibangun dalam repositori ini:

### 1. 📄 ScholarSync (Document RAG)
Sistem tanya-jawab cerdas yang memungkinkan pengguna berinteraksi dengan jurnal ilmiah atau laporan bisnis.
* **Fitur**: Upload PDF, *Chunking*, Embedding, dan QA Chain.
* **Studi Kasus**: Diuji menggunakan paper *"Attention Is All You Need"* dan *"LLM Papers"*.
* **Lokasi**: `/DOCUMENT_PROJCT`

### 2. 💰 AI Financial Analyst
Asisten AI yang dirancang untuk membaca laporan keuangan/bisnis dan memberikan *insight* strategis.
* **Studi Kasus**: Menganalisis dokumen *"The AdSense Report"* untuk strategi monetisasi.
* **Lokasi**: `/AI_ASSISTENT_EARN`

### 3. 🤖 Conversational Memory Bot
Prototipe chatbot yang tidak mereset konteks setiap kali ditanya. Menggunakan *buffer memory* untuk menjaga alur diskusi tetap natural.
* **Lokasi**: `/ConverChatbotQA`

---

## 🧰 Teknologi & Tools

Stack teknologi yang digunakan dalam bootcamp ini:

* **Core**: Python, LangChain, LangGraph.
* **LLM Provider**: OpenAI (GPT-3.5/GPT-4), HuggingFace (Open Source Models).
* **Vector Store**: FAISS (Local), ChromaDB.
* **Tools**: PyPDF (Document Loading), Pandas (Data Manipulation).

---

## 🚀 Cara Menjalankan

Ingin mencoba kode di laptop Anda sendiri? Ikuti langkah ini:

1.  **Clone Repositori**
    ```bash
    git clone [https://github.com/Farmil23/langchain-series.git](https://github.com/Farmil23/langchain-series.git)
    cd langchain-series
    ```

2.  **Setup Environment**
    Disarankan menggunakan Virtual Environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # Untuk Mac/Linux
    venv\Scripts\activate     # Untuk Windows
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfigurasi API Key**
    Buat file `.env` dan masukkan kunci rahasia Anda:
    ```env
    OPENAI_API_KEY=sk-proj-xxxx...
    ```

5.  **Jalankan Notebook/Script**
    Masuk ke folder proyek yang diinginkan dan jalankan via Jupyter atau Terminal:
    ```bash
    cd DOCUMENT_PROJCT
    python main.py
    ```

---

## 📈 What's Next?

Langkah selanjutnya dalam perjalanan **LangGraph**:
- [ ] Membangun **Reflection Agent** (Agen yang mengkritik outputnya sendiri).
- [ ] Implementasi **Human-in-the-loop** (Persetujuan manusia sebelum eksekusi tool sensitif).
- [ ] Membuat **Multi-Agent Coding Team** (Satu agen menulis kode, agen lain melakukan testing).

---

<div align="center">
  <p>Dibuat dengan 💻 dan ☕ oleh <b>Farhan Kamil Hermansyah - 152024150</b> sebagai bagian dari perjalanan menjadi AI Engineer.</p>
</div>

```

