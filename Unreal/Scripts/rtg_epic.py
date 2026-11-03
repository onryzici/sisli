# RTG_Manny_Cocuk2 hedef pozunu Epic mankenine SADIK olacak şekilde çözer: çocukta her segmentin yönü (gövde, boyun, köprücük,
# üst/ön kol, uyluk, baldır) aynı karede Epic mankeninkiyle aynı olsun (MM_Idle + Walk_Fwd, birkaç kare; Gauss-Newton, sayısal Jacobian).
# Kendi hedef uydurmak yok. Sonuç: Anim/Test/RTG_Epic (kopya) + test animasyonları *_E. Ana RTG'ye dokunmaz.
import unreal, math, traceback, json
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; TD = D + "/Anim/Test"; T = unreal.RetargetSourceOrTarget.TARGET
MANNY = eal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"); CHILD = eal.load_asset("/Game/child_test_2/mesh/unreal_file")
MU = "/Game/Characters/Mannequins/Anims/Unarmed/"
ANIMS = [MU + "MM_Idle", MU + "Walk/MF_Unarmed_Walk_Fwd"]
SEG = [("pelvis", "neck_01"), ("neck_01", "head"),
       ("clavicle_l", "upperarm_l"), ("upperarm_l", "lowerarm_l"), ("lowerarm_l", "hand_l"),
       ("clavicle_r", "upperarm_r"), ("upperarm_r", "lowerarm_r"), ("lowerarm_r", "hand_r"),
       ("thigh_l", "calf_l"), ("calf_l", "foot_l"), ("thigh_r", "calf_r"), ("calf_r", "foot_r")]
# parametre kemikleri: her biri (X, Y) dünya ekseni etrafında açı; omurga açısı spine_01/02/03'e eşit bölünür
PAR = ["SPINE", "neck_01", "clavicle_l", "upperarm_l", "lowerarm_l", "clavicle_r", "upperarm_r", "lowerarm_r", "thigh_l", "calf_l", "thigh_r", "calf_r"]
SPINE = ["spine_01", "spine_02", "spine_03"]
def qmul(a, b):
    x1, y1, z1, w1 = a; x2, y2, z2, w2 = b
    return (w1*x2 + x1*w2 + y1*z2 - z1*y2, w1*y2 - x1*z2 + y1*w2 + z1*x2, w1*z2 + x1*y2 - y1*x2 + z1*w2, w1*w2 - x1*x2 - y1*y2 - z1*z2)
def qinv(a): return (-a[0], -a[1], -a[2], a[3])
def qax(ax, deg):
    r = math.radians(deg) / 2; s = math.sin(r); return (ax[0]*s, ax[1]*s, ax[2]*s, math.cos(r))
def tq(q): return (q.x, q.y, q.z, q.w)
def coz(A, b):
    n = len(b); M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-12: continue
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]; M[r] = [M[r][k] - f * M[c][k] for k in range(n + 1)]
    return [M[i][n] / M[i][i] if abs(M[i][i]) > 1e-12 else 0.0 for i in range(n)]
def olc(an, mesh, zamanlar):
    o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", mesh); v = []
    for t in zamanlar:
        pose = APE.get_anim_pose_at_time(an, t, o); P = lambda b: APE.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation
        for a, b in SEG:
            d = (P(b) - P(a)).normal(); v += [d.x, d.y, d.z]
    return v
