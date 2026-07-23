import sqlite3
import json
import math

def kosinus_benzerligi(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def veritabanindan_bilgi_getir(soru):
    # Simüle edilmiş soru vektörü
    soru_vektoru = [0.10, 0.40, 0.90, -0.30] 
    
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
            
    # Eğer benzerlik çok düşükse (yani soru veri tabanındaki konuyla alakasızsa) boş döndür
    if en_iyi_skor < 0.5:
        return ""
        
    return en_iyi_metin

def asistana_sor(kullanici_sorusu):
    # 1. RAG - Retrieve (Geri Getirme)
    baglam_metni = veritabanindan_bilgi_getir(kullanici_sorusu)
    
    print("\n[Yerel model yanıt üretiyor...]")
    
    # 2. DİNAMİK YANIT: Soruya göre veri tabanından gelen cevabı şekillendirir
    if baglam_metni:
        return f"Veri tabanındaki ilgili belgeye göre: '{baglam_metni}'"
    else:
        return "Üzgünüm, hafızamdaki belgelerde bu soruyla ilgili bir bilgi bulunamadı. Lütfen Arrakis veya baharat ile ilgili bir şey sorun."

def main():
    print("--- YEREL RAG ASİSTANI BAŞLATILDI ---")
    print("Çıkmak için 'q' veya 'cikis' yazabilirsiniz.\n")
    
    while True:
        soru = input("Sorunuz: ")
        if soru.lower() in ['q', 'cikis']:
            print("Asistan kapatılıyor. Görüşmek üzere!")
            break
            
        cevap = asistana_sor(soru)
        print(f"\nAsistan: {cevap}\n")
        print("-" * 40)

if __name__ == "__main__":
    main()