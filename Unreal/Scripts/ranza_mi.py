# Ranza (glTF) dokularını tanı + M_Sisli'ye Nanite bayrağı (oyuncaklar)
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary
try:
    for i in range(3):
        t = eal.load_asset(f"/Game/Uyanis/Fab/Ranza/bunk_bed/Textures/bunk_bed_texture_{i}")
        OUT.append(f"doku{i} srgb={t.get_editor_property('srgb')} sik={t.get_editor_property('compression_settings')} boyut={t.blueprint_get_size_x()}")
    mi = eal.load_asset("/Game/Uyanis/Fab/Ranza/bunk_bed/Materials/DefaultMaterial1")
    for v in mi.get_editor_property("texture_parameter_values"):
        pv = v.get_editor_property("parameter_value")
        OUT.append("param " + str(v.get_editor_property("parameter_info").get_editor_property("name")) + " = " + (pv.get_name() if pv else "-"))
    OUT.append("ebeveyn " + str(mi.get_editor_property("parent").get_path_name()))
    ms = eal.load_asset("/Game/Sisli/Malzeme/M_Sisli"); ms.set_editor_property("used_with_nanite", True); mel.recompile_material(ms); eal.save_loaded_asset(ms); OUT.append("M_Sisli nanite ok")
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/ranza_mi_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
