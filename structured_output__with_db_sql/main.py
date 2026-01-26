import sqlite3
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
load_dotenv()


def init_db():
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        ipk FLOAT NOT NULL
    ) """)
    conn.commit()
    return conn
   
class CVData(BaseModel):
    name: str = Field(description="Name of the candidate")
    age: int = Field(description="Age of the candidate")
    ipk: float = Field(description="IPK of the candidate")

def process_CV_data(cv:str):
    model = ChatGroq(model_name="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))

    structured_llm = model.with_structured_output(CVData)

    try:
        response = structured_llm.invoke(f"Proses data tersebut dan ambil nama, age dan ipk dari {cv} tersebut")
        return response
    except Exception as e:
        print(f"Error processing CV data: {e}")
        return None

def save_to_sql(data:CVData):
    conn = init_db()
    cursor = conn.cursor() 
    cursor.execute("""
    INSERT INTO users (name, age, ipk)
    VALUES (?, ?, ?)
    """, (data.name, data.age, data.ipk))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    list_cv = [
        # 1. Narasi Standar
        "Perkenalkan saya Andi Pratama, usia saat ini 23 tahun. Saya lulusan Teknik Sipil dengan IPK 3.55.",
        
        # 2. Format Key-Value
        "Nama: Budi Santoso | Umur: 21 | IPK Terakhir: 3.20 | Skill: Python",
        
        # 3. Bahasa Inggris
        "My name is Citra Lestari. I am a 22 years old fresh graduate with a GPA of 3.88 from UI.",
        
        # 4. Format Chatting / Informal
        "halo kak, kenalin aku Diki. umurku baru 20 thn nih, kemaren lulus d3 dapet ipk 3.45. ada lowongan ga?",
        
        # 5. Data Tersembunyi di Tengah Kalimat
        "Meskipun sempat cuti kuliah, Eka Saputra (25 tahun) akhirnya berhasil wisuda dengan raihan IPK 3.10 yang memuaskan.",
        
        # 6. Format Singkat / Baris
        "Fajar / 24 th / 3.75 / Jakarta Selatan", 
        
        # 7. Penulisan IPK menggunakan Koma
        "Gita Pertiwi. Usia 22. Lulusan Sastra Jepang dengan nilai indeks prestasi 3,65.",
        
        # 8. Format Laporan / Header
        "[DATA KANDIDAT] Hendi Gunawan. USIA: 26. PENDIDIKAN: S1 Informatika (IPK 3.30).",
        
        # 9. Narasi Panjang
        "Saya adalah Indah Permata, seorang desainer grafis yang bersemangat. Di usia saya yang ke-23 ini, saya membawa portofolio kuat dan latar belakang akademis dengan IPK 3.90.",
        
        # 10. Format Terbalik (IPK duluan)
        "IPK 3.50 berhasil diraih oleh Joko Anwar yang saat ini genap berusia 21 tahun.",
        
        # 11. Bahasa Campuran (Indo-Inggris)
        "Name: Kartika Sari. Age: 22 tahun. My cumulative GPA is 3.72.",
        
        # 12. Format Email
        "Subjek: Lamaran Kerja Lukman (24). Isi: Terlampir transkrip nilai dengan IPK 3.15.",
        
        # 13. Data dengan Distraksi Angka Lain
        "Maya (22 th) memiliki pengalaman kerja 2 tahun dan mengharapkan gaji 5 juta. IPK-nya 3.60.",
        
        # 14. Typo / Singkatan
        "Naufal, umr 23. lulusan itb predikat cumlaude (3.95). siap kerja.",
        
        # 15. Format List Bullet
        "- Kandidat: Olivia\n- Usia: 21\n- Skor Akademik: 3.40",
        
        # 16. Narasi Orang Ketiga
        "Kandidat bernama Putra ini sangat potensial. Usianya masih muda, 20 tahun, namun IPK-nya sudah 3.82.",
        
        # 17. Format Tanpa Label Jelas (Hard Mode)
        "Qory / 22 / 3.25",
        
        # 18. Fokus Prestasi
        "Rama, 23 tahun. Juara lomba coding nasional. Akademis kuat dengan IPK 3.78.",
        
        # 19. Format Surat Resmi
        "Yang bertanda tangan di bawah ini, Siska (24 tahun), menyatakan bahwa benar memiliki IPK 3.05.",
        
        # 20. Variasi Nama Panggilan
        "Panggil saja Tio. Umur 21. Kuliah lancar jaya dapet 3.58."
    ]
    
    for cv in list_cv:
        data = process_CV_data(cv)
        if data:
            save_to_sql(data)