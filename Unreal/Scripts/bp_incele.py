import unreal
out = []
bp = unreal.EditorAssetLibrary.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
gm = unreal.EditorAssetLibrary.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode")
gcdo = unreal.get_default_object(gm.generated_class())
out.append("GM pawn: %s" % gcdo.get_editor_property("default_pawn_class"))
cdo = unreal.get_default_object(bp.generated_class())
sk = cdo.get_editor_property("mesh")
out.append("mesh asset: %s anim: %s loc: %s rot: %s vis: %s hidden: %s" % (sk.get_editor_property("skeletal_mesh_asset"), sk.get_editor_property("anim_class"), sk.get_editor_property("relative_location"), sk.get_editor_property("relative_rotation"), sk.get_editor_property("visible"), sk.get_editor_property("hidden_in_game")))
cap = cdo.get_editor_property("capsule_component")
out.append("capsule: %s %s" % (cap.get_editor_property("capsule_half_height"), cap.get_editor_property("capsule_radius")))
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    d = sds.k2_find_subobject_data_from_handle(h)
    o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
    if o is None: continue
    line = "SCS %s (%s) outer=%s" % (o.get_name(), o.get_class().get_name(), o.get_outer().get_name())
    if isinstance(o, unreal.SpringArmComponent):
        line += " arm=%s rot=%s pawnrot=%s" % (o.get_editor_property("target_arm_length"), o.get_editor_property("relative_rotation"), o.get_editor_property("use_pawn_control_rotation"))
    if isinstance(o, unreal.CameraComponent):
        line += " fov=%s pawnrot=%s attach=%s" % (o.get_editor_property("field_of_view"), o.get_editor_property("use_pawn_control_rotation"), o.get_attach_parent())
    out.append(line)
# çalışma anı bileşenleri (CDO'nun alt nesneleri)
for c in cdo.get_components_by_class(unreal.ActorComponent):
    out.append("CDO comp %s %s" % (c.get_name(), c.get_class().get_name()))
open("C:/Users/Onur/Sisli/Unreal/Scripts/bp_incele_out.txt", "w").write("\n".join(out))
