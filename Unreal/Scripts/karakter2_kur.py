# Yeni çocuk (NoEdge / Character Creator, /Game/child_test_2) → oyuncu karakteri.
# IK_Cocuk2 + RTG_Manny_Cocuk2 (ABP + yürüme) + RTG_UE4_Cocuk2 (çömelme, korkmuş yürüyüş). Kapsül ve ayak hizası ölçüden.
import unreal, traceback, sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary
D = "/Game/Sisli/Cocuk2"; SK = "/Game/child_test_2/mesh/unreal_file"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"; UE4 = "/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin"
def ikrig(ad, sk):
    p = f"{D}/{ad}"
    if eal.does_asset_exist(p): return eal.load_asset(p)
    r = at.create_asset(ad, D, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory()); c = unreal.IKRigController.get_controller(r); c.set_skeletal_mesh(sk)
    log(ad, "oto tanım", c.apply_auto_generated_retarget_definition())
    try: c.apply_auto_fbik()
    except Exception as e: log("fbik", e)
    log(ad, "kök", c.get_retarget_root(), "zincir", [str(ch.get_editor_property("chain_name")) for ch in c.get_retarget_chains()])
    eal.save_loaded_asset(r); return r
def rtg(ad, kaynak_rig, kaynak_sk, hedef_rig, hedef_sk):
    p = f"{D}/{ad}"
    r = eal.load_asset(p) if eal.does_asset_exist(p) else at.create_asset(ad, D, unreal.IKRetargeter, unreal.IKRetargetFactory())
    rc = unreal.IKRetargeterController.get_controller(r)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, kaynak_rig); rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, hedef_rig)
    try: rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, kaynak_sk); rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, hedef_sk)
    except Exception as e: log("preview", e)
    try:
        rc.remove_all_ops(); rc.add_default_ops()
        rc.assign_ik_rig_to_all_ops(unreal.RetargetSourceOrTarget.TARGET, hedef_rig); rc.assign_ik_rig_to_all_ops(unreal.RetargetSourceOrTarget.SOURCE, kaynak_rig)
    except Exception as e: log("ops", e)
    try: rc.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
    except Exception as e: log("automap", e)
    try: rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
    except Exception as e: log("autoalign", e)
    for i in range(rc.get_num_retarget_ops()):
        try: rc.run_op_initial_setup(i)
        except Exception: pass
    eal.save_loaded_asset(r); return r
try:
    sk = eal.load_asset(SK); manny = eal.load_asset(MANNY); ue4 = eal.load_asset(UE4)
    assert sk, "yeni karakter yok"
    bb = sk.get_bounds(); log("sınır merkez", bb.origin, "yarı boyut", bb.box_extent)
    rc_ = ikrig("IK_Cocuk2", sk); rm = eal.load_asset("/Game/Sisli/Cocuk/IK_Manny"); ru = eal.load_asset("/Game/Sisli/Cocuk/IK_UE4")
    r1 = rtg("RTG_Manny_Cocuk2", rm, manny, rc_, sk); r2 = rtg("RTG_UE4_Cocuk2", ru, ue4, rc_, sk)
    if not eal.does_asset_exist(D + "/Anim/ABP_Unarmed_Cocuk2"):
        res = unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed")], manny, sk, r1,
              search="", replace="", prefix="", suffix="_Cocuk2", target_path=D + "/Anim", include_referenced_assets=True)
        log("ABP+yürüme", len(res))
    MCO = ["/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/MOB1_Crouch_Idle_V2_IPC", "/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/MOB1_CrouchWalk_F_IPC",
           "/Game/MCO_Mocap_Basics/Animation/Scared/In_Place/SCR_Walk_Scared_Fwd_Look_Left_Loop_IP", "/Game/MCO_Mocap_Basics/Animation/Scared/In_Place/SCR_Walk_Scared_Fwd_Look_Right_Loop_IP"]
    res = unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(a) for a in MCO], ue4, sk, r2, search="", replace="", prefix="", suffix="_Cocuk2",
          target_path=D + "/Anim/MCO", include_referenced_assets=False)
    log("MCO", [str(r.package_name) for r in res])
    abp = eal.load_asset(D + "/Anim/ABP_Unarmed_Cocuk2"); log("ABP", abp)
    # karakter BP
    bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"); cdo = unreal.get_default_object(bp.generated_class())
    m = cdo.get_editor_property("mesh"); m.set_editor_property("skeletal_mesh_asset", sk)
    m.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT); m.set_editor_property("anim_class", abp.generated_class())
    m.set_editor_property("receives_decals", False)
    # ölçü: mesh tabanı z=min; kapsül yarı yüksekliği = boy/2
    zmin = bb.origin.z - bb.box_extent.z; boy = bb.box_extent.z * 2
    yari = max(40.0, boy / 2.0 + 1.0); cap = cdo.get_editor_property("capsule_component")
    cap.set_editor_property("capsule_half_height", yari); cap.set_editor_property("capsule_radius", 22.0)
    m.set_editor_property("relative_location", unreal.Vector(0, 0, -yari - zmin - 2.5)); m.set_editor_property("relative_rotation", unreal.Rotator(roll=0, pitch=0, yaw=-90))
    log("boy", round(boy, 1), "kapsül yarı", round(yari, 1), "mesh z", round(-yari - zmin - 2.5, 1))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp); eal.save_loaded_asset(bp)
    eal.save_directory(D, only_if_is_dirty=False, recursive=True); log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/karakter2_kur_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
