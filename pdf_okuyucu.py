import PyPDF2

def pdf_ten_metne(pdf_dosyasi, txt_dosyasi):
    print(f"{pdf_dosyasi} okunuyor...")
    with open(pdf_dosyasi, 'rb') as okunan_pdf:
        pdf_okuyucu = PyPDF2.PdfReader(okunan_pdf)
        toplam_sayfa = len(pdf_okuyucu.pages)
        
        # Tüm sayfaları dolaşıp metinleri birleştiriyoruz
        tum_metin = ""
        for sayfa_no in range(toplam_sayfa):
            sayfa = pdf_okuyucu.pages[sayfa_no]
            tum_metin += sayfa.extract_text() + "\n"
            
    # Elde edilen devasa metni bizim sistemimizin okuyacağı .txt dosyasına yazıyoruz
    with open(txt_dosyasi, 'w', encoding='utf-8') as yazilan_txt:
        yazilan_txt.write(tum_metin)
        
    print(f"Başarılı! {toplam_sayfa} sayfalık kitap {txt_dosyasi} dosyasına aktarıldı.")

if __name__ == "__main__":
    # Kendi PDF dosyanın adını buraya yazmalısın
    pdf_ten_metne("dune_book1.pdf", "bilgi_kaynagi.txt")