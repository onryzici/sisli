# Yerinde (root motion'sız) animasyonun doğal zemin hızı: duruş fazındaki ayağın gövdeye göre geri kayma hızı
import unreal, math
out = []
eal = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary; ML = unreal.MathLibrary
def foot_track(anim, chain):
    n = AL.get_num_frames(anim); L = anim.get_play_length()
    out.append("  %s kare %d süre %.3f" % (anim.get_name(), n, L))
    pts = []
    for fr in range(n):
        t = None
        for b in chain:
            l = AL.get_bone_pose_for_frame(anim, b, fr, False); t = l if t is None else ML.compose_transforms(l, t)
        pts.append(t.translation)
    return pts, L / max(1, n - 1)
def speed(anim, chain):
    pts, dt = foot_track(anim, chain)
    zmin = min(p.z for p in pts); zs = sorted(p.z for p in pts)
    thr = zs[int(len(zs) * 0.35)]   # en alçak %35 = yere basma
    v = [math.hypot(pts[i + 1].x - pts[i].x, pts[i + 1].y - pts[i].y) / dt for i in range(len(pts) - 1) if pts[i].z <= thr and pts[i + 1].z <= thr]
    v.sort(); out.append("  x aralık %.1f y aralık %.1f" % (max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts))); return v[len(v) // 2] if v else 0
MC = ["root", "pelvis", "thigh_l", "calf_l", "foot_l"]; CC = ["root", "Hips", "LeftUpLeg", "LeftLeg", "LeftFoot"]
for nm in ("Walk/MF_Unarmed_Walk_Fwd", "Jog/MF_Unarmed_Jog_Fwd"):
    m = eal.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/" + nm); c = eal.load_asset("/Game/Sisli/Cocuk/Anim/" + nm.split("/")[1] + "_Cocuk")
    out.append("%s  Manny %.0f cm/s  Çocuk %.0f cm/s" % (nm, speed(m, MC), speed(c, CC)))
open("C:/Users/Onur/Sisli/Unreal/Scripts/olc_hiz_out.txt", "w", encoding="utf-8").write("\n".join(out))
