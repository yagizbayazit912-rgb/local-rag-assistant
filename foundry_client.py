"""
foundry_client.py
------------------
Microsoft Foundry Local ile konuşan tek merkez modül.
main.py ve app.py bu modülü import ederek hem embedding hem de
chat (metin üretim) istemcilerini alır.

Kurulum (kendi bilgisayarında, bu sandbox'ta DEĞİL):
    pip install foundry-local-sdk        # macOS / Linux / Windows (hızlandırmasız)
    # Windows'ta donanım hızlandırma istiyorsan onun yerine:
    # pip install foundry-local-sdk-winml

İlk çalıştırmada modelleri indirmek biraz zaman alabilir (birkaç GB).
"""

from foundry_local_sdk import Configuration, FoundryLocalManager

# --- Kullanılacak model takma adları (alias) ---
# Not: "qwen2.5-3b" katalogda yoksa, en yakın seçenek olarak qwen2.5-7b
# veya phi-3.5-mini kullan. Kendi makinende hangilerinin mevcut olduğunu
# görmek için: `foundry model list` komutunu terminalde çalıştır.
CHAT_MODEL_ALIAS = "qwen2.5-7b"          # sohbet / cevap üretme modeli
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"  # vektörleştirme modeli

_manager = None


def _get_manager():
    """FoundryLocalManager'ı tek seferlik (singleton) başlatır."""
    global _manager
    if _manager is None:
        config = Configuration(app_name="local_rag_assistant")
        FoundryLocalManager.initialize(config)
        _manager = FoundryLocalManager.instance
    return _manager


def get_embedding_client(alias: str = EMBEDDING_MODEL_ALIAS):
    """Embedding üretmek için hazır bir istemci döner."""
    manager = _get_manager()
    model = manager.catalog.get_model(alias)
    if not model.is_cached:
        print(f"'{alias}' modeli indiriliyor (ilk çalıştırmada bir kez olur)...")
        model.download(lambda p: print(f"\r  İndiriliyor: %{p:.0f}", end="", flush=True))
        print()
    model.load()
    return model.get_embedding_client()


def get_chat_client(alias: str = CHAT_MODEL_ALIAS):
    """Sohbet/metin üretimi için hazır bir istemci döner."""
    manager = _get_manager()
    model = manager.catalog.get_model(alias)
    if not model.is_cached:
        print(f"'{alias}' modeli indiriliyor (ilk çalıştırmada bir kez olur)...")
        model.download(lambda p: print(f"\r  İndiriliyor: %{p:.0f}", end="", flush=True))
        print()
    model.load()
    client = model.get_chat_client()
    client.settings.temperature = 0.1
    client.settings.max_tokens = 200
    return client


def embed_text(embedding_client, text: str):
    """Tek bir metni vektöre çevirip liste (List[float]) olarak döner."""
    response = embedding_client.generate_embedding(text)
    return response.data[0].embedding
