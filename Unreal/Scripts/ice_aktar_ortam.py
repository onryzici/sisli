# 1. geçiş: SourceArt/Ortam/*.fbx → /Game/Sisli/Ortam (statik mesh + malzeme + doku), çarpışma = karmaşık
import unreal, glob, os, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary
import os
SRC = os.environ.get("SISLI_SRC", "C:/Users/Onur/Sisli/Unreal/SourceArt/Ortam"); DST = os.environ.get("SISLI_DST", "/Game/Sisli/Ortam")
try:
    tasks = []
    for f in sorted(glob.glob(SRC + "/*.fbx")):
        name = os.path.splitext(os.path.basename(f))[0]
        if eal.does_asset_exist(f"{DST}/{name}/{name}"): continue
        t = unreal.AssetImportTask(); t.filename = f; t.destination_path = f"{DST}/{name}"; t.automated = True; t.save = True; t.replace_existing = True
        ui = unreal.FbxImportUI(); ui.import_mesh = True; ui.import_as_skeletal = False; ui.import_materials = True; ui.import_textures = True
        ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        ui.static_mesh_import_data.combine_meshes = True
        ui.static_mesh_import_data.auto_generate_collision = False
        t.options = ui; tasks.append(t)
    at.import_asset_tasks(tasks)
    for t in tasks: log("İÇE", t.filename.split("/")[-1], len(t.imported_object_paths))
    for p in eal.list_assets(DST, recursive=True):
        a = eal.load_asset(p)
        if isinstance(a, unreal.StaticMesh):
            bs = a.get_editor_property("body_setup")
            if bs: bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            eal.save_loaded_asset(a)
            mats = [a.get_material(i) for i in range(a.get_num_sections(0))]
            log("SM", p.split(".")[0], "malz:", [m.get_path_name().split(".")[0] if m else None for m in mats])
    # örnek malzeme parametreleri
    for p in eal.list_assets(DST, recursive=True):
        a = eal.load_asset(p)
        if isinstance(a, unreal.MaterialInstanceConstant):
            par = a.get_editor_property("parent")
            tex = [(str(v.get_editor_property("parameter_info").get_editor_property("name")), v.get_editor_property("parameter_value").get_name() if v.get_editor_property("parameter_value") else None) for v in a.get_editor_property("texture_parameter_values")]
            sc = [(str(v.get_editor_property("parameter_info").get_editor_property("name")), round(v.get_editor_property("parameter_value"), 3)) for v in a.get_editor_property("scalar_parameter_values")]
            log("MI", p.split(".")[0].split("/")[-1], "parent:", par.get_name() if par else None, "tex:", tex, "skaler:", sc)
        elif isinstance(a, unreal.Material):
            log("MAT", p.split(".")[0].split("/")[-1])
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/ice_aktar_ortam_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
