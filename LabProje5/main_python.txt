import customtkinter as ctk
from tkinter import messagebox
from database import DatabaseManager
from datetime import datetime
import os
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

#İzleme Ekranı
class IzlemeEkrani(ctk.CTkToplevel):
    def __init__(self, parent, k_id, p_id, p_ad, p_tip, bolum_no=1, kaldigi_dk=0):
        super().__init__(parent)
        self.k_id = k_id
        self.p_id = p_id
        self.p_tip = p_tip
        self.bolum_no = bolum_no
        self.db = DatabaseManager()

        self.title(f"İzleniyor: {p_ad}")
        self.geometry("500x600")
        self.transient(parent); self.grab_set(); self.focus_force()

        baslik = f"{p_ad}" if p_tip == "Film" else f"{p_ad} - {bolum_no}. Bölüm"
        ctk.CTkLabel(self, text=baslik, font=("Arial", 22, "bold"), text_color="#E50914").pack(pady=20)
        if kaldigi_dk > 0: ctk.CTkLabel(self, text=f"Kaldığınız Yerden Devam Ediliyor: {kaldigi_dk}. Dakika", text_color="orange").pack(pady=5)

        ctk.CTkLabel(self, text="Kaç dakika izlediniz? (Örn: 45)").pack(pady=(20, 5))
        self.sure_entry = ctk.CTkEntry(self, placeholder_text="Uzunluk (Dk)", width=150)
        self.sure_entry.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="İzlemeyi Tamamla", fg_color="#E50914", command=lambda: self.izlemeyi_kaydet(True)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Kaldığım Yere Kaydet", fg_color="gray", command=lambda: self.izlemeyi_kaydet(False)).pack(side="left", padx=10)

        ctk.CTkLabel(self, text="--- İçeriği Puanla (1-10) ---", text_color="gray").pack(pady=(30, 10))
        self.puan_combo = ctk.CTkComboBox(self, values=[str(i) for i in range(1, 11)], width=120)
        self.puan_combo.set("Puan Seç")
        self.puan_combo.pack(pady=5)
        ctk.CTkButton(self, text="Puan Ver", width=120, command=self.puan_ver).pack(pady=10)

    def izlemeyi_kaydet(self, tamamlandi):
        sure_str = self.sure_entry.get().strip()
        if not sure_str.isdigit(): messagebox.showwarning("Uyarı", "Geçerli bir dakika giriniz!"); return
        sure = int(sure_str)
        if self.db.connect():
            try:
                self.db.cursor.execute("INSERT INTO IzlemeLog (kullanici_id, program_id, bolum_no, izlenen_sure, tamamlandi_mi) VALUES (%s, %s, %s, %s, %s)", 
                                       (self.k_id, self.p_id, self.bolum_no, sure, tamamlandi))
                self.db.cursor.execute("UPDATE Program SET izlenme_sayisi = izlenme_sayisi + 1 WHERE id = %s", (self.p_id,))
                self.db.connection.commit(); messagebox.showinfo("Başarılı", f"Durum: {'Tamamlandı' if tamamlandi else 'Kaydedildi'}."); self.destroy()
            except Exception as e: messagebox.showerror("Hata", f"Hata: {e}")
            finally: self.db.close_connection()

    def puan_ver(self):
        puan_str = self.puan_combo.get()
        if not puan_str.isdigit(): messagebox.showwarning("Uyarı", "Puan seçin."); return
        puan = int(puan_str)
        if self.db.connect():
            try:
                self.db.cursor.execute("SELECT * FROM KullaniciProgram WHERE kullanici_id=%s AND program_id=%s", (self.k_id, self.p_id))
                if self.db.cursor.fetchone(): self.db.cursor.execute("UPDATE KullaniciProgram SET verilen_puan=%s WHERE kullanici_id=%s AND program_id=%s", (puan, self.k_id, self.p_id))
                else: self.db.cursor.execute("INSERT INTO KullaniciProgram (kullanici_id, program_id, verilen_puan) VALUES (%s, %s, %s)", (self.k_id, self.p_id, puan))
                self.db.cursor.execute("SELECT AVG(verilen_puan) as ort FROM KullaniciProgram WHERE program_id=%s", (self.p_id,))
                yeni_ort = self.db.cursor.fetchone()['ort']
                self.db.cursor.execute("UPDATE Program SET ortalama_puan=%s WHERE id=%s", (yeni_ort, self.p_id))
                self.db.connection.commit(); messagebox.showinfo("Başarılı", "Puan kaydedildi.")
            except Exception as e: messagebox.showerror("Hata", f"Hata: {e}")
            finally: self.db.close_connection()

