# Çömelme: MoCap Online ücretsiz paket (UE4 Mannequin iskeleti) → çocuk. IK_UE4 + RTG_UE4_Cocuk, yerinde (IPC/IP) animasyonları kopyala.
# Karakter: çömelebilir, çömelik kapsül 42 cm, çömelik hız 100.
import unreal, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary
C = "/Game/Sisli/Cocuk"; HEDEF = C + "/Anim/MCO"
UE4 = "/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin"
ANIM = ["/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/MOB1_Crouch_Idle_V2_IPC",
        "/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/MOB1_CrouchWalk_F_IPC",
        "/Game/MCO_Mocap_Basics/Animation/Scared/In_Place/SCR_Walk_Scared_Fwd_Look_Left_Loop_IP",
        "/Game/MCO_Mocap_Basics/Animation/Scared/In_Place/SCR_Walk_Scared_Fwd_Look_Right_Loop_IP"]
try:
    ue4 = eal.load_asset(UE4); cocuk = eal.load_asset(C + "/SK_Cocuk"); rig_c = eal.load_asset(C + "/IK_Cocuk")
    assert ue4 and cocuk and rig_c, "kaynak/hedef yok"
    rp = C + "/IK_UE4"
    if eal.does_asset_exist(rp): rig_u = eal.load_asset(rp)
    else:
        rig_u = at.create_asset("IK_UE4", C, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
        c = unreal.IKRigController.get_controller(rig_u); c.set_skeletal_mesh(ue4)
        log("IK_UE4 oto tanım", c.apply_auto_generated_retarget_definition())
        try: c.apply_auto_fbik()
        except Exception as e: log("fbik", e)
        log("zincirler", [str(ch.get_editor_property("chain_name")) for ch in c.get_retarget_chains()])
        eal.save_loaded_asset(rig_u)
    tp = C + "/RTG_UE4_Cocuk"
    rtg = eal.load_asset(tp) if eal.does_asset_exist(tp) else at.create_asset("RTG_UE4_Cocuk", C, unreal.IKRetargeter, unreal.IKRetargetFactory())
    rc = unreal.IKRetargeterController.get_controller(rtg)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, rig_u); rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, rig_c)
    try: rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, ue4); rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, cocuk)
    except Exception as e: log("preview", e)
    try:
        rc.remove_all_ops(); rc.add_default_ops()
        rc.assign_ik_rig_to_all_ops(unreal.RetargetSourceOrTarget.TARGET, rig_c); rc.assign_ik_rig_to_all_ops(unreal.RetargetSourceOrTarget.SOURCE, rig_u)
    except Exception as e: log("ops", e)
    try: rc.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
    except Exception as e: log("automap", e)
    try: rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
    except Exception as e: log("autoalign", e)
    for i in range(rc.get_num_retarget_ops()):
        try: rc.run_op_initial_setup(i)
        except Exception: pass
    eal.save_loaded_asset(rtg)
    ad = [eal.find_asset_data(a) for a in ANIM]
    res = unreal.IKRetargetBatchOperation.duplicate_and_retarget(ad, ue4, cocuk, rtg, search="", replace="", prefix="", suffix="_Cocuk", target_path=HEDEF, include_referenced_assets=False)
    for r in res:
        a = eal.load_asset(str(r.package_name))
        log("ANIM", r.package_name, "süre %.2f" % a.get_play_length() if a else "-")
    # karakter: çömelme
    bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"); cdo = unreal.get_default_object(bp.generated_class())
    mv = cdo.get_editor_property("character_movement")
    na = mv.get_editor_property("nav_agent_props"); na.set_editor_property("can_crouch", True); mv.set_editor_property("nav_agent_props", na)
    mv.set_editor_property("crouched_half_height", 42.0); mv.set_editor_property("max_walk_speed_crouched", 100.0)
    try: mv.set_editor_property("can_walk_off_ledges_when_crouching", True)
    except Exception as e: log("ledge", e)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp); eal.save_loaded_asset(bp)
    log("çömelme açık", mv.get_editor_property("nav_agent_props").get_editor_property("can_crouch"), mv.get_editor_property("crouched_half_height"))
    eal.save_directory(C, only_if_is_dirty=True, recursive=True)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/comelme_kur_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