def aci_ozet(m, h):   # segment başına ortalama açı farkı (derece)
    r = {}
    for si, (a, b) in enumerate(SEG):
        top = 0.0; k = 0
        for ti in range(len(m) // (3 * len(SEG))):
            i = (ti * len(SEG) + si) * 3
            d = max(-1, min(1, m[i]*h[i] + m[i+1]*h[i+1] + m[i+2]*h[i+2])); top += math.degrees(math.acos(d)); k += 1
        r[f"{a}>{b}"] = round(top / k, 1)
    return r
try:
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a_ = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -5000)); c_ = a_.get_editor_property("skeletal_mesh_component"); c_.set_skeletal_mesh_asset(CHILD)
    G = {b: tq(c_.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_COMPONENT).rotation) for b in SPINE + PAR[1:]}
    a_.destroy_actor()
    yerel = lambda b, dW: qmul(qinv(G[b]), qmul(dW, G[b]))
    ry = f"{TD}/RTG_Epic"
    if eal.does_asset_exist(ry): eal.delete_asset(ry)
    rtg = eal.duplicate_asset(D + "/RTG_Manny_Cocuk2", ry); rc = unreal.IKRetargeterController.get_controller(rtg)
    rc.reset_retarget_pose(rc.get_current_retarget_pose_name(T), [], T)
    ops = [(str(rc.get_op_name(i)), rc.get_retarget_op_enabled(i)) for i in range(rc.get_num_retarget_ops())]; log("ops", ops)
    # hedef: Epic mankenindeki yönler (aynı zamanlar)
    kaynak = [eal.load_asset(a) for a in ANIMS]
    ZAM = [[0.0, k.get_play_length() * 0.37, k.get_play_length() * 0.71] for k in kaynak]
    hedef = []
    for k, z in zip(kaynak, ZAM): hedef += olc(k, MANNY, z)
    def uygula(p):
        for i, b in enumerate(PAR):
            dW = qmul(qax((1, 0, 0), p[2*i]), qax((0, 1, 0), p[2*i+1]))
            if b == "SPINE":
                for s in SPINE:
                    rc.set_rotation_offset_for_retarget_pose_bone(s, unreal.Quat(*yerel(s, qmul(qax((1, 0, 0), p[0] / 3), qax((0, 1, 0), p[1] / 3)))), T)
            else:
                rc.set_rotation_offset_for_retarget_pose_bone(b, unreal.Quat(*yerel(b, dW)), T)
    sayac = [0]
    def deg(p):
        uygula(p); m = []
        for yol, z in zip(ANIMS, ZAM):
            sayac[0] += 1; ad = yol.split("/")[-1]; son = f"_e{sayac[0]}"
            unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(yol)], MANNY, CHILD, rtg, search="", replace="", prefix="",
                                                                    suffix=son, target_path=TD, include_referenced_assets=False)
            an = eal.load_asset(f"{TD}/{ad}{son}"); m += olc(an, CHILD, z); eal.delete_asset(f"{TD}/{ad}{son}")
        return m
    n = 2 * len(PAR); p = [0.0] * n
    for adim in range(4):
        m0 = deg(p); e = [hedef[i] - m0[i] for i in range(len(m0))]
        log(f"adım {adim} hata² {sum(x*x for x in e):.4f}", aci_ozet(m0, hedef))
        J = [[0.0] * n for _ in range(len(m0))]; d = 3.0
        for j in range(n):
            p2 = list(p); p2[j] += d; m1 = deg(p2)
            for i in range(len(m0)): J[i][j] = (m1[i] - m0[i]) / d
        JtJ = [[sum(J[k][i] * J[k][j] for k in range(len(m0))) + (1e-4 if i == j else 0) for j in range(n)] for i in range(n)]
        Jte = [sum(J[k][i] * e[k] for k in range(len(m0))) for i in range(n)]
        dp = coz(JtJ, Jte); p = [p[i] + max(-20, min(20, dp[i])) for i in range(n)]
    m = deg(p); log("SON hata² %.4f" % sum((hedef[i] - m[i])**2 for i in range(len(m))), aci_ozet(m, hedef))
    log("parametreler", {PAR[i]: (round(p[2*i], 1), round(p[2*i+1], 1)) for i in range(len(PAR))})
    uygula(p); eal.save_loaded_asset(rtg, only_if_is_dirty=False)
    for yol in ANIMS:
        ad = yol.split("/")[-1]
        if eal.does_asset_exist(f"{TD}/{ad}_E"): eal.delete_asset(f"{TD}/{ad}_E")
        unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(yol)], MANNY, CHILD, rtg, search="", replace="", prefix="",
                                                                suffix="_E", target_path=TD, include_referenced_assets=False)
    eal.save_directory(TD, only_if_is_dirty=False, recursive=True)
    json.dump({"par": p}, open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_epic.json", "w"))
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_epic_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