# İçerik Detay Sayfası
class IcerikDetaySayfasi(ctk.CTkToplevel):
    def __init__(self, parent, k_id, p_id):
        super().__init__(parent)
        self.geometry("700x780") 
        self.transient(parent); self.grab_set(); self.focus_force()      
        self.db = DatabaseManager()
        self.k_id = k_id
        self.p_id = p_id
        self.verileri_cek()

    def verileri_cek(self):
        if not self.db.connect(): self.destroy(); return
        try:
            self.db.cursor.execute("SELECT * FROM Program WHERE id=%s", (self.p_id,))
            p_data = self.db.cursor.fetchone()
            if not p_data: self.destroy(); return
            
            p_ad = p_data['ad'] if isinstance(p_data, dict) else p_data[1]
            self.p_tip = p_data['tip'] if isinstance(p_data, dict) else p_data[2]
            p_aciklama = p_data['aciklama'] if isinstance(p_data, dict) else p_data[3]
            p_yil = p_data['yayin_yili'] if isinstance(p_data, dict) else p_data[4]
            p_uzunluk = p_data['uzunluk'] if isinstance(p_data, dict) else p_data[5]
            self.p_bolum = p_data['bolum_sayisi'] if isinstance(p_data, dict) else p_data[6]
            if not self.p_bolum: self.p_bolum = 1
            p_ort = p_data['ortalama_puan'] if isinstance(p_data, dict) else p_data[7]
            if not p_ort: p_ort = 0.0
            
            self.title(f"Detay: {p_ad}")
            self.db.cursor.execute("SELECT t.ad FROM Tur t JOIN ProgramTur pt ON t.id = pt.tur_id WHERE pt.program_id=%s", (self.p_id,))
            tur_str = ", ".join([t['ad'] if isinstance(t, dict) else t[0] for t in self.db.cursor.fetchall()])
            
            self.db.cursor.execute("SELECT * FROM Favori WHERE kullanici_id=%s AND program_id=%s", (self.k_id, self.p_id))
            self.is_favori = bool(self.db.cursor.fetchone())

            self.db.cursor.execute("SELECT bolum_no, izlenen_sure FROM IzlemeLog WHERE kullanici_id=%s AND program_id=%s ORDER BY izleme_tarihi DESC LIMIT 1", (self.k_id, self.p_id))
            son_izleme = self.db.cursor.fetchone()
            self.son_bol = son_izleme['bolum_no'] if isinstance(son_izleme, dict) else (son_izleme[0] if son_izleme else 1)
            self.son_dk = son_izleme['izlenen_sure'] if isinstance(son_izleme, dict) else (son_izleme[1] if son_izleme else 0)

            img_path = next((f"posters/{p_ad}{ext}" for ext in [".jpg", ".png", ".jpeg", ".webp"] if os.path.exists(f"posters/{p_ad}{ext}")), None)
            if img_path:
                try: ctk.CTkLabel(self, text="", image=ctk.CTkImage(light_image=Image.open(img_path), size=(200, 300))).pack(pady=15)
                except: ctk.CTkLabel(self, text="Bozuk Poster", width=200, height=300, fg_color="#333333").pack(pady=15)
            else: ctk.CTkLabel(self, text="Resim Yok", width=200, height=300, fg_color="#333333").pack(pady=15)
            
            ctk.CTkLabel(self, text=p_ad, font=("Arial", 28, "bold"), text_color="#E50914").pack()
            ctk.CTkLabel(self, text=f"{self.p_tip} | Tür: {tur_str} | Yıl: {p_yil}", font=("Arial", 14), text_color="gray").pack(pady=5)
            ctk.CTkLabel(self, text=f"Puan: ★ {p_ort:.1f} | Bölüm: {self.p_bolum} | Uzunluk: {p_uzunluk} Dk", font=("Arial", 12, "bold")).pack(pady=10)
            ctk.CTkLabel(self, text=p_aciklama if p_aciklama else "Açıklama yok.", wraplength=600).pack(pady=10)

            btn_frame = ctk.CTkFrame(self, fg_color="transparent")
            btn_frame.pack(pady=20)
            self.fav_btn = ctk.CTkButton(btn_frame, text="Favoriden Çıkar" if self.is_favori else "Favoriye Ekle", fg_color="#333333" if self.is_favori else "#E50914", command=self.favori_islemi)
            self.fav_btn.pack(side="left", padx=10)

            if self.p_tip == "Dizi":
                self.b_combo = ctk.CTkComboBox(btn_frame, values=[f"{i}. Bölüm" for i in range(1, self.p_bolum + 1)], width=120)
                self.b_combo.set(f"{self.son_bol}. Bölüm")
                self.b_combo.pack(side="left", padx=10)

            ctk.CTkButton(btn_frame, text=f"Devam Et ({self.son_dk}. Dk)" if self.son_dk > 0 else "İzle", fg_color="#E50914", 
                          command=lambda: self.izleme_ekranini_ac(p_ad)).pack(side="left", padx=10)
        finally: self.db.close_connection()

    def favori_islemi(self):
        if not self.db.connect(): return
        try:
            if self.is_favori: self.db.cursor.execute("DELETE FROM Favori WHERE kullanici_id=%s AND program_id=%s", (self.k_id, self.p_id))
            else: self.db.cursor.execute("INSERT INTO Favori (kullanici_id, program_id) VALUES (%s, %s)", (self.k_id, self.p_id))
            self.db.connection.commit()
            self.is_favori = not self.is_favori
            self.fav_btn.configure(text="Favoriden Çıkar" if self.is_favori else "Favoriye Ekle", fg_color="#333333" if self.is_favori else "#E50914")
        finally: self.db.close_connection()

    def izleme_ekranini_ac(self, p_ad):
        sec_b = int(self.b_combo.get().split(".")[0]) if self.p_tip == "Dizi" else 1
        IzlemeEkrani(self, self.k_id, self.p_id, p_ad, self.p_tip, sec_b, self.son_dk)

