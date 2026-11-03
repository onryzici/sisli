# Hazır Epic Third Person animasyonları (Manny: MM_Idle, Walk_Fwd, Jog_Fwd) → çocuk (RTG_Manny_Cocuk2, gövde sıfır).
# Elle kol/omurga ofsetleri GERİ ALINIR (RTG_UE4_Cocuk2 hedef poz sıfır); çömelme MCO'dan aynı (sıfır) RTG ile. Hepsi Anim/Hazir/*_H.
# Ayakta BS örnekleri Manny animasyonları, çömelik MCO; adım hızı ölçülüp örnek hız ölçeği (rate_scale) ayarlanır.
import unreal, math, traceback
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; H = D + "/Anim/Hazir"; T = unreal.RetargetSourceOrTarget.TARGET
CHILD = eal.load_asset("/Game/child_test_2/mesh/unreal_file")
MCO = "/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/"; MU = "/Game/Characters/Mannequins/Anims/Unarmed/"
def aktar(yollar, kaynak_mesh, rtg):
    gerek = [y for y in yollar if not eal.does_asset_exist(f"{H}/{y.split('/')[-1]}_H")]
    if gerek:
        res = unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(y) for y in gerek], eal.load_asset(kaynak_mesh), CHILD, rtg,
              search="", replace="", prefix="", suffix="_H", target_path=H, include_referenced_assets=False)
        log("aktarılan", [str(x.package_name).split("/")[-1] for x in res])
def adim_hizi(an):   # yerinde animasyonda basan ayağın yatay hızı = animasyonun "doğal" yürüme hızı (cm/s, çocuk mesh oranlarıyla)
    o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", CHILD)
    L = an.get_play_length(); n = max(20, int(L * 60)); dt = L / n; hiz = []
    for ayak in ("foot_l", "foot_r"):
        ps = [APE.get_bone_pose(APE.get_anim_pose_at_time(an, i * dt, o), ayak, unreal.AnimPoseSpaces.WORLD).translation for i in range(n + 1)]
        zmin = min(p.z for p in ps)
        for i in range(n):
            if ps[i].z < zmin + 1.5:
                hiz.append(math.hypot(ps[i + 1].x - ps[i].x, ps[i + 1].y - ps[i].y) / dt)
    hiz.sort(); return hiz[len(hiz) // 2] if hiz else 0.0
try:
    ru = eal.load_asset(D + "/RTG_UE4_Cocuk2"); rc = unreal.IKRetargeterController.get_controller(ru)
    rc.reset_retarget_pose(rc.get_current_retarget_pose_name(T), [], T); eal.save_loaded_asset(ru, only_if_is_dirty=False)
    log("RTG_UE4_Cocuk2 hedef poz sıfırlandı")
    aktar([MCO + "MOB1_Crouch_Idle_V2_IPC", MCO + "MOB1_CrouchWalk_F_IPC", MCO + "MOB1_Walk_F_IPC", MCO + "MOB1_Jog_F_IPC"],
          "/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin", ru)
    aktar([MU + "MM_Idle", MU + "Walk/MF_Unarmed_Walk_Fwd", MU + "Jog/MF_Unarmed_Jog_Fwd"], "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple",
          eal.load_asset(D + "/RTG_Manny_Cocuk2"))
    eal.save_directory(H, only_if_is_dirty=False, recursive=True)
    A = lambda n: eal.load_asset(f"{H}/{n}_H")
    hz = {n: adim_hizi(A(n)) for n in ("MOB1_Walk_F_IPC", "MOB1_Jog_F_IPC", "MF_Unarmed_Walk_Fwd", "MF_Unarmed_Jog_Fwd", "MOB1_CrouchWalk_F_IPC")}
    log("adım hızları cm/s", {k: round(v, 1) for k, v in hz.items()})
    # eski BS düzeni MCO yürüyüşüne göre ayarlıydı (Y=300 → MCO walk, Y=600 → MCO jog); Manny örnekleri aynı yerde, aynı hızı versin diye rate_scale
    rw = hz["MOB1_Walk_F_IPC"] / hz["MF_Unarmed_Walk_Fwd"] if hz["MF_Unarmed_Walk_Fwd"] else 1.0
    rj = hz["MOB1_Jog_F_IPC"] / hz["MF_Unarmed_Jog_Fwd"] if hz["MF_Unarmed_Jog_Fwd"] else 1.0
    log("rate yürüme %.2f koşu %.2f" % (rw, rj))
    AYAK = {0: (A("MM_Idle"), 1.0), 300: (A("MF_Unarmed_Walk_Fwd"), rw), 600: (A("MF_Unarmed_Jog_Fwd"), rj)}
    COMEL = {0: (A("MOB1_Crouch_Idle_V2_IPC"), 1.0), 300: (A("MOB1_CrouchWalk_F_IPC"), 1.0), 600: (A("MOB1_CrouchWalk_F_IPC"), 1.0)}
    bs = eal.load_asset(D + "/Anim/BS_Cocuk2_Hareket2"); ornek = list(bs.get_editor_property("sample_data"))
    for i, s in enumerate(ornek):
        v = s.get_editor_property("sample_value"); h = (COMEL if abs(round(v.x)) >= 90 else AYAK).get(int(round(v.y)))
        if h:
            s.set_editor_property("animation", h[0]); s.set_editor_property("rate_scale", h[1]); ornek[i] = s
    bs.set_editor_property("sample_data", ornek); eal.save_loaded_asset(bs, only_if_is_dirty=False)
    log("BS", sorted(set((s.get_editor_property("animation").get_name(), round(s.get_editor_property("rate_scale"), 2)) for s in bs.get_editor_property("sample_data"))))
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/hazir_anim_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
