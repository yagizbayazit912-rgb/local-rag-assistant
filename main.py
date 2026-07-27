import sqlite3
import json
import math
import transformers
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Terminal kirliliğini tamamen önlüyoruz
transformers.logging.set_verbosity_error()

print("Sistem başlatılıyor: Vektör arama motoru yükleniyor...")
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("Yerel Üretim Modeli (Qwen 3B) RAM'e alınıyor...")
try:
    generator = pipeline("text-generation", model="Qwen/Qwen2.5-3B-Instruct")
    model_basarili = True
except Exception as e:
    print(f"Uyarı: Model yüklenemedi. Hata: {e}")
    model_basarili = False

def kosinus_benzerligi(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def veritabanindan_bilgi_getir(soru):
    soru_vektoru = embedding_model.encode(soru).tolist()
    
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
            
    # Eşik değerini biraz daha hassas hale getirdik (0.20)
    if en_iyi_skor < 0.20: 
        return ""
        
    return en_iyi_metin

def asistana_sor(kullanici_sorusu):
    # 1. Güvenlik filtresi: Genel sohbet kelimelerini (merhaba, naber, nasılsın vb.) doğrudan engelliyoruz
    anlamli_sohbet_engeli = ["merhaba", "selam", "naber", "nasılsın", "günaydın", "iyi akşamlar", "hey", "hi", "hello"]
    if any(kelime in kullanici_sorusu.lower().strip() for kelime in anlamli_sohbet_engeli):
        return "Ben bir belge analiz asistanıyım, günlük sohbet edemem. Lütfen yüklenen belgelerle ilgili bir soru sorun."

    baglam_metni = veritabanindan_bilgi_getir(kullanici_sorusu)

    if not baglam_metni:
        return "Elimdeki belgelerde bu bilgiye sahip değilim."

    if model_basarili:
        try:
            # 2. Çok sert ve kısıtlayıcı sistem promptu (Asla uydurma yapmaz)
            prompt = f"<|im_start|>system\nSen katı bir veri analisti ve RAG asistanısın. Görevin, SADECE aşağıda verilen 'Metin' içindeki gerçekleri kullanarak soruya doğrudan ve kısa bir yanıt vermektir. Metinde kesinlikle yer almayan hiçbir ismi, olayı, unvanı veya bilgiyi uydurma, yorumlama veya dış dünyadan bilgi ekleme. Eğer metin soruyu yanıtlamak için yetersizse, sadece 'Elimdeki belgelerde bu bilgiye sahip değilim.' de.<|im_end|>\n<|im_start|>user\nMetin: {baglam_metni}\nSoru: {kullanici_sorusu}<|im_end|>\n<|im_start|>assistant\n"
            
            cevap = generator(
                prompt, 
                max_new_tokens=120, 
                return_full_text=False,
                truncation=True,
                temperature=0.1 # Yaratıcılığı en aza indirip mantıksal doğruluğu maksimuma çıkarıyoruz
            )[0]['generated_text']
            
            temiz_cevap = cevap.replace("<|im_end|>", "").strip()
            
            return f"{temiz_cevap}\n\n(Kaynak Paragraf: '{baglam_metni}')"
        except Exception as e:
            return f"[Üretim Hatası - Ham Kaynak Gösteriliyor]:\n{baglam_metni}"
    else:
        return f"[Ham Kaynak Gösteriliyor]:\n{baglam_metni}"

def main():
    print("\n--- YEREL RAG ASİSTANI (PROD READY) AKTİF ---")
    print("Çıkmak için 'q' veya 'cikis' yazabilirsiniz.\n")
    
    while True:
        soru = input("Sorunuz: ")
        if soru.lower() in ['q', 'cikis']:
            print("Asistan kapatılıyor. Görüşmek üzere!")
            break
            
        cevap = asistana_sor(soru)
        print(f"\nAsistan:\n{cevap}\n")
        print("-" * 60)

if __name__ == "__main__":
    main()