# Profil Sayfası
class ProfilSayfasi(ctk.CTkToplevel):
    def __init__(self, parent, k_id):
        super().__init__(parent)
        self.title("Profilim")
        self.geometry("750x650")
        self.transient(parent); self.grab_set(); self.focus_force()
        self.db = DatabaseManager()
        self.k_id = k_id

        self.tabview = ctk.CTkTabview(self, width=700, height=550)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.tab_bilgi = self.tabview.add("Profil Bilgileri")
        self.tab_gecmis = self.tabview.add("İzleme Geçmişi")
        self.tab_fav = self.tabview.add("Favorilerim")

        self.bilgileri_yukle()
        self.gecmisi_yukle()
        self.favorileri_yukle()

    def bilgileri_yukle(self):
        if not self.db.connect(): return
        try:
            self.db.cursor.execute("SELECT ad, soyad, email, dogum_tarihi, ulke FROM Kullanici WHERE id=%s", (self.k_id,))
            u = self.db.cursor.fetchone()
            self.db.cursor.execute("SELECT SUM(izlenen_sure) as t_sure, COUNT(DISTINCT program_id) as t_icerik FROM IzlemeLog WHERE kullanici_id=%s", (self.k_id,))
            ist = self.db.cursor.fetchone()
            
            self.db.cursor.execute("SELECT t.ad FROM Tur t JOIN KullaniciTur kt ON t.id=kt.tur_id WHERE kt.kullanici_id=%s", (self.k_id,))
            f_turler = ", ".join([t['ad'] if isinstance(t, dict) else t[0] for t in self.db.cursor.fetchall()])

            u_ad = u['ad'] if isinstance(u, dict) else u[0]
            u_soy = u['soyad'] if isinstance(u, dict) else u[1]
            u_mail = u['email'] if isinstance(u, dict) else u[2]
            u_dog = u['dogum_tarihi'] if isinstance(u, dict) else u[3]
            u_ulke = u['ulke'] if isinstance(u, dict) else u[4]
            t_sure = ist['t_sure'] if isinstance(ist, dict) else ist[0]
            t_icerik = ist['t_icerik'] if isinstance(ist, dict) else ist[1]

            ctk.CTkLabel(self.tab_bilgi, text=f"👤 {u_ad} {u_soy}", font=("Arial", 24, "bold"), text_color="#E50914").pack(pady=10)
            detay = f"📧 E-mail: {u_mail}\n🎂 Doğum: {u_dog}\n🌍 Ülke: {u_ulke}\n⭐ Favori Türler: {f_turler}"
            ctk.CTkLabel(self.tab_bilgi, text=detay, font=("Arial", 14), justify="left").pack(pady=10)
            
            ctk.CTkLabel(self.tab_bilgi, text=f"Toplam İzleme: {t_sure if t_sure else 0} Dk | İzlenen İçerik: {t_icerik}", font=("Arial", 14, "bold"), text_color="orange").pack(pady=10)
            
            ctk.CTkLabel(self.tab_bilgi, text="Şifre Güncelle", font=("Arial", 16, "bold")).pack(pady=(20, 5))
            self.y_sifre = ctk.CTkEntry(self.tab_bilgi, placeholder_text="Yeni Şifre", show="*")
            self.y_sifre.pack(pady=5)
            ctk.CTkButton(self.tab_bilgi, text="Güncelle", fg_color="#E50914", command=self.sifre_guncelle).pack(pady=5)
        finally: self.db.close_connection()

    def sifre_guncelle(self):
        yeni = self.y_sifre.get().strip()
        if len(yeni) < 6: messagebox.showwarning("Hata", "Min 6 karakter!"); return
        if self.db.connect():
            try:
                self.db.cursor.execute("UPDATE Kullanici SET sifre=%s WHERE id=%s", (yeni, self.k_id))
                self.db.connection.commit(); messagebox.showinfo("Başarılı", "Şifreniz güncellendi!")
            finally: self.db.close_connection()

    def gecmisi_yukle(self):
        liste = ctk.CTkTextbox(self.tab_gecmis, width=650, height=400)
        liste.pack(pady=10)
        if self.db.connect():
            try:
                self.db.cursor.execute("SELECT p.ad, i.izlenen_sure, i.izleme_tarihi, i.tamamlandi_mi FROM IzlemeLog i JOIN Program p ON i.program_id = p.id WHERE i.kullanici_id=%s ORDER BY i.izleme_tarihi DESC", (self.k_id,))
                for g in self.db.cursor.fetchall():
                    p_ad = g['ad'] if isinstance(g, dict) else g[0]
                    sure = g['izlenen_sure'] if isinstance(g, dict) else g[1]
                    tarih = g['izleme_tarihi'] if isinstance(g, dict) else g[2]
                    drm = "Bitti" if (g['tamamlandi_mi'] if isinstance(g, dict) else g[3]) else "Yarım"
                    liste.insert("end", f"🎬 {p_ad} | {sure} Dk | {drm} | Tarih: {tarih}\n\n")
            finally: self.db.close_connection()

    def favorileri_yukle(self):
        # Favori Filtre
        filtre_frame = ctk.CTkFrame(self.tab_fav, fg_color="transparent")
        filtre_frame.pack(fill="x", pady=5)
        self.fav_combo = ctk.CTkComboBox(filtre_frame, values=["Hepsi", "Film", "Dizi"], command=lambda x: self.fav_guncelle())
        self.fav_combo.set("Hepsi")
        self.fav_combo.pack(side="left", padx=10)
        
        self.fav_liste = ctk.CTkTextbox(self.tab_fav, width=650, height=350)
        self.fav_liste.pack(pady=10)
        self.fav_guncelle()

    def fav_guncelle(self):
        self.fav_liste.delete("1.0", "end")
        if not self.db.connect(): return
        try:
            tip = self.fav_combo.get()
            q = "SELECT p.ad, p.tip FROM Favori f JOIN Program p ON f.program_id = p.id WHERE f.kullanici_id=%s"
            params = [self.k_id]
            if tip != "Hepsi": q += " AND p.tip=%s"; params.append(tip)
            self.db.cursor.execute(q, tuple(params))
            for f in self.db.cursor.fetchall():
                p_ad = f['ad'] if isinstance(f, dict) else f[0]; p_tip = f['tip'] if isinstance(f, dict) else f[1]
                self.fav_liste.insert("end", f"❤️ {p_ad} ({p_tip})\n")
        finally: self.db.close_connection()

