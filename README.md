\# Yerel RAG (Retrieval-Augmented Generation) Asistanı



Bu proje, tamamen çevrimdışı çalışan ve RAG mimarisini kullanan bir Soru-Cevap yapay zeka asistanıdır. Microsoft Foundry Local konsepti referans alınarak, dış ağ bağlantısına ihtiyaç duymayan yerel bir vektör arama motoru kurgulanmıştır.



\## 🚀 Proje Mimarisi

\* \*\*Veri Katmanı:\*\* Metin parçaları ve gömme (embedding) vektörleri, sunucusuz ve hafif bir yapı sunan \*\*SQLite\*\* üzerinde depolanmaktadır.

\* \*\*Geri Getirme (Retrieval):\*\* Kullanıcı sorguları vektörize edilerek, veri tabanındaki belgelerle \*\*Kosinüs Benzerliği (Cosine Similarity)\*\* algoritması üzerinden eşleştirilir.

\* \*\*Üretim (Generation):\*\* En yüksek eşleşme skoruna sahip bağlam, sistem istemiyle (prompt engineering) birleştirilerek yerel LLM'e (Büyük Dil Modeli) aktarılır. Bu sayede modelin halüsinasyon görmesi engellenir.



\## 🛠️ Kurulum ve Çalıştırma

1\. Repoyu bilgisayarınıza klonlayın.

2\. Gerekli SDK'yı kurun: `pip install foundry-local-sdk`

3\. Veri tabanını ve tabloları başlatmak için: `python veri\_hazirlik.py`

4\. Belgeleri vektörize edip kaydetmek için: `python veri\_isleme.py`

5\. RAG Asistanı CLI arayüzünü başlatmak için: `python main.py`

