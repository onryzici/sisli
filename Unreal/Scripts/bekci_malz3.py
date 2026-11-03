import unreal, traceback
OUT=[]
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
try:
    for p in ("/Game/Sisli/Malzeme/M_Sisli","/Game/Uyanis/Malzeme/M_MS"):
        M=eal.load_asset(p)
        log(p, "vec", mel.get_vector_parameter_names(M), "sc", mel.get_scalar_parameter_names(M), "tex", mel.get_texture_parameter_names(M))
        for n in mel.get_texture_parameter_names(M): log("  tex", n, mel.get_material_default_texture_parameter_value(M, n))
        for n in mel.get_vector_parameter_names(M): log("  vec", n, mel.get_material_default_vector_parameter_value(M, n))
        log("  usage skel", M.get_editor_property("used_with_skeletal_mesh"), "shading", M.get_editor_property("shading_model"), "blend", M.get_editor_property("blend_mode"))
    mi=eal.load_asset("/Game/Uyanis/Sahne/MI_Bekci_Kumas")
    import os
    if os.environ.get("UY_KIRMIZI"):
        mel.set_material_instance_vector_parameter_value(mi,"Ton",unreal.LinearColor(*[float(v) for v in os.environ["UY_KIRMIZI"].split()],1)); eal.save_loaded_asset(mi); log("TON")
    log("mi Ton", mel.get_material_instance_vector_parameter_value(mi,"Ton"))
except Exception: log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/bekci_malz3_out.txt","w",encoding="utf-8").write("\n".join(OUT))
