import unreal
out = []
eal = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary
for p, bones in (("/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd", ["root", "pelvis"]), ("/Game/Sisli/Cocuk/Anim/MF_Unarmed_Walk_Fwd_Cocuk", ["root", "Hips"]),
                 ("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle", ["root", "pelvis"]), ("/Game/Sisli/Cocuk/Anim/MM_Idle_Cocuk", ["root", "Hips"])):
    a = eal.load_asset(p); n = AL.get_num_frames(a)
    out.append("== %s rootmotion=%s rootlock=%s kilit=%s" % (a.get_name(), a.get_editor_property("enable_root_motion"), a.get_editor_property("force_root_lock"), a.get_editor_property("root_motion_root_lock")))
    for b in bones:
        ys = [AL.get_bone_pose_for_frame(a, b, fr, False).translation for fr in (0, n // 2, n - 1)]
        out.append("  %s y: %s" % (b, ["%.1f/%.1f/%.1f" % (v.x, v.y, v.z) for v in ys]))
open("C:/Users/Onur/Sisli/Unreal/Scripts/olc_kok_out.txt", "w", encoding="utf-8").write("\n".join(out))
