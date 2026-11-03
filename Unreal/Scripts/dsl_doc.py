import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
from toolset_registry.tool_call_impl import tool_raising_exceptions
_c = tool_raising_exceptions(); _c.__enter__()
open("C:/Users/Onur/Sisli/Unreal/Scripts/dsl_doc_out.txt", "w", encoding="utf-8").write(str(BT.get_graph_dsl_docs()))
