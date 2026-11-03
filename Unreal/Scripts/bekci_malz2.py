import unreal, traceback
OUT=[]
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
try:
    for p in ("/Game/Uyanis/Malzeme/M_MS","/Game/Sisli/Malzeme/M_Sisli"):
        M=eal.load_asset(p); once=M.get_editor_property("used_with_skeletal_mesh")
        if not once:
            M.set_editor_property("used_with_skeletal_mesh",True); mel.recompile_material(M)
        ok=eal.save_loaded_asset(M, only_if_is_dirty=False)
        log(p, "once", once, "simdi", M.get_editor_property("used_with_skeletal_mesh"), "kayit", ok)
    mi=eal.load_asset("/Game/Uyanis/Sahne/MI_Bekci_Kumas"); log("mi parent", mi.parent.get_path_name())
    bp=eal.load_asset("/Game/Uyanis/Mekanik/BP_Bekci") or eal.load_asset("/Game/Uyanis/BP/BP_Bekci")
    log("bp", bp)
except Exception: log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/bekci_malz2_out.txt","w",encoding="utf-8").write("\n".join(OUT))
