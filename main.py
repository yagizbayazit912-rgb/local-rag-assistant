import sqlite3
import json
import math
from sentence_transformers import SentenceTransformer

print("Sistem başlatılıyor, çok dilli yerel model yükleniyor...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def kosinus_benzerligi(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def veritabanindan_bilgi_getir(soru):
    soru_vektoru = model.encode(soru).tolist()
    
    conn = sqlite3.connect("rag_veritabani.db")
    cursor = conn.cursor()
    cursor.execute("SELECT metin_parcasi, vektor_verisi FROM belgeler")
    kayitlar = cursor.fetchall()
    conn.close()
    
    en_iyi_skor = -1
    en_iyi_metin = ""
    
    for kayit in kayitlar:
        metin = kayit[0]
        db_vektoru = json.loads(kayit[1])
        skor = kosinus_benzerligi(soru_vektoru, db_vektoru)
        if skor > en_iyi_skor:
            en_iyi_skor = skor
            en_iyi_metin = metin
            
    print(f"\n[Debug] En iyi eşleşme skoru: {en_iyi_skor:.4f}")
            
    if en_iyi_skor < 0.15:
        return ""
        
    return en_iyi_metin

def asistana_sor(kullanici_sorusu):
    baglam_metni = veritabanindan_bilgi_getir(kullanici_sorusu)
    
    if baglam_metni:
        return f"Kitaptan bulduğum en alakalı paragraf: \n\n'{baglam_metni}'"
    else:
        return "Üzgünüm, veri tabanında bu soruyla ilgili geçerli bir bağlam bulunamadı."

def main():
    print("\n--- YEREL RAG ASİSTANI BAŞLATILDI ---")
    print("Çıkmak için 'q' veya 'cikis' yazabilirsiniz.\n")
    
    while True:
        soru = input("Dune evreni hakkında sorunuz: ")
        if soru.lower() in ['q', 'cikis']:
            print("Asistan kapatılıyor. Görüşmek üzere!")
            break
            
        cevap = asistana_sor(soru)
        print(f"\nAsistan: {cevap}\n")
        print("-" * 60)

if __name__ == "__main__":
    main()