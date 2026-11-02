# Sisli: çocuk karakteri içe aktar, Manny animasyonlarını yeniden hedefle, BP_ThirdPersonCharacter'a bağla.
# Çalıştırma (başsız): UnrealEditor-Cmd.exe Sisli.uproject -run=pythonscript -script=.../kur_karakter.py
import unreal, traceback, sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
LOG = []
def log(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); unreal.log("SISLI " + s)
at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
DST = "/Game/Sisli/Cocuk"
FBX = "C:/Users/Onur/Sisli/Unreal/SourceArt/Cocuk/SK_Cocuk.fbx"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
try:
    # ---- 1) içe aktar ----
    if not eal.does_asset_exist(DST + "/SK_Cocuk"):
        task = unreal.AssetImportTask()
        task.filename = FBX; task.destination_path = DST; task.automated = True; task.save = True; task.replace_existing = True
        ui = unreal.FbxImportUI()
        ui.import_mesh = True; ui.import_as_skeletal = True; ui.import_animations = False
        ui.import_materials = True; ui.import_textures = True; ui.create_physics_asset = True
        ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
        task.options = ui
        at.import_asset_tasks([task])
        log("içe aktarılan:", list(task.imported_object_paths))
    for p in eal.list_assets(DST, recursive=True): log("  varlık", p)
    mesh = None
    for p in eal.list_assets(DST, recursive=True):
        a = eal.load_asset(p)
        if isinstance(a, unreal.SkeletalMesh): mesh = a
    log("mesh", mesh.get_path_name() if mesh else None)
    bb = mesh.get_bounds(); log("sınırlar", bb.origin, bb.box_extent)
    manny = eal.load_asset(MANNY)

    # ---- 2) IK rig'ler ----
    def ikrig(name, sk):
        path = DST + "/" + name
        if eal.does_asset_exist(path): return eal.load_asset(path)
        rig = at.create_asset(name, DST, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
        c = unreal.IKRigController.get_controller(rig)
        c.set_skeletal_mesh(sk)
        ok = c.apply_auto_generated_retarget_definition()
        try: c.apply_auto_fbik()
        except Exception as e: log("fbik", e)
        log(name, "oto tanım:", ok, "kök:", c.get_retarget_root(), "zincirler:", [ (ch.get_editor_property("chain_name"), str(ch.get_editor_property("start_bone").get_editor_property("bone_name")), str(ch.get_editor_property("end_bone").get_editor_property("bone_name"))) for ch in c.get_retarget_chains()])
        eal.save_loaded_asset(rig)
        return rig
    rig_m = ikrig("IK_Manny", manny)
    rig_c = ikrig("IK_Cocuk", mesh)

    # ---- 3) yeniden hedefleyici ----
    rpath = DST + "/RTG_Manny_Cocuk"
    if eal.does_asset_exist(rpath): rtg = eal.load_asset(rpath)
    else:
        rtg = at.create_asset("RTG_Manny_Cocuk", DST, unreal.IKRetargeter, unreal.IKRetargetFactory())
    rc = unreal.IKRetargeterController.get_controller(rtg)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, rig_m)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, rig_c)
    try: rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, manny); rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, mesh)
    except Exception as e: log("preview", e)
    try:
        rc.remove_all_ops(); rc.add_default_ops(); log("op sayısı", rc.get_num_retarget_ops())
        try: rc.assign_ik_rig_to_all_ops(unreal.RetargetSourceOrTarget.TARGET, rig_c)
        except Exception as e: log("assign target", e)
        try: rc.assign_ik_rig_to_all_ops(unreal.RetargetSourceOrTarget.SOURCE, rig_m)
        except Exception as e: log("assign source", e)
    except Exception as e: log("ops", e)
    try: rc.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
    except Exception as e: log("automap", e)
    try: rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
    except Exception as e: log("autoalign", e)
    for i in range(rc.get_num_retarget_ops()):
        try: rc.run_op_initial_setup(i)
        except Exception: pass
    eal.save_loaded_asset(rtg)

    # ---- 4) ABP + animasyonları kopyala ve yeniden hedefle ----
    abp_src = "/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed"
    if not eal.does_asset_exist("/Game/Sisli/Cocuk/Anim/ABP_Unarmed_Cocuk"):
        ad = [eal.find_asset_data(abp_src)]
        log("DOC", unreal.IKRetargetBatchOperation.duplicate_and_retarget.__doc__)
        res = unreal.IKRetargetBatchOperation.duplicate_and_retarget(ad, manny, mesh, rtg, search="", replace="", prefix="", suffix="_Cocuk", target_path="/Game/Sisli/Cocuk/Anim", include_referenced_assets=True)
        log("yeniden hedeflenen:", [str(r.package_name) for r in res])
    eal.save_directory("/Game/Sisli", only_if_is_dirty=False, recursive=True)
    abp = eal.load_asset("/Game/Sisli/Cocuk/Anim/ABP_Unarmed_Cocuk")
    log("ABP", abp)

    # ---- 5) karakter BP ----
    bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
    cdo = unreal.get_default_object(bp.generated_class())
    sk = cdo.get_editor_property("mesh")
    sk.set_editor_property("skeletal_mesh_asset", mesh)
    sk.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    sk.set_editor_property("anim_class", abp.generated_class())
    t = unreal.AnimationLibrary.get_bone_pose_for_frame(eal.load_asset("/Game/Sisli/Cocuk/Anim/MM_Idle_Cocuk"), "Head", 0, False)
    log("KONTROL idle Head yerel çeviri", t.translation, "kök ölçek", unreal.AnimationLibrary.get_bone_pose_for_frame(eal.load_asset("/Game/Sisli/Cocuk/Anim/MM_Idle_Cocuk"), "root", 0, False).scale3d)
    cap = cdo.get_editor_property("capsule_component")
    cap.set_editor_property("capsule_half_height", 64.0); cap.set_editor_property("capsule_radius", 24.0)
    sk.set_editor_property("relative_location", unreal.Vector(0, 0, -66.5))   # ayak teması: hareket bileşeni kapsülü ~2 cm havada tutar
    sk.set_editor_property("receives_decals", False)   # zemin dekalları ayağa/paçaya yansımasın
    mv = cdo.get_editor_property("character_movement")
    mv.set_editor_property("max_walk_speed", 200.0)      # çocuk yürüyüşü (REANIMAL koşusu 285); blend space ×0.65
    mv.set_editor_property("max_acceleration", 900.0)
    mv.set_editor_property("rotation_rate", unreal.Rotator(roll=0, pitch=0, yaw=540))
    # kamera: serbest fare kamerası (kamera_ayar.py); fareyle bakış eşlemeleri (IMC) şablondaki gibi açık kalır
    import importlib, kamera_ayar; importlib.reload(kamera_ayar)
    kamera_ayar.uygula(bp, log)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    eal.save_loaded_asset(bp)
    log("BP kaydedildi")
    eal.save_directory("/Game/Sisli", only_if_is_dirty=False, recursive=True)
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/kur_karakter_out.txt", "w", encoding="utf-8").write("\n".join(LOG))
