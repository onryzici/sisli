# F_Garamond / F_Altyazi: FontFactory ile FontFace'lerden oluştur (composite font alanları Python'a kapalı)
import unreal, os, traceback
OUT = []; eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools()
def log(*a): OUT.append(" ".join(str(x) for x in a))
FD = "/Game/Uyanis/UI/Font"; BOY = int(os.environ.get("ALTYAZI_BOY", "30"))
try:
    ff = unreal.FontFactory(); log("FontFactory alanları", [x for x in dir(ff) if not x.startswith("_") and "font" in x.lower()])
    Y = lambda n: eal.load_asset(f"{FD}/FF_EBGaramond_{n}")
    def yap(ad, yuzler, boy=None):
        yol = f"/Game/Uyanis/UI/{ad}"
        if eal.does_asset_exist(yol): log("sil", yol, eal.delete_asset(yol))
        f_ = unreal.FontFactory()
        try: f_.set_editor_property("initial_font_faces", yuzler)
        except Exception as e: log("initial_font_faces yok", e)
        fo = at.create_asset(ad, "/Game/Uyanis/UI", unreal.Font, f_)
        fo.set_editor_property("font_cache_type", unreal.FontCacheType.RUNTIME)
        if boy: fo.set_editor_property("legacy_font_size", boy)
        eal.save_loaded_asset(fo, only_if_is_dirty=False)
        log("font", ad, fo, "cache", fo.get_editor_property("font_cache_type"), "boy", fo.get_editor_property("legacy_font_size"))
        try: log("  typeface", [str(n) for n in unreal.FontLibrary.get_font_face_names(fo)] if hasattr(unreal, "FontLibrary") else "-")
        except Exception as e: log("  typeface okunamadı", e)
    yap("F_Garamond", [Y("Regular"), Y("Italic"), Y("Medium"), Y("SemiBold")])
    yap("F_Altyazi", [Y("Italic")], BOY)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/font_kur2_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
unreal.SystemLibrary.quit_editor()
