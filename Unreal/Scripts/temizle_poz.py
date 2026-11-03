# Duruş/ABP işinden kalan test ve eski varlıkları siler (başvurusu kalmayanları)
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2/Anim"
try:
    adaylar = [str(a) for a in eal.list_assets(D + "/Test", recursive=True, include_folder=False)]
    adaylar += [str(a) for a in eal.list_assets(D + "/MCO3", recursive=True, include_folder=False)]
    for p in adaylar:
        p = p.split(".")[0]
        ref = [str(r) for r in eal.find_package_referencers_for_asset(p, False)]
        if ref: log("kaldı (başvuru)", p, ref)
        else: log("silindi" if eal.delete_asset(p) else "SİLİNEMEDİ", p)
    log("BS örnekleri", sorted(set(s.get_editor_property("animation").get_name() for s in eal.load_asset(D + "/BS_Cocuk2_Hareket2").get_editor_property("sample_data"))))
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/temizle_poz_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
