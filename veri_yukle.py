import sqlite3
import json
import PyPDF2
import os
import glob
from sentence_transformers import SentenceTransformer

print("1/4 - Embedding modeli yükleniyor...")
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("2/4 - Veritabanı hazırlanıyor...")
conn = sqlite3.connect("rag_veritabani.db")
cursor = conn.cursor()

# Tablomuza 'kaynak_dosya' adında yeni bir sütun ekledik!
cursor.execute('''CREATE TABLE IF NOT EXISTS belgeler 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   kaynak_dosya TEXT,
                   metin_parcasi TEXT, 
                   vektor_verisi TEXT)''')

# Her çalıştırmada eski verileri temizle ki klasördeki güncel havuz baştan kurulsun
cursor.execute('DELETE FROM belgeler')

print("3/4 - 'belgeler' klasöründeki tüm PDF'ler taranıyor...")
# Klasördeki tüm pdf uzantılı dosyaları bulur
pdf_dosyalari = glob.glob("belgeler/*.pdf")

if not pdf_dosyalari:
    print("HATA: 'belgeler' klasöründe hiç PDF bulunamadı! Lütfen dosyaları ekleyin.")
    exit()

toplam_parca = 0

for pdf_yolu in pdf_dosyalari:
    dosya_adi = os.path.basename(pdf_yolu)
    print(f"-> Okunuyor: {dosya_adi}")
    
    try:
        with open(pdf_yolu, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            tam_metin = ""
            for page in reader.pages:
                if page.extract_text():
                    tam_metin += page.extract_text() + "\n"
                    
        chunk_boyutu = 600
        for i in range(0, len(tam_metin), chunk_boyutu):
            parca = tam_metin[i:i+chunk_boyutu].strip()
            if len(parca) > 50:
                vektor = embedding_model.encode(parca).tolist()
                # Metni kaydederken hangi dosyadan geldiğini de SQLite'a yazıyoruz
                cursor.execute("INSERT INTO belgeler (kaynak_dosya, metin_parcasi, vektor_verisi) VALUES (?, ?, ?)", 
                               (dosya_adi, parca, json.dumps(vektor)))
                toplam_parca += 1
                
    except Exception as e:
        print(f"UYARI: {dosya_adi} okunamadı. Hata: {e}")

conn.commit()
conn.close()

print("\n--- İŞLEM BAŞARILI ---")
print(f"Toplam {len(pdf_dosyalari)} belgeden {toplam_parca} paragraf başarıyla veritabanına işlendi!")