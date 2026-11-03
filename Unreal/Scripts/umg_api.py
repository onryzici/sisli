import unreal, json, traceback
OUT = []; TR = unreal.ToolsetRegistry
try:
    sc = json.loads(str(TR.get_toolset_json_schema(unreal.UMGToolSet.static_class())))
    for t in sc["tools"]:
        if t["name"].split(".")[-1] in ("CreateWidgetBlueprint", "AddWidget", "ToggleWidgetAsVariable", "CompileWidgetBlueprint", "GetWidgets"):
            OUT.append(t["name"] + " giriş: " + json.dumps({k: v.get("title", v.get("type")) for k, v in t["inputSchema"]["properties"].items()}) + " zorunlu: " + str(t["inputSchema"].get("required")))
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/umg_api_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
