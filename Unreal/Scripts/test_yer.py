# Başlangıç noktasını test için taşı: test_yer.txt = "x y z yaw" (UE cm)
import unreal
x, y, z, yaw = [float(v) for v in open("C:/Users/Onur/Sisli/Unreal/Scripts/test_yer.txt").read().split()]
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.load_level("/Game/Sisli/Maps/L_Sisli")
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "Baslangic":
        a.set_actor_location_and_rotation(unreal.Vector(x, y, z), unreal.Rotator(roll=0, pitch=0, yaw=yaw), False, True)
les.save_current_level()
open("C:/Users/Onur/Sisli/Unreal/Scripts/test_yer_out.txt", "w").write("ok %s" % [x, y, z, yaw])
