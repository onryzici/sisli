# L_Kat02 — "Mutfak / The Kitchen" (TASARIM.md kat 2). REANIMAL: BP_Pickup_ThrowableBase_TinCan + BP_HidingSpot_Refrigerator/_Oven + iri düşman.
#  Batı yarı: yemekhane (masalar, tabureler, Ela'nın tepsisi). Varış asansörü güneybatıda.
#  x=1000: paslanmaz servis tezgâhı (95 cm) — çömelince arkasında görünmezsin; kuzey ve güney uçlarından geçilir.
#  Doğu yarı: mutfak — doğu duvarında ocaklar + davlumbaz, ortada hazırlık adası. İRİ AŞÇI (BP_Bekci ölçek 1.2, kirli önlük, loş baş lambası)
#    adanın çevresinde döner; tenekenin sesini duyunca (Duyma 1800) oraya yürür, tezgâha/masaya takılırsa orada durup bakınır.
#  Anahtar ocakların kuzey ucunda çivide (BP_Incele Al) → kuzey duvardaki asansör (x 1200) zincirli: anahtar alınınca L_Kat03'e çıkar.
#  Saklanma: kuzey duvarda iki soğuk oda kapısı, iki yemek masasının altı. Teneke (BP_Atilabilir) x3.
# Testler: UY_TENEKE=1 (oyuncu tenekenin yanında başlar; teneke kendiliğinden alınıp UY_TENEKE_HEDEF'e atılır), UY_KAT_OTO=1 (anahtar + asansör kendiliğinden),
#          UY_BEKCI_KOR, UY_BEKCI_DUR, UY_KAMERA, UY_BASLA, UY_YURU, UY_TAVANSIZ
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
import unreal, os, traceback
from kat_ortak import Kat, V, R, eal
from metinler import iki, sure
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
env = os.environ.get
try:
    k = Kat("/Game/Uyanis/Maps/L_Kat02", log)
    ZEMIN = k.smi("K2_Zemin", k.yz("Zemin_Kahve"), {"Olcek": 200.0, "PuruzCarpan": 0.8}, {"Ton": (0.42, 0.40, 0.37)})
    DUVAR = k.smi("K2_Duvar", k.yz("Siva"), {"Olcek": 240.0}, {"Ton": (0.46, 0.44, 0.40)})
    TAVAN = k.smi("K2_Tavan", k.yz("Beton_Kalip"), {"Olcek": 300.0}, {"Ton": (0.28, 0.28, 0.29)})
    METAL = k.smi("Metal_Koyu", k.M_MS, {"Metal": 0.7, "PuruzCarpan": 0.45}, {"Ton": (0.035, 0.036, 0.04)})
    KARO = k.smi("K2_Karo", k.yz("Beton_Panel"), {"Olcek": 45.0, "PuruzCarpan": 0.5}, {"Ton": (0.30, 0.33, 0.31)})   # mutfak: küçük, yeşilimsi karo
    CELIK = k.smi("K2_Celik", k.M_MS, {"Metal": 0.9, "PuruzCarpan": 0.35}, {"Ton": (0.34, 0.34, 0.35)})              # paslanmaz tezgâh
    TENCERE = k.smi("K2_Tencere", k.M_MS, {"Metal": 0.85, "PuruzCarpan": 0.5}, {"Ton": (0.16, 0.15, 0.14)})
    ATES = k.smi("K2_Ates", k.M_MS, {"PuruzCarpan": 1.0}, {"Ton": (0.02, 0.01, 0.0), "Isima": (5.0, 1.3, 0.15)})
    BUZ = k.smi("K2_Buz", k.M_MS, {"Metal": 0.6, "PuruzCarpan": 0.55}, {"Ton": (0.40, 0.43, 0.45)})
    CORBA = k.smi("K2_Corba", k.M_MS, {"PuruzCarpan": 0.25}, {"Ton": (0.05, 0.12, 0.2)})                             # mavi çorba
    W, L_, H = 2000.0, 1600.0, 380.0; CX = 1200.0   # CX: çıkış asansörü (kuzey duvar)
    # ---------- kabuk ----------
    k.kutu("Zemin", -30, W + 30, -30, L_ + 30, -30, 0, ZEMIN)
    k.kutu("Mutfak_Karo", 1045, W, 0, L_, 0, 1.2, KARO, golge=False)
    if not env("UY_TAVANSIZ"): k.kutu("Tavan", -30, W + 30, -30, L_ + 30, H, H + 40, TAVAN)
    k.kutu("BatiDuvar", -30, 0, 0, L_, 0, H, DUVAR); k.kutu("DoguDuvar", W, W + 30, 0, L_, 0, H, DUVAR)
    k.kutu("GuneyDuvar_A", -30, 80, -30, 0, 0, H, DUVAR); k.kutu("GuneyDuvar_B", 320, W + 30, -30, 0, 0, H, DUVAR)
    k.kutu("KuzeyDuvar_A", -30, CX - 120, L_, L_ + 30, 0, H, DUVAR); k.kutu("KuzeyDuvar_B", CX + 120, W + 30, L_, L_ + 30, 0, H, DUVAR)
    k.kutu("GuneyLento", 80, 320, -30, 0, 300, H, DUVAR); k.kutu("KuzeyLento", CX - 120, CX + 120, L_, L_ + 30, 300, H, DUVAR)
    var_ic = k.asansor_kabini("AsansorVaris", 200.0, 0.0, +1, DUVAR, METAL, METAL)
    cik_ic = k.asansor_kabini("AsansorCikis", CX, L_, -1, DUVAR, METAL, METAL)
    k.kutu("Mutfak_DuvarKaro", 1997, W, 250, 1150, 92, 250, KARO, golge=False, carpisma=False)   # ocak arkası fayans
    def silindir(et, x, y, z0, cap, boy, mt, carp=False):
        a = k.spawn(unreal.StaticMeshActor, V(x, y, z0 + boy / 2.0), R(), et); c = a.static_mesh_component
        c.set_static_mesh(k.SIL); a.set_actor_scale3d(V(cap / 100.0, cap / 100.0, boy / 100.0)); c.set_material(0, mt)
        if not carp: c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        return a
    # ---------- servis tezgâhı (x=1000) ----------
    k.kutu("Tezgah", 965, 1035, 250, 1350, 0, 90, METAL); k.kutu("Tezgah_Ust", 960, 1040, 245, 1355, 90, 95, CELIK)
    # Ela'nın tepsisi: iki kâse, biri dolu (mavi çorba)
    k.kutu("Tepsi", 985, 1015, 680, 722, 95, 96.5, CELIK, golge=False, carpisma=False)
    silindir("Kase_A", 1000, 692, 96.5, 14, 6, CELIK); silindir("Kase_A_Corba", 1000, 692, 101.6, 12, 0.6, CORBA)
    silindir("Kase_B", 1000, 711, 96.5, 14, 6, CELIK)
    # ---------- mutfak: ocaklar, davlumbaz, hazırlık adası ----------
    for i, yc in enumerate((350.0, 550.0, 750.0, 950.0)):
        k.kutu(f"Ocak{i}", 1880, W, yc - 96, yc + 96, 0, 90, METAL); k.kutu(f"Ocak{i}_Ust", 1875, W, yc - 98, yc + 98, 90, 94, CELIK)
        k.kutu(f"Ocak{i}_Kapak", 1874, 1876, yc - 70, yc + 70, 18, 70, CELIK, golge=False, carpisma=False)   # fırın kapağı
        for j, dy in enumerate((-45.0, 45.0)):
            silindir(f"Ocak{i}_Ates{j}", 1935, yc + dy, 94, 26, 0.8, ATES)
            if (i + j) % 2 == 0: silindir(f"Ocak{i}_Tencere{j}", 1935, yc + dy, 95, 42 if i != 1 else 56, 34 if i != 1 else 48, TENCERE)
    k.kutu("Davlumbaz", 1810, W, 240, 1060, 250, 300, METAL)
    k.kutu("Ada", 1465, 1585, 480, 1020, 0, 88, METAL); k.kutu("Ada_Ust", 1460, 1590, 475, 1025, 88, 92, CELIK)
    silindir("Ada_Tencere", 1525, 600, 92, 60, 52, TENCERE); silindir("Ada_Tencere2", 1510, 880, 92, 36, 24, TENCERE)
    k.kutu("Ada_Kesme", 1490, 1560, 720, 790, 92, 95, k.smi("K2_Tahta", k.M_MS, {"PuruzCarpan": 0.85}, {"Ton": (0.32, 0.22, 0.14)}), golge=False)
    # kiler köşesi (güneydoğu): çuvallar, kolile, varil
    for (ad, x, y, yaw) in (("Moloz_Torba", 1720, 70, 10), ("Moloz_Torba", 1800, 80, -25), ("Karton_A", 1900, 90, 4), ("Karton_B", 1905, 160, 40), ("Varil", 1960, 230, 0)):
        try: k.koy(ad, x, y, yaw, 1.2, 0.3, etiket=f"Kiler_{ad}_{x}")
        except Exception as e: log("kiler", ad, e)
    # ---------- soğuk oda kapıları (kuzey duvar) = saklanma ----------
    SAK = []
    for i, xc in enumerate((1450.0, 1750.0)):
        k.kutu(f"SogukOda{i}", xc - 65, xc + 65, L_ - 70, L_, 0, 235, BUZ); k.kutu(f"SogukOda{i}_Kol", xc + 40, xc + 48, L_ - 78, L_ - 70, 95, 140, CELIK, golge=False)
        SAK.append((xc, L_ - 130))
    # ---------- yemekhane: masalar + tabureler ----------
    mw, md, mh = k.boyut("Masa"); log("masa boyutu", round(mw), round(md), round(mh))
    MASALAR = [(x, y) for y in (450.0, 800.0, 1150.0) for x in (380.0, 700.0)]
    for i, (x, y) in enumerate(MASALAR):
        k.koy("Masa", x, y, 90.0 + ((i * 7) % 5 - 2) * 1.2, 0.0, 0.3, etiket=f"Masa_{i}")
        for s_ in (-1, 1):
            k.koy("Tabure", x + s_ * 18.0, y + s_ * 62.0, i * 23.0 + s_ * 40, 0.0, 0.3, etiket=f"Tabure_{i}_{s_}")
    SAK += [(380.0, 800.0), (700.0, 1150.0)]   # masa altı
    for (sx, sy) in SAK:
        b = k.spawn(k.bpcls("BP_Saklanma"), V(sx, sy, 90.0), R(), f"Saklanma_{int(sx)}_{int(sy)}")
        if env("UY_SAKLAN"): k.sset(b, "TestOto", True)
    # ---------- inceleme ----------
    def incele(et, x, y, z, satirlar, yaricap=130.0, al=None):
        b = k.spawn(k.bpcls("BP_Incele"), V(x, y, z), R(), "Incele_" + et)
        for i, kk in enumerate(satirlar[:3]): k.sset(b, f"Metin{i + 1}", iki(kk))
        k.sset(b, "Yaricap", yaricap); k.sset(b, "Sure1", sure(satirlar[0]) + 0.6); k.sset(b, "Sure2", (sure(satirlar[1]) + 0.6) if len(satirlar) > 1 else 3.0)
        if al is not None: k.sset(b, "Al", True); k.sset(b, "AlinanAktor", al)
        if env("UY_KAT_OTO"): k.sset(b, "TestOto", True)
        return b
    incele("Tepsi", 1000.0, 700.0, 110.0, ["kat2_tepsi1", "kat2_tepsi2"], 120.0)
    incele("Masa", 700.0, 450.0, 95.0, ["kat2_masa"], 110.0)
    try: anahtar = k.koy("Anahtarlik", 1990.0, 1250.0, 90.0, 128.0, 0.0, carpisma="yok", etiket="Anahtar")
    except Exception as e:
        log("anahtar mesh", e); anahtar = k.spawn(unreal.StaticMeshActor, V(1990, 1250, 135), R(), "Anahtar")
    k.kutu("Anahtar_Civi", 1992, W, 1248, 1252, 138, 142, METAL, golge=False, carpisma=False)
    incele("Anahtar", 1945.0, 1250.0, 110.0, ["kat2_anahtar1", "kat2_anahtar2"], 125.0, al=anahtar)
    # ---------- asansör (zincirli: anahtar alınınca açılır) ----------
    asn = k.spawn(k.bpcls("BP_Asansor"), V(cik_ic.x, cik_ic.y, 110.0), R(), "Asansor_Cikis")
    k.sset(asn, "Hedef", "L_Kat03"); k.sset(asn, "Sigorta", anahtar); k.sset(asn, "KilitMetin", iki("kat2_kilit"))
    if env("UY_KAT_OTO"): k.sset(asn, "TestOto", True)
    k.kutu("Asma_Kilit", CX + 112, CX + 122, L_ - 6, L_ + 2, 100, 116, CELIK, golge=False, carpisma=False)
    # ---------- teneke ----------
    TENEKELER = [("Masa", 380.0, 450.0, mh), ("Gecit", 880.0, 1450.0, 0.0), ("Tezgah", 1000.0, 1180.0, 95.0)]
    for (et, x, y, z) in TENEKELER:
        t = k.spawn(k.bpcls("BP_Atilabilir"), V(x, y, z), R(yaw=x * 0.37), "Teneke_" + et)
        if env("UY_TENEKE") and et == "Gecit":
            h_ = [float(v) for v in env("UY_TENEKE_HEDEF", "300 450 0").split()]
            k.sset(t, "TestOto", True); k.sset(t, "TestHedef", V(*h_))
    # ---------- aşçı ----------
    bk = k.spawn(k.bpcls("BP_Bekci"), V(1650.0, 350.0, 0.0), R(yaw=90), "Asci"); bk.set_actor_scale3d(V(1.2, 1.2, 1.2))
    for n_, p_ in (("P2", (1650.0, 1150.0, 0.0)), ("P3", (1400.0, 1150.0, 0.0)), ("P4", (1400.0, 350.0, 0.0)), ("Donus", (var_ic.x, var_ic.y, 95.0))):
        k.sset(bk, n_, V(*p_))
    for n_, v_ in (("Hiz", 90.0), ("AnimHiz", 0.46), ("Duyma", 1800.0), ("Bekle", 5.0), ("FenerGuc", 70.0), ("SesPerde", 0.7)):
        k.sset(bk, n_, v_)
    k.sset(bk, "Kumas", eal.load_asset("/Game/Uyanis/Sahne/MI_Asci_Onluk"))
    if env("UY_BEKCI_KOR"): k.sset(bk, "TestKor", True)
    if env("UY_BEKCI_DUR"): k.sset(bk, "Hiz", 0.0); k.sset(bk, "TestKor", True)
    # ---------- ışık ----------
    for i, (fx, fy) in enumerate(((540, 620), (540, 1180), (1500, 300), (1500, 1200), (1250, 800))):
        k.spawn(k.bpcls("BP_Floresan"), V(fx, fy, H), R(yaw=90.0), f"Floresan{i}")
    for i, oy_ in enumerate((450.0, 850.0)):
        k.isik(unreal.PointLight, f"Ocak_Isik{i}", V(1915, oy_, 112), intensity=7.0, attenuation_radius=380.0, source_radius=8.0, use_temperature=True, temperature=1800.0)
    k.spawn(k.bpcls("BP_KirmiziLamba"), V(CX, L_ - 6.0, 262.0), R(yaw=-90.0), "KirmiziLamba")
    k.isik(unreal.PointLight, "Varis_Lamba", V(var_ic.x, var_ic.y, 250), intensity=4.0, attenuation_radius=400.0, source_radius=2.0, use_temperature=True, temperature=4200.0)
    k.atmosfer(gok=float(env("UY_GOK", "1.2")), sis=0.035, exp=float(env("UY_EXP", "2.4")))
    # ---------- oyuncu + kat açılışı ----------
    k.spawn(k.bpcls("BP_Fener"), V(0, 0, 0), R(), "Fener")
    gi = k.spawn(k.bpcls("BP_KatGiris"), V(0, 0, 0), R(), "KatGiris")
    k.sset(gi, "Metin1", iki("kat2_giris")); k.sset(gi, "Metin2", iki("kat2_asci")); k.sset(gi, "Bekle1", 2.5); k.sset(gi, "Bekle2", sure("kat2_giris") + 0.8)
    if env("UY_YURU"):
        t_ = [float(v) for v in env("UY_YURU").split()]; tw = k.spawn(k.bpcls("BP_TestYuru"), V(0, 0, 0), R(), "TestYuru")
        for i in range(len(t_) // 2): k.sset(tw, f"H{i + 1}", V(t_[2 * i], t_[2 * i + 1], 0))
        k.sset(tw, "Son", float(len(t_) // 2))
    vars_ = "880 1380 200" if env("UY_TENEKE") else f"{var_ic.x} {var_ic.y} 90"
    b_ = [float(v) for v in env("UY_BASLA", vars_).split()]
    k.test_kamera(); k.baslangic(b_[0], b_[1], b_[2])
    k.kaydet(); log("TAMAM", "masa", len(MASALAR), "saklanma", len(SAK), "teneke", len(TENEKELER))
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/kur_kat02_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
