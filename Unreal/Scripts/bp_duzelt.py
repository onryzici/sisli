import unreal
out = []
eal = unreal.EditorAssetLibrary
bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
cdo = unreal.get_default_object(bp.generated_class())
mv = cdo.get_editor_property("character_movement")
mv.set_editor_property("rotation_rate", unreal.Rotator(roll=0, pitch=0, yaw=540))
mv.set_editor_property("orient_rotation_to_movement", True)
cdo.set_editor_property("use_controller_rotation_yaw", False)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sds.k2_find_subobject_data_from_handle(h))
    if isinstance(o, unreal.SpringArmComponent):
        o.set_editor_property("relative_rotation", unreal.Rotator(roll=0, pitch=-32, yaw=0))
        o.set_editor_property("target_arm_length", 1500.0)
    if isinstance(o, unreal.CameraComponent):
        o.set_editor_property("field_of_view", 35.0)
        out.append("arm rot %s" % o.get_editor_property("relative_rotation"))
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
eal.save_loaded_asset(bp)
out.append("rate %s" % mv.get_editor_property("rotation_rate"))
open("C:/Users/Onur/Sisli/Unreal/Scripts/bp_duzelt_out.txt", "w").write("\n".join(out))
