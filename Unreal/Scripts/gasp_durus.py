# GASP aktarımında kamburluk düzeltmesi: hedef = kullanıcının beğendiği Manny aktarımındaki (Test/*_E) çocuk duruşu.
# Ölçüler (döngü ortalaması, çocuk mesh): gövde eğimi pelvis→neck_01, göğüs spine_03→neck_01, baş neck_01→head, omuz clavicle→upperarm öne açısı.
# Parametreler (RTG_GASP_Cocuk2 mevcut ofsetlerinin ÜSTÜNE): omurga öne/arka, boyun, köprücük öne/arka. Sonra GASP animasyonları yeniden aktarılır.
import unreal, math, traceback, json, os
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; G2 = D + "/Anim/GASP"; TD = D + "/Anim/Test"; T = unreal.RetargetSourceOrTarget.TARGET
U = "/Game/Characters/UEFN_Mannequin"; A = U + "/Animations/"
SRC = eal.load_asset(U + "/Meshes/SKM_UEFN_Mannequin"); CHILD = eal.load_asset("/Game/child_test_2/mesh/unreal_file")
SECIM = ["Idle/M_Neutral_Stand_Idle_Loop", "Idle/M_Relaxed_Stand_Idle_Loop", "Idle/M_Neutral_Crouch_Idle_Loop", "Walk/M_Neutral_Walk_Loop_F",
         "Walk/M_Relaxed_Walk_Loop_F", "Crouch/M_Neutral_Crouch_Loop_F", "Jump/M_Neutral_Jump_F_Start_Stand_Lfoot", "Jump/M_Neutral_Jump_Loop_Fall",
         "Jump/M_Neutral_Jump_F_Land_Stand_Light_Lfoot"]
CIFT = [(A + "Idle/M_Neutral_Stand_Idle_Loop", TD + "/MM_Idle_E"), (A + "Walk/M_Neutral_Walk_Loop_F", TD + "/MF_Unarmed_Walk_Fwd_E")]
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
def egim(v): n = v.normal(); return math.degrees(math.atan2(n.y, n.z))
def durus(an, N=16):
    o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", CHILD); L = an.get_play_length(); s = [0.0] * 4
    for i in range(N):
        pose = APE.get_anim_pose_at_time(an, L * i / N, o); P = lambda b: APE.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation
        s[0] += egim(P("neck_01") - P("pelvis")) / N; s[1] += egim(P("neck_01") - P("spine_03")) / N; s[2] += egim(P("head") - P("neck_01")) / N
        om = 0.0
        for k in ("l", "r"):
            v = (P("upperarm_" + k) - P("clavicle_" + k)).normal(); om += math.degrees(math.asin(max(-1, min(1, v.y)))) / 2
        s[3] += om / N
    return s
AD = ["gövde", "göğüs", "baş", "omuz"]
fmt = lambda s: " ".join(f"{a} {v:+.1f}" for a, v in zip(AD, s))
try:
    hedef = []
    for g, e in CIFT:
        h = durus(eal.load_asset(e)); hedef += h; log("HEDEF (beğenilen)", e.split("/")[-1], fmt(h))
        log("ŞİMDİ (GASP)    ", g.split("/")[-1], fmt(durus(eal.load_asset(f"{G2}/{g.split('/')[-1]}_C"))))
    a_ = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -5000))
    c_ = a_.get_editor_property("skeletal_mesh_component"); c_.set_skeletal_mesh_asset(CHILD)
    KEM = ["spine_01", "spine_02", "spine_03", "neck_01", "clavicle_l", "clavicle_r"]
    G = {b: tq(c_.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_COMPONENT).rotation) for b in KEM}; a_.destroy_actor()
    rtg = eal.load_asset(D + "/RTG_GASP_Cocuk2"); rc = unreal.IKRetargeterController.get_controller(rtg)
    O0 = {b: tq(rc.get_rotation_offset_for_retarget_pose_bone(b, T)) for b in KEM}
    yerel = lambda b, dW: qmul(qinv(G[b]), qmul(dW, G[b]))
    X = (1, 0, 0)
    def uygula(p):   # p = [omurga öne(+)/arka, boyun, köprücük]; öne = -X ekseni (yukarı vektörü +Y'ye)
        for s_ in ("spine_01", "spine_02", "spine_03"): rc.set_rotation_offset_for_retarget_pose_bone(s_, unreal.Quat(*qmul(O0[s_], yerel(s_, qax(X, -p[0] / 3)))), T)
        rc.set_rotation_offset_for_retarget_pose_bone("neck_01", unreal.Quat(*qmul(O0["neck_01"], yerel("neck_01", qax(X, -p[1])))), T)
        for k in ("clavicle_l", "clavicle_r"): rc.set_rotation_offset_for_retarget_pose_bone(k, unreal.Quat(*qmul(O0[k], yerel(k, qax(X, -p[2])))), T)
    say = [0]
    def deg(p):
        uygula(p); m = []
        for g, _ in CIFT:
            say[0] += 1; n_ = g.split("/")[-1]; son = f"_d{say[0]}"
            unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(g)], SRC, CHILD, rtg, search="", replace="", prefix="",
                                                                    suffix=son, target_path=TD, include_referenced_assets=False)
            an = eal.load_asset(f"{TD}/{n_}{son}"); m += durus(an); eal.delete_asset(f"{TD}/{n_}{son}")
        return m
    p = [0.0, 0.0, 0.0]; W = [1.0, 0.6, 1.0, 0.8] * 2   # ağırlıklar: göğüs biraz düşük
    for adim in range(4):
        m0 = deg(p); e = [(hedef[i] - m0[i]) * W[i] for i in range(8)]
        log(f"adım {adim} p={[round(v, 1) for v in p]} idle {fmt(m0[:4])} | yürüme {fmt(m0[4:])}")
        J = [[0.0] * 3 for _ in range(8)]
        for j in range(3):
            p2 = list(p); p2[j] += 3.0; m1 = deg(p2)
            for i in range(8): J[i][j] = (m1[i] - m0[i]) / 3.0 * W[i]
        JtJ = [[sum(J[k][i] * J[k][j] for k in range(8)) + (1e-3 if i == j else 0) for j in range(3)] for i in range(3)]
        Jte = [sum(J[k][i] * e[k] for k in range(8)) for i in range(3)]
        dp = coz(JtJ, Jte); p = [p[i] + max(-15, min(15, dp[i])) for i in range(3)]
    m = deg(p); log(f"SON p={[round(v, 1) for v in p]} idle {fmt(m[:4])} | yürüme {fmt(m[4:])}")
    eal.save_loaded_asset(rtg, only_if_is_dirty=False)
    for y in SECIM:
        n_ = y.split("/")[-1]
        if eal.does_asset_exist(f"{G2}/{n_}_C"): eal.delete_asset(f"{G2}/{n_}_C")
    unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(A + y) for y in SECIM], SRC, CHILD, rtg, search="", replace="", prefix="",
                                                            suffix="_C", target_path=G2, include_referenced_assets=False)
    eal.save_directory(G2, only_if_is_dirty=False, recursive=True)
    json.dump({"p": p}, open("C:/Users/Onur/Sisli/Unreal/Scripts/gasp_durus.json", "w"))
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/gasp_durus_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
