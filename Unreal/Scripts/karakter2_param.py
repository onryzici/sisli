# Yeni çocuğun malzeme parametreleri (renk ayarı için) + doku boyutları
import unreal
OUT = []; eal = unreal.EditorAssetLibrary
for ad in ("Std_Skin_Head_HQ_Inst", "hair1_Transparency_LWHQ_Inst", "Basic_T_shirts_Inst", "Waistband_Inst", "Basketball_Shoes_Inst", "Std_Eyelash_LWHQ_Inst"):
    m = eal.load_asset(f"/Game/child_test_2/Materials/unreal_file/{ad}")
    if not m: OUT.append("YOK " + ad); continue
    OUT.append("== " + ad + " ebeveyn " + (m.get_editor_property("parent").get_name() if m.get_editor_property("parent") else "-"))
    for v in m.get_editor_property("vector_parameter_values"):
        c = v.get_editor_property("parameter_value"); OUT.append("  V %s = (%.2f %.2f %.2f)" % (v.get_editor_property("parameter_info").get_editor_property("name"), c.r, c.g, c.b))
    for v in m.get_editor_property("scalar_parameter_values"):
        OUT.append("  S %s = %.3f" % (v.get_editor_property("parameter_info").get_editor_property("name"), v.get_editor_property("parameter_value")))
    for v in m.get_editor_property("texture_parameter_values"):
        t = v.get_editor_property("parameter_value")
        OUT.append("  T %s = %s %s" % (v.get_editor_property("parameter_info").get_editor_property("name"), t.get_name() if t else "-", ("%dx%d" % (t.blueprint_get_size_x(), t.blueprint_get_size_y())) if t else ""))
open("C:/Users/Onur/Sisli/Unreal/Scripts/karakter2_param_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
