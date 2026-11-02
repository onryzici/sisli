# Yeniden hedeflenmiş animasyonlarda gövde (Spine) ve boyun (Neck) yönünü, kaynak Manny animasyonunun aynı karesindeki
# yöne eşitler (bileşen uzayında en küçük dönüş). Kafa boyunla birlikte gelir.
import unreal, math, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary; ML = unreal.MathLibrary
M_CH = ["root", "pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "neck_02", "head"]
C_CH = ["root", "Hips", "Spine", "Spine1", "Spine2", "Neck", "Head"]
SRC_ROOT = "/Game/Characters/Mannequins/Anims/Unarmed"

def chain_comp(locals_):
    comps = []; t = None
    for l in locals_:
        t = l if t is None else ML.compose_transforms(l, t); comps.append(t)
    return comps
def quat_between(a, b):
    a = a.normal(); b = b.normal()
    ax = a.cross(b); s = ax.length(); c = max(-1.0, min(1.0, a.dot(b)))
    if s < 1e-6: return unreal.Quat(0, 0, 0, 1)
    return unreal.Quat(axis=ax.normal(), angle=math.atan2(s, c)) if False else unreal.MathLibrary.quat_make_from_axis_angle(ax.normal(), math.atan2(s, c)) if hasattr(unreal.MathLibrary, "quat_make_from_axis_angle") else _qaxis(ax.normal(), math.atan2(s, c))
def _qaxis(ax, ang):
    h = ang / 2; sn = math.sin(h); return unreal.Quat(ax.x * sn, ax.y * sn, ax.z * sn, math.cos(h))
def qmul(a, b): return a.multiply(b) if hasattr(a, "multiply") else a * b
def qinv(q): return q.inversed() if hasattr(q, "inversed") else unreal.Quat(-q.x, -q.y, -q.z, q.w)
def pitch(v):
    v = v.normal(); return math.degrees(math.atan2(v.y, v.z))

src_index = {}
for p in eal.list_assets(SRC_ROOT, recursive=True):
    src_index[p.split("/")[-1].split(".")[0]] = p
try:
    for p in eal.list_assets("/Game/Sisli/Cocuk/Anim", recursive=False):
        a = eal.load_asset(p)
        if not isinstance(a, unreal.AnimSequence): continue
        name = a.get_name(); base = name[:-6] if name.endswith("_Cocuk") else name
        sp = src_index.get(base)
        if not sp: log("kaynak yok", name); continue
        s = eal.load_asset(sp)
        n = AL.get_num_frames(a)
        keys = {b: ([], [], []) for b in ("Spine", "Neck")}
        before = []; after = []
        for fr in range(n + 1):
            try:
                ml = [AL.get_bone_pose_for_frame(s, b, min(fr, n), False) for b in M_CH]
                cl = [AL.get_bone_pose_for_frame(a, b, min(fr, n), False) for b in C_CH]
            except Exception:
                break
            mc = chain_comp(ml); cc = chain_comp(cl)
            M = dict(zip(M_CH, mc)); C = dict(zip(C_CH, cc)); CL = dict(zip(C_CH, cl))
            m_t = M["neck_01"].translation - M["spine_01"].translation
            m_n = M["head"].translation - M["neck_01"].translation
            c_t = C["Neck"].translation - C["Spine"].translation
            before.append(pitch(c_t) - pitch(m_t))
            # gövde: Spine'ı döndür
            q1 = _qaxis(c_t.cross(m_t).normal(), math.atan2(c_t.normal().cross(m_t.normal()).length(), c_t.normal().dot(m_t.normal()))) if c_t.normal().cross(m_t.normal()).length() > 1e-6 else unreal.Quat(0, 0, 0, 1)
            par = C["Hips"].rotation
            sp_comp = C["Spine"].rotation
            new_sp_comp = qmul(q1, sp_comp)
            new_sp_local = qmul(qinv(par), new_sp_comp)
            # boyun: gövde düzeltmesinden sonra boyun yönü q1 ile döner
            c_n = C["Head"].translation - C["Neck"].translation
            c_n2 = q1.rotate_vector(c_n)
            q2 = _qaxis(c_n2.cross(m_n).normal(), math.atan2(c_n2.normal().cross(m_n.normal()).length(), c_n2.normal().dot(m_n.normal()))) if c_n2.normal().cross(m_n.normal()).length() > 1e-6 else unreal.Quat(0, 0, 0, 1)
            nk_par_new = qmul(q1, C["Spine2"].rotation)
            nk_comp_new = qmul(q2, qmul(q1, C["Neck"].rotation))
            new_nk_local = qmul(qinv(nk_par_new), nk_comp_new)
            after.append(pitch(q1.rotate_vector(c_t)) - pitch(m_t))
            for b, rot in (("Spine", new_sp_local), ("Neck", new_nk_local)):
                keys[b][0].append(CL[b].translation); keys[b][1].append(rot); keys[b][2].append(CL[b].scale3d)
        ctrl = a.get_controller() if hasattr(a, "get_controller") else a.get_editor_property("controller")
        ok = True
        for b, (pk, rk, sk) in keys.items():
            try:
                ctrl.set_bone_track_keys(b, pk, rk, sk, True)
            except Exception as e:
                ok = False; log("yazma hatası", name, b, len(pk), str(e)[:200])
        if ok: eal.save_loaded_asset(a)
        log("%s kare %d gövde farkı önce %.1f° sonra %.1f°" % (name, len(keys["Spine"][0]), sum(before) / max(1, len(before)), sum(after) / max(1, len(after))))
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/duzelt_egim_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
