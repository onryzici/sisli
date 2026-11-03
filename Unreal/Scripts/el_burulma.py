# Yürürken kol öne sallanınca avucun yere dönmesini yumuşakça giderir (v2).
# 1) lowerarm/hand/twist izleri, yeniden aktarılmış temiz kopyadan (RTG_MCO_Cocuk2) GERİ YÜKLENİR.
# 2) Her karede önkol ekseni etrafındaki avuç açısı φ ölçülür; φ0 = kolun en dik sarktığı karelerin medyanı.
# 3) Düzeltme YALNIZ kol öne sallanırken (ağırlık: kol yönünün öne bileşeni 0.05→0.35 arası yumuşak geçiş), en fazla ±MAKS°.
# 4) Dönüş dirseğe değil, BİLEĞE uygulanır: hand tam θ, lowerarm_twist_01 θ/2 (deri önkol boyunca yayılır). Dirsek/omuz değişmez.
import unreal, math, traceback, os
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions; AL = unreal.AnimationLibrary
def log(*a): OUT.append(" ".join(str(x) for x in a))
CHILD = eal.load_asset("/Game/child_test_2/mesh/unreal_file"); MAKS = float(os.environ.get("EL_MAKS", "40"))
HEDEF = "/Game/Sisli/Cocuk2/Anim/MCOK/Walk_06_Look_Around_Loop_IP_C"
KAYNAK = "/Game/MCO_Mocap_Basics/Animation/Walks/In_Place/Walk_06_Look_Around_Loop_IP"; TD = "/Game/Sisli/Cocuk2/Anim/Test"
def qmul(a, b):
    x1, y1, z1, w1 = a; x2, y2, z2, w2 = b
    return (w1*x2 + x1*w2 + y1*z2 - z1*y2, w1*y2 - x1*z2 + y1*w2 + z1*x2, w1*z2 + x1*y2 - y1*x2 + z1*w2, w1*w2 - x1*x2 - y1*y2 - z1*z2)
def qinv(a): return (-a[0], -a[1], -a[2], a[3])
def tq(q): return (q.x, q.y, q.z, q.w)
def v3(v): return (v.x, v.y, v.z)
def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def nrm(a): l = math.sqrt(dot(a, a)) or 1.0; return (a[0]/l, a[1]/l, a[2]/l)
def proj(v, a): d = dot(v, a); return nrm((v[0]-d*a[0], v[1]-d*a[1], v[2]-d*a[2]))
def wrap(x): return (x + 180.0) % 360.0 - 180.0
def aqu(a, deg): t = math.radians(deg) / 2; return (a[0]*math.sin(t), a[1]*math.sin(t), a[2]*math.sin(t), math.cos(t))
def olc(an, k, s):
    o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", CHILD)
    pose = APE.get_anim_pose_at_frame(an, k, o); T = lambda b: APE.get_bone_pose(pose, b, unreal.AnimPoseSpaces.WORLD); P = lambda b: v3(T(b).translation)
    a = nrm(sub(P("hand_" + s), P("lowerarm_" + s)))
    n = nrm(cross(sub(P("middle_01_" + s), P("hand_" + s)), sub(P("index_01_" + s), P("pinky_01_" + s))))
    w = (-1.0, 0.0, 0.0) if s == "l" else (1.0, 0.0, 0.0)
    np_, wp = proj(n, a), proj(w, a)
    ust = nrm(sub(P("lowerarm_" + s), P("upperarm_" + s)))
    # gövde çerçevesi: L sola (köprücükler), F öne, U yukarı — salınım ve dirsek sınırı bu çerçevede (gövde dönünce de doğru)
    L = nrm(sub(P("clavicle_l"), P("clavicle_r"))); U0 = nrm(sub(P("neck_01"), P("spine_02"))); F = nrm(cross(U0, L)); U = cross(L, F)
    dis = L if s == "l" else (-L[0], -L[1], -L[2])
    return {"L": L, "F": F, "U": U, "g_th": math.degrees(math.atan2(dot(ust, F), -dot(ust, U))), "g_ab": math.degrees(math.atan2(dot(ust, dis), -dot(ust, U))),"phi": math.degrees(math.atan2(dot(cross(wp, np_), a), dot(wp, np_))), "a": a, "on": ust[1], "dik": -ust[2],
            "th_up": math.degrees(math.atan2(ust[1], -ust[2])), "q_up": tq(T("upperarm_" + s).rotation), "q_clav": tq(T("clavicle_" + s).rotation),
            "q_low": tq(T("lowerarm_" + s).rotation), "q_hand": tq(T("hand_" + s).rotation), "q_tw": tq(T("lowerarm_twist_01_" + s).rotation)}
def yaz(an, kemik, rotlar):
    pos, rot, scl = [], [], []
    for k, q in enumerate(rotlar):
        lt = AL.get_bone_pose_for_frame(an, kemik, k, False)
        pos.append(lt.translation); rot.append(unreal.Quat(*q) if q else lt.rotation); scl.append(lt.scale3d)
    an.get_editor_property("controller").set_bone_track_keys(kemik, pos, rot, scl, True)
