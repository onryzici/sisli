# L_Kat01 — "Dolaplar / The Lockers" (TASARIM.md kat 1): soyunma salonu, sırt sırta dolap adaları arasında koridorlar.
# Bekçi (BP_Bekci) koridorlarda fenerle devriye gezer; görürse yakalar (varış asansörüne döndürür). BP_Saklanma dolaplarında saklanılır.
# Sigorta kuzeydoğudaki duşlarda (BP_Incele Al) → kuzeybatıdaki çıkış asansörü (BP_Asansor, Sigorta) L_Kat02'ye çıkar.
# Testler: UY_YURU="x y ..." (BP_TestYuru), UY_SAKLAN=1 (saklanma dolapları kendiliğinden), UY_KAT_OTO=1 (sigorta + asansör kendiliğinden), UY_BEKCI_KOR=1
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
import unreal, os, traceback
from kat_ortak import Kat, V, R, eal
from metinler import iki, sure
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
try:
    k = Kat("/Game/Uyanis/Maps/L_Kat01", log)
    ZEMIN = k.smi("K1_Zemin", k.yz("Zemin_Tozlu"), {"Olcek": 240.0, "PuruzCarpan": 0.9}, {"Ton": (0.40, 0.42, 0.43)})
    DUVAR = k.smi("K1_Duvar", k.yz("Beton_Boya"), {"Olcek": 260.0}, {"Ton": (0.30, 0.37, 0.36)})   # kurum yeşili boyalı beton
    TAVAN = k.smi("K1_Tavan", k.yz("Beton_Kalip"), {"Olcek": 300.0}, {"Ton": (0.28, 0.29, 0.31)})
    METAL = k.smi("Metal_Koyu", k.M_MS, {"Metal": 0.7, "PuruzCarpan": 0.45}, {"Ton": (0.035, 0.036, 0.04)})
    KAROLAJ = k.smi("K1_Karo", k.yz("Beton_Panel"), {"Olcek": 60.0, "PuruzCarpan": 0.6}, {"Ton": (0.52, 0.56, 0.55)})   # duş: küçük karolu
    W, L_, H = 2200.0, 1800.0, 360.0
    # ---------- kabuk ----------
    k.kutu("Zemin", -30, W + 30, -30, L_ + 30, -30, 0, ZEMIN)
    if not os.environ.get("UY_TAVANSIZ"): k.kutu("Tavan", -30, W + 30, -30, L_ + 30, H, H + 40, TAVAN)   # test: tepeden yerleşim görüntüsü
    k.kutu("BatiDuvar", -30, 0, 0, L_, 0, H, DUVAR); k.kutu("DoguDuvar", W, W + 30, 0, L_, 0, H, DUVAR)
    for (et, y0, y1) in (("GuneyDuvar", -30, 0), ("KuzeyDuvar", L_, L_ + 30)):   # asansör ağızları x 80..320
        k.kutu(et + "_A", -30, 80, y0, y1, 0, H, DUVAR); k.kutu(et + "_B", 320, W + 30, y0, y1, 0, H, DUVAR)
    # ---------- asansörler ----------
    var_ic = k.asansor_kabini("AsansorVaris", 200.0, 0.0, +1, DUVAR, METAL, METAL)
    cik_ic = k.asansor_kabini("AsansorCikis", 200.0, L_, -1, DUVAR, METAL, METAL)
    # ---------- dolap adaları (sırt sırta; ön yüz yaw 0 → +Y) ----------
    dw, dd, dh = k.boyut("Dolap"); log("dolap boyutu", round(dw), round(dd), round(dh))
    ADALAR = (600.0, 1000.0, 1400.0); BLOKLAR = ((300.0, 950.0), (1200.0, 1900.0)); SAKLANMA = []
    for ai, yc in enumerate(ADALAR):
        for (x0, x1) in BLOKLAR:
            n = int((x1 - x0) // (dw + 2)); xs = [x0 + (i + 0.5) * (x1 - x0) / n for i in range(n)]
            for i, x in enumerate(xs):
                for yon, yaw in ((-1, 180.0), (+1, 0.0)):   # güney yüzlü ve kuzey yüzlü sıra
                    y = yc + yon * (dd / 2 + 1.0)
                    k.koy("Dolap", x, y, yaw + ((i * 37 + ai * 11) % 5 - 2) * 0.6, 0.0, 0.3, etiket=f"Dolap_{ai}_{int(x)}_{yon}")
                    SAKLANMA.append((x, y + yon * (dd / 2 + 55.0), yon, ai))
    # saklanılabilen dolaplar (koridorlara bakanlar arasından seçili)
    sec = [(650, 0, +1), (1550, 0, +1), (800, 1, -1), (1700, 1, -1), (500, 1, +1), (1400, 1, +1), (1300, 2, -1), (1800, 2, -1)]
    for (sx, sai, syon) in sec:
        c = min((s for s in SAKLANMA if s[3] == sai and s[2] == syon), key=lambda s: abs(s[0] - sx))
        b = k.spawn(k.bpcls("BP_Saklanma"), V(c[0], c[1], 90.0), R(), f"Saklanma_{sai}_{int(c[0])}")
        if os.environ.get("UY_SAKLAN"): k.sset(b, "TestOto", True)
    # ---------- duşlar (kuzeydoğu): karolu bölmeler, sıcak tek lamba, sigorta masada ----------
    k.kutu("Dus_Zemin", 1700, W, 1520, L_, 0, 1.5, KAROLAJ)
    for i, xb in enumerate((1800.0, 1950.0, 2100.0)):
        k.kutu(f"Dus_Bolme{i}", xb - 4, xb + 4, 1620, L_, 1.5, 210, KAROLAJ)
    masa = k.koy("Masa", 1880.0, 1560.0, 180.0, 1.5, 0.3, etiket="Dus_Masa"); mh = k.boyut("Masa")[2]
    sig = k.spawn(unreal.StaticMeshActor, V(1880.0, 1560.0, 1.5 + mh + 5.0), R(), "Sigorta"); sc_ = sig.static_mesh_component
    sc_.set_static_mesh(k.SIL); sig.set_actor_scale3d(V(0.05, 0.05, 0.1)); sc_.set_material(0, k.smi("Sigorta", k.M_MS, {"Metal": 0.9, "PuruzCarpan": 0.3}, {"Ton": (0.5, 0.42, 0.25), "Isima": (0.4, 0.15, 0.02)}))
    sc_.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    k.isik(unreal.PointLight, "Dus_Lamba", V(1880, 1640, 300), intensity=9.0, attenuation_radius=650.0, source_radius=3.0, use_temperature=True, temperature=2900.0)
    def incele(et, x, y, z, satirlar, yaricap=130.0, al=None):
        b = k.spawn(k.bpcls("BP_Incele"), V(x, y, z), R(), "Incele_" + et)
        for i, kk in enumerate(satirlar[:3]): k.sset(b, f"Metin{i + 1}", iki(kk))
        k.sset(b, "Yaricap", yaricap); k.sset(b, "Sure1", sure(satirlar[0]) + 0.6); k.sset(b, "Sure2", (sure(satirlar[1]) + 0.6) if len(satirlar) > 1 else 3.0)
        if al is not None: k.sset(b, "Al", True); k.sset(b, "AlinanAktor", al)
        if os.environ.get("UY_KAT_OTO"): k.sset(b, "TestOto", True)
        return b
    incele("Sigorta", 1880.0, 1530.0, 100.0, ["sigorta1", "sigorta2"], 120.0, al=sig)
    # çocuk notu: ilk saklanma dolabının kapağında beyaz kâğıt parçası
    n1 = SAKLANMA[0]
    incele("Not1", 650.0, 720.0, 100.0, ["kat1_not1"], 110.0)
    k.kutu("Not1_Kagit", 640, 660, 600 + dd / 2 + 1.2, 600 + dd / 2 + 1.6, 120, 135, k.smi("Kagit_Beyaz", k.M_MS, {"PuruzCarpan": 0.9}, {"Ton": (0.75, 0.73, 0.68)}), golge=False, carpisma=False)
    # ---------- asansör mekaniği ----------
    asn = k.spawn(k.bpcls("BP_Asansor"), V(cik_ic.x, cik_ic.y, 110.0), R(), "Asansor_Cikis")
    k.sset(asn, "Hedef", "L_Kat02"); k.sset(asn, "Sigorta", sig)
    if os.environ.get("UY_KAT_OTO"): k.sset(asn, "TestOto", True)
    # ---------- bekçi ----------
    bk = k.spawn(k.bpcls("BP_Bekci"), V(150.0, 800.0, 0.0), R(yaw=0), "Bekci")
    for n_, p_ in (("P2", (2050.0, 800.0, 0.0)), ("P3", (2050.0, 1200.0, 0.0)), ("P4", (150.0, 1200.0, 0.0)), ("Donus", (var_ic.x, var_ic.y, 95.0))):
        k.sset(bk, n_, V(*p_))
    if os.environ.get("UY_BEKCI_KOR"): k.sset(bk, "TestKor", True)
    if os.environ.get("UY_BEKCI_DUR"): k.sset(bk, "Hiz", 0.0); k.sset(bk, "TestKor", True)   # görüntü testi: yerinde dursun
    # ---------- ışık: seyrek floresanlar (bazıları ölü), çıkışın üstünde kırmızı yol lambası ----------
    for i, (fx, fy) in enumerate(((500, 800), (1400, 800), (1000, 1200), (1800, 1200), (300, 300), (1500, 300))):
        k.spawn(k.bpcls("BP_Floresan"), V(fx, fy, H), R(yaw=90.0), f"Floresan{i}")
    k.spawn(k.bpcls("BP_KirmiziLamba"), V(200.0, L_ - 6.0, 262.0), R(yaw=-90.0), "KirmiziLamba_Cikis")
    k.isik(unreal.PointLight, "Varis_Lamba", V(var_ic.x, var_ic.y, 250), intensity=4.0, attenuation_radius=400.0, source_radius=2.0, use_temperature=True, temperature=4200.0)
    k.atmosfer(gok=float(os.environ.get("UY_GOK", "1.3")), sis=0.03, exp=float(os.environ.get("UY_EXP", "2.4")))
    # ---------- oyuncu + kat açılışı ----------
    fen = k.spawn(k.bpcls("BP_Fener"), V(0, 0, 0), R(), "Fener")
    gi = k.spawn(k.bpcls("BP_KatGiris"), V(0, 0, 0), R(), "KatGiris")
    k.sset(gi, "Metin1", iki("kat1_giris")); k.sset(gi, "Metin2", iki("kat1_bekci")); k.sset(gi, "Bekle1", 2.5); k.sset(gi, "Bekle2", sure("kat1_giris") + 0.8)
    if os.environ.get("UY_YURU"):
        t_ = [float(v) for v in os.environ["UY_YURU"].split()]; tw = k.spawn(k.bpcls("BP_TestYuru"), V(0, 0, 0), R(), "TestYuru")
        for i in range(len(t_) // 2): k.sset(tw, f"H{i + 1}", V(t_[2 * i], t_[2 * i + 1], 0))
        k.sset(tw, "Son", float(len(t_) // 2))
    b_ = [float(v) for v in os.environ.get("UY_BASLA", f"{var_ic.x} {var_ic.y} 90").split()]
    k.test_kamera(); k.baslangic(b_[0], b_[1], b_[2])
    k.kaydet()
    log("TAMAM", "dolap", len(SAKLANMA), "saklanma", len(sec))
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/kur_kat01_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
