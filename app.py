import streamlit as st
import sqlite3
import json
import numpy as np

from foundry_client import get_embedding_client, get_chat_client, embed_text


# 1. Modelleri yukle ve hafizada tut (sayfa yenilendiginde tekrar yuklenmesin diye cache kullaniyoruz)
@st.cache_resource
def sistem_hazirla():
    print("Foundry Local istemcileri hazirlaniyor, lutfen bekleyin...")
    emb_client = get_embedding_client()
    chat_client = get_chat_client()
    return emb_client, chat_client

embedding_client, chat_client = sistem_hazirla()


# 2. Vektor Arama Fonksiyonu
def belge_ara(soru, limit=2):
    soru_vektoru = np.array(embed_text(embedding_client, soru))

    conn = sqlite3.connect("rag_veritabani.db")
    cursor = conn.cursor()
    cursor.execute("SELECT kaynak_dosya, metin_parcasi, vektor_verisi FROM belgeler")
    kayitlar = cursor.fetchall()
    conn.close()

    benzerlikler = []
    for kayit in kayitlar:
        kaynak, metin, vektor_json = kayit
        kayit_vektoru = np.array(json.loads(vektor_json))

        dot_product = np.dot(soru_vektoru, kayit_vektoru)
        norm_a = np.linalg.norm(soru_vektoru)
        norm_b = np.linalg.norm(kayit_vektoru)
        skor = 0.0 if norm_a == 0 or norm_b == 0 else dot_product / (norm_a * norm_b)

        benzerlikler.append((skor, kaynak, metin))

    benzerlikler.sort(reverse=True, key=lambda x: x[0])

    if benzerlikler and benzerlikler[0][0] > 0.20:
        return benzerlikler[:limit]
    else:
        return []


# 3. Web arayuzu tasarimi
st.set_page_config(page_title="Yerel RAG Asistani", page_icon="🤖")
st.title("Yerel RAG Asistani 📚 (Foundry Local ile)")
st.markdown("""
    <style>
    [data-testid="stAppDeployButton"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if soru := st.chat_input("Yuklenen belgelerle ilgili bir soru sorun..."):
    anlamli_sohbet_engeli = ["merhaba", "selam", "naber", "nasilsin", "gunaydin", "iyi aksamlar", "hey", "hi", "hello"]
    if any(kelime in soru.lower().strip() for kelime in anlamli_sohbet_engeli):
        st.warning("Ben bir belge analiz asistaniyim, gunluk sohbet edemem. Lutfen belgelere dair bir soru sorun.")
    else:
        st.session_state.messages.append({"role": "user", "content": soru})
        with st.chat_message("user"):
            st.markdown(soru)

        with st.chat_message("assistant"):
            durum_mesaji = st.empty()
            durum_mesaji.markdown("Belgeler taraniyor ve Foundry Local modeli dusunuyor... 🧠")

            bulunan_metinler = belge_ara(soru)

            if not bulunan_metinler:
                nihai_cevap = "Elimdeki belgelerde bu bilgiye sahip degilim."
            else:
                baglam = "\n".join([f"[{kaynak}] {metin}" for skor, kaynak, metin in bulunan_metinler])

                sistem_mesaji = (
                    "Sen katı bir veri analisti ve RAG asistanısın. Görevin, SADECE verilen 'Metin' "
                    "içindeki gerçekleri kullanarak soruya doğrudan ve kısa bir yanıt vermektir. "
                    "Metinde kesinlikle yer almayan hiçbir ismi, olayı, unvanı veya bilgiyi uydurma. "
                    "Eğer metin soruyu yanıtlamak için yetersizse, sadece "
                    "'Elimdeki belgelerde bu bilgiye sahip değilim.' de."
                )
                kullanici_mesaji = f"Metin: {baglam}\nSoru: {soru}"

                try:
                    sonuc = chat_client.complete_chat([
                        {"role": "system", "content": sistem_mesaji},
                        {"role": "user", "content": kullanici_mesaji},
                    ])
                    temiz_cevap = sonuc.choices[0].message.content.strip()
                    nihai_cevap = f"{temiz_cevap}\n\n**(Kaynaklar):**\n*{baglam}*"

                except Exception as e:
                    nihai_cevap = f"Uretim Hatasi: {e}\n\nBulunan Kaynak: {baglam}"

            durum_mesaji.markdown(nihai_cevap)

        st.session_state.messages.append({"role": "assistant", "content": nihai_cevap})
