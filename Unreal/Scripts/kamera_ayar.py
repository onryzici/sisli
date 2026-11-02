# Serbest (fareyle dönen) üçüncü şahıs kamera ayarları — BP_ThirdPersonCharacter'in SpringArm + Camera bileşenleri.
# WASD kontrol yönüne göre (şablon Move: GetControlRotation yaw) → kamera nereye bakıyorsa oraya yürünür.
# kur_karakter.py ve serbest_kamera.py ortak kullanır.
import unreal

KOL_BOY = 380.0            # cm, çocuğun arkasından uzaklık
KOL_YUKSEK = 62.0          # kol pivotu kapsül merkezinin (64 cm) üstünde → ~1.26 m
FOV = 78.0

def uygula(bp, log=print):
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(sds.k2_find_subobject_data_from_handle(h))
        if isinstance(o, unreal.SpringArmComponent):
            o.set_editor_property("target_arm_length", KOL_BOY)
            o.set_editor_property("use_pawn_control_rotation", True)    # yaw + pitch fareden
            o.set_editor_property("absolute_rotation", False)
            o.set_editor_property("inherit_yaw", True)
            o.set_editor_property("inherit_pitch", True)
            o.set_editor_property("inherit_roll", False)
            o.set_editor_property("relative_rotation", unreal.Rotator(roll=0, pitch=0, yaw=0))
            o.set_editor_property("relative_location", unreal.Vector(0, 0, KOL_YUKSEK))
            o.set_editor_property("socket_offset", unreal.Vector(0, 0, 45))   # dar yerde kol kısalsa da omuz üstünden bakar
            o.set_editor_property("probe_size", 12.0)
            o.set_editor_property("do_collision_test", True)            # dar odada duvara girmesin, kol kısalır
            o.set_editor_property("enable_camera_lag", True); o.set_editor_property("camera_lag_speed", 10.0)
            o.set_editor_property("enable_camera_rotation_lag", False)
            log("SpringArm serbest", o.get_name())
        if isinstance(o, unreal.CameraComponent):
            o.set_editor_property("field_of_view", FOV)
            log("Kamera FOV", FOV)
