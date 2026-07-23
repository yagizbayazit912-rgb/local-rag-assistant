import sqlite3

def veritabani_kur():
    # Veri tabanı dosyasına bağlanır (dosya yoksa otomatik oluşturur)
    conn = sqlite3.connect("rag_veritabani.db")
    cursor = conn.cursor()

    # Belgeleri ve vektörleri (embedding) tutacak tablomuzu oluşturuyoruz
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS belgeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metin_parcasi TEXT NOT NULL,
            vektor_verisi TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("SQLite veri tabanı ve 'belgeler' tablosu başarıyla oluşturuldu!")

if __name__ == "__main__":
    veritabani_kur()