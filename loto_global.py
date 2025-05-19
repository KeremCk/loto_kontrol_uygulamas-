import requests
import sqlite3

def veritabani_olustur():
    baglanti = sqlite3.connect("lotodb.db")
    imlec = baglanti.cursor()
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS kayitlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ulke TEXT,
            oyun TEXT,
            tarih TEXT,
            kullanici_sayilari TEXT,
            dogru_sayilar TEXT,
            kazanc TEXT
        )
    """)
    baglanti.commit()
    baglanti.close()

def veriyi_kaydet(ulke, oyun, tarih, kullanici_sayilari, dogru_sayilar, kazanc):
    baglanti = sqlite3.connect("lotodb.db")
    imlec = baglanti.cursor()
    imlec.execute("""
        INSERT INTO kayitlar (ulke, oyun, tarih, kullanici_sayilari, dogru_sayilar, kazanc)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ulke, oyun, tarih, str(kullanici_sayilari), str(dogru_sayilar), kazanc))
    baglanti.commit()
    baglanti.close()

def veri_cek(api_adi):
    url = f"https://api.collectapi.com/chancegame/{api_adi}"
    basliklar = {
        "content-type": "application/json",
        "authorization": "apikey 1WcEusJ4iSFOGi6dqxOSdJ:2J570ImUSKuSoUXoI9KANV"
    }
    cevap = requests.get(url, headers=basliklar)
    if cevap.status_code == 200:
        sonuc = cevap.json().get("result", [])
        # Eğer veri bir sözlükse, listeye çevir
        if isinstance(sonuc, dict):
            return [sonuc]
        return sonuc
    else:
        print("❌ API'dan veri alınamadı!", cevap.status_code)
        return []


def sonuc_karsilastir(kullanici_sayilari, cekilis_verisi):
    numaralar = cekilis_verisi.get("rakamlar") or cekilis_verisi.get("numbers")

    if isinstance(numaralar, dict):
        kazananlar = list(map(int, numaralar.values()))
    else:
        kazananlar = list(map(int, numaralar.split(" - ")))

    #  tarih veya date anahtarını kabul et
    tarih = cekilis_verisi.get("tarih") or cekilis_verisi.get("date")
    eslesenler = list(set(kullanici_sayilari) & set(kazananlar))
    dogru_sayi = len(eslesenler)

    kazanc_tablosu = {
        6: "🏆 Büyük ikramiye kazandınız!",
        5: "🎉 50.000₺",
        4: "🎉 300₺",
        3: "🎉 45₺",
        2: "🎉 12₺",
        1: "Kazanç yok.",
        0: "Hiçbir sayı tutmadı."
    }

    kazanc = kazanc_tablosu.get(dogru_sayi, "Bilinmeyen")

    return {
        "tarih": tarih,
        "kazananlar": kazananlar,
        "dogru_sayilar": eslesenler,
        "dogru_adet": dogru_sayi,
        "kazanc": kazanc
    }


def kayitlari_getir(ulke=None, oyun=None):
    baglanti = sqlite3.connect("lotodb.db")
    imlec = baglanti.cursor()
    sorgu = "SELECT tarih, kullanici_sayilari, dogru_sayilar, kazanc FROM kayitlar"
    parametreler = []

    if ulke and oyun:
        sorgu += " WHERE ulke=? AND oyun=?"
        parametreler = [ulke, oyun]
    elif ulke:
        sorgu += " WHERE ulke=?"
        parametreler = [ulke]
    elif oyun:
        sorgu += " WHERE oyun=?"
        parametreler = [oyun]

    imlec.execute(sorgu, parametreler)
    sonuc = imlec.fetchall()
    baglanti.close()
    return sonuc
