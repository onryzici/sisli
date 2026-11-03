# 2. aşama: Test/RTG_Epic üzerine el (bilek dönüşü dahil) ve parmak ofsetleri — çocuktaki avuç ve parmak boğumu yönleri Epic mankenindekiyle aynı olsun.
# Gövde/kol/bacak ofsetleri (rtg_epic.py) korunur. Gauss-Newton, sayısal Jacobian. Test animasyonları *_E yeniden üretilir.
import unreal, math, traceback, json
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; TD = D + "/Anim/Test"; T = unreal.RetargetSourceOrTarget.TARGET
MANNY = eal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"); CHILD = eal.load_asset("/Game/child_test_2/mesh/unreal_file")
MU = "/Game/Characters/Mannequins/Anims/Unarmed/"
ANIMS = [MU + "MM_Idle", MU + "Walk/MF_Unarmed_Walk_Fwd"]
PARMAK = ["thumb", "index", "middle", "ring", "pinky"]
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
try:
    # iki mesh'te de bulunan kemikler
    def kemikler(mesh):
        a_ = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -5000))
        c_ = a_.get_editor_property("skeletal_mesh_component"); c_.set_skeletal_mesh_asset(mesh)
        ad = set(str(c_.get_bone_name(i)) for i in range(c_.get_num_bones()))
        G = {b: tq(c_.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_COMPONENT).rotation) for b in ad}
        a_.destroy_actor(); return ad, G
    ad_m, _ = kemikler(MANNY); ad_c, G = kemikler(CHILD)
    ortak = ad_m & ad_c
    SEG = []; PAR = []   # PAR: (kemik, eksen sayısı)
    for s in ("l", "r"):
        SEG += [(f"pinky_01_{s}", f"index_01_{s}"), (f"hand_{s}", f"middle_01_{s}")]   # avuç enine ekseni + avuç yönü
        PAR.append((f"hand_{s}", 3))
        for f in PARMAK:
            z = [f"{f}_0{i}_{s}" for i in (1, 2, 3)]
            if all(b in ortak for b in z):
                SEG += [(z[0], z[1]), (z[1], z[2])]; PAR += [(z[0], 2), (z[1], 2)]
    SEG = [sg for sg in SEG if sg[0] in ortak and sg[1] in ortak]
    log("segment", len(SEG), "parametre", sum(k for _, k in PAR), "eksik parmak kemikleri", sorted(b for b in ad_c if any(f in b for f in PARMAK) and b not in ad_m)[:10])
    rtg = eal.load_asset(f"{TD}/RTG_Epic"); rc = unreal.IKRetargeterController.get_controller(rtg)
    yerel = lambda b, dW: qmul(qinv(G[b]), qmul(dW, G[b]))
    def olc(an, mesh, zamanlar):
        o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", mesh); v = []
        for t in zamanlar:
            pose = APE.get_anim_pose_at_time(an, t, o); P = lambda b: APE.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD).translation
            for a, b in SEG:
                d = (P(b) - P(a)).normal(); v += [d.x, d.y, d.z]
        return v
    kaynak = [eal.load_asset(a) for a in ANIMS]
    ZAM = [[0.0, k.get_play_length() * 0.37, k.get_play_length() * 0.71] for k in kaynak]
    hedef = []
    for k, z in zip(kaynak, ZAM): hedef += olc(k, MANNY, z)
    def uygula(p):
        i = 0
        for b, k in PAR:
            dW = qmul(qax((1, 0, 0), p[i]), qax((0, 1, 0), p[i+1]))
            if k == 3: dW = qmul(dW, qax((0, 0, 1), p[i+2]))
            rc.set_rotation_offset_for_retarget_pose_bone(b, unreal.Quat(*yerel(b, dW)), T); i += k
    sayac = [0]
    def deg(p):
        uygula(p); m = []
        for yol, z in zip(ANIMS, ZAM):
            sayac[0] += 1; ad = yol.split("/")[-1]; son = f"_h{sayac[0]}"
            unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(yol)], MANNY, CHILD, rtg, search="", replace="", prefix="",
                                                                    suffix=son, target_path=TD, include_referenced_assets=False)
            an = eal.load_asset(f"{TD}/{ad}{son}"); m += olc(an, CHILD, z); eal.delete_asset(f"{TD}/{ad}{son}")
        return m
    def ozet(m):
        r = {}
        for si, (a, b) in enumerate(SEG):
            top = 0.0; k = 0
            for ti in range(len(m) // (3 * len(SEG))):
                i = (ti * len(SEG) + si) * 3; d = max(-1, min(1, m[i]*hedef[i] + m[i+1]*hedef[i+1] + m[i+2]*hedef[i+2])); top += math.degrees(math.acos(d)); k += 1
            r[f"{a}>{b}"] = round(top / k, 1)
        return r
    n = sum(k for _, k in PAR); p = [0.0] * n
    for adim in range(4):
        m0 = deg(p); e = [hedef[i] - m0[i] for i in range(len(m0))]
        oz = ozet(m0); log(f"adım {adim} hata² {sum(x*x for x in e):.4f} en kötü", sorted(oz.items(), key=lambda kv: -kv[1])[:8])
        J = [[0.0] * n for _ in range(len(m0))]; d = 4.0
        for j in range(n):
            p2 = list(p); p2[j] += d; m1 = deg(p2)
            for i in range(len(m0)): J[i][j] = (m1[i] - m0[i]) / d
        JtJ = [[sum(J[k][i] * J[k][j] for k in range(len(m0))) + (1e-3 if i == j else 0) for j in range(n)] for i in range(n)]
        Jte = [sum(J[k][i] * e[k] for k in range(len(m0))) for i in range(n)]
        dp = coz(JtJ, Jte); p = [p[i] + max(-25, min(25, dp[i])) for i in range(n)]
    m = deg(p); oz = ozet(m); log("SON hata² %.4f" % sum((hedef[i] - m[i])**2 for i in range(len(m))), "en kötü", sorted(oz.items(), key=lambda kv: -kv[1])[:8])
    log("başparmak", {k: v for k, v in oz.items() if "thumb" in k})
    uygula(p); eal.save_loaded_asset(rtg, only_if_is_dirty=False)
    for yol in ANIMS:
        ad = yol.split("/")[-1]
        if eal.does_asset_exist(f"{TD}/{ad}_E"): eal.delete_asset(f"{TD}/{ad}_E")
        unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(yol)], MANNY, CHILD, rtg, search="", replace="", prefix="",
                                                                suffix="_E", target_path=TD, include_referenced_assets=False)
    eal.save_directory(TD, only_if_is_dirty=False, recursive=True)
    json.dump({"par": p, "PAR": PAR}, open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_el.json", "w"))
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_el_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