# Ana Sayfa 
class AnaSayfa(ctk.CTkToplevel):
    def __init__(self, parent, k_id, kullanici_adi):
        super().__init__(parent)
        self.title("Netflix Platform - Ana Sayfa")
        self.geometry("1100x800") 
        self.db = DatabaseManager()
        self.k_id = k_id 

        self.header_frame = ctk.CTkFrame(self, height=120, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(10, 5), padx=30)
        
        #  Başlıktaki ilk satır
        top_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        top_frame.pack(fill="x")
        ctk.CTkLabel(top_frame, text=f"Hoş Geldin, {kullanici_adi}!", font=("Arial", 24, "bold"), text_color="#E50914").pack(side="left")
        ctk.CTkButton(top_frame, text="👤 Profilim", fg_color="#333333", width=100, command=lambda: ProfilSayfasi(self, self.k_id)).pack(side="right")

        #  Başlığın ikinci satırı 
        filter_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=10)
        
        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Arama...", width=150)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.programlari_yukle()) 
        
        turler = ["Hepsi", "Aksiyon ve Macera", "Bilim Kurgu ve Fantastik", "Komedi", "Drama", "Korku", "Belgesel", "Anime"]
        self.tur_combo = ctk.CTkComboBox(filter_frame, values=turler, width=130); self.tur_combo.set("Tür Seç")
        self.tur_combo.pack(side="left", padx=5)

        self.tip_combo = ctk.CTkComboBox(filter_frame, values=["Hepsi", "Film", "Dizi"], width=100); self.tip_combo.set("Tip Seç")
        self.tip_combo.pack(side="left", padx=5)

        self.sirala_combo = ctk.CTkComboBox(filter_frame, values=["Sıralama", "En Yüksek Puan", "En Çok İzlenen"], width=140); self.sirala_combo.set("Sıralama")
        self.sirala_combo.pack(side="left", padx=5)

        ctk.CTkButton(filter_frame, text="Filtrele", width=80, fg_color="#E50914", command=self.programlari_yukle).pack(side="left", padx=5)

        self.main_scroll = ctk.CTkScrollableFrame(self, width=1050, height=650, fg_color="transparent")
        self.main_scroll.pack(pady=10, padx=10, fill="both", expand=True)
        self.programlari_yukle()

    def programlari_yukle(self):
        for child in self.main_scroll.winfo_children(): child.destroy()
        if not self.db.connect(): return
        try:
            arama = self.search_entry.get().strip()
            tur = self.tur_combo.get()
            tip = self.tip_combo.get()
            sirala = self.sirala_combo.get()
            
            # Öneriler
            if not arama and (tur == "Hepsi" or tur == "Tür Seç") and (tip == "Hepsi" or tip == "Tip Seç") and sirala == "Sıralama":
                ctk.CTkLabel(self.main_scroll, text="Size Özel Öneriler", font=("Arial", 18, "bold"), text_color="#E50914").grid(row=0, column=0, columnspan=4, pady=(10, 5), sticky="w", padx=15)
                self.db.cursor.execute("SELECT tur_id FROM KullaniciTur WHERE kullanici_id=%s", (self.k_id,))
                f_turler = [t['tur_id'] if isinstance(t, dict) else t[0] for t in self.db.cursor.fetchall()]
                oneriler = []
                for t_id in f_turler:
                    self.db.cursor.execute("SELECT p.id, p.ad, p.tip, t.ad as tur_adi, p.ortalama_puan FROM Program p JOIN ProgramTur pt ON p.id = pt.program_id JOIN Tur t ON pt.tur_id = t.id WHERE pt.tur_id=%s ORDER BY p.ortalama_puan DESC LIMIT 2", (t_id,))
                    oneriler.extend(self.db.cursor.fetchall())
                oneriler_unique = { (p['id'] if isinstance(p, dict) else p[0]): p for p in oneriler }.values()
                self.filmleri_ciz(list(oneriler_unique), 1)
                
                ctk.CTkLabel(self.main_scroll, text="Tüm İçerikler", font=("Arial", 18, "bold")).grid(row=5, column=0, columnspan=4, pady=(30, 5), sticky="w", padx=15)
                b_satiri = 6
            else: b_satiri = 0

            #filtreleme sorgusu oluşturma
            query = "SELECT DISTINCT p.id, p.ad, p.tip, p.ortalama_puan, p.izlenme_sayisi, (SELECT t.ad FROM Tur t JOIN ProgramTur pt2 ON t.id=pt2.tur_id WHERE pt2.program_id=p.id LIMIT 1) as tur_adi FROM Program p LEFT JOIN ProgramTur pt ON p.id = pt.program_id LEFT JOIN Tur t ON pt.tur_id = t.id WHERE 1=1"
            params = []
            if arama: query += " AND p.ad LIKE %s"; params.append(f"%{arama}%")
            if tur != "Hepsi" and tur != "Tür Seç": query += " AND t.ad = %s"; params.append(tur)
            if tip != "Hepsi" and tip != "Tip Seç": query += " AND p.tip = %s"; params.append(tip)
            
            if sirala == "En Yüksek Puan": query += " ORDER BY p.ortalama_puan DESC"
            elif sirala == "En Çok İzlenen": query += " ORDER BY p.izlenme_sayisi DESC"
            else: query += " ORDER BY p.id DESC"

            self.db.cursor.execute(query, tuple(params))
            programlar = self.db.cursor.fetchall()
            if not programlar: ctk.CTkLabel(self.main_scroll, text="Sonuç bulunamadı.", text_color="gray").grid(row=b_satiri, column=0, pady=50); return
            self.filmleri_ciz(programlar, b_satiri)
        finally: self.db.close_connection()

    def filmleri_ciz(self, lst, baslangic_row):
        row, col = baslangic_row, 0
        for p in lst:
            p_id = p['id'] if isinstance(p, dict) else p[0]; ad = p['ad'] if isinstance(p, dict) else p[1]; tip = p['tip'] if isinstance(p, dict) else p[2]; tur = p['tur_adi'] if isinstance(p, dict) else p[5] if len(p)>5 else p[3]
            tur = tur if tur else "Genel"

            card = ctk.CTkFrame(self.main_scroll, width=210, height=390, corner_radius=15, fg_color="#1a1a1a")
            card.grid(row=row, column=col, padx=15, pady=15)
            card.grid_propagate(False)

            img_path = next((f"posters/{ad}{ext}" for ext in [".jpg", ".png", ".jpeg", ".webp"] if os.path.exists(f"posters/{ad}{ext}")), None)
            if img_path:
                try: ctk.CTkLabel(card, text="", image=ctk.CTkImage(light_image=Image.open(img_path), size=(160, 220))).pack(pady=(15, 5))
                except: ctk.CTkLabel(card, text="Bozuk", width=160, height=220, fg_color="#333333").pack(pady=(15, 5))
            else: ctk.CTkLabel(card, text="Resim Yok", width=160, height=220, fg_color="#333333").pack(pady=(15, 5))

            ctk.CTkLabel(card, text=ad, font=("Arial", 14, "bold"), wraplength=180).pack(pady=2)
            ctk.CTkLabel(card, text=f"{tip} | {tur}", font=("Arial", 10), text_color="#E50914").pack(pady=2)
            ctk.CTkButton(card, text="İncele & İzle", width=110, height=32, fg_color="#E50914", command=lambda pid=p_id: IcerikDetaySayfasi(self, self.k_id, pid)).pack(side="bottom", pady=15)
            col += 1
            if col > 3: col, row = 0, row + 1

