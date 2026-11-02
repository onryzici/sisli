import unreal
eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level("/Game/Sisli/Maps/L_Sisli")
for lbl, path, loc in (("TEST_Manny", "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple", (260, -280, 0)), ("TEST_Cocuk", "/Game/Sisli/Cocuk/SK_Cocuk", (-20, -250, 0))):
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == lbl: eas.destroy_actor(a)
    a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(*loc), unreal.Rotator(roll=0, pitch=0, yaw=0))
    a.set_actor_label(lbl); a.skeletal_mesh_component.set_skinned_asset_and_update(eal.load_asset(path))
les.save_current_level()
open("C:/Users/Onur/Sisli/Unreal/Scripts/test_manny_out.txt", "w").write("ok")
