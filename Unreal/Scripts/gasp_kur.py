# GASP (Epic Game Animation Sample, UEFN mankeni) → çocuk. RTG_GASP_Cocuk2: kaynak IK_UEFN_Mannequin, hedef IK_Cocuk2.
# Hedef poz ofsetleri Epic mankenine SADIK çözülür (rtg_epic.py + rtg_el.py yöntemi): 1. aşama gövde/boyun/kol/bacak, 2. aşama el + parmaklar.
# Sonra seçili animasyonlar Anim/GASP/*_C olarak aktarılır, doğal yürüme hızları (çocuk ölçeği 0.86) ölçülür. Oyuna/BS'e DOKUNMAZ.
import unreal, math, traceback, json
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; G2 = D + "/Anim/GASP"; TD = D + "/Anim/Test"; T = unreal.RetargetSourceOrTarget.TARGET; S = unreal.RetargetSourceOrTarget.SOURCE
U = "/Game/Characters/UEFN_Mannequin"; A = U + "/Animations/"
SRC = eal.load_asset(U + "/Meshes/SKM_UEFN_Mannequin"); CHILD = eal.load_asset("/Game/child_test_2/mesh/unreal_file")
FIT = [A + "Idle/M_Neutral_Stand_Idle_Loop", A + "Walk/M_Neutral_Walk_Loop_F"]
SECIM = ["Idle/M_Neutral_Stand_Idle_Loop", "Idle/M_Relaxed_Stand_Idle_Loop", "Idle/M_Neutral_Crouch_Idle_Loop", "Walk/M_Neutral_Walk_Loop_F",
         "Walk/M_Relaxed_Walk_Loop_F", "Crouch/M_Neutral_Crouch_Loop_F", "Jump/M_Neutral_Jump_F_Start_Stand_Lfoot", "Jump/M_Neutral_Jump_Loop_Fall",
         "Jump/M_Neutral_Jump_F_Land_Stand_Light_Lfoot"]
def qmul(a, b):
    x1, y1, z1, w1 = a; x2, y2, z2, w2 = b
    return (w1*x2 + x1*w2 + y1*z2 - z1*y2, w1*y2 - x1*z2 + y1*w2 + z1*x2, w1*z2 + x1*y2 - y1*x2 + z1*w2, w1*w2 - x1*x2 - y1*y2 - z1*z2)
def qinv(a): return (-a[0], -a[1], -a[2], a[3])
def qax(ax, deg):
    r = math.radians(deg) / 2; s = math.sin(r); return (ax[0]*s, ax[1]*s, ax[2]*s, math.cos(r))
def tq(q): return (q.x, q.y, q.z, q.w)
def coz(A_, b):
    n = len(b); M = [list(A_[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-12: continue
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]; M[r] = [M[r][k] - f * M[c][k] for k in range(n + 1)]
    return [M[i][n] / M[i][i] if abs(M[i][i]) > 1e-12 else 0.0 for i in range(n)]
def bag(mesh):
    a_ = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -5000))
    c_ = a_.get_editor_property("skeletal_mesh_component"); c_.set_skeletal_mesh_asset(mesh)
    ad = set(str(c_.get_bone_name(i)) for i in range(c_.get_num_bones()))
    G = {b: tq(c_.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_COMPONENT).rotation) for b in ad}
    a_.destroy_actor(); return ad, G
