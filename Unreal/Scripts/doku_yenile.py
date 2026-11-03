import unreal, traceback
OUT = []; at = unreal.AssetToolsHelpers.get_asset_tools()
try:
    t = unreal.AssetImportTask(); t.filename = "C:/Users/Onur/Sisli/Unreal/SourceArt/UI/T_AltyaziHale.png"; t.destination_path = "/Game/Uyanis/UI"; t.destination_name = "T_AltyaziHale"
    t.automated = True; t.save = True; t.replace_existing = True; at.import_asset_tasks([t]); OUT.append(str(list(t.get_editor_property("imported_object_paths"))))
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/doku_yenile_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
