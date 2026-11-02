# Çocuk (UE4 manken iskeleti kopyası) ↔ MoCap paketinin UE4 iskeleti: uyumlu iskelet → MCO animasyonları aktarıcısız doğrudan oynar
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
try:
    sk = eal.load_asset("/Game/child_test_2/mesh/unreal_file"); isk = sk.get_editor_property("skeleton"); OUT.append("çocuk iskeleti " + isk.get_path_name())
    mco = eal.load_asset("/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin").get_editor_property("skeleton"); OUT.append("MCO iskeleti " + mco.get_path_name())
    l = list(isk.get_editor_property("compatible_skeletons")); OUT.append("önce " + str(l))
    if mco.get_path_name() not in [str(x) for x in l] and mco != isk:
        l.append(mco); isk.set_editor_property("compatible_skeletons", l); eal.save_loaded_asset(isk, only_if_is_dirty=False)
    OUT.append("sonra " + str(list(isk.get_editor_property("compatible_skeletons"))))
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/uyumlu_iskelet_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
