import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
try:
    m = eal.load_asset("/Game/Uyanis/Malzeme/M_MS")
    OUT.append("önce " + str(m.get_editor_property("used_with_skeletal_mesh")))
    m.set_editor_property("used_with_skeletal_mesh", True)
    unreal.MaterialEditingLibrary.recompile_material(m); eal.save_loaded_asset(m, only_if_is_dirty=False)
    OUT.append("sonra " + str(m.get_editor_property("used_with_skeletal_mesh")))
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/malz_isk_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
