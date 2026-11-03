import unreal, math, traceback
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions
def log(*a): OUT.append(" ".join(str(x) for x in a))
H = "/Game/Sisli/Cocuk2/Anim/Hazir"; CHILD = eal.load_asset("/Game/child_test_2/mesh/unreal_file")
try:
    for n in ("MF_Unarmed_Walk_Fwd", "MF_Unarmed_Jog_Fwd", "MOB1_Walk_F_IPC", "MOB1_Jog_F_IPC", "MM_Idle"):
        an = eal.load_asset(f"{H}/{n}_H"); o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", CHILD)
        L = an.get_play_length(); N = 120; dt = L / N
        po = [APE.get_anim_pose_at_time(an, i * dt, o) for i in range(N + 1)]
        P = lambda k, b: APE.get_bone_pose(po[k], b, unreal.AnimPoseSpaces.WORLD).translation
        r0, r1 = P(0, "root"), P(N, "root"); p0, p1 = P(0, "pelvis"), P(N, "pelvis")
        hiz = []
        for ay in ("foot_l", "foot_r"):
            rel = [P(k, ay) - P(k, "pelvis") for k in range(N + 1)]; ab = [P(k, ay) for k in range(N + 1)]
            zmin = min(a.z for a in ab)
            for k in range(N):
                if ab[k].z < zmin + 1.5: hiz.append(math.hypot(rel[k+1].x - rel[k].x, rel[k+1].y - rel[k].y) / dt)
        hiz.sort()
        log(n, "süre %.2f" % L, "root kayma", [round(v, 1) for v in (r1.x - r0.x, r1.y - r0.y)], "pelvis kayma", [round(v, 1) for v in (p1.x - p0.x, p1.y - p0.y)],
            "basan ayak hızı (pelvise göre) %.1f" % (hiz[len(hiz)//2] if hiz else 0), "root motion", an.get_editor_property("enable_root_motion"), "kilit", an.get_editor_property("force_root_lock"))
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/kok_olc_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
