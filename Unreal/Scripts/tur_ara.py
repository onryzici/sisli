import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
from mekanik_lib import *
g = BT.get_graph(eal.load_asset("/Game/Sisli/Mekanik/BP_Bekci"), "EventGraph")
log("SetMaterial", [x for x in BT.find_node_types(g, "SetMaterial") if "Cast" not in x][:8])
m = eal.load_asset("/Game/Characters/UEFN_Mannequin/Meshes/SKM_UEFN_Mannequin"); log("slot", len(m.get_editor_property("materials")))
yaz("C:/Users/Onur/Sisli/Unreal/Scripts/tur_ara_out.txt")
