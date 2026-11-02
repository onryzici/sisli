# Aktarıcı hedef pozu: omurga/boyun/baş döndürme kaymaları — kamburluk buradan mı? Test kopyalarıyla karşılaştır.
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; SK = "/Game/child_test_2/mesh/unreal_file"; T = unreal.RetargetSourceOrTarget.TARGET
GOVDE = ["pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head"]
KOL = ["clavicle_l", "upperarm_l", "lowerarm_l", "clavicle_r", "upperarm_r"]
try:
    rc0 = unreal.IKRetargeterController.get_controller(eal.load_asset(D + "/RTG_UE4_Cocuk2"))
    log("yöntemler", [m for m in dir(rc0) if "align" in m or "reset" in m])
    for ad in ("RTG_UE4_Cocuk2", "RTG_Manny_Cocuk2"):
        rc = unreal.IKRetargeterController.get_controller(eal.load_asset(f"{D}/{ad}")); poz = rc.get_current_retarget_pose_name(T)
        for b in GOVDE + KOL:
            q = rc.get_rotation_offset_for_retarget_pose_bone(b, T); r = q.rotator()
            log(ad, b, "ofset p%.1f y%.1f r%.1f" % (r.pitch, r.yaw, r.roll))
    # test 1: UE4 aktarıcı, hedef poz tamamen sıfır
    for ad, yeni, kemik in (("RTG_UE4_Cocuk2", "RTG_UE4_Cocuk2_Sifir", []), ("RTG_Manny_Cocuk2", "RTG_Manny_Cocuk2_Govde", GOVDE)):
        p = f"{D}/{yeni}"
        if not eal.does_asset_exist(p): eal.duplicate_asset(f"{D}/{ad}", p)
        r = eal.load_asset(p); rc = unreal.IKRetargeterController.get_controller(r)
        rc.reset_retarget_pose(rc.get_current_retarget_pose_name(T), [unreal.Name(k) for k in kemik], T)
        eal.save_loaded_asset(r, only_if_is_dirty=False)
        log(yeni, "sıfırlandı", kemik or "tümü", [round(rc.get_rotation_offset_for_retarget_pose_bone(b, T).rotator().pitch, 1) for b in GOVDE])
    sk = eal.load_asset(SK); ue4 = eal.load_asset("/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin"); manny = eal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
    for kaynak, mesh, rtg, sonek in ((["/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/MOB1_Stand_Relaxed_Idle_v2_IPC"], ue4, "RTG_UE4_Cocuk2_Sifir", "_S"),
                                     (["/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle", "/Game/Characters/Mannequins/Anims/Unarmed/Jump/MM_Jump"], manny, "RTG_Manny_Cocuk2_Govde", "_G")):
        res = unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(a) for a in kaynak], mesh, sk, eal.load_asset(f"{D}/{rtg}"),
              search="", replace="", prefix="", suffix=sonek, target_path=D + "/Anim/Test", include_referenced_assets=False)
        log("aktarılan", [str(x.package_name) for x in res])
    eal.save_directory(D + "/Anim/Test", only_if_is_dirty=False, recursive=True); log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_poz_test_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
