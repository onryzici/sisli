# Manny kaynak animasyonu ile çocuğa aktarılmış animasyonda gövde/boyun/kafa yönlerini karşılaştırır (bileşen uzayı)
import unreal, math
out = []
eal = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary; ML = unreal.MathLibrary
def comp(anim, chain, frame):
    t = None; res = {}
    for b in chain:
        loc = AL.get_bone_pose_for_frame(anim, b, frame, False)
        t = loc if t is None else ML.compose_transforms(loc, t)
        res[b] = t
    return res
def ang(a, b):
    a = a.normal(); b = b.normal(); d = max(-1, min(1, a.dot(b))); return math.degrees(math.acos(d))
def pitch(v):   # yüz +Y; öne eğim = +Y yönüne yatma (derece, dikeyden)
    v = v.normal(); return math.degrees(math.atan2(v.y, v.z))
M_CH = ["root", "pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "neck_02", "head"]
C_CH = ["root", "Hips", "Spine", "Spine1", "Spine2", "Neck", "Head"]
for src, dst in (("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle", "/Game/Sisli/Cocuk/Anim/MM_Idle_Cocuk"),
                 ("/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd", "/Game/Sisli/Cocuk/Anim/MF_Unarmed_Walk_Fwd_Cocuk")):
    a = eal.load_asset(src); b = eal.load_asset(dst)
    for fr in (0, 10, 20):
        m = comp(a, M_CH, fr); c = comp(b, C_CH, fr)
        mt = m["neck_01"].translation - m["spine_01"].translation; ct = c["Neck"].translation - c["Spine"].translation
        mn = m["head"].translation - m["neck_01"].translation; cn = c["Head"].translation - c["Neck"].translation
        mh = m["head"].rotation.get_axis_x(); ch = c["Head"].rotation.get_axis_y()
        out.append("%s kare %d | gövde M %.1f C %.1f | boyun M %.1f C %.1f | kafa M %.1f C %.1f" % (dst.split("/")[-1], fr, pitch(mt), pitch(ct), pitch(mn), pitch(cn), pitch(mh), pitch(ch)))
open("C:/Users/Onur/Sisli/Unreal/Scripts/olc_egim_out.txt", "w").write("\n".join(out))
