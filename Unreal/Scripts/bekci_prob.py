import unreal, traceback
OUT=[]
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal=unreal.EditorAssetLibrary
try:
    bp=eal.load_asset("/Game/Sisli/Mekanik/BP_Bekci")
    gc=bp.generated_class(); cdo=unreal.get_default_object(gc)
    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    hs=sds.k2_gather_subobject_data_for_blueprint(bp)
    for h in hs:
        d=unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h)
        o=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        log("bilesen", o.get_name() if o else None, type(o).__name__)
        if isinstance(o, unreal.SkeletalMeshComponent):
            log("  override", [m.get_path_name() if m else None for m in o.get_editor_property("override_materials")])
            log("  mesh", o.get_editor_property("skeletal_mesh_asset"))
    for g in unreal.BlueprintEditorLibrary.find_event_graph(bp) and [unreal.BlueprintEditorLibrary.find_event_graph(bp)] or []:
        pass
    # düğümlerde SetMaterial ara
    try:
        g=unreal.BlueprintEditorLibrary.find_event_graph(bp)
        for n in g.get_editor_property("nodes"):
            t=n.get_node_title(unreal.NodeTitleType.LIST_VIEW) if hasattr(n,"get_node_title") else str(n)
            if "Material" in str(t):
                log("dugum", t)
                for p in n.get_editor_property("pins") if hasattr(n,"pins") else []:
                    log("  pin", p)
    except Exception as e: log("graf", e)
except Exception: log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/bekci_prob_out.txt","w",encoding="utf-8").write("\n".join(OUT))
