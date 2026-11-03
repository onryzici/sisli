# gasp_durus.py'nin eklediği omurga/boyun/köprücük ofsetlerini geri alır (O0 = O_yeni * yerel(dW)^-1) ve GASP animasyonlarını yeniden aktarır.
import unreal, math, traceback, json
OUT = []; eal = unreal.EditorAssetLibrary
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; G2 = D + "/Anim/GASP"; T = unreal.RetargetSourceOrTarget.TARGET
U = "/Game/Characters/UEFN_Mannequin"; A = U + "/Animations/"
SRC = eal.load_asset(U + "/Meshes/SKM_UEFN_Mannequin"); CHILD = eal.load_asset("/Game/child_test_2/mesh/unreal_file")
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
try:
    p = json.load(open("C:/Users/Onur/Sisli/Unreal/Scripts/gasp_durus.json"))["p"]; log("geri alınan p", p)
    a_ = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -5000))
    c_ = a_.get_editor_property("skeletal_mesh_component"); c_.set_skeletal_mesh_asset(CHILD)
    KEM = ["spine_01", "spine_02", "spine_03", "neck_01", "clavicle_l", "clavicle_r"]
    G = {b: tq(c_.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_COMPONENT).rotation) for b in KEM}; a_.destroy_actor()
    yerel = lambda b, dW: qmul(qinv(G[b]), qmul(dW, G[b]))
    rtg = eal.load_asset(D + "/RTG_GASP_Cocuk2"); rc = unreal.IKRetargeterController.get_controller(rtg); X = (1, 0, 0)
    ek = {"spine_01": -p[0] / 3, "spine_02": -p[0] / 3, "spine_03": -p[0] / 3, "neck_01": -p[1], "clavicle_l": -p[2], "clavicle_r": -p[2]}
    for b, aci in ek.items():
        cur = tq(rc.get_rotation_offset_for_retarget_pose_bone(b, T))
        rc.set_rotation_offset_for_retarget_pose_bone(b, unreal.Quat(*qmul(cur, qinv(yerel(b, qax(X, aci))))), T)
    eal.save_loaded_asset(rtg, only_if_is_dirty=False)
    for y in SECIM:
        n_ = y.split("/")[-1]
        if eal.does_asset_exist(f"{G2}/{n_}_C"): eal.delete_asset(f"{G2}/{n_}_C")
    unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(A + y) for y in SECIM], SRC, CHILD, rtg, search="", replace="", prefix="",
                                                            suffix="_C", target_path=G2, include_referenced_assets=False)
    eal.save_directory(G2, only_if_is_dirty=False, recursive=True)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/gasp_geri_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
