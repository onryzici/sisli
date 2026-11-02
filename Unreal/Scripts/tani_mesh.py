import unreal
out = []
eal = unreal.EditorAssetLibrary
sk = eal.load_asset("/Game/Sisli/Cocuk/SK_Cocuk")
out.append("physics asset: %s" % sk.get_editor_property("physics_asset"))
b = sk.get_bounds(); out.append("asset bounds origin %s extent %s" % (b.origin, b.box_extent))
out.append("imported bounds %s" % sk.get_imported_bounds())
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level("/Game/Sisli/Maps/L_Sisli")
a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(100, 200, 0), unreal.Rotator(roll=0, pitch=0, yaw=0))
c = a.skeletal_mesh_component; c.set_skinned_asset_and_update(sk)
o, e = a.get_actor_bounds(False); out.append("actor bounds origin %s extent %s" % (o, e))
for bn in ["root", "Hips", "Head", "LeftFoot", "RightHand"]:
    out.append("kemik %s dünya %s" % (bn, c.get_socket_location(bn)))
out.append("bones: %s" % [str(c.get_bone_name(i)) for i in range(min(30, c.get_num_bones()))])
open("C:/Users/Onur/Sisli/Unreal/Scripts/tani_mesh_out.txt", "w").write("\n".join(out))