try:
    ad_s, _ = bag(SRC); ad_c, G = bag(CHILD); ortak = ad_s & ad_c
    ry = D + "/RTG_GASP_Cocuk2"
    if eal.does_asset_exist(ry): eal.delete_asset(ry)
    rtg = eal.duplicate_asset(D + "/RTG_Manny_Cocuk2", ry); rc = unreal.IKRetargeterController.get_controller(rtg)
    rc.set_ik_rig(S, eal.load_asset(U + "/Rigs/IK_UEFN_Mannequin")); rc.set_preview_mesh(S, SRC)
    try: rc.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    except Exception as e: log("auto_map", e)
    rc.reset_retarget_pose(rc.get_current_retarget_pose_name(T), [], T)
    log("ops", [(str(rc.get_op_name(i)), rc.get_retarget_op_enabled(i)) for i in range(rc.get_num_retarget_ops())])
    yerel = lambda b, dW: qmul(qinv(G[b]), qmul(dW, G[b]))
    kaynak = [eal.load_asset(a) for a in FIT]; ZAM = [[0.0, k.get_play_length() * 0.37, k.get_play_length() * 0.71] for k in kaynak]
    def olc(an, mesh, zamanlar, SEG):
        o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", mesh); v = []
        for t in zamanlar:
            pose = APE.get_anim_pose_at_time(an, t, o); P = lambda b: APE.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation
            for a, b in SEG:
                d = (P(b) - P(a)).normal(); v += [d.x, d.y, d.z]
        return v
    sayac = [0]
    def coz_asama(ad, SEG, PAR, uygula, adim_say, d):
        hedef = []
        for k, z in zip(kaynak, ZAM): hedef += olc(k, SRC, z, SEG)
        def deg(p):
            uygula(p); m = []
            for yol, z in zip(FIT, ZAM):
                sayac[0] += 1; n_ = yol.split("/")[-1]; son = f"_g{sayac[0]}"
                unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(yol)], SRC, CHILD, rtg, search="", replace="", prefix="",
                                                                        suffix=son, target_path=TD, include_referenced_assets=False)
                an = eal.load_asset(f"{TD}/{n_}{son}"); m += olc(an, CHILD, z, SEG); eal.delete_asset(f"{TD}/{n_}{son}")
            return m
        def ozet(m):
            r = {}
            for si, (a, b) in enumerate(SEG):
                top = 0.0; k = 0
                for ti in range(len(m) // (3 * len(SEG))):
                    i = (ti * len(SEG) + si) * 3; dd = max(-1, min(1, m[i]*hedef[i] + m[i+1]*hedef[i+1] + m[i+2]*hedef[i+2])); top += math.degrees(math.acos(dd)); k += 1
                r[f"{a}>{b}"] = round(top / k, 1)
            return sorted(r.items(), key=lambda kv: -kv[1])[:6]
        n = len(PAR); p = [0.0] * n
        for adim in range(adim_say):
            m0 = deg(p); e = [hedef[i] - m0[i] for i in range(len(m0))]
            log(f"{ad} adım {adim} hata² {sum(x*x for x in e):.4f}", ozet(m0))
            J = [[0.0] * n for _ in range(len(m0))]
            for j in range(n):
                p2 = list(p); p2[j] += d; m1 = deg(p2)
                for i in range(len(m0)): J[i][j] = (m1[i] - m0[i]) / d
            JtJ = [[sum(J[k][i] * J[k][j] for k in range(len(m0))) + (1e-3 if i == j else 0) for j in range(n)] for i in range(n)]
            Jte = [sum(J[k][i] * e[k] for k in range(len(m0))) for i in range(n)]
            dp = coz(JtJ, Jte); p = [p[i] + max(-25, min(25, dp[i])) for i in range(n)]
        m = deg(p); log(f"{ad} SON hata² {sum((hedef[i] - m[i])**2 for i in range(len(m))):.4f}", ozet(m)); uygula(p); return p
    # 1. aşama: gövde/boyun/köprücük/kol/bacak
    SEG1 = [("pelvis", "neck_01"), ("neck_01", "head")] + [(a + s, b + s) for s in ("_l", "_r") for a, b in
            (("clavicle", "upperarm"), ("upperarm", "lowerarm"), ("lowerarm", "hand"), ("thigh", "calf"), ("calf", "foot"))]
    B1 = ["SPINE", "neck_01"] + [b + s for s in ("_l", "_r") for b in ("clavicle", "upperarm", "lowerarm", "thigh", "calf")]
    PAR1 = [(b, ax) for b in B1 for ax in ((1, 0, 0), (0, 1, 0))]
    def uyg1(p):
        for b in B1:
            dW = (0, 0, 0, 1)
            for (bb, ax), v in zip(PAR1, p):
                if bb == b: dW = qmul(dW, qax(ax, v))
            if b == "SPINE":
                ax_ = [v for (bb, _), v in zip(PAR1, p) if bb == "SPINE"]
                for s_ in ("spine_01", "spine_02", "spine_03"):
                    rc.set_rotation_offset_for_retarget_pose_bone(s_, unreal.Quat(*yerel(s_, qmul(qax((1, 0, 0), ax_[0] / 3), qax((0, 1, 0), ax_[1] / 3)))), T)
            else: rc.set_rotation_offset_for_retarget_pose_bone(b, unreal.Quat(*yerel(b, dW)), T)
    coz_asama("gövde", SEG1, PAR1, uyg1, 4, 3.0)
    # 2. aşama: el + parmaklar
    SEG2 = []; B2 = []
    for s in ("l", "r"):
        SEG2 += [(f"pinky_01_{s}", f"index_01_{s}"), (f"hand_{s}", f"middle_01_{s}")]; B2.append((f"hand_{s}", 3))
        for f in ("thumb", "index", "middle", "ring", "pinky"):
            z = [f"{f}_0{i}_{s}" for i in (1, 2, 3)]
            if all(b in ortak for b in z): SEG2 += [(z[0], z[1]), (z[1], z[2])]; B2 += [(z[0], 2), (z[1], 2)]
    PAR2 = [(b, ax) for b, k in B2 for ax in ((1, 0, 0), (0, 1, 0), (0, 0, 1))[:k]]
    def uyg2(p):
        for b, _ in B2:
            dW = (0, 0, 0, 1)
            for (bb, ax), v in zip(PAR2, p):
                if bb == b: dW = qmul(dW, qax(ax, v))
            rc.set_rotation_offset_for_retarget_pose_bone(b, unreal.Quat(*yerel(b, dW)), T)
    coz_asama("el", SEG2, PAR2, uyg2, 3, 4.0)
    eal.save_loaded_asset(rtg, only_if_is_dirty=False)
    # seçili animasyonlar
    for y in SECIM:
        n_ = y.split("/")[-1]
        if eal.does_asset_exist(f"{G2}/{n_}_C"): eal.delete_asset(f"{G2}/{n_}_C")
    unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(A + y) for y in SECIM], SRC, CHILD, rtg, search="", replace="", prefix="",
                                                            suffix="_C", target_path=G2, include_referenced_assets=False)
    eal.save_directory(G2, only_if_is_dirty=False, recursive=True)
    for y in SECIM:
        an = eal.load_asset(f"{G2}/{y.split('/')[-1]}_C"); o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", CHILD)
        L = an.get_play_length(); r0 = APE.get_bone_pose(APE.get_anim_pose_at_time(an, 0.0, o), "root", unreal.AnimPoseSpaces.WORLD).translation
        r1 = APE.get_bone_pose(APE.get_anim_pose_at_time(an, L, o), "root", unreal.AnimPoseSpaces.WORLD).translation
        log("anim", y.split("/")[-1], "süre %.2f" % L, "doğal hız (oyunda, ×0.86) %.0f cm/s" % (math.hypot(r1.x - r0.x, r1.y - r0.y) / L * 0.86),
            "root lock", an.get_editor_property("force_root_lock"))
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/gasp_kur_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
