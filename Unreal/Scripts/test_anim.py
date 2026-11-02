# Geçici: BP karakterine tek animasyon + yakın kamera (mod=test) ya da ABP + normal kamera (mod=geri)
import unreal, sys
eal = unreal.EditorAssetLibrary
MODE = open("C:/Users/Onur/Sisli/Unreal/Scripts/test_anim_mod.txt").read().split()
bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
cdo = unreal.get_default_object(bp.generated_class())
sk = cdo.get_editor_property("mesh")
if MODE[0] == "test":
    sk.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    d = sk.get_editor_property("animation_data"); d.set_editor_property("anim_to_play", eal.load_asset("/Game/Sisli/Cocuk/Anim/" + MODE[1]))
    d.set_editor_property("saved_looping", True); d.set_editor_property("saved_playing", True); sk.set_editor_property("animation_data", d)
    arm, rot = float(MODE[3]) if len(MODE) > 3 else 380.0, unreal.Rotator(roll=0, pitch=float(MODE[4]) if len(MODE) > 4 else -12, yaw=float(MODE[2]))
    absrot = True
else:
    sk.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    arm, rot = 2000.0, unreal.Rotator(roll=0, pitch=-48, yaw=0)
    absrot = False
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sds.k2_find_subobject_data_from_handle(h))
    if isinstance(o, unreal.SpringArmComponent):
        o.set_editor_property("target_arm_length", arm); o.set_editor_property("relative_rotation", rot)
        o.set_editor_property("absolute_rotation", absrot); o.set_editor_property("use_pawn_control_rotation", not absrot)
        o.set_editor_property("enable_camera_lag", not absrot)
        o.set_editor_property("do_collision_test", True); o.set_editor_property("probe_size", 14.0)
    if isinstance(o, unreal.CameraComponent): o.set_editor_property("field_of_view", 32.0)
unreal.BlueprintEditorLibrary.compile_blueprint(bp); eal.save_loaded_asset(bp)
