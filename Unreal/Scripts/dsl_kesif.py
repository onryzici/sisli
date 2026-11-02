# DSL düğüm tür kimliklerini keşfet: bileşenli/değişkenli bir test BP üzerinde anahtar kelime ara
import unreal, traceback
OUT = []
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
from toolset_registry.tool_call_impl import tool_raising_exceptions
_ctx = tool_raising_exceptions(); _ctx.__enter__()
eal = unreal.EditorAssetLibrary; BEL = unreal.BlueprintEditorLibrary
try:
    P = "/Game/Sisli/Mekanik/BP_Kesif"
    bp = eal.load_asset(P) if eal.does_asset_exist(P) else BT.create("/Game/Sisli/Mekanik", "BP_Kesif", unreal.Actor.static_class())
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    handles = sds.k2_gather_subobject_data_for_blueprint(bp)
    names = [str(unreal.SubobjectDataBlueprintFunctionLibrary.get_variable_name(sds.k2_find_subobject_data_from_handle(h))) for h in handles]
    OUT.append("bileşenler: %s" % names)
    if "Isik" not in names:
        root = handles[0]
        for cls, nm in ((unreal.PointLightComponent, "Isik"), (unreal.BoxComponent, "Kutu"), (unreal.StaticMeshComponent, "Govde")):
            p = unreal.AddNewSubobjectParams(parent_handle=root, new_class=cls, blueprint_context=bp)
            h, fail = sds.add_new_subobject(p)
            sds.rename_subobject(h, unreal.Text(nm))
            OUT.append("ekle %s %s" % (nm, fail))
        BEL.add_member_variable(bp, "Hiz", BEL.get_basic_type_by_name("real"))
        BEL.add_member_variable(bp, "Hedef", BEL.get_object_reference_type(unreal.Actor.static_class()))
        BEL.compile_blueprint(bp)
    g = BT.get_graph(bp, "EventGraph")
    for kw in ["PrintString", "SetActorLocation", "GetPlayerCharacter", "GetPlayerPawn", "StartCameraFade", "GetPlayerCameraManager", "Delay", "MoveComponentTo",
               "SetVisibility", "ToggleVisibility", "LineTraceByChannel", "GetForwardVector", "Dot Product", "SetIntensity", "RandomFloatInRange", "SetLightColor",
               "OpenLevel", "SetWorldRotation", "MakeRotator", "Sin", "GetGameTimeInSeconds", "DestroyActor", "CastToCharacter", "PlaySound2D", "PlaySoundAtLocation",
               "GetActorLocation", "VectorLength", "Normal", "BeginOverlap", "Isik", "Kutu", "Govde", "Hiz", "Hedef", "EqualEqual_ObjectObject", "Greater_DoubleDouble",
               "SetRelativeRotation", "GetWorldLocation", "FInterpTo", "Lerp", "LinearColorLerp", "SetActorTickEnabled", "CustomEvent", "Sequence", "DoOnce", "Flip"]:
        try:
            ids = BT.find_node_types(g, kw)
            OUT.append("%-24s %s" % (kw, ids[:8]))
        except Exception as e:
            OUT.append("%-24s HATA %s" % (kw, str(e)[:100]))
    eal.save_loaded_asset(bp)
except Exception:
    OUT.append(traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/dsl_kesif_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
