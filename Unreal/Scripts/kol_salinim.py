# Kol salınımı ölçümü: üst kolun öne/geri açısı (sagital, dikeyden; + öne) ve köprücüğün geri çekilmesi; kaynak manken ↔ çocuk
import unreal, math, traceback
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions; AL = unreal.AnimationLibrary
def log(*a): OUT.append(" ".join(str(x) for x in a))
try:
    CH = eal.load_asset("/Game/child_test_2/mesh/unreal_file"); MN = eal.load_asset("/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin")
    for ad, yol, mesh in (("KAYNAK", "/Game/MCO_Mocap_Basics/Animation/Walks/In_Place/Walk_06_Look_Around_Loop_IP", MN), ("ÇOCUK", "/Game/Sisli/Cocuk2/Anim/MCOK/Walk_06_Look_Around_Loop_IP_C", CH)):
        an = eal.load_asset(yol); nk = AL.get_num_keys(an); o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", mesh)
        r = {}
        for s in ("l", "r"):
            ua, la, kl, tor = [], [], [], []
            for k in range(0, nk, 2):
                p = APE.get_anim_pose_at_frame(an, k, o); P = lambda b: APE.get_bone_pose(p, b, unreal.AnimPoseSpaces.WORLD).translation
                u = (P("lowerarm_" + s) - P("upperarm_" + s)).normal(); ua.append(math.degrees(math.atan2(u.y, -u.z)))
                f = (P("hand_" + s) - P("upperarm_" + s)).normal(); la.append(math.degrees(math.atan2(f.y, -f.z)))
                c = (P("upperarm_" + s) - P("clavicle_" + s)).normal(); kl.append(math.degrees(math.asin(max(-1, min(1, c.y)))))
                g = (P("neck_01") - P("pelvis")).normal(); tor.append(math.degrees(math.atan2(g.y, g.z)))
            r[s] = (ua, la, kl)
            log(f"{ad} {s}: üst kol en geri {min(ua):+.1f}° en ileri {max(ua):+.1f}° | omuz→el en geri {min(la):+.1f}° ileri {max(la):+.1f}° | köprücük {min(kl):+.1f}..{max(kl):+.1f}° | gövde {min(tor):+.1f}..{max(tor):+.1f}")
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/kol_salinim_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
