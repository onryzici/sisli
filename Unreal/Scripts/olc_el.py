# El ve parmak yönlerini Manny kaynak animasyonu ile karşılaştırır (bileşen uzayı, derece)
import unreal, math
out = []
eal = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary; ML = unreal.MathLibrary

def build(anim, parents, fr):
    comp = {}
    for b, p in parents:
        l = AL.get_bone_pose_for_frame(anim, b, fr, False)
        comp[b] = l if p is None else ML.compose_transforms(l, comp[p])
    return comp
def ang(a, b):
    a = a.normal(); b = b.normal(); return math.degrees(math.acos(max(-1, min(1, a.dot(b)))))
def M_par(s):
    P = [("root", None), ("pelvis", "root"), ("spine_01", "pelvis"), ("spine_02", "spine_01"), ("spine_03", "spine_02"), ("spine_04", "spine_03"), ("spine_05", "spine_04"),
         (f"clavicle_{s}", "spine_05"), (f"upperarm_{s}", f"clavicle_{s}"), (f"lowerarm_{s}", f"upperarm_{s}"), (f"hand_{s}", f"lowerarm_{s}")]
    for f in ("index", "middle", "ring", "pinky"):
        P += [(f"{f}_metacarpal_{s}", f"hand_{s}"), (f"{f}_01_{s}", f"{f}_metacarpal_{s}"), (f"{f}_02_{s}", f"{f}_01_{s}"), (f"{f}_03_{s}", f"{f}_02_{s}")]
    P += [(f"thumb_01_{s}", f"hand_{s}"), (f"thumb_02_{s}", f"thumb_01_{s}"), (f"thumb_03_{s}", f"thumb_02_{s}")]
    return P
def C_par(S):
    P = [("root", None), ("Hips", "root"), ("Spine", "Hips"), ("Spine1", "Spine"), ("Spine2", "Spine1"), (f"{S}Shoulder", "Spine2"), (f"{S}Arm", f"{S}Shoulder"),
         (f"{S}ForeArm", f"{S}Arm"), (f"{S}Hand", f"{S}ForeArm")]
    for f in ("Thumb", "Index", "Middle", "Ring", "Pinky"):
        P += [(f"{S}Hand{f}1", f"{S}Hand"), (f"{S}Hand{f}2", f"{S}Hand{f}1"), (f"{S}Hand{f}3", f"{S}Hand{f}2")]
    return P
pairs = [("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle", "/Game/Sisli/Cocuk/Anim/MM_Idle_Cocuk"),
         ("/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd", "/Game/Sisli/Cocuk/Anim/MF_Unarmed_Walk_Fwd_Cocuk")]
for src, dst in pairs:
    a = eal.load_asset(src); b = eal.load_asset(dst)
    for s, S in (("l", "Left"), ("r", "Right")):
        m = build(a, M_par(s), 0); c = build(b, C_par(S), 0)
        T = lambda d, k: d[k].translation
        # avuç ekseni ve boğum ekseni
        dm = T(m, f"middle_01_{s}") - T(m, f"hand_{s}"); dc = T(c, f"{S}HandMiddle1") - T(c, f"{S}Hand")
        km = T(m, f"pinky_01_{s}") - T(m, f"index_01_{s}"); kc = T(c, f"{S}HandPinky1") - T(c, f"{S}HandIndex1")
        # önkol
        fm = T(m, f"hand_{s}") - T(m, f"lowerarm_{s}"); fc = T(c, f"{S}Hand") - T(c, f"{S}ForeArm")
        line = "%s %s | önkol %.0f° | avuç yönü %.0f° | boğum ekseni %.0f°" % (dst.split("/")[-1][:14], S, ang(fm, fc), ang(dm, dc), ang(km, kc))
        for f, F in (("index", "Index"), ("middle", "Middle"), ("thumb", "Thumb")):
            if f == "thumb":
                sm = T(m, f"thumb_02_{s}") - T(m, f"thumb_01_{s}"); sc = T(c, f"{S}HandThumb2") - T(c, f"{S}HandThumb1")
                sm2 = T(m, f"thumb_03_{s}") - T(m, f"thumb_02_{s}"); sc2 = T(c, f"{S}HandThumb3") - T(c, f"{S}HandThumb2")
            else:
                sm = T(m, f"{f}_02_{s}") - T(m, f"{f}_01_{s}"); sc = T(c, f"{S}Hand{F}2") - T(c, f"{S}Hand{F}1")
                sm2 = T(m, f"{f}_03_{s}") - T(m, f"{f}_02_{s}"); sc2 = T(c, f"{S}Hand{F}3") - T(c, f"{S}Hand{F}2")
            line += " | %s %.0f°/%.0f°" % (F, ang(sm, sc), ang(sm2, sc2))
        out.append(line)
open("C:/Users/Onur/Sisli/Unreal/Scripts/olc_el_out.txt", "w", encoding="utf-8").write("\n".join(out))
