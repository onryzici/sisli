# Koşu adayları: MCO Jog/Run (RTG_MCO_Cocuk2) + GASP Neutral/Relaxed Run (RTG_GASP_Cocuk2) → çocuk; doğal hızlar (×0.86) ölçülür
import unreal, math, traceback
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; CH = eal.load_asset("/Game/child_test_2/mesh/unreal_file")
def aktar(yollar, mesh, rtg, hedef):
    gerek = [y for y in yollar if not eal.does_asset_exist(f"{hedef}/{y.split('/')[-1]}_C")]
    if gerek: unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(y) for y in gerek], eal.load_asset(mesh), CH, eal.load_asset(rtg),
                                                                     search="", replace="", prefix="", suffix="_C", target_path=hedef, include_referenced_assets=False)
    eal.save_directory(hedef, only_if_is_dirty=False, recursive=True)
def hiz(an):   # basan ayağın pelvise göre yatay hızı (yerinde/kök hareketli fark etmez)
    o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", CH); L = an.get_play_length(); N = 120; dt = L / N
    po = [APE.get_anim_pose_at_time(an, i * dt, o) for i in range(N + 1)]; P = lambda k, b: APE.get_bone_pose(po[k], b, unreal.AnimPoseSpaces.WORLD).translation; hz = []
    for ay in ("foot_l", "foot_r"):
        ab = [P(k, ay) for k in range(N + 1)]; rel = [ab[k] - P(k, "pelvis") for k in range(N + 1)]; zmin = min(a.z for a in ab)
        for k in range(N):
            if ab[k].z < zmin + 2.0: hz.append(math.hypot(rel[k+1].x - rel[k].x, rel[k+1].y - rel[k].y) / dt)
    hz.sort(); return (hz[len(hz)//2] if hz else 0) * 0.86, L
try:
    M = "/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/"
    aktar([M + "MOB1_Jog_F_IPC", M + "MOB1_Run_F_IPC"], "/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin", D + "/RTG_MCO_Cocuk2", D + "/Anim/MCOK")
    G = "/Game/Characters/UEFN_Mannequin/Animations/Run/"
    aktar([G + "M_Neutral_Run_Loop_F", G + "M_Relaxed_Run_Loop_F"], "/Game/Characters/UEFN_Mannequin/Meshes/SKM_UEFN_Mannequin", D + "/RTG_GASP_Cocuk2", D + "/Anim/GASP")
    for p in (D + "/Anim/MCOK/MOB1_Jog_F_IPC_C", D + "/Anim/MCOK/MOB1_Run_F_IPC_C", D + "/Anim/GASP/M_Neutral_Run_Loop_F_C", D + "/Anim/GASP/M_Relaxed_Run_Loop_F_C",
              D + "/Anim/MCOK/Walk_06_Look_Around_Loop_IP_C"):
        v, L = hiz(eal.load_asset(p)); log(p.split("/")[-1], "doğal hız %.0f cm/s" % v, "süre %.2f" % L)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/kosu_aday_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
