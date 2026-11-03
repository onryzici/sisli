# AnimBP keşfi: yeni ABP oluştur, AnimGraph'ta hangi düğüm türleri oluşturulabiliyor?
import unreal, traceback
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
from toolset_registry.tool_call_impl import tool_raising_exceptions
_ctx = tool_raising_exceptions(); _ctx.__enter__()
OUT = []; eal = unreal.EditorAssetLibrary
def log(*a): OUT.append(" ".join(str(x) for x in a))
P = "/Game/Sisli/Cocuk2/Anim/ABP_Kesif"
try:
    if eal.does_asset_exist(P): eal.delete_asset(P)
    f = unreal.AnimBlueprintFactory(); f.set_editor_property("target_skeleton", eal.load_asset("/Game/Characters/Mannequin_UE4/Meshes/SK_Mannequin_Skeleton"))
    f.set_editor_property("parent_class", unreal.AnimInstance)
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("ABP_Kesif", "/Game/Sisli/Cocuk2/Anim", unreal.AnimBlueprint, f)
    log("abp", bp)
    gs = BT.list_graphs(bp); log("grafikler", [g.get_name() for g in gs])
    ag = [g for g in gs if g.get_name() == "AnimGraph"][0]
    log("AnimGraph düğümleri", [n.get_name() for n in BT.find_nodes(ag)] if hasattr(BT, "find_nodes") else "-")
    log("kategoriler", BT.find_node_categories(ag, "")[:80])
    for flt in ("Slot", "Blend Space", "BlendSpace", "BS_Cocuk2", "Sequence", "Blend Poses", "Inertializ", "Cached", "State Machine", "Layered", "Output"):
        r = BT.find_node_types(ag, flt); log("filtre", flt, len(r), r[:25])
    eg = [g for g in gs if g.get_name() == "EventGraph"][0]
    for flt in ("BlueprintUpdateAnimation", "TryGetPawnOwner", "Try Get Pawn"):
        r = BT.find_node_types(eg, flt); log("olay filtre", flt, r[:10])
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/abp_kesif_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
