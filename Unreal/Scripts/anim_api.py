import unreal
OUT = []; eal = unreal.EditorAssetLibrary
an = eal.load_asset("/Game/Sisli/Cocuk2/Anim/MCOK/Walk_06_Look_Around_Loop_IP_C")
OUT.append("anim dir: " + str([x for x in dir(an) if any(k in x.lower() for k in ("control", "model", "frame", "key", "rate"))]))
try:
    c = an.get_editor_property("controller"); OUT.append("controller prop: " + str(c))
except Exception as e: OUT.append("controller prop yok: " + str(e))
for nm in ("controller", "get_controller", "data_model", "get_data_model"):
    if hasattr(an, nm):
        try: v = getattr(an, nm); v = v() if callable(v) else v; OUT.append(nm + " → " + str(v) + " | " + str([x for x in dir(v) if not x.startswith("_")][:80]))
        except Exception as e: OUT.append(nm + " HATA " + str(e))
OUT.append("AL: " + str([x for x in dir(unreal.AnimationLibrary) if any(k in x for k in ("frame", "key", "bone_pose", "num"))]))
OUT.append("ADC: " + str([x for x in dir(unreal.AnimationDataController) if not x.startswith("_")][:120]) if hasattr(unreal, "AnimationDataController") else "ADC yok")
open("C:/Users/Onur/Sisli/Unreal/Scripts/anim_api_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
