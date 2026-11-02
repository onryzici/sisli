# Kol burulması: üst kol (dirsek büküm ekseni) + önkol (elin burulmasının BUR_PAY kadarı). Yalnız kemiğin kendi çerçevesi döner,
# eklem konumları değişmez. Ref poz: SK_Cocuk T-poz (bileşen uzayı, sahneye konmuş SkeletalMeshActor'dan).
import unreal, math, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary; ML = unreal.MathLibrary
BUR_PAY = 0.6
FWD = unreal.Vector(0, 1, 0)   # mesh uzayında çocuğun önü +Y
def qaxis(ax, ang):
    h = ang / 2; s = math.sin(h); return unreal.Quat(ax.x * s, ax.y * s, ax.z * s, math.cos(h))
def qmul(a, b): return a.multiply(b) if hasattr(a, "multiply") else a * b
def qinv(q): return q.inversed() if hasattr(q, "inversed") else unreal.Quat(-q.x, -q.y, -q.z, q.w)
def proj(v, n): return v - n * v.dot(n)
def signed(a, b, n):
    a = proj(a, n); b = proj(b, n)
    if a.length() < 1e-6 or b.length() < 1e-6: return 0.0
    a = a.normal(); b = b.normal(); return math.atan2(n.dot(a.cross(b)), max(-1, min(1, a.dot(b))))
try:
    # --- ref poz ---
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les.load_level("/Game/Sisli/Maps/L_Sisli")
    act = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(roll=0, pitch=0, yaw=0))
    smc = act.skeletal_mesh_component; smc.set_skinned_asset_and_update(eal.load_asset("/Game/Sisli/Cocuk/SK_Cocuk"))
    REF = {}
    for i in range(smc.get_num_bones()):
        b = str(smc.get_bone_name(i)); REF[b] = smc.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_COMPONENT)
    eas.destroy_actor(act)
    log("ref kemik", len(REF), "LeftArm", REF["LeftArm"].translation)
    def C_par(S):
        return [("root", None), ("Hips", "root"), ("Spine", "Hips"), ("Spine1", "Spine"), ("Spine2", "Spine1"), (f"{S}Shoulder", "Spine2"), (f"{S}Arm", f"{S}Shoulder"),
                (f"{S}ForeArm", f"{S}Arm"), (f"{S}Hand", f"{S}ForeArm"), (f"{S}HandIndex1", f"{S}Hand"), (f"{S}HandPinky1", f"{S}Hand")]
    for ap in eal.list_assets("/Game/Sisli/Cocuk/Anim", recursive=False):
        a = eal.load_asset(ap)
        if not isinstance(a, unreal.AnimSequence): continue
        n = AL.get_num_frames(a); tracks = {}; st = {"ust": [], "on": []}
        for fr in range(n + 1):
            try:
                data = []
                for S in ("Left", "Right"):
                    P = C_par(S); loc = {}; comp = {}
                    for b, p in P:
                        l = AL.get_bone_pose_for_frame(a, b, min(fr, n), False); loc[b] = l
                        comp[b] = l if p is None else ML.compose_transforms(l, comp[p])
                    data.append((S, P, loc, comp))
            except Exception:
                break
            for S, P, loc, comp in data:
                rot = {b: comp[b].rotation for b in comp}; pos = {b: comp[b].translation for b in comp}
                A_, F_, H_ = f"{S}Arm", f"{S}ForeArm", f"{S}Hand"
                # üst kol: büküm ekseni
                u = (pos[F_] - pos[A_]).normal(); f = (pos[H_] - pos[F_]).normal()
                bend = u.cross(f); s = bend.length()
                w = max(0.0, min(1.0, (s - 0.05) / 0.15))
                u0 = (REF[F_].translation - REF[A_].translation).normal(); b0 = u0.cross(FWD).normal()
                delta = qmul(rot[A_], qinv(REF[A_].rotation))
                tw_u = signed(delta.rotate_vector(b0), bend, u) * w if s > 1e-6 else 0.0
                rot[A_] = qmul(qaxis(u, tw_u), rot[A_])
                # önkol: elin burulma payı
                k0 = (REF[f"{S}HandPinky1"].translation - REF[f"{S}HandIndex1"].translation).normal()
                pred = qmul(rot[F_], qinv(REF[F_].rotation)).rotate_vector(k0)
                k = (pos[f"{S}HandPinky1"] - pos[f"{S}HandIndex1"]).normal()
                tw_f = signed(pred, k, f) * BUR_PAY
                rot[F_] = qmul(qaxis(f, tw_f), rot[F_])
                st["ust"].append(abs(math.degrees(tw_u))); st["on"].append(abs(math.degrees(tw_f)))
                par = dict(P)
                for b in (A_, F_, H_):
                    lr = qmul(qinv(rot[par[b]]), rot[b])
                    tr = tracks.setdefault(b, ([], [], [])); tr[0].append(loc[b].translation); tr[1].append(lr); tr[2].append(loc[b].scale3d)
        ctrl = a.get_editor_property("controller"); ok = True
        for b, (pk, rk, sk) in tracks.items():
            try: ctrl.set_bone_track_keys(b, pk, rk, sk, True)
            except Exception as e: ok = False; log("yazma", a.get_name(), b, str(e)[:120])
        if ok: eal.save_loaded_asset(a)
        log("%s üst kol burulma düz. ort %.1f° | önkol %.1f°" % (a.get_name(), sum(st["ust"]) / max(1, len(st["ust"])), sum(st["on"]) / max(1, len(st["on"]))))
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/duzelt_burulma_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
