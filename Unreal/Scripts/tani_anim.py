import unreal
out = []
eal = unreal.EditorAssetLibrary
for p in ["/Game/Sisli/Cocuk/Anim/MM_Idle_Cocuk", "/Game/Sisli/Cocuk/Anim/MF_Unarmed_Walk_Fwd_Cocuk", "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle"]:
    a = eal.load_asset(p)
    if not a: out.append("YOK " + p); continue
    out.append("== %s skel=%s kare=%s" % (p.split("/")[-1], a.get_editor_property("skeleton").get_name(), unreal.AnimationLibrary.get_num_frames(a)))
    names = unreal.AnimationLibrary.get_animation_track_names(a)
    out.append("  iz sayısı %d: %s" % (len(names), [str(n) for n in names][:30]))
    for bn in ["root", "Hips", "pelvis", "Spine", "Head", "LeftFoot"]:
        try:
            t = unreal.AnimationLibrary.get_bone_pose_for_frame(a, bn, 0, False)
            out.append("  %s t=%s r=%s s=%s" % (bn, t.translation, t.rotation.rotator(), t.scale3d))
        except Exception as e:
            out.append("  %s hata %s" % (bn, str(e)[:80]))
open("C:/Users/Onur/Sisli/Unreal/Scripts/tani_anim_out.txt", "w").write("\n".join(out))
