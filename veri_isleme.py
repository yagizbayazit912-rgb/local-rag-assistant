import sqlite3
import json
from sentence_transformers import SentenceTransformer

print("Çok dilli model yükleniyor...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2') 

conn = sqlite3.connect("rag_veritabani.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS belgeler (id INTEGER PRIMARY KEY, metin_parcasi TEXT, vektor_verisi TEXT)")
cursor.execute("DELETE FROM belgeler") 

print("Kitap okunuyor ve YENİ YÖNTEMLE parçalanıyor...")
with open("bilgi_kaynagi.txt", "r", encoding="utf-8") as f:
    metin = f.read()

# YENİ PARÇALAMA (CHUNKING) STRATEJİSİ:
# Koca paragraflar yerine metni yaklaşık 400 karakterlik küçük bloklara bölüyoruz.
parcalar = []
blok_boyutu = 400

# Kelime ortasından bölünmemesi için önce kelimelere ayırıyoruz
kelimeler = metin.split()
gecici_blok = ""

for kelime in kelimeler:
    gecici_blok += kelime + " "
    # Blok boyutu 400 karaktere ulaştığında paketi kapatıp listeye ekle
    if len(gecici_blok) >= blok_boyutu:
        parcalar.append(gecici_blok.strip())
        gecici_blok = ""
        
# Sonda kalan son kelimeleri de ekle
if gecici_blok:
    parcalar.append(gecici_blok.strip())

print(f"Toplam {len(parcalar)} küçük lokma (chunk) bulundu. Vektörlere dönüştürülüyor...")
print("Lütfen bekleyin...")

for parca in parcalar:
    vektor = model.encode(parca).tolist()
    cursor.execute("INSERT INTO belgeler (metin_parcasi, vektor_verisi) VALUES (?, ?)", (parca, json.dumps(vektor)))

conn.commit()
conn.close()
print("İşlem tamamlandı! Veri tabanı küçük ve keskin parçalarla güncellendi.")