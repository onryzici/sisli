# EB Garamond yüzleri FontFileImportFactory(BatchCreateFontAsset=YES) ile → her yüz için FF_* (FontFace) + FF_*_Font (Font, typeface "Default").
# F_Altyazi = İtalik font kopyası (motor altyazısı, legacy boyut ALTYAZI_BOY). UMG: /Game/Uyanis/UI/Font/FF_EBGaramond_<Yüz>_Font
import unreal, os, traceback
OUT = []; eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools()
def log(*a): OUT.append(" ".join(str(x) for x in a))
FD = "/Game/Uyanis/UI/Font"; SRC = "C:/Users/Onur/Sisli/Unreal/SourceArt/Font/"; BOY = int(os.environ.get("ALTYAZI_BOY", "30"))
try:
    for p in [str(a).split(".")[0] for a in eal.list_assets(FD, recursive=True, include_folder=False)] + ["/Game/Uyanis/UI/F_Garamond", "/Game/Uyanis/UI/F_Altyazi"]:
        if eal.does_asset_exist(p): log("sil", p, eal.delete_asset(p))
    for n in ("Regular", "Italic", "Medium", "SemiBold"):
        fac = unreal.FontFileImportFactory(); fac.set_editor_property("batch_create_font_asset", unreal.BatchCreateFontAsset.YES)
        t = unreal.AssetImportTask(); t.filename = f"{SRC}EBGaramond-{n}.ttf"; t.destination_path = FD; t.destination_name = f"FF_EBGaramond_{n}"
        t.automated = True; t.save = True; t.replace_existing = True; t.factory = fac; at.import_asset_tasks([t])
        log("içe", n, [str(x) for x in t.get_editor_property("imported_object_paths")])
    eal.save_directory(FD, only_if_is_dirty=False, recursive=True)
    log("klasör", [str(a) for a in eal.list_assets(FD, recursive=True, include_folder=False)])
    it = f"{FD}/FF_EBGaramond_Italic_Font"
    if eal.does_asset_exist(it):
        fa = eal.duplicate_asset(it, "/Game/Uyanis/UI/F_Altyazi"); fa.set_editor_property("legacy_font_size", BOY)
        eal.save_loaded_asset(fa, only_if_is_dirty=False); log("F_Altyazi", fa.get_editor_property("legacy_font_size"), fa.get_editor_property("font_cache_type"))
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/font_kur3_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
unreal.SystemLibrary.quit_editor()
