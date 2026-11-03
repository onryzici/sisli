import unreal, traceback
OUT=[]
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
try:
    sk=eal.load_asset("/Game/Characters/UEFN_Mannequin/Meshes/SKM_UEFN_Mannequin")
    log("slotlar", [ (m.material_slot_name, m.material_interface.get_path_name() if m.material_interface else None) for m in sk.materials])
    mi=eal.load_asset("/Game/Uyanis/Sahne/MI_Bekci_Kumas")
    log("mi parent", mi.parent.get_path_name() if mi else None)
    bpc=unreal.load_object(None,"/Game/Uyanis/Mekanik/BP_Bekci.BP_Bekci_C")
    log("bpc", bpc)
    M=eal.load_asset("/Game/Sisli/Malzeme/M_Sisli")
    log("M_Sisli skel", M.get_editor_property("used_with_skeletal_mesh"))
    p="/Game/Uyanis/Sahne/MI_Bekci_Kumas"
    mel.set_material_instance_parent(mi, M)
    mel.clear_all_material_instance_parameters(mi)
    mel.set_material_instance_vector_parameter_value(mi,"Ton",unreal.LinearColor(0.035,0.034,0.036,1))
    mel.set_material_instance_scalar_parameter_value(mi,"PuruzCarpan",0.95)
    mel.set_material_instance_scalar_parameter_value(mi,"MetalCarpan",0.0)
    eal.save_loaded_asset(mi)
    log("yeni parent", mi.parent.get_path_name())
except Exception: log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/bekci_malz_out.txt","w",encoding="utf-8").write("\n".join(OUT))
