import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

from loto_global import (
    veri_cek,
    veritabani_olustur,
    veriyi_kaydet,
    sonuc_karsilastir,
    kayitlari_getir
)

GORSSEL_DIZINI = os.path.dirname(os.path.abspath(__file__))

KARANLIK_ARKAPLAN = "#1a1a1a"
YAZI_RENGI = "#ffffff"

def gorsel_yukle(dosya_adi, boyut):
    yol = os.path.join(GORSSEL_DIZINI, dosya_adi)
    resim = Image.open(yol).resize(boyut, Image.LANCZOS)
    return ImageTk.PhotoImage(resim)

class LotoArayuz(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loto Uygulaması")
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(bg=KARANLIK_ARKAPLAN)

        self.sayfalar = {}
        for Sayfa in (AnaMenu, UlkeSecimi, OyunSecimi, SayiGiris, KayitGoruntule):
            sayfa_adi = Sayfa.__name__
            cerceve = Sayfa(parent=self, denetleyici=self)
            self.sayfalar[sayfa_adi] = cerceve
            cerceve.grid(row=0, column=0, sticky="nsew")

        self.sayfa_goster("AnaMenu")
        veritabani_olustur()

    def sayfa_goster(self, ad):
        cerceve = self.sayfalar[ad]
        cerceve.tkraise()

class AnaMenu(tk.Frame):
    def __init__(self, parent, denetleyici):
        super().__init__(parent, bg=KARANLIK_ARKAPLAN)
        self.denetleyici = denetleyici

        tk.Label(self, text="🎰 LOTO UYGULAMASINA HOŞ GELDİN", font=("Arial", 20), bg=KARANLIK_ARKAPLAN, fg=YAZI_RENGI).pack(pady=40)

        tk.Button(self, text="Loto Sorgula", font=("Arial", 14), width=20, height=2,
                  command=lambda: denetleyici.sayfa_goster("UlkeSecimi"), bg="#333", fg=YAZI_RENGI).pack(pady=20)

        tk.Button(self, text="Kayıtları Görüntüle", font=("Arial", 14), width=20, height=2,
                  command=lambda: denetleyici.sayfa_goster("KayitGoruntule"), bg="#333", fg=YAZI_RENGI).pack(pady=10)

class UlkeSecimi(tk.Frame):
    def __init__(self, parent, denetleyici):
        super().__init__(parent, bg=KARANLIK_ARKAPLAN)
        self.denetleyici = denetleyici
        tk.Label(self, text="🌍 Ülke Seçimi", font=("Arial", 18), bg=KARANLIK_ARKAPLAN, fg=YAZI_RENGI).pack(pady=10)

        self.gorseller = {
            "Türkiye": gorsel_yukle("turkey.png", (200, 120)),
            "ABD": gorsel_yukle("usa.png", (200, 120)),
            "Avrupa": gorsel_yukle("eu.png", (200, 120)),
        }

        self.butonlari_olustur()
        self.ana_menu_butonu()

    def butonlari_olustur(self):
        cerceve = tk.Frame(self, bg=KARANLIK_ARKAPLAN)
        cerceve.pack(pady=30)

        for i, (ulke, img) in enumerate(self.gorseller.items()):
            btn = tk.Button(cerceve, image=img, command=lambda u=ulke: self.oyun_secimine_git(u), borderwidth=0)
            btn.image = img
            btn.grid(row=0, column=i, padx=30)

    def oyun_secimine_git(self, ulke):
        oyun_ekrani = self.denetleyici.sayfalar["OyunSecimi"]
        oyun_ekrani.ulke_ayarla(ulke)
        self.denetleyici.sayfa_goster("OyunSecimi")

    def ana_menu_butonu(self):
        menu_img = gorsel_yukle("mainmenu.png", (50, 50))
        btn = tk.Button(self, image=menu_img, command=lambda: self.denetleyici.sayfa_goster("AnaMenu"),
                        borderwidth=0, bg=KARANLIK_ARKAPLAN, activebackground=KARANLIK_ARKAPLAN)
        btn.image = menu_img
        btn.place(x=740, y=10)

class OyunSecimi(tk.Frame):
    oyunlar = {
        "Türkiye": {
            "Sayısal Loto": "sayisal.png",
            "Süper Loto": "super.png",
            "On Numara": "onnumara.png",
            "Şans Topu": "sans.png",
            "Milli Piyango": "millipiyango.png"
        },
        "ABD": {
            "Powerball": "powerball.png",
            "Mega Millions": "megamillions.png",
            "SuperLotto Plus": "superlotto.png"
        },
        "Avrupa": {
            "EuroMillions": "euromillions.png"
        }
    }

    api_haritasi = {
        "Sayısal Loto": "sayisalLoto",
        "Süper Loto": "superLoto",
        "On Numara": "onNumara",
        "Şans Topu": "sanstopu",
        "Milli Piyango": "millipiyango",
        "Powerball": "usaPowerball",
        "Mega Millions": "usaMegaMillions",
        "SuperLotto Plus": "usaSuperLottoPlus",
        "EuroMillions": "euroMillions"
    }

    def __init__(self, parent, denetleyici):
        super().__init__(parent, bg=KARANLIK_ARKAPLAN)
        self.denetleyici = denetleyici
        self.ulke = None
        self.baslik = tk.Label(self, text="🎮 Oyun Seçimi", font=("Arial", 18), bg=KARANLIK_ARKAPLAN, fg=YAZI_RENGI)
        self.baslik.pack(pady=10)

        self.oyun_cerceve = tk.Frame(self, bg=KARANLIK_ARKAPLAN)
        self.oyun_cerceve.pack(pady=20)

        self.ana_menu_butonu()

    def ulke_ayarla(self, ulke):
        self.ulke = ulke
        self.baslik.config(text=f"🎮 {ulke} Oyunları")
        for widget in self.oyun_cerceve.winfo_children():
            widget.destroy()

        oyunlar = self.oyunlar.get(ulke, {})
        for i, (oyun_adi, resim) in enumerate(oyunlar.items()):
            img = gorsel_yukle(resim, (200, 120))
            btn = tk.Button(self.oyun_cerceve, image=img,
                            command=lambda o=oyun_adi: self.sayi_girisine_git(o), borderwidth=0)
            btn.image = img
            btn.grid(row=i // 3, column=i % 3, padx=20, pady=15)

    def sayi_girisine_git(self, oyun):
        ekran = self.denetleyici.sayfalar["SayiGiris"]
        ekran.ayarlar_ata(self.ulke, oyun, self.api_haritasi[oyun])
        self.denetleyici.sayfa_goster("SayiGiris")

    def ana_menu_butonu(self):
        menu_img = gorsel_yukle("mainmenu.png", (50, 50))
        btn = tk.Button(self, image=menu_img, command=lambda: self.denetleyici.sayfa_goster("AnaMenu"),
                        borderwidth=0, bg=KARANLIK_ARKAPLAN, activebackground=KARANLIK_ARKAPLAN)
        btn.image = menu_img
        btn.place(x=740, y=10)

class SayiGiris(tk.Frame):
    def __init__(self, parent, denetleyici):
        super().__init__(parent, bg=KARANLIK_ARKAPLAN)
        self.denetleyici = denetleyici
        self.kutular = []
        self.ulke = ""
        self.oyun = ""
        self.api = ""
        self.cekilisler = []
        self.secili_cekilis = tk.StringVar()

        self.baslik = tk.Label(self, text="Sayılarınızı giriniz (1-90)", font=("Arial", 16), bg=KARANLIK_ARKAPLAN, fg=YAZI_RENGI)
        self.baslik.pack(pady=10)

        self.tarih_secim = tk.OptionMenu(self, self.secili_cekilis, "")
        self.tarih_secim.config(bg="#333", fg=YAZI_RENGI)
        self.tarih_secim.pack(pady=5)

        kutu_cerceve = tk.Frame(self, bg=KARANLIK_ARKAPLAN)
        kutu_cerceve.pack(pady=10)
        for i in range(6):
            kutu = tk.Entry(kutu_cerceve, width=5, font=("Arial", 14), justify="center")
            kutu.grid(row=0, column=i, padx=5)
            self.kutular.append(kutu)

        tk.Button(self, text="Sonuçları Kontrol Et", command=self.kontrol_et, bg="#333", fg=YAZI_RENGI).pack(pady=10)
        self.sonuc_etiket = tk.Label(self, text="", font=("Arial", 12), bg=KARANLIK_ARKAPLAN, fg=YAZI_RENGI)
        self.sonuc_etiket.pack(pady=10)

        self.ana_menu_butonu()

    def ayarlar_ata(self, ulke, oyun, api):
        self.ulke = ulke
        self.oyun = oyun
        self.api = api
        self.sonuc_etiket.config(text="")
        for kutu in self.kutular:
            kutu.delete(0, tk.END)

        self.cekilisler = veri_cek(api)


        # Hatalı veri yapısını düzeltme
        if isinstance(self.cekilisler, dict):
            self.cekilisler = list(self.cekilisler.values())

        if not isinstance(self.cekilisler, list) or not self.cekilisler:
            self.secili_cekilis.set("Veri yok")
            return

        tarihler = [c.get("tarih") or c.get("date") for c in self.cekilisler[:5]]

        self.secili_cekilis.set(tarihler[0])
        self.tarih_secim['menu'].delete(0, 'end')
        for tarih in tarihler:
            self.tarih_secim['menu'].add_command(label=tarih, command=tk._setit(self.secili_cekilis, tarih))

    def kontrol_et(self):
        try:
            sayilar = [int(k.get()) for k in self.kutular]
        except:
            messagebox.showerror("Hata", "Geçerli 6 sayı giriniz.")
            return

        if len(set(sayilar)) != 6 or not all(1 <= s <= 90 for s in sayilar):
            messagebox.showerror("Hata", "1-90 arası 6 farklı sayı girin.")
            return

        secilen_tarih = self.secili_cekilis.get()
        veri = next((c for c in self.cekilisler if (c.get("tarih") or c.get("date")) == secilen_tarih), None)


        if not veri:
            messagebox.showerror("Hata", "Seçilen tarih verisi bulunamadı.")
            return

        sonuc = sonuc_karsilastir(sayilar, veri)
        mesaj = f"{sonuc['dogru_adet']} doğru tahmin!\nKazanç: {sonuc['kazanc']}"
        self.sonuc_etiket.config(text=mesaj)

        if messagebox.askyesno("Kayıt", "Sonucu veritabanına kaydetmek ister misin?"):
            veriyi_kaydet(self.ulke, self.oyun, sonuc['tarih'], sayilar, sonuc['dogru_sayilar'], sonuc['kazanc'])
            messagebox.showinfo("Bilgi", "Kayıt başarıyla eklendi.")

    def ana_menu_butonu(self):
        menu_img = gorsel_yukle("mainmenu.png", (50, 50))
        btn = tk.Button(self, image=menu_img, command=lambda: self.denetleyici.sayfa_goster("AnaMenu"),
                        borderwidth=0, bg=KARANLIK_ARKAPLAN, activebackground=KARANLIK_ARKAPLAN)
        btn.image = menu_img
        btn.place(x=740, y=10)


class KayitGoruntule(tk.Frame):
    def __init__(self, parent, denetleyici):
        super().__init__(parent, bg=KARANLIK_ARKAPLAN)
        self.denetleyici = denetleyici
        self.ulke_var = tk.StringVar()
        self.oyun_var = tk.StringVar()

        tk.Label(self, text="🔍 Kayıtları Görüntüle", font=("Arial", 18), bg=KARANLIK_ARKAPLAN, fg=YAZI_RENGI).pack(pady=10)

        form = tk.Frame(self, bg=KARANLIK_ARKAPLAN)
        form.pack(pady=5)
        tk.Label(form, text="Ülke:", bg=KARANLIK_ARKAPLAN, fg=YAZI_RENGI).grid(row=0, column=0, padx=5)
        tk.Entry(form, textvariable=self.ulke_var).grid(row=0, column=1, padx=5)

        tk.Label(form, text="Oyun:", bg=KARANLIK_ARKAPLAN, fg=YAZI_RENGI).grid(row=0, column=2, padx=5)
        tk.Entry(form, textvariable=self.oyun_var).grid(row=0, column=3, padx=5)

        tk.Button(form, text="Sorgula", command=self.kayitlari_goster, bg="#333", fg=YAZI_RENGI).grid(row=0, column=4, padx=5)

        self.liste = tk.Text(self, width=90, height=20, bg="#222", fg=YAZI_RENGI)
        self.liste.pack(pady=10)

        self.ana_menu_butonu()

    def kayitlari_goster(self):
        ulke = self.ulke_var.get().strip()
        oyun = self.oyun_var.get().strip()
        kayitlar = kayitlari_getir(ulke if ulke else None, oyun if oyun else None)

        self.liste.delete("1.0", tk.END)
        if not kayitlar:
            self.liste.insert(tk.END, "Kayıt bulunamadı.\n")
        else:
            for k in kayitlar:
                self.liste.insert(tk.END, f"Tarih: {k[0]}\nTahmin: {k[1]}\nDoğrular: {k[2]}\nKazanç: {k[3]}\n---\n")

    def ana_menu_butonu(self):
        menu_img = gorsel_yukle("mainmenu.png", (50, 50))
        btn = tk.Button(self, image=menu_img, command=lambda: self.denetleyici.sayfa_goster("AnaMenu"),
                        borderwidth=0, bg=KARANLIK_ARKAPLAN, activebackground=KARANLIK_ARKAPLAN)
        btn.image = menu_img
        btn.place(x=740, y=10)


if __name__ == "__main__":
    uygulama = LotoArayuz()
    uygulama.mainloop()

