# Kol/el/parmak yönlerini kaynak Manny animasyonunun aynı karesine eşitler (bileşen uzayı, sırayla: üst kol → önkol → el → parmak boğumları)
import unreal, math, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary; ML = unreal.MathLibrary
FING = [("Thumb", "thumb"), ("Index", "index"), ("Middle", "middle"), ("Ring", "ring"), ("Pinky", "pinky")]

def qaxis(ax, ang):
    h = ang / 2; s = math.sin(h); return unreal.Quat(ax.x * s, ax.y * s, ax.z * s, math.cos(h))
def qmul(a, b): return a.multiply(b) if hasattr(a, "multiply") else a * b
def qinv(q): return q.inversed() if hasattr(q, "inversed") else unreal.Quat(-q.x, -q.y, -q.z, q.w)
def q_between(a, b):
    a = a.normal(); b = b.normal(); c = a.cross(b); s = c.length(); d = max(-1, min(1, a.dot(b)))
    if s < 1e-7: return unreal.Quat(0, 0, 0, 1)
    return qaxis(c.normal(), math.atan2(s, d))
def q_frame(dc, kc, dm, km):
    q1 = q_between(dc, dm)
    k1 = q1.rotate_vector(kc); n = dm.normal()
    p1 = (k1 - n * k1.dot(n)); p2 = (km - n * km.dot(n))
    if p1.length() < 1e-6 or p2.length() < 1e-6: return q1
    p1 = p1.normal(); p2 = p2.normal()
    ang = math.atan2(n.dot(p1.cross(p2)), max(-1, min(1, p1.dot(p2))))
    return qmul(qaxis(n, ang), q1)

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
    for F, _ in FING:
        P += [(f"{S}Hand{F}1", f"{S}Hand"), (f"{S}Hand{F}2", f"{S}Hand{F}1"), (f"{S}Hand{F}3", f"{S}Hand{F}2")]
    return P

def build(anim, parents, fr):
    loc = {}; comp = {}
    for b, p in parents:
        l = AL.get_bone_pose_for_frame(anim, b, fr, False); loc[b] = l
        comp[b] = l if p is None else ML.compose_transforms(l, comp[p])
    pos = {b: comp[b].translation for b in comp}; rot = {b: comp[b].rotation for b in comp}
    return loc, pos, rot

src_index = {p.split("/")[-1].split(".")[0]: p for p in eal.list_assets("/Game/Characters/Mannequins/Anims/Unarmed", recursive=True)}
try:
    for ap in eal.list_assets("/Game/Sisli/Cocuk/Anim", recursive=False):
        a = eal.load_asset(ap)
        if not isinstance(a, unreal.AnimSequence): continue
        name = a.get_name(); s_asset = eal.load_asset(src_index.get(name[:-6], "")) if name.endswith("_Cocuk") else None
        if not s_asset: log("kaynak yok", name); continue
        n = AL.get_num_frames(a)
        tracks = {}
        err_b = []; err_a = []
        for fr in range(n + 1):
            try:
                frames = []
                for s, S in (("l", "Left"), ("r", "Right")):
                    MP = M_par(s); CP = C_par(S)
                    _, mpos, _ = build(s_asset, MP, min(fr, n))
                    cloc, cpos, crot = build(a, CP, min(fr, n))
                    frames.append((s, S, CP, mpos, cloc, cpos, crot))
            except Exception as e:
                if fr <= n - 1: log("kare okunamadı", name, fr, str(e)[:80])
                break
            for s, S, CP, mpos, cloc, cpos, crot in frames:
                parent = dict(CP)
                children = {}
                for b, p in CP: children.setdefault(p, []).append(b)
                def subtree(b):
                    out = [b]
                    for ch in children.get(b, []): out += subtree(ch)
                    return out
                def rotate(b, q):
                    piv = cpos[b]
                    for d in subtree(b):
                        cpos[d] = piv + q.rotate_vector(cpos[d] - piv); crot[d] = qmul(q, crot[d])
                # ölçüm (önce)
                e0 = (cpos[f"{S}Hand"] - cpos[f"{S}ForeArm"]).normal().dot((mpos[f"hand_{s}"] - mpos[f"lowerarm_{s}"]).normal())
                # 1) üst kol, 2) önkol: yön
                rotate(f"{S}Arm", q_between(cpos[f"{S}ForeArm"] - cpos[f"{S}Arm"], mpos[f"lowerarm_{s}"] - mpos[f"upperarm_{s}"]))
                rotate(f"{S}ForeArm", q_between(cpos[f"{S}Hand"] - cpos[f"{S}ForeArm"], mpos[f"hand_{s}"] - mpos[f"lowerarm_{s}"]))
                # 3) el: avuç yönü + boğum ekseni
                dc = cpos[f"{S}HandMiddle1"] - cpos[f"{S}Hand"]; kc = cpos[f"{S}HandPinky1"] - cpos[f"{S}HandIndex1"]
                dm = mpos[f"middle_01_{s}"] - mpos[f"hand_{s}"]; km = mpos[f"pinky_01_{s}"] - mpos[f"index_01_{s}"]
                rotate(f"{S}Hand", q_frame(dc, kc, dm, km))
                # 4) parmak boğumları 1 ve 2: yön
                for F, f in FING:
                    for j in (1, 2):
                        a0 = f"{S}Hand{F}{j}"; a1 = f"{S}Hand{F}{j+1}"
                        m0 = f"{f}_0{j}_{s}"; m1 = f"{f}_0{j+1}_{s}"
                        rotate(a0, q_between(cpos[a1] - cpos[a0], mpos[m1] - mpos[m0]))
                e1 = (cpos[f"{S}Hand"] - cpos[f"{S}ForeArm"]).normal().dot((mpos[f"hand_{s}"] - mpos[f"lowerarm_{s}"]).normal())
                err_b.append(math.degrees(math.acos(max(-1, min(1, e0))))); err_a.append(math.degrees(math.acos(max(-1, min(1, e1)))))
                # yerel dönüşlere çevir ve kaydet
                for b in [f"{S}Arm", f"{S}ForeArm", f"{S}Hand"] + [f"{S}Hand{F}{j}" for F, _ in FING for j in (1, 2)]:
                    lr = qmul(qinv(crot[parent[b]]), crot[b])
                    tr = tracks.setdefault(b, ([], [], []))
                    tr[0].append(cloc[b].translation); tr[1].append(lr); tr[2].append(cloc[b].scale3d)
        ctrl = a.get_controller() if hasattr(a, "get_controller") else a.get_editor_property("controller")
        ok = True
        for b, (pk, rk, sk) in tracks.items():
            try: ctrl.set_bone_track_keys(b, pk, rk, sk, True)
            except Exception as e: ok = False; log("yazma hatası", name, b, str(e)[:150])
        if ok: eal.save_loaded_asset(a)
        log("%s önkol farkı önce %.1f° sonra %.1f°" % (name, sum(err_b) / max(1, len(err_b)), sum(err_a) / max(1, len(err_a))))
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/duzelt_el_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
