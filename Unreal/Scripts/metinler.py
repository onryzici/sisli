# Oyun metinleri — İngilizce + Türkçe EŞZAMANLI (kullanıcı 2026-11-04: "hikayeyi türkçe ve ingilizce olarak senkron yap").
# Tek kaynak: mek_hepsi.py (WBP_Altyazi çağrıları), kur_uyanis.py (BP_Incele Metin1..3), ui_kur.py (inceleme ekranları), TASARIM.md.
# Oyunda dil: L tuşu (Unreal "culture" en/tr, ayara kaydedilir). Widget'lara "EN~~TR" olarak gider, gösterirken seçilir.
# Seslendirme (ileride): SourceArt/Ses/VO/<dil>/<id>.wav — süre metin uzunluğundan; ses gelince ses süresi esas alınacak (NOTLAR.md).
AYIR = "~~"
SATIR = {
    "giris":        ("Ela...?", "Ela...?"),
    "kontrol":      ("Mouse look  ·  WASD walk  ·  Shift run  ·  Ctrl sneak  ·  E inspect  ·  F flashlight  ·  L Türkçe",
                     "Fare bak  ·  WASD yürü  ·  Shift koş  ·  Ctrl sin  ·  E incele  ·  F fener  ·  L English"),
    "ipucu":        ("E   Inspect", "E   İncele"),
    "tavsan1":      ("Her rabbit. She never sleeps without it.", "Tavşanı. Onsuz hiç uyumaz."),
    "tavsan2":      ("She wouldn't have left it here.", "Onu burada bırakmazdı."),
    "yatak_ela":    ("Her side of the bunk. Cold.", "Ranzanın onun tarafı. Soğuk."),
    "yatak_ben":    ("She always wanted the bottom bunk. And still climbed up to mine when the lights went out.",
                     "Hep alt ranzayı isterdi. Yine de ışıklar sönünce benimkine tırmanırdı."),
    "cizim1":       ("She drew us. Holding hands.", "Bizi çizmiş. El ele."),
    "cizim2":       ("And a red light on top of the tower. I never told her about the red light.",
                     "Bir de kulenin tepesinde kırmızı bir ışık. Ona kırmızı ışıktan hiç bahsetmemiştim."),
    "kurallar1":    ("The rules. I used to read them to her, like a bedtime story.", "Kurallar. Ona masal gibi okurdum."),
    "kurallar2":    ("Someone scratched a line under the last one.", "Biri sonuncusunun altını tırnağıyla çizmiş."),
    "pencere":      ("Fog. And walls, as far as the fog lets me see.", "Sis. Ve sisin izin verdiği yere kadar duvarlar."),
    "dolap_ela":    ("Her locker. Emptied. Not even her coat.", "Dolabı. Boşaltılmış. Montu bile yok."),
    "dolap_bakici": ("Locked. It smells of medicine.", "Kilitli. İlaç kokuyor."),
    "defter1":      ("The night log. Twenty-three names. Mine. Not hers.", "Gece defteri. Yirmi üç isim. Benimki var. Onunki yok."),
    "defter2":      ("02:40. Her initial. Block 7. 'Do not inform the brother.'", "02:40. Baş harfi. 7. Blok. 'Ağabeyine bildirilmeyecek.'"),
    "defter3":      ("They knew I'd look for her.", "Onu arayacağımı biliyorlardı."),
    "kapi_kilitli": ("Locked. The caretaker has the keys.", "Kilitli. Anahtarlar bakıcıda."),
    "anahtar":      ("The caretaker's keys. Still warm.", "Bakıcının anahtarları. Hâlâ sıcak."),
    "kapi_acik":    ("Wait for me, Ela.", "Bekle beni, Ela."),
    # --- kule / tower (bodrum avlusu + Kat 1: Dolaplar) ---
    "avlu":         ("The tower. Her tower. The red light is up there.", "Kule. Onun kulesi. Kırmızı ışık orada, yukarıda."),
    "asansor_ipucu": ("E   Elevator", "E   Asansör"),
    "asansor":      ("Up. Always up.", "Yukarı. Hep yukarı."),
    "asansor_guc_yok": ("No power. The fuse is missing.", "Güç yok. Sigorta yerinde değil."),
    "saklan_ipucu": ("E   Hide", "E   Saklan"),
    "kat1_giris":   ("The lockers. We changed here before every inspection.", "Dolaplar. Her teftişten önce burada giyinirdik."),
    "kat1_bekci":   ("Someone is walking between the rows. A lamp. Slow steps.", "Sıraların arasında biri yürüyor. Bir lamba. Yavaş adımlar."),
    "sigorta1":     ("A fuse. Still warm from the box.", "Bir sigorta. Kutudan yeni çıkarılmış gibi, hâlâ ılık."),
    "sigorta2":     ("The elevator might run now.", "Asansör artık çalışabilir."),
    "kat1_not1":    ("A note in a child's hand: 'He can't see you if you don't breathe.'", "Bir çocuğun el yazısıyla not: 'Nefes almazsan seni göremez.'"),
    "kat2_giris":   ("The second floor. The smell of soup and bleach.", "İkinci kat. Çorba ve çamaşır suyu kokusu."),
    # --- Kat 2: Mutfak / The Kitchen ---
    "kat2_asci":    ("Someone big is breathing by the stoves. He hears more than he sees.",
                     "Ocakların başında iri biri soluyor. Gördüğünden çok duyuyor."),
    "teneke_ipucu": ("E   Pick up", "E   Al"),
    "teneke_al":    ("An empty tin. Left click to throw it. Noise draws them away.",
                     "Boş bir teneke. Sol tık: fırlat. Gürültü onları başka yere çeker."),
    "kat2_kilit":   ("The elevator gate is chained shut. A padlock.", "Asansör kapısı zincirlenmiş. Bir asma kilit."),
    "kat2_anahtar1": ("A small key on a greasy hook by the stove.", "Ocağın yanında, yağlı bir çivide küçük bir anahtar."),
    "kat2_anahtar2": ("It should fit the padlock on the elevator.", "Asansördeki asma kilide uymalı."),
    "kat2_tepsi1":  ("A tray with two bowls. One has an 'E' scratched into the rim.", "İki kâseli bir tepsi. Birinin kenarına 'E' kazınmış."),
    "kat2_tepsi2":  ("Still full. She didn't eat. She never eats when she's scared.", "Hâlâ dolu. Yememiş. Korkunca hiç yemez."),
    "kat2_masa":    ("Scratched into the table: 'Don't eat the blue soup.'", "Masaya kazınmış: 'Mavi çorbayı yeme.'"),
    "dolap_buz":    ("A cold-room door. It doesn't lock from the inside.", "Soğuk oda kapısı. İçeriden kilitlenmiyor."),
    "kat3_giris":   ("The classrooms. The lights are still on, as if a lesson might start any minute.",
                     "Sınıflar. Işıklar hâlâ açık, sanki her an bir ders başlayacak."),
    "devam":        ("To be continued.", "Devam edecek."),
}
def iki(k): en, tr = SATIR[k]; return en + AYIR + tr
def ikili(en, tr): return en + AYIR + tr
def sure(k):   # WBP_Altyazi ile AYNI formül (okuma hızı ~12 karakter/sn + 2.8 sn, 3.2..12 sn)
    n = max(len(SATIR[k][0]), len(SATIR[k][1])); return max(3.2, min(12.0, 2.8 + 0.085 * n))
