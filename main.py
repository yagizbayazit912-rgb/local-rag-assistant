import sqlite3
import json
import math

from foundry_client import get_embedding_client, get_chat_client, embed_text

print("Sistem baslatiliyor: Foundry Local embedding istemcisi hazirlaniyor...")
embedding_client = get_embedding_client()

print("Sistem baslatiliyor: Foundry Local sohbet modeli hazirlaniyor...")
try:
    chat_client = get_chat_client()
    model_basarili = True
except Exception as e:
    print(f"Uyari: Model yuklenemedi. Hata: {e}")
    model_basarili = False


def kosinus_benzerligi(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)


def veritabanindan_bilgi_getir(soru):
    soru_vektoru = embed_text(embedding_client, soru)

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

    if en_iyi_skor < 0.20:
        return ""

    return en_iyi_metin


def asistana_sor(kullanici_sorusu):
    anlamli_sohbet_engeli = ["merhaba", "selam", "naber", "nasilsin", "gunaydin", "iyi aksamlar", "hey", "hi", "hello"]
    if any(kelime in kullanici_sorusu.lower().strip() for kelime in anlamli_sohbet_engeli):
        return "Ben bir belge analiz asistaniyim, gunluk sohbet edemem. Lutfen yuklenen belgelerle ilgili bir soru sorun."

    baglam_metni = veritabanindan_bilgi_getir(kullanici_sorusu)

    if not baglam_metni:
        return "Elimdeki belgelerde bu bilgiye sahip degilim."

    if model_basarili:
        try:
            sistem_mesaji = (
                "Sen katı bir veri analisti ve RAG asistanısın. Görevin, SADECE verilen 'Metin' "
                "içindeki gerçekleri kullanarak soruya doğrudan ve kısa bir yanıt vermektir. "
                "Metinde kesinlikle yer almayan hiçbir ismi, olayı, unvanı veya bilgiyi uydurma. "
                "Eğer metin soruyu yanıtlamak için yetersizse, sadece "
                "'Elimdeki belgelerde bu bilgiye sahip değilim.' de."
            )
            kullanici_mesaji = f"Metin: {baglam_metni}\nSoru: {kullanici_sorusu}"

            sonuc = chat_client.complete_chat([
                {"role": "system", "content": sistem_mesaji},
                {"role": "user", "content": kullanici_mesaji},
            ])

            temiz_cevap = sonuc.choices[0].message.content.strip()

            return f"{temiz_cevap}\n\n(Kaynak Paragraf: '{baglam_metni}')"
        except Exception as e:
            return f"[Üretim Hatası - Ham Kaynak Gösteriliyor]:\n{baglam_metni}"
    else:
        return f"[Ham Kaynak Gösteriliyor]:\n{baglam_metni}"


def main():
    print("\n--- YEREL RAG ASISTANI (Foundry Local ile) AKTIF ---")
    print("Cikmak icin 'q' veya 'cikis' yazabilirsiniz.\n")

    while True:
        soru = input("Sorunuz: ")
        if soru.lower() in ['q', 'cikis']:
            print("Asistan kapatiliyor. Gorusmek uzere!")
            break

        cevap = asistana_sor(soru)
        print(f"\nAsistan:\n{cevap}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
