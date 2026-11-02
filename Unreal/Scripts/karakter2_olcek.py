# Yeni çocuk: 0.86 ölçek (~135 cm, 9-10 yaş), kapsül ve ayak hizası buna göre
import unreal, traceback
OUT = []
try:
    eal = unreal.EditorAssetLibrary
    sk = eal.load_asset("/Game/child_test_2/mesh/unreal_file"); bb = sk.get_bounds()
    S = 0.86; zmin = bb.origin.z - bb.box_extent.z; boy = bb.box_extent.z * 2 * S
    bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"); cdo = unreal.get_default_object(bp.generated_class())
    m = cdo.get_editor_property("mesh"); cap = cdo.get_editor_property("capsule_component")
    yari = boy / 2.0 + 1.0
    cap.set_editor_property("capsule_half_height", yari); cap.set_editor_property("capsule_radius", 21.0)
    m.set_editor_property("relative_scale3d", unreal.Vector(S, S, S))
    m.set_editor_property("relative_location", unreal.Vector(0, 0, -yari - zmin * S - 2.5))
    mv = cdo.get_editor_property("character_movement"); mv.set_editor_property("crouched_half_height", 44.0)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp); eal.save_loaded_asset(bp)
    OUT.append("boy %.1f kapsül yarı %.1f mesh z %.1f" % (boy, yari, -yari - zmin * S - 2.5))
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/karakter2_olcek_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
