import sqlite3
import json

def metni_parcala(dosya_yolu):
    # Dosyayı okuyoruz
    with open(dosya_yolu, "r", encoding="utf-8") as f:
        metin = f.read()
    
    # Metni noktalardan bölerek küçük parçalara (cümle/paragraf) ayırıyoruz
    # Çok kısa parçaları (örn. 10 karakterden az) almıyoruz
    parcalar = [p.strip() + "." for p in metin.split('.') if len(p.strip()) > 10]
    return parcalar

def veritabanina_kaydet():
    print("Metin okunuyor ve parçalara ayrılıyor...")
    parcalar = metni_parcala("bilgi_kaynagi.txt")
    
    # SQLite veri tabanımıza bağlanıyoruz
    conn = sqlite3.connect("rag_veritabani.db")
    cursor = conn.cursor()
    
    # Vektör modelimizi burada Foundry Local üzerinden çağırıyoruz
    # (Şimdilik sistemin nasıl çalıştığını görmek için simüle edilmiş bir vektör dizisi kullanıyoruz)
    
    for parca in parcalar:
        print(f"İşleniyor: {parca[:30]}...")
        
        # GERÇEK SENARYODA BURASI ŞÖYLE OLUR:
        # response = client.embeddings.create(model="qwen3-embedding-0.6b", input=parca)
        # vektor_dizisi = response.data[0].embedding
        
        # Test için örnek bir matematiksel vektör (embedding)
        vektor_dizisi = [0.12, 0.45, 0.89, -0.34] 
        
        # Vektör dizisini (list) veri tabanına TEXT olarak kaydedebilmek için JSON formatına çeviriyoruz
        vektor_json = json.dumps(vektor_dizisi)
        
        # Hem metin parçasını hem de vektörünü tabloya ekliyoruz
        cursor.execute(
            "INSERT INTO belgeler (metin_parcasi, vektor_verisi) VALUES (?, ?)", 
            (parca, vektor_json)
        )
    
    conn.commit()
    conn.close()
    print(f"\nBaşarılı! Toplam {len(parcalar)} parça vektörleştirildi ve veri tabanına kaydedildi.")

if __name__ == "__main__":
    veritabanina_kaydet()