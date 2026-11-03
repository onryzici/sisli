# Duruş düzeltmesi: RTG_UE4_Cocuk2 hedef pozuna kol (üst+ön kol) ve omurga/boyun ofsetleri.
# Kollar: hedef yönlere Jacobian/Newton ile otomatik çözülür (ofset anlamından bağımsız). Omurga: varyant başına öne eğim θ.
# Çıktı: /Game/Sisli/Cocuk2/Anim/Test/RTG_V<i> + MOB1_Stand_Relaxed_Idle_v2_IPC_V<i>, ofsetler rtg_ayar.json
import unreal, math, traceback, json, os
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; TD = D + "/Anim/Test"; T = unreal.RetargetSourceOrTarget.TARGET
IDLE = "/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/MOB1_Stand_Relaxed_Idle_v2_IPC"
VARYANT = json.loads(os.environ.get("RTG_VARYANT", '[[1, 0], [2, 5], [3, 9]]'))   # [no, öne eğim derece]
HEDEF = {"uL": (0.17, -0.02), "fL": (0.03, 0.12), "uR": (-0.17, -0.02), "fR": (-0.03, 0.12)}
KEMIK = {"uL": "upperarm_l", "fL": "lowerarm_l", "uR": "upperarm_r", "fR": "lowerarm_r"}
SIRA = ["uL", "fL", "uR", "fR"]
# --- kuaterniyon (x, y, z, w) ---
def qmul(a, b):
    x1, y1, z1, w1 = a; x2, y2, z2, w2 = b
    return (w1*x2 + x1*w2 + y1*z2 - z1*y2, w1*y2 - x1*z2 + y1*w2 + z1*x2, w1*z2 + x1*y2 - y1*x2 + z1*w2, w1*w2 - x1*x2 - y1*y2 - z1*z2)
def qinv(a): return (-a[0], -a[1], -a[2], a[3])
def qax(ax, deg):
    r = math.radians(deg) / 2; s = math.sin(r); return (ax[0]*s, ax[1]*s, ax[2]*s, math.cos(r))
def tq(q): return (q.x, q.y, q.z, q.w)
def uq(t): return unreal.Quat(t[0], t[1], t[2], t[3])
X = (1, 0, 0); Y = (0, 1, 0)
def coz(A, b):   # Gauss (kısmi pivot)
    n = len(b); M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-9: continue
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]; M[r] = [M[r][k] - f * M[c][k] for k in range(n + 1)]
    return [M[i][n] / M[i][i] if abs(M[i][i]) > 1e-9 else 0.0 for i in range(n)]
