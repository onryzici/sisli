# Denemelerden kalan, artık başvurulmayan animasyon/RTG varlıklarını siler
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
try:
    D = "/Game/Sisli/Cocuk2"
    for kl in (D + "/Anim/Test", D + "/Anim/Hazir", D + "/Anim/MCO4"):
        for p in [str(a).split(".")[0] for a in eal.list_assets(kl, recursive=True, include_folder=False)]:
            ref = [str(r) for r in eal.find_package_referencers_for_asset(p, False)]
            OUT.append(("kaldı " + p + " ← " + str(ref)) if ref else (("silindi " if eal.delete_asset(p) else "SİLİNEMEDİ ") + p))
    OUT.append("BS " + str(sorted(set(s.get_editor_property("animation").get_name() for s in eal.load_asset(D + "/Anim/BS_Cocuk2_Hareket2").get_editor_property("sample_data")))))
    OUT.append("TAMAM")
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/temizle_anim_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
