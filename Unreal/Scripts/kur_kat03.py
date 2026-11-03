# L_Kat03 — "Sınıflar / Classrooms" (TASARIM.md kat 3) — ŞİMDİLİK YER TUTUCU: asansörle varış, ışıkları açık boş sınıf, "devam edecek".
# Sonraki adım (TASARIM.md): tahtalardaki "dersler" ipucu, 4 haneli şifre makinesi (REANIMAL BP_CodeMachine_4x3), kod çizimlerin tarihinde.
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
import unreal, os, traceback
from kat_ortak import Kat, V, R, eal
from metinler import iki, sure
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
try:
    k = Kat("/Game/Uyanis/Maps/L_Kat03", log)
    ZEMIN = k.smi("K3_Zemin", k.yz("Zemin_Tozlu"), {"Olcek": 220.0, "PuruzCarpan": 0.85}, {"Ton": (0.40, 0.36, 0.30)})
    DUVAR = k.smi("K3_Duvar", k.yz("Beton_Boya"), {"Olcek": 260.0}, {"Ton": (0.42, 0.40, 0.33)})
    TAVAN = k.smi("K3_Tavan", k.yz("Beton_Kalip"), {"Olcek": 300.0}, {"Ton": (0.30, 0.30, 0.30)})
    METAL = k.smi("Metal_Koyu", k.M_MS, {"Metal": 0.7, "PuruzCarpan": 0.45}, {"Ton": (0.035, 0.036, 0.04)})
    TAHTA = k.smi("K3_KaraTahta", k.M_MS, {"PuruzCarpan": 0.9}, {"Ton": (0.035, 0.06, 0.045)})
    W, L_, H = 1600.0, 1200.0, 340.0
    k.kutu("Zemin", -30, W + 30, -30, L_ + 30, -30, 0, ZEMIN); k.kutu("Tavan", -30, W + 30, -30, L_ + 30, H, H + 40, TAVAN)
    k.kutu("BatiDuvar", -30, 0, 0, L_, 0, H, DUVAR); k.kutu("DoguDuvar", W, W + 30, 0, L_, 0, H, DUVAR); k.kutu("KuzeyDuvar", -30, W + 30, L_, L_ + 30, 0, H, DUVAR)
    k.kutu("GuneyDuvar_A", -30, 80, -30, 0, 0, H, DUVAR); k.kutu("GuneyDuvar_B", 320, W + 30, -30, 0, 0, H, DUVAR); k.kutu("GuneyLento", 80, 320, -30, 0, 300, H, DUVAR)
    var_ic = k.asansor_kabini("AsansorVaris", 200.0, 0.0, +1, DUVAR, METAL, METAL)
    k.kutu("KaraTahta", 500, 1300, L_ - 4, L_, 100, 230, TAHTA, golge=False)
    k.kutu("KaraTahta_Cerceve", 495, 1305, L_ - 6, L_, 96, 100, METAL, golge=False)
    for j, y in enumerate((450.0, 650.0, 850.0)):          # sıralar tahtaya bakar (+Y)
        for i, x in enumerate((550.0, 800.0, 1050.0, 1300.0)):
            k.koy("Masa", x, y, ((i * 13 + j * 7) % 5 - 2) * 1.0, 0.0, 0.3, etiket=f"Sira_{j}_{i}")
            k.koy("Sandalye", x, y - 60.0, 180.0 + ((i + j) % 3 - 1) * 6.0, 0.0, 0.3, etiket=f"Sandalye_{j}_{i}")
    for i, (fx, fy) in enumerate(((600, 450), (1100, 450), (600, 900), (1100, 900))):
        k.spawn(k.bpcls("BP_Floresan"), V(fx, fy, H), R(yaw=90.0), f"Floresan{i}")
    k.isik(unreal.PointLight, "Varis_Lamba", V(var_ic.x, var_ic.y, 250), intensity=4.0, attenuation_radius=400.0, source_radius=2.0, use_temperature=True, temperature=4200.0)
    k.atmosfer(gok=1.3, sis=0.03, exp=2.4)
    k.spawn(k.bpcls("BP_Fener"), V(0, 0, 0), R(), "Fener")
    gi = k.spawn(k.bpcls("BP_KatGiris"), V(0, 0, 0), R(), "KatGiris")
    k.sset(gi, "Metin1", iki("kat3_giris")); k.sset(gi, "Metin2", iki("devam")); k.sset(gi, "Bekle1", 2.5); k.sset(gi, "Bekle2", sure("kat3_giris") + 1.5)
    k.test_kamera(); k.baslangic(var_ic.x, var_ic.y, 90.0)
    k.kaydet(); log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/kur_kat03_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