try:
    M_SRC = eal.load_asset("/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin"); M_DST = eal.load_asset("/Game/child_test_2/mesh/unreal_file")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a_ = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -5000))
    c_ = a_.get_editor_property("skeletal_mesh_component"); c_.set_skeletal_mesh_asset(M_DST)
    G = {b: tq(c_.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_COMPONENT).rotation)
         for b in ("spine_01", "spine_02", "neck_01", "head", "upperarm_l", "lowerarm_l", "upperarm_r", "lowerarm_r")}
    a_.destroy_actor()
    def yerel(b, dW): return qmul(qinv(G[b]), qmul(dW, G[b]))   # dünya dönüşü → bağlama çerçevesinde ofset
    def olc(an):
        o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", M_DST)
        top = {k: [0.0, 0.0] for k in SIRA}; ek = {"govde": 0.0, "kafa": 0.0, "el": [0.0, 0.0, 0.0]}
        zs = (0.0, an.get_play_length() * 0.5)
        for t in zs:
            pose = APE.get_anim_pose_at_time(an, t, o); P = lambda b: APE.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation
            for k, (a, b) in (("uL", ("upperarm_l", "lowerarm_l")), ("fL", ("lowerarm_l", "hand_l")), ("uR", ("upperarm_r", "lowerarm_r")), ("fR", ("lowerarm_r", "hand_r"))):
                v = (P(b) - P(a)).normal(); top[k][0] += v.x / len(zs); top[k][1] += v.y / len(zs)
            g = (P("neck_01") - P("pelvis")).normal(); ek["govde"] += math.degrees(math.atan2(g.y, g.z)) / len(zs)
            h = (P("head") - P("neck_01")).normal(); ek["kafa"] += math.degrees(math.atan2(h.y, h.z)) / len(zs)
            e = P("hand_l") - P("thigh_l"); ek["el"] = [ek["el"][i] + (e.x, e.y, e.z)[i] / len(zs) for i in range(3)]
        return [top[k][j] for k in SIRA for j in (0, 1)], ek
    def aktar(rtg, sonek):
        yol = f"{TD}/MOB1_Stand_Relaxed_Idle_v2_IPC{sonek}"
        if eal.does_asset_exist(yol): eal.delete_asset(yol)
        unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(IDLE)], M_SRC, M_DST, rtg,
            search="", replace="", prefix="", suffix=sonek, target_path=TD, include_referenced_assets=False)
        return eal.load_asset(yol), yol
    hedef = [HEDEF[k][j] for k in SIRA for j in (0, 1)]
    sonuc = {}
    for no, teta in VARYANT:
        ry = f"{TD}/RTG_V{no}"
        if eal.does_asset_exist(ry): eal.delete_asset(ry)
        rtg = eal.duplicate_asset(D + "/RTG_UE4_Cocuk2", ry); rc = unreal.IKRetargeterController.get_controller(rtg)
        sabit = {}
        if teta:
            sabit["spine_01"] = yerel("spine_01", qax(X, -teta * 0.5)); sabit["spine_02"] = yerel("spine_02", qax(X, -teta * 0.5))
            sabit["neck_01"] = yerel("neck_01", qax(X, teta))
        for b, q in sabit.items(): rc.set_rotation_offset_for_retarget_pose_bone(b, uq(q), T)
        par = [0.0] * 8   # her kol kemiği için (X açısı, Y açısı) derece
        def uygula(pr):
            for i, k in enumerate(SIRA):
                rc.set_rotation_offset_for_retarget_pose_bone(KEMIK[k], uq(yerel(KEMIK[k], qmul(qax(X, pr[2*i]), qax(Y, pr[2*i+1])))), T)
        def deg(pr, tag):
            uygula(pr); an, yol = aktar(rtg, "_tmp" + tag); m, ek = olc(an); eal.delete_asset(yol); return m, ek
        for adim in range(3):
            m0, ek0 = deg(par, "0")
            hata = [hedef[i] - m0[i] for i in range(8)]
            log(f"V{no} adım {adim} hata", [round(h, 3) for h in hata], "gövde %.1f kafa %.1f el %s" % (ek0["govde"], ek0["kafa"], [round(v, 1) for v in ek0["el"]]))
            if max(abs(h) for h in hata) < 0.012: break
            J = [[0.0] * 8 for _ in range(8)]; d = 4.0
            for j in range(8):
                p2 = list(par); p2[j] += d; m1, _ = deg(p2, "j")
                for i in range(8): J[i][j] = (m1[i] - m0[i]) / d
            dp = coz(J, hata); par = [par[i] + max(-25, min(25, dp[i])) for i in range(8)]
        uygula(par); an, yol = aktar(rtg, f"_V{no}"); m, ek = olc(an)
        log(f"V{no} θ={teta} SON yönler", [round(v, 3) for v in m], "hedef", hedef, "gövde %.1f kafa %.1f el−uyluk %s" % (ek["govde"], ek["kafa"], [round(v, 1) for v in ek["el"]]))
        log(f"V{no} kol parametreleri (X°,Y°)", [round(v, 1) for v in par])
        eal.save_loaded_asset(rtg, only_if_is_dirty=False)
        sonuc[no] = {"teta": teta, "par": par, "ofset": {b: list(tq(rc.get_rotation_offset_for_retarget_pose_bone(b, T)))
                     for b in list(sabit) + list(KEMIK.values())}}
    eal.save_directory(TD, only_if_is_dirty=False, recursive=True)
    json.dump(sonuc, open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_ayar.json", "w"), indent=1)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_ayar_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
