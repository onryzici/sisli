import unreal
out = []
out.append("BlueprintGraphEditor: " + ", ".join(m for m in dir(unreal.BlueprintGraphEditor) if not m.startswith("_")))
bp = unreal.EditorAssetLibrary.load_asset("/Game/Sisli/Mekanik/BP_Titrek")
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
g = BT.get_graph(bp, "EventGraph")
ed = unreal.BlueprintGraphEditor.get_graph_editor(g)
for kw in ("Karanlik", "Isik", "TemelSiddet"):
    try: out.append(kw + " ctx: " + str([n for n in ed.list_available_nodes([]) if kw.lower() in n.lower()][:5]))
    except Exception as e: out.append(kw + " hata " + str(e))
open("C:/Users/Onur/Sisli/Unreal/Scripts/kesif2_out.txt", "w").write("\n".join(out))