try:
    an = eal.load_asset(HEDEF); nk = AL.get_num_keys(an)
    # 1) temiz kopya
    tem = f"{TD}/Walk_06_Look_Around_Loop_IP_temiz"
    if eal.does_asset_exist(tem): eal.delete_asset(tem)
    unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(KAYNAK)], eal.load_asset("/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin"), CHILD,
        eal.load_asset("/Game/Sisli/Cocuk2/RTG_MCO_Cocuk2"), search="", replace="", prefix="", suffix="_temiz", target_path=TD, include_referenced_assets=False)
    tz = eal.load_asset(tem); log("temiz anahtar", AL.get_num_keys(tz), "hedef", nk)
    for s in ("l", "r"):
        for b in (f"upperarm_{s}", f"lowerarm_{s}", f"hand_{s}", f"lowerarm_twist_01_{s}"):
            yaz(an, b, [tq(AL.get_bone_pose_for_frame(tz, b, k, False).rotation) for k in range(nk)])
    log("geri yüklendi")
    # 1b) sol kol salınımı: kaynak mocap'te sol kol sağdan ~%35 geniş sallanıyor → üst kol öne/geri açısı orta nokta etrafında SALINIM_L ile daraltılır
    #     v4: daraltma GÖVDE ekseni etrafında (eskiden dünya X'i → gövde dönünce dirsek sırta gidiyordu). Ayrıca iki kolda dirsek sınırı:
    #     geri açı GERI_SINIR'ı aşarsa yumuşak sıkıştırma; gövde arkasında içe (sırta doğru) kayma ICE_SINIR'ın altına inmez.
    S_L = float(os.environ.get("SALINIM_L", "0.75")); GERI = float(os.environ.get("GERI_SINIR", "-28")); ICE = float(os.environ.get("ICE_SINIR", "4"))
    def ozet(s):
        V = [olc(an, k, s) for k in range(nk)]
        return f"geri/ileri {min(v['g_th'] for v in V):+.1f}..{max(v['g_th'] for v in V):+.1f}°  açıklık {min(v['g_ab'] for v in V):+.1f}..{max(v['g_ab'] for v in V):+.1f}°"
    for s in ("l", "r"): log(f"{s} önce (gövdeye göre): {ozet(s)}")
    for s in ("l", "r"):
        V = [olc(an, k, s) for k in range(nk)]; th = [v["g_th"] for v in V]; orta = (max(th) + min(th)) / 2
        yeni = []
        for v, t in zip(V, th):
            hedef = orta + (t - orta) * S_L if s == "l" else t
            if hedef < GERI: hedef = GERI + (hedef - GERI) * 0.3
            dth = hedef - t
            dab = max(0.0, ICE - v["g_ab"]) if v["g_th"] < 0 else 0.0   # yalnız kol gerideyken içe kaymayı dışarı it
            q = qmul(aqu(v["L"], dth), v["q_up"])
            q = qmul(aqu(v["F"], -dab if s == "l" else dab), q)
            yeni.append(qmul(qinv(v["q_clav"]), q))
        yaz(an, f"upperarm_{s}", yeni)
    for s in ("l", "r"): log(f"{s} sonra (gövdeye göre): {ozet(s)}")
    # 2) KURAL (kullanıcı): yürürken avuç içi HER AN bacağa / vücuda dönük. Avuç normali (sol elde işaret ters) gövdeye doğru yatay yönle
    #    hizalanır: hedef φ = 0, bütün döngü, iki el. Dönüş önkol ekseni etrafında: hand tam θ, lowerarm_twist_01 0.6θ; dirsek/omuz değişmez.
    #    SAĞ el kullanıcıya göre "güzel" (v2): referans = kolun en dik sarktığı karelerdeki açı, yalnız öne salınımda, en fazla 40°.
    for s in ("l", "r"):
        V = [olc(an, k, s) for k in range(nk)]
        if s == "l":
            isaret = 180.0                     # sol elde cross(el→orta parmak, serçe→işaret) avucun DIŞINI gösterir → hedef: avuç vücuda
            agirlik = [1.0] * nk; maks = MAKS
        else:
            dik = sorted(range(nk), key=lambda k: -V[k]["dik"])[: max(3, nk // 6)]
            ref = sorted(wrap(V[k]["phi"]) for k in dik); isaret = ref[len(ref) // 2]
            agirlik = [min(1.0, max(0.0, (v["on"] - 0.05) / 0.30)) for v in V]; agirlik = [w * w * (3 - 2 * w) for w in agirlik]; maks = 40.0
        dev = [wrap(v["phi"] - isaret) for v in V]
        log(f"{s}: önce sapma ort {sum(abs(d) for d in dev)/nk:.1f}° maks {max(abs(d) for d in dev):.1f}°")
        el, tw = [], []
        for v, d, w in zip(V, dev, agirlik):
            th = -max(-maks, min(maks, d)) * w
            el.append(qmul(qinv(v["q_low"]), qmul(aqu(v["a"], th), v["q_hand"])))
            tw.append(qmul(qinv(v["q_low"]), qmul(aqu(v["a"], th * (0.6 if s == "l" else 0.5)), v["q_tw"])))
        yaz(an, f"hand_{s}", el); yaz(an, f"lowerarm_twist_01_{s}", tw)
        V2 = [olc(an, k, s) for k in range(nk)]
        dev2 = [wrap(v["phi"] - isaret) for v in V2]
        log(f"{s}: sonra sapma ort {sum(abs(d) for d in dev2)/nk:.1f}° maks {max(abs(d) for d in dev2):.1f}°, "
            f"dirsek değişimi {max(math.degrees(2*math.acos(min(1, abs(dot(V[k]['q_low'][:3], V2[k]['q_low'][:3]) + V[k]['q_low'][3]*V2[k]['q_low'][3])))) for k in range(nk)):.2f}°")
    eal.save_loaded_asset(an, only_if_is_dirty=False); eal.delete_asset(tem)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/el_burulma_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
