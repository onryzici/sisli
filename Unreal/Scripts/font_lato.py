# Lato (OFL, SourceArt/Font/Lato) → FF_Lato_<Yüz> + FF_Lato_<Yüz>_Font; altyazı halesi dokusu T_AltyaziHale. TAM EDİTÖRLE çalıştır (Slate gerekiyor).
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools()
def log(*a): OUT.append(" ".join(str(x) for x in a))
FD = "/Game/Uyanis/UI/Font"; SRC = "C:/Users/Onur/Sisli/Unreal/SourceArt/Font/Lato/"
try:
    for n in ("Regular", "Italic"):
        for p in (f"{FD}/FF_Lato_{n}", f"{FD}/FF_Lato_{n}_Font"):
            if eal.does_asset_exist(p): eal.delete_asset(p)
        fac = unreal.FontFileImportFactory(); fac.set_editor_property("batch_create_font_asset", unreal.BatchCreateFontAsset.YES)
        t = unreal.AssetImportTask(); t.filename = f"{SRC}Lato-{n}.ttf"; t.destination_path = FD; t.destination_name = f"FF_Lato_{n}"
        t.automated = True; t.save = True; t.replace_existing = True; t.factory = fac; at.import_asset_tasks([t]); log("içe", n, [str(x) for x in t.get_editor_property("imported_object_paths")])
    t = unreal.AssetImportTask(); t.filename = "C:/Users/Onur/Sisli/Unreal/SourceArt/UI/T_AltyaziHale.png"; t.destination_path = "/Game/Uyanis/UI"; t.destination_name = "T_AltyaziHale"
    t.automated = True; t.save = True; t.replace_existing = True; at.import_asset_tasks([t]); log("hale", [str(x) for x in t.get_editor_property("imported_object_paths")])
    eal.save_directory("/Game/Uyanis/UI", only_if_is_dirty=False, recursive=True)
    log("klasör", [str(a).split("/")[-1] for a in eal.list_assets(FD, recursive=True, include_folder=False) if "Lato" in str(a)])
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/font_lato_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
unreal.SystemLibrary.quit_editor()
