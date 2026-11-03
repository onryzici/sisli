# EB Garamond (OFL, SourceArt/Font) → FontFace varlıkları /Game/Uyanis/UI/Font; F_Garamond (UMG: Regular/Italic/Medium) ve
# F_Altyazi (motor altyazısı: tek yüz İtalik, legacy boyut ALTYAZI_BOY) bu yüzlere bağlanır. Kâğıt dokuları da (İngilizce) yeniden içe alınır.
import unreal, os, traceback
OUT = []; eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools()
def log(*a): OUT.append(" ".join(str(x) for x in a))
FD = "/Game/Uyanis/UI/Font"; SRC = "C:/Users/Onur/Sisli/Unreal/SourceArt/Font/"; BOY = int(os.environ.get("ALTYAZI_BOY", "30"))
YUZ = {"Regular": "EBGaramond-Regular", "Italic": "EBGaramond-Italic", "Medium": "EBGaramond-Medium", "SemiBold": "EBGaramond-SemiBold"}
def ice_al(dosya, hedef, ad):
    t = unreal.AssetImportTask(); t.filename = dosya; t.destination_path = hedef; t.destination_name = ad; t.automated = True; t.save = True; t.replace_existing = True
    at.import_asset_tasks([t]); return [str(p) for p in t.get_editor_property("imported_object_paths")]
try:
    yuzler = {}
    for ad, dosya in YUZ.items():
        r = ice_al(SRC + dosya + ".ttf", FD, "FF_" + dosya.replace("-", "_")); log("içe", ad, r)
        yuzler[ad] = eal.load_asset(f"{FD}/FF_{dosya.replace('-', '_')}")
        log("  sınıf", yuzler[ad].get_class().get_name() if yuzler[ad] else None)
    def font_yap(yol, girisler):
        if not eal.does_asset_exist(yol): eal.duplicate_asset("/Engine/EngineFonts/Roboto", yol)
        f = eal.load_asset(yol); cf = f.get_editor_property("composite_font"); tf = cf.get_editor_property("default_typeface")
        fonts = []
        for isim, yuz in girisler:
            fd = unreal.FontData()
            try: fd.set_editor_property("font_face_asset", yuz)
            except Exception as e: log("font_face_asset yazılamadı", e, [x for x in dir(fd) if not x.startswith("_")][:30])
            te = unreal.TypefaceEntry(); te.set_editor_property("name", isim); te.set_editor_property("font", fd); fonts.append(te)
        tf.set_editor_property("fonts", fonts); cf.set_editor_property("default_typeface", tf)
        try: cf.set_editor_property("fallback_typefaces", [])
        except Exception: pass
        f.set_editor_property("composite_font", cf); f.set_editor_property("font_cache_type", unreal.FontCacheType.RUNTIME)
        eal.save_loaded_asset(f, only_if_is_dirty=False)
        kont = f.get_editor_property("composite_font").get_editor_property("default_typeface").get_editor_property("fonts")
        log("font", yol, [(str(e.get_editor_property("name")), str(e.get_editor_property("font").get_editor_property("font_face_asset"))) for e in kont])
        return f
    font_yap("/Game/Uyanis/UI/F_Garamond", [("Regular", yuzler["Regular"]), ("Italic", yuzler["Italic"]), ("Medium", yuzler["Medium"]), ("SemiBold", yuzler["SemiBold"])])
    fa = font_yap("/Game/Uyanis/UI/F_Altyazi", [("Regular", yuzler["Italic"])])
    fa.set_editor_property("legacy_font_size", BOY); eal.save_loaded_asset(fa, only_if_is_dirty=False); log("altyazı boyutu", fa.get_editor_property("legacy_font_size"))
    for fn in ("T_Kurallar", "T_ElaCizim"):
        log("doku", ice_al(f"C:/Users/Onur/Sisli/Unreal/SourceArt/Kagit/{fn}.png", "/Game/Uyanis/Kagit", fn))
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/font_kur_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
unreal.SystemLibrary.quit_editor()
