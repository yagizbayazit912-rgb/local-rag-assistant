import streamlit as st
import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import transformers

# Terminal kirliliğini önle
transformers.logging.set_verbosity_error()

# 1. Modelleri Yükle ve Hafızaya Al (Sayfa yenilendiğinde tekrar yüklenmemesi için cache kullanıyoruz)
@st.cache_resource
def sistem_hazirla():
    print("Modeller RAM'e alınıyor, lütfen bekleyin...")
    emb_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    gen_model = pipeline("text-generation", model="Qwen/Qwen2.5-3B-Instruct")
    return emb_model, gen_model

# Sayfa açılır açılmaz modeller RAM'e yüklenir
embedding_model, generator = sistem_hazirla()

# 2. Vektör Arama Fonksiyonu (main.py'deki mantık)
def belge_ara(soru, limit=2):
    soru_vektoru = embedding_model.encode(soru)
    
    conn = sqlite3.connect("rag_veritabani.db")
    cursor = conn.cursor()
    cursor.execute("SELECT kaynak_dosya, metin_parcasi, vektor_verisi FROM belgeler")
    kayitlar = cursor.fetchall()
    conn.close()
    
    benzerlikler = []
    for kayit in kayitlar:
        kaynak, metin, vektor_json = kayit
        kayit_vektoru = np.array(json.loads(vektor_json))
        
        # Kosinüs Benzerliği
        dot_product = np.dot(soru_vektoru, kayit_vektoru)
        norm_a = np.linalg.norm(soru_vektoru)
        norm_b = np.linalg.norm(kayit_vektoru)
        skor = 0.0 if norm_a == 0 or norm_b == 0 else dot_product / (norm_a * norm_b)
        
        benzerlikler.append((skor, kaynak, metin))
        
    benzerlikler.sort(reverse=True, key=lambda x: x[0])
    
    if benzerlikler and benzerlikler[0][0] > 0.20: # main.py'deki eşik değerin
        return benzerlikler[:limit]
    else:
        return []

# 3. Web Arayüzü Tasarımı
st.set_page_config(page_title="Yerel RAG Asistanı", page_icon="🤖")
st.title("Yerel RAG Asistanı 📚")
# Streamlit'in güncel sürümlerinde Deploy butonunu gizleme
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

# Kullanıcı Sorusunu Al
if soru := st.chat_input("Yüklenen belgelerle ilgili bir soru sorun..."):
    # 1. Güvenlik filtresi (main.py'deki)
    anlamli_sohbet_engeli = ["merhaba", "selam", "naber", "nasılsın", "günaydın", "iyi akşamlar", "hey", "hi", "hello"]
    if any(kelime in soru.lower().strip() for kelime in anlamli_sohbet_engeli):
        st.warning("Ben bir belge analiz asistanıyım, günlük sohbet edemem. Lütfen belgelere dair bir soru sorun.")
    else:
        st.session_state.messages.append({"role": "user", "content": soru})
        with st.chat_message("user"):
            st.markdown(soru)

        with st.chat_message("assistant"):
            durum_mesaji = st.empty()
            durum_mesaji.markdown("Belgeler taranıyor ve Qwen düşünüyor... 🧠")
            
            bulunan_metinler = belge_ara(soru)
            
            if not bulunan_metinler:
                nihai_cevap = "Elimdeki belgelerde bu bilgiye sahip değilim."
            else:
                # Bağlamı oluştur
                baglam = "\n".join([f"[{kaynak}] {metin}" for skor, kaynak, metin in bulunan_metinler])
                
                # main.py'deki o katı mühendislik prompt'unu koruyoruz
                qwen_prompt = f"<|im_start|>system\nSen katı bir veri analisti ve RAG asistanısın. Görevin, SADECE aşağıda verilen 'Metin' içindeki gerçekleri kullanarak soruya doğrudan ve kısa bir yanıt vermektir. Metinde kesinlikle yer almayan hiçbir ismi, olayı, unvanı veya bilgiyi uydurma, yorumlama veya dış dünyadan bilgi ekleme. Eğer metin soruyu yanıtlamak için yetersizse, sadece 'Elimdeki belgelerde bu bilgiye sahip değilim.' de.<|im_end|>\n<|im_start|>user\nMetin: {baglam}\nSoru: {soru}<|im_end|>\n<|im_start|>assistant\n"
                
                try:
                    # Qwen Modeline Gönder
                    cevap = generator(
                        qwen_prompt, 
                        max_new_tokens=120, 
                        return_full_text=False,
                        truncation=True,
                        temperature=0.1
                    )[0]['generated_text']
                    
                    temiz_cevap = cevap.replace("<|im_end|>", "").strip()
                    nihai_cevap = f"{temiz_cevap}\n\n**(Kaynaklar):**\n*{baglam}*"
                    
                except Exception as e:
                    nihai_cevap = f"Üretim Hatası: {e}\n\nBulunan Kaynak: {baglam}"
                
            durum_mesaji.markdown(nihai_cevap)
            
        st.session_state.messages.append({"role": "assistant", "content": nihai_cevap})