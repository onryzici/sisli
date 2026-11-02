import unreal
OUT = []; eal = unreal.EditorAssetLibrary
bs = eal.load_asset("/Game/Sisli/Cocuk2/Anim/BS_Cocuk2_Hareket")
OUT.append("yöntemler: " + ", ".join(n for n in dir(bs) if not n.startswith("_") and any(k in n.lower() for k in ("sample", "valid", "grid", "blend", "resample", "update", "tri", "data"))))
tpl = eal.load_asset("/Game/Sisli/Cocuk2/Anim/BS_Idle_Walk_Run_Cocuk2") or eal.load_asset("/Game/Sisli/Cocuk/Anim/BS_Idle_Walk_Run_Cocuk")
if tpl:
    OUT.append("şablon " + tpl.get_path_name() + " sınıf " + tpl.get_class().get_name())
    for s in tpl.get_editor_property("sample_data"): OUT.append("  %s %s" % (s.get_editor_property("animation").get_name() if s.get_editor_property("animation") else None, s.get_editor_property("sample_value")))
    for b in list(tpl.get_editor_property("blend_parameters"))[:2]: OUT.append("  eksen %s %s %s" % (b.get_editor_property("display_name"), b.get_editor_property("min"), b.get_editor_property("max")))
for p in eal.list_assets("/Game/Sisli/Cocuk2/Anim", recursive=False):
    a = eal.load_asset(p)
    if isinstance(a, unreal.BlendSpace): OUT.append("BS: " + p)
open("C:/Users/Onur/Sisli/Unreal/Scripts/bs_yoklama_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
