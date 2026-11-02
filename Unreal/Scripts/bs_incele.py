import unreal
out = []
eal = unreal.EditorAssetLibrary
for p in ("/Game/Sisli/Cocuk/Anim/BS_Idle_Walk_Run_Cocuk", "/Game/Characters/Mannequins/Anims/Unarmed/BS_Idle_Walk_Run"):
    bs = eal.load_asset(p); out.append("== %s %s" % (p.split("/")[-1], bs.get_class().get_name()))
    for i, bp in enumerate(bs.get_editor_property("blend_parameters")):
        out.append("  eksen %d %s min %.0f max %.0f" % (i, bp.get_editor_property("display_name"), bp.get_editor_property("min"), bp.get_editor_property("max")))
    for sd in bs.get_editor_property("sample_data"):
        an = sd.get_editor_property("animation"); out.append("  örnek %s → %s hız %.2f" % (sd.get_editor_property("sample_value"), an.get_name() if an else None, sd.get_editor_property("rate_scale")))
open("C:/Users/Onur/Sisli/Unreal/Scripts/bs_incele_out.txt", "w", encoding="utf-8").write("\n".join(out))
