# Kamburluk kökü: otomatik hizalama hedef pozda spine_01/-13°, spine_02/+20° bükmüştü. Hedef pozu sıfırla (UE4: tümü, Manny: gövde),
# FBIK kapalı kalsın; MCO → Anim/MCO3 (_C3), Manny zıplama → Anim/Ziplama (_G); BS örnekleri yerinde değişir; test/eski kopyalar silinir.
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; SK = "/Game/child_test_2/mesh/unreal_file"; T = unreal.RetargetSourceOrTarget.TARGET
GOVDE = ["pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head"]
MCO = "/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/"; MJ = "/Game/Characters/Mannequins/Anims/Unarmed/Jump/"
def sifirla(ad, kemik):
    r = eal.load_asset(f"{D}/{ad}"); rc = unreal.IKRetargeterController.get_controller(r)
    rc.reset_retarget_pose(rc.get_current_retarget_pose_name(T), [unreal.Name(k) for k in kemik], T)
    for i in range(rc.get_num_retarget_ops()):
        if str(rc.get_op_name(i)) == "Run IK Rig": rc.set_retarget_op_enabled(i, False)
    eal.save_loaded_asset(r, only_if_is_dirty=False)
    log(ad, "gövde ofset", [round(rc.get_rotation_offset_for_retarget_pose_bone(b, T).rotator().yaw, 1) for b in GOVDE]); return r
def aktar(adlar, kok, mesh, rtg, hedef, sonek):
    gerek = [a for a in adlar if not eal.does_asset_exist(f"{hedef}/{a}{sonek}")]
    if gerek:
        res = unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(kok + a) for a in gerek], mesh, eal.load_asset(SK), rtg,
              search="", replace="", prefix="", suffix=sonek, target_path=hedef, include_referenced_assets=False)
        log("aktarılan", [str(x.package_name).split("/")[-1] for x in res])
    eal.save_directory(hedef, only_if_is_dirty=False, recursive=True)
try:
    ru = sifirla("RTG_UE4_Cocuk2", []); rm = sifirla("RTG_Manny_Cocuk2", GOVDE)
    aktar(["MOB1_Stand_Relaxed_Idle_v2_IPC", "MOB1_Walk_F_IPC", "MOB1_Jog_F_IPC", "MOB1_Crouch_Idle_V2_IPC", "MOB1_CrouchWalk_F_IPC"], MCO,
          eal.load_asset("/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin"), ru, D + "/Anim/MCO3", "_C3")
    aktar(["MM_Jump", "MM_Fall_Loop", "MM_Land"], MJ, eal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"), rm, D + "/Anim/Ziplama", "_G")
    bs = eal.load_asset(D + "/Anim/BS_Cocuk2_Hareket2"); A = lambda n: eal.load_asset(f"{D}/Anim/MCO3/{n}_C3")
    AYAK = {0: A("MOB1_Stand_Relaxed_Idle_v2_IPC"), 300: A("MOB1_Walk_F_IPC"), 600: A("MOB1_Jog_F_IPC")}
    COMEL = {0: A("MOB1_Crouch_Idle_V2_IPC"), 300: A("MOB1_CrouchWalk_F_IPC"), 600: A("MOB1_CrouchWalk_F_IPC")}
    ornek = list(bs.get_editor_property("sample_data"))
    for i, s in enumerate(ornek):
        v = s.get_editor_property("sample_value"); h = (COMEL if abs(round(v.x)) >= 90 else AYAK).get(int(round(v.y)))
        if h: s.set_editor_property("animation", h); ornek[i] = s
    bs.set_editor_property("sample_data", ornek); eal.save_loaded_asset(bs, only_if_is_dirty=False)
    log("BS anim", sorted(set(s.get_editor_property("animation").get_name() for s in bs.get_editor_property("sample_data"))))
    sil = [f"{D}/Anim/Test/MOB1_Stand_Relaxed_Idle_v2_IPC_S", f"{D}/Anim/Test/MM_Idle_G", f"{D}/Anim/Test/MM_Jump_G", f"{D}/RTG_UE4_Cocuk2_Sifir", f"{D}/RTG_Manny_Cocuk2_Govde"]
    sil += [f"{D}/Anim/Ziplama/{n}_C2" for n in ("MM_Jump", "MM_Fall_Loop", "MM_Land")]
    sil += [f"{D}/Anim/MCO2/{n}_C2" for n in ("MOB1_Stand_Relaxed_Idle_v2_IPC", "MOB1_Walk_F_IPC", "MOB1_Jog_F_IPC", "MOB1_Crouch_Idle_V2_IPC", "MOB1_CrouchWalk_F_IPC")]
    log("silinen", sum(1 for p in sil if eal.does_asset_exist(p) and eal.delete_asset(p)), "/", len(sil))
    for n in ("MM_Jump", "MM_Fall_Loop", "MM_Land"): log(n, "süre %.3f" % eal.load_asset(f"{D}/Anim/Ziplama/{n}_G").get_play_length())
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_son_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
