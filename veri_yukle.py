import sqlite3
import json
import fitz  # PyMuPDF
import os
import glob

from foundry_client import get_embedding_client, embed_text

print("1/4 - Foundry Local embedding modeli yükleniyor...")
embedding_client = get_embedding_client()

print("2/4 - Veritabanı hazırlanıyor...")
conn = sqlite3.connect("rag_veritabani.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS belgeler 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   kaynak_dosya TEXT,
                   metin_parcasi TEXT, 
                   vektor_verisi TEXT)''')

# Her calistirmada eski verileri temizle ki klasordeki guncel havuz bastan kurulsun
cursor.execute('DELETE FROM belgeler')

print("3/4 - 'belgeler' klasorundeki tum PDF'ler taraniyor...")
pdf_dosyalari = glob.glob("belgeler/*.pdf")

if not pdf_dosyalari:
    print("HATA: 'belgeler' klasorunde hic PDF bulunamadi! Lutfen dosyalari ekleyin.")
    exit()

toplam_parca = 0

for pdf_yolu in pdf_dosyalari:
    dosya_adi = os.path.basename(pdf_yolu)
    print(f"-> Okunuyor: {dosya_adi}")

    try:
        tam_metin = ""
        with fitz.open(pdf_yolu) as doc:
            for page in doc:
                tam_metin += page.get_text() + "\n"

        chunk_boyutu = 600
        for i in range(0, len(tam_metin), chunk_boyutu):
            parca = tam_metin[i:i + chunk_boyutu].strip()
            if len(parca) > 50:
                vektor = embed_text(embedding_client, parca)
                cursor.execute(
                    "INSERT INTO belgeler (kaynak_dosya, metin_parcasi, vektor_verisi) VALUES (?, ?, ?)",
                    (dosya_adi, parca, json.dumps(vektor)),
                )
                toplam_parca += 1

    except Exception as e:
        print(f"UYARI: {dosya_adi} okunamadi. Hata: {e}")

conn.commit()
conn.close()

print("\n--- ISLEM BASARILI (Foundry Local embedding ile) ---")
print(f"Toplam {len(pdf_dosyalari)} belgeden {toplam_parca} paragraf basariyla veritabanina islendi!")