# Yönetici Paneli
class AdminPaneli(ctk.CTkToplevel):
    def __init__(self, parent, admin_adi):
        super().__init__(parent)
        self.title("Netflix Platform - Yönetici Paneli")
        self.geometry("850x700") 
        self.grab_set(); self.focus_force()
        self.db = DatabaseManager()

        ctk.CTkLabel(self, text=f"Yönetici Paneli - Hoş Geldin, {admin_adi}", font=("Arial", 24, "bold"), text_color="#E50914").pack(pady=(15, 10))
        self.tabview = ctk.CTkTabview(self, width=800, height=600)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tab_icerik = self.tabview.add("İçerik Yönetimi")
        self.tab_tur = self.tabview.add("Tür Yönetimi")       
        self.tab_kullanici = self.tabview.add("Kullanıcılar") 
        self.tab_rapor = self.tabview.add("Raporlar")         

        self.icerik_sekmesini_olustur()
        self.tur_sekmesini_olustur()
        self.kullanici_sekmesini_olustur()
        self.rapor_sekmesini_olustur()

    def icerik_sekmesini_olustur(self):
        input_frame = ctk.CTkFrame(self.tab_icerik, fg_color="transparent")
        input_frame.pack(pady=5, fill="x", padx=10)
        self.ad_entry = ctk.CTkEntry(input_frame, placeholder_text="Program Adı", width=250)
        self.ad_entry.grid(row=0, column=0, padx=5, pady=5)
        self.tip_combo = ctk.CTkComboBox(input_frame, values=["Film", "Dizi"], width=150)
        self.tip_combo.grid(row=0, column=1, padx=5, pady=5)
        self.yil_entry = ctk.CTkEntry(input_frame, placeholder_text="Yılı", width=150)
        self.yil_entry.grid(row=0, column=2, padx=5, pady=5)
        self.aciklama_entry = ctk.CTkEntry(input_frame, placeholder_text="Açıklama", width=250)
        self.aciklama_entry.grid(row=1, column=0, padx=5, pady=5)
        self.bolum_entry = ctk.CTkEntry(input_frame, placeholder_text="Bölüm", width=150)
        self.bolum_entry.grid(row=1, column=1, padx=5, pady=5)
        self.uzunluk_entry = ctk.CTkEntry(input_frame, placeholder_text="Uzunluk(Dk)", width=150)
        self.uzunluk_entry.grid(row=1, column=2, padx=5, pady=5)
        
        t_list = self.turleri_getir()
        self.tur1_combo = ctk.CTkComboBox(input_frame, values=t_list, width=180); self.tur1_combo.grid(row=3, column=0, padx=5, pady=5)
        self.tur2_combo = ctk.CTkComboBox(input_frame, values=["Seçilmedi"] + t_list, width=180); self.tur2_combo.set("Seçilmedi"); self.tur2_combo.grid(row=3, column=1, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(self.tab_icerik, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Ekle", fg_color="#E50914", width=120, command=self.p_ekle).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Güncelle", fg_color="#2196F3", width=120, command=self.p_guncelle).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Sil", fg_color="gray", width=120, command=self.p_sil).pack(side="left", padx=5)

        self.p_liste = ctk.CTkTextbox(self.tab_icerik, width=700, height=180)
        self.p_liste.pack(pady=10)
        self.p_listele()

    def p_ekle(self):
        ad, tip, yil = self.ad_entry.get().strip(), self.tip_combo.get(), self.yil_entry.get().strip()
        ack, bol, uz = self.aciklama_entry.get().strip(), self.bolum_entry.get().strip(), self.uzunluk_entry.get().strip()
        if not ad: return
        if self.db.connect():
            try:
                b_s = bol if bol else 1; u_s = uz if uz else 0; y_s = yil if yil else 2020
                self.db.cursor.execute("INSERT INTO Program (ad, tip, aciklama, yayin_yili, uzunluk, bolum_sayisi) VALUES (%s,%s,%s,%s,%s,%s)", (ad, tip, ack, y_s, u_s, b_s))
                p_id = self.db.cursor.lastrowid
                for t in [self.tur1_combo.get(), self.tur2_combo.get()]:
                    if t and t != "Seçilmedi":
                        self.db.cursor.execute("SELECT id FROM Tur WHERE ad=%s", (t,))
                        res = self.db.cursor.fetchone()
                        if res: self.db.cursor.execute("INSERT INTO ProgramTur (program_id, tur_id) VALUES (%s,%s)", (p_id, (res['id'] if isinstance(res, dict) else res[0])))
                self.db.connection.commit(); messagebox.showinfo("Başarılı", "Eklendi."); self.p_listele()
            finally: self.db.close_connection()

    def p_sil(self):
        from tkinter import simpledialog
        sid = simpledialog.askstring("Sil", "ID:")
        if sid and sid.isdigit():
            if self.db.connect():
                try: self.db.cursor.execute("DELETE FROM Program WHERE id=%s", (sid,)); self.db.connection.commit(); self.p_listele()
                finally: self.db.close_connection()

    def p_guncelle(self):
        from tkinter import simpledialog
        pid = simpledialog.askstring("Güncelle", "ID:")
        if not pid or not pid.isdigit(): return
        yad = simpledialog.askstring("Güncelle", "Yeni Ad (Boş geçilebilir):")
        ybol = simpledialog.askstring("Güncelle", "Yeni Bölüm Sayısı:")
        if self.db.connect():
            try:
                if yad: self.db.cursor.execute("UPDATE Program SET ad=%s WHERE id=%s", (yad, pid))
                if ybol and ybol.isdigit(): self.db.cursor.execute("UPDATE Program SET bolum_sayisi=%s WHERE id=%s", (ybol, pid))
                self.db.connection.commit(); messagebox.showinfo("Başarılı", "Güncellendi."); self.p_listele()
            finally: self.db.close_connection()

    def p_listele(self):
        self.p_liste.delete("1.0", "end")
        if self.db.connect():
            try:
                self.db.cursor.execute("SELECT id, ad, tip FROM Program ORDER BY id DESC")
                for p in self.db.cursor.fetchall(): self.p_liste.insert("end", f"ID: {(p['id'] if isinstance(p, dict) else p[0])} | {(p['ad'] if isinstance(p, dict) else p[1])}\n")
            finally: self.db.close_connection()

    def tur_sekmesini_olustur(self):
        self.t_entry = ctk.CTkEntry(self.tab_tur, placeholder_text="Yeni Tür Adı", width=300); self.t_entry.pack(pady=20)
        btn_frame = ctk.CTkFrame(self.tab_tur, fg_color="transparent"); btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Ekle", fg_color="#E50914", command=self.t_ekle).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Sil", fg_color="gray", command=self.t_sil).pack(side="left", padx=10)
        self.t_liste = ctk.CTkTextbox(self.tab_tur, width=400, height=200); self.t_liste.pack(pady=20)
        self.t_listele()

    def turleri_getir(self):
        if self.db.connect():
            try: self.db.cursor.execute("SELECT ad FROM Tur"); return [r['ad'] if isinstance(r, dict) else r[0] for r in self.db.cursor.fetchall()]
            finally: self.db.close_connection()
        return []

    def t_listele(self):
        self.t_liste.delete("1.0", "end")
        if self.db.connect():
            try:
                self.db.cursor.execute("SELECT id, ad FROM Tur ORDER BY id ASC")
                for t in self.db.cursor.fetchall(): self.t_liste.insert("end", f"ID: {(t['id'] if isinstance(t, dict) else t[0])} | {(t['ad'] if isinstance(t, dict) else t[1])}\n")
            finally: self.db.close_connection()

    def t_ekle(self):
        ad = self.t_entry.get().strip()
        if not ad: return
        if self.db.connect():
            try: self.db.cursor.execute("INSERT INTO Tur (ad) VALUES (%s)", (ad,)); self.db.connection.commit(); self.t_listele()
            finally: self.db.close_connection()

    def t_sil(self):
        from tkinter import simpledialog
        sid = simpledialog.askstring("Sil", "Tür ID:")
        if sid and sid.isdigit():
            if self.db.connect():
                try:
                    self.db.cursor.execute("SELECT COUNT(*) FROM ProgramTur WHERE tur_id=%s", (sid,))
                    if (self.db.cursor.fetchone()['COUNT(*)'] if isinstance(self.db.cursor.fetchone(), dict) else self.db.cursor.fetchone()[0]) > 0: messagebox.showerror("Hata", "Bu türe bağlı film var!"); return
                    self.db.cursor.execute("DELETE FROM Tur WHERE id=%s", (sid,)); self.db.connection.commit(); self.t_listele()
                finally: self.db.close_connection()

    def kullanici_sekmesini_olustur(self):
        frm = ctk.CTkFrame(self.tab_kullanici, fg_color="transparent"); frm.pack(pady=10)
        ctk.CTkButton(frm, text="Yenile", command=self.k_listele).pack(side="left", padx=5)
        self.k_id_entry = ctk.CTkEntry(frm, placeholder_text="ID", width=100); self.k_id_entry.pack(side="left", padx=15)
        ctk.CTkButton(frm, text="Durum Değiştir", fg_color="#E50914", command=self.k_durum).pack(side="left", padx=5)
        self.k_liste = ctk.CTkTextbox(self.tab_kullanici, width=750, height=350); self.k_liste.pack(pady=10)
        self.k_listele()

    def k_listele(self):
        self.k_liste.delete("1.0", "end")
        if self.db.connect():
            try:
                self.db.cursor.execute("SELECT id, ad, email, aktif_mi FROM Kullanici WHERE rol_id=2")
                for k in self.db.cursor.fetchall():
                    drm = "Aktif" if (k['aktif_mi'] if isinstance(k, dict) else k[3]) else "Pasif"
                    self.k_liste.insert("end", f"ID: {(k['id'] if isinstance(k, dict) else k[0])} | {(k['ad'] if isinstance(k, dict) else k[1])} | {drm}\n")
            finally: self.db.close_connection()

    def k_durum(self):
        kid = self.k_id_entry.get()
        if not kid.isdigit(): return
        if self.db.connect():
            try:
                self.db.cursor.execute("SELECT aktif_mi FROM Kullanici WHERE id=%s", (kid,))
                res = self.db.cursor.fetchone()
                if res: self.db.cursor.execute("UPDATE Kullanici SET aktif_mi=%s WHERE id=%s", (not (res['aktif_mi'] if isinstance(res, dict) else res[0]), kid)); self.db.connection.commit(); self.k_listele()
            finally: self.db.close_connection()

    def rapor_sekmesini_olustur(self):
        scroll = ctk.CTkScrollableFrame(self.tab_rapor, width=750, height=500, fg_color="transparent")
        scroll.pack(pady=10, fill="both", expand=True)

        if not self.db.connect(): return
        try:
            self.db.cursor.execute("SELECT COUNT(*) FROM Kullanici WHERE rol_id=2")
            k_s = self.db.cursor.fetchone(); k_s = k_s['COUNT(*)'] if isinstance(k_s, dict) else k_s[0]
            self.db.cursor.execute("SELECT SUM(izlenme_sayisi) FROM Program")
            izl = self.db.cursor.fetchone(); izl = izl['SUM(izlenme_sayisi)'] if isinstance(izl, dict) else izl[0]; izl = izl if izl else 0
            
            genel_frame = ctk.CTkFrame(scroll, fg_color="#1a1a1a"); genel_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(genel_frame, text="📊 Genel İstatistikler", font=("Arial", 18, "bold"), text_color="#E50914").pack(pady=5)
            ctk.CTkLabel(genel_frame, text=f"Kullanıcı: {k_s} | Toplam İzlenme: {izl}", font=("Arial", 14)).pack(pady=5)

            self.db.cursor.execute("SELECT ad, izlenme_sayisi FROM Program ORDER BY izlenme_sayisi DESC LIMIT 10")
            self.r_ciz(scroll, "🔥 En Çok İzlenen 10 İçerik", self.db.cursor.fetchall(), "izlenme_sayisi", "Kez")

            self.db.cursor.execute("SELECT ad, ortalama_puan FROM Program ORDER BY ortalama_puan DESC LIMIT 10")
            self.r_ciz(scroll, "⭐ En Yüksek Puanlı 10 İçerik", self.db.cursor.fetchall(), "ortalama_puan", "Puan")

            self.db.cursor.execute("SELECT u.ad, SUM(i.izlenen_sure) as sure FROM IzlemeLog i JOIN Kullanici u ON i.kullanici_id = u.id GROUP BY u.id ORDER BY sure DESC LIMIT 5")
            self.r_ciz(scroll, "👑 En Aktif Kullanıcılar", self.db.cursor.fetchall(), "sure", "Dakika")

            self.db.cursor.execute("SELECT t.ad, SUM(p.izlenme_sayisi) as toplam FROM Tur t JOIN ProgramTur pt ON t.id=pt.tur_id JOIN Program p ON pt.program_id=p.id GROUP BY t.id ORDER BY toplam DESC LIMIT 5")
            self.r_ciz(scroll, "🎭 En Çok İzlenen Türler", self.db.cursor.fetchall(), "toplam", "Kez")

            self.db.cursor.execute("SELECT p.ad, i.izleme_tarihi FROM IzlemeLog i JOIN Program p ON i.program_id=p.id WHERE i.izleme_tarihi >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) ORDER BY i.izleme_tarihi DESC LIMIT 10")
            self.r_ciz(scroll, "📅 Son 7 Günde İzlenenler", self.db.cursor.fetchall(), "izleme_tarihi", "")

        finally: self.db.close_connection()

    def r_ciz(self, parent, baslik, veriler, anahtar, birim):
        f = ctk.CTkFrame(parent, fg_color="#222222"); f.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(f, text=baslik, font=("Arial", 16, "bold"), text_color="#E50914").pack(pady=5)
        if not veriler: ctk.CTkLabel(f, text="Veri yok.", text_color="gray").pack(pady=5); return
        m = ""
        for i, v in enumerate(veriler, 1):
            ad = list(v.values())[0] if isinstance(v, dict) else v[0]
            dg = v[anahtar] if isinstance(v, dict) else v[1]
            if isinstance(dg, float): dg = round(dg, 1)
            m += f"{i}. {ad} - {dg} {birim}\n"
        ctk.CTkLabel(f, text=m, justify="left", font=("Arial", 14)).pack(pady=5)

#  Kayıt Penceresi
class kayiypenceresi(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Kayıt Ol")
        self.geometry("480x750")
        self.grab_set()

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=450, height=680) 
        self.scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(self.scroll_frame, text="Yeni Hesap", font=("Arial",26,"bold"), text_color="#E50914").pack(pady=20)

        self.ad_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Adınız", height=35); self.ad_entry.pack(pady=8, padx=30, fill="x")
        self.soyad_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Soyadınız", height=35); self.soyad_entry.pack(pady=8, padx=30, fill="x")
        self.email_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="E-mail", height=35); self.email_entry.pack(pady=8, padx=30, fill="x")
        self.sifre_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Şifre", show="*", height=35); self.sifre_entry.pack(pady=8, padx=30, fill="x")
        self.sifre_tek_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Şifre Tekrar", show="*", height=35); self.sifre_tek_entry.pack(pady=8, padx=30, fill="x")
        self.dogum_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Doğum Tarihi (YYYY-AA-GG)", height=35); self.dogum_entry.pack(pady=8, padx=30, fill="x")

        self.cinsiyet_combo = ctk.CTkComboBox(self.scroll_frame, values=["Erkek", "Kadın"], height=35); self.cinsiyet_combo.pack(pady=8, padx=30, fill="x")
        self.ulke_combo = ctk.CTkComboBox(self.scroll_frame, values=["Türkiye", "Suriye", "Almanya"], height=35); self.ulke_combo.pack(pady=8, padx=30, fill="x")

        ctk.CTkLabel(self.scroll_frame, text="Favori 3 Türünüz:").pack(pady=10)
        tur_list = ["Aksiyon ve Macera", "Bilim Kurgu ve Fantastik", "Romantik", "Komedi", "Korku", "Belgesel", "Drama", "Anime"]
        self.t1 = ctk.CTkComboBox(self.scroll_frame, values=tur_list, height=35); self.t1.pack(pady=5, padx=30, fill="x")
        self.t2 = ctk.CTkComboBox(self.scroll_frame, values=tur_list, height=35); self.t2.pack(pady=5, padx=30, fill="x")
        self.t3 = ctk.CTkComboBox(self.scroll_frame, values=tur_list, height=35); self.t3.pack(pady=5, padx=30, fill="x")

        ctk.CTkButton(self.scroll_frame, text="Kayıt Ol", fg_color="#E50914", height=45, command=self.kayit_islemi).pack(pady=30, padx=30, fill="x")

    def kayit_islemi(self):
        ad, soy, mail, sif, sif2, dog = self.ad_entry.get().strip(), self.soyad_entry.get().strip(), self.email_entry.get().strip(), self.sifre_entry.get().strip(), self.sifre_tek_entry.get().strip(), self.dogum_entry.get().strip()
        if not all([ad, soy, mail, sif, dog]): messagebox.showwarning("Uyarı", "Boş alan bırakmayınız!"); return
        if sif != sif2 or len(sif)<6: messagebox.showwarning("Hata", "Şifre hatası!"); return
        db = DatabaseManager()
        if db.connect():
            try:
                db.cursor.execute("INSERT INTO Kullanici (ad, soyad, email, sifre, dogum_tarihi, cinsiyet, ulke, rol_id) VALUES (%s,%s,%s,%s,%s,%s,%s, 2)", (ad, soy, mail, sif, dog, self.cinsiyet_combo.get(), self.ulke_combo.get()))
                k_id = db.cursor.lastrowid
                for tur in [self.t1.get(), self.t2.get(), self.t3.get()]:
                    db.cursor.execute("SELECT id FROM Tur WHERE ad=%s", (tur,))
                    r = db.cursor.fetchone()
                    if r: db.cursor.execute("INSERT INTO KullaniciTur (kullanici_id, tur_id) VALUES (%s, %s)", (k_id, (r['id'] if isinstance(r, dict) else r[0])))
                db.connection.commit(); messagebox.showinfo("Başarılı", "Kayıt Başarılı!"); self.destroy()
            finally: db.close_connection()

class NetflixApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Netflix Platform - Giriş")
        self.geometry("400x520")
        self.db = DatabaseManager()
        self.giris_ekrani_olustur()

    def giris_ekrani_olustur(self):
        ctk.CTkLabel(self, text="NETFLIX", font=("Arial",40,"bold"), text_color="#E50914").pack(pady=(60,40))
        self.email_entry = ctk.CTkEntry(self, placeholder_text="E-mail", width=320, height=45)
        self.email_entry.pack(pady=10)
        self.sifre_entry = ctk.CTkEntry(self, placeholder_text="Şifre", show="*", width=320, height=45)
        self.sifre_entry.pack(pady=10)
        ctk.CTkButton(self, text="Giriş Yap", font=("Arial",16,"bold"), fg_color="#E50914", width=320, height=50, command=self.giris_yap).pack(pady=20)
        ctk.CTkButton(self, text="Yeni Hesap Oluştur", fg_color="transparent", text_color="gray", command=lambda: kayiypenceresi(self)).pack()

    def giris_yap(self):
        mail, sif = self.email_entry.get().strip(), self.sifre_entry.get().strip()
        if not mail or not sif: messagebox.showwarning("Uyarı", "Boş alan bırakmayınız!"); return
        if self.db.connect():
            try:
                self.db.cursor.execute("SELECT id, ad, rol_id, aktif_mi FROM Kullanici WHERE email=%s AND sifre=%s", (mail, sif))
                user = self.db.cursor.fetchone()
                if user:
                    k_id = user['id'] if isinstance(user, dict) else user[0]
                    isim = user['ad'] if isinstance(user, dict) else user[1]
                    rol = user['rol_id'] if isinstance(user, dict) else user[2]
                    if not (user['aktif_mi'] if isinstance(user, dict) else user[3]): messagebox.showerror("Hata", "Hesabınız dondurulmuştur."); return
                    
                    # OturumLog 
                    self.db.cursor.execute("INSERT INTO OturumLog (kullanici_id) VALUES (%s)", (k_id,))
                    self.db.connection.commit()

                    self.withdraw()
                    if rol == 1: AdminPaneli(self, isim)
                    else: AnaSayfa(self, k_id, isim)
                else: messagebox.showerror("Hata", "E-mail veya şifre hatalı!")
            finally: self.db.close_connection()

if __name__ == "__main__":
    app = NetflixApp()
    app.mainloop()