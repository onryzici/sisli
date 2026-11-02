import unreal
OUT = []; eal = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary
for p in ("/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/MOB1_Walk_F_IPC", "/Game/Sisli/Cocuk2/Anim/MCO/MOB1_Walk_F_IPC_Cocuk2",
          "/Game/Sisli/Cocuk2/Anim/MCO/MOB1_Crouch_Idle_V2_IPC_Cocuk2", "/Game/Sisli/Cocuk2/Anim/MF_Unarmed_Walk_Fwd_Cocuk2"):
    a = eal.load_asset(p)
    if not a: OUT.append("YOK " + p); continue
    sk = a.get_editor_property("skeleton"); n = AL.get_num_frames(a)
    r = []
    for fr in (0, n // 4, n // 2):
        try: t = AL.get_bone_pose_for_frame(a, "thigh_l", fr, False); r.append("f%d rot %s" % (fr, str(t.rotation.rotator())[30:90]))
        except Exception as e: r.append("hata %s" % str(e)[:80])
    OUT.append("%s | iskelet %s | kare %d | %s" % (p.split("/")[-1], sk.get_path_name() if sk else None, n, " ; ".join(r)))
bs = eal.load_asset("/Game/Sisli/Cocuk2/Anim/BS_Cocuk2_Hareket")
OUT.append("BS iskelet %s örnek %d" % (bs.get_editor_property("skeleton").get_path_name(), len(bs.get_editor_property("sample_data"))))
for s in bs.get_editor_property("sample_data"):
    an = s.get_editor_property("animation"); OUT.append("  örnek %s %s" % (an.get_name() if an else None, s.get_editor_property("sample_value")))
open("C:/Users/Onur/Sisli/Unreal/Scripts/anim_kontrol_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
