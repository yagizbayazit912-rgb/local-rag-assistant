import sqlite3
import json
import math

# Vektörler arası açıyı (benzerliği) ölçen matematiksel fonksiyonumuz
def kosinus_benzerligi(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def en_iyi_metni_bul(soru):
    # 1. Gerçek senaryoda kullanıcının sorusunu da vektöre çeviririz
    # response = client.embeddings.create(model="qwen3-embedding-0.6b", input=soru)
    # soru_vektoru = response.data[0].embedding
    
    # Test için örnek bir soru vektörü kullanıyoruz
    soru_vektoru = [0.10, 0.40, 0.90, -0.30] 
    
    # 2. Veri tabanına bağlan ve kayıtlı belgeleri çek
    conn = sqlite3.connect("rag_veritabani.db")
    cursor = conn.cursor()
    cursor.execute("SELECT metin_parcasi, vektor_verisi FROM belgeler")
    kayitlar = cursor.fetchall()
    conn.close()
    
    en_iyi_skor = -1
    en_iyi_metin = ""
    
    # 3. Sorunun vektörü ile veri tabanındaki metinlerin vektörlerini karşılaştır
    for kayit in kayitlar:
        metin = kayit[0]
        db_vektoru = json.loads(kayit[1]) # JSON formatındaki vektörü listeye çeviriyoruz
        
        skor = kosinus_benzerligi(soru_vektoru, db_vektoru)
        
        if skor > en_iyi_skor:
            en_iyi_skor = skor
            en_iyi_metin = metin
            
    return en_iyi_metin, en_iyi_skor

if __name__ == "__main__":
    test_sorusu = "Dune evreninde uzay yolculuğunu ne sağlar?"
    print(f"Soru: {test_sorusu}\n")
    print("Veri tabanında aranıyor...\n")
    
    bulunan_metin, skor = en_iyi_metni_bul(test_sorusu)
    
    print("--- BULUNAN EN ALAKALI BİLGİ ---")
    print(bulunan_metin)
    print(f"\n(Eşleşme Skoru: {skor:.4f})")