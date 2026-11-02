import unreal, traceback
OUT = []
def step(name, fn):
    try:
        r = fn(); OUT.append("OK %s %s" % (name, str(r)[:300])); return r
    except Exception:
        OUT.append("HATA %s %s" % (name, traceback.format_exc()[-600:]))
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
from toolset_registry.tool_call_impl import tool_raising_exceptions
_ctx = tool_raising_exceptions(); _ctx.__enter__()
eal = unreal.EditorAssetLibrary
bp = eal.load_asset("/Game/Sisli/Mekanik/BP_DslTest") if eal.does_asset_exist("/Game/Sisli/Mekanik/BP_DslTest") else step("create", lambda: BT.create("/Game/Sisli/Mekanik", "BP_DslTest", unreal.Actor.static_class()))
OUT.append("bp %s" % bp)
g = step("graph", lambda: BT.get_graph(bp, "EventGraph"))
step("write", lambda: BT.write_graph_dsl(g, '(event EventBeginPlay\n  (Development|PrintString "SISLI_DSL_CALISIYOR" :Duration 5.0))'))
step("nodes", lambda: [BT._get_node_info(n).type_id for n in BT.find_nodes(g)])
step("compile", lambda: BT.compile_blueprint(bp))
step("save", lambda: eal.save_loaded_asset(bp))
step("read", lambda: BT.read_graph_dsl(g))
open("C:/Users/Onur/Sisli/Unreal/Scripts/dsl_test_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
