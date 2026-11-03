# Seçilen duruş varyantını (rtg_ayar.py → Test/RTG_V<n>) ana RTG_UE4_Cocuk2'ye uygular, MCO animasyonlarını Anim/MCO4 (_C4) olarak
# yeniden aktarır, BS_Cocuk2_Hareket2 örneklerini değiştirir; artık kullanılmayan MCO3 ve test varlıklarını siler.
import unreal, traceback, os
OUT = []; eal = unreal.EditorAssetLibrary
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; TD = D + "/Anim/Test"; T = unreal.RetargetSourceOrTarget.TARGET
V = os.environ.get("RTG_SECIM", "2")
MCO = "/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/"
ADLAR = ["MOB1_Stand_Relaxed_Idle_v2_IPC", "MOB1_Walk_F_IPC", "MOB1_Jog_F_IPC", "MOB1_Crouch_Idle_V2_IPC", "MOB1_CrouchWalk_F_IPC"]
KEMIKLER = ["spine_01", "spine_02", "neck_01", "upperarm_l", "lowerarm_l", "upperarm_r", "lowerarm_r"]
try:
    kaynak = unreal.IKRetargeterController.get_controller(eal.load_asset(f"{TD}/RTG_V{V}"))
    ana = eal.load_asset(D + "/RTG_UE4_Cocuk2"); rc = unreal.IKRetargeterController.get_controller(ana)
    for b in KEMIKLER:
        q = kaynak.get_rotation_offset_for_retarget_pose_bone(b, T); rc.set_rotation_offset_for_retarget_pose_bone(b, q, T)
        log("ofset", b, [round(v, 4) for v in (q.x, q.y, q.z, q.w)])
    eal.save_loaded_asset(ana, only_if_is_dirty=False)
    hedef = D + "/Anim/MCO4"
    gerek = [a for a in ADLAR if not eal.does_asset_exist(f"{hedef}/{a}_C4")]
    if gerek:
        res = unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(MCO + a) for a in gerek],
              eal.load_asset("/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin"), eal.load_asset("/Game/child_test_2/mesh/unreal_file"), ana,
              search="", replace="", prefix="", suffix="_C4", target_path=hedef, include_referenced_assets=False)
        log("aktarılan", [str(x.package_name).split("/")[-1] for x in res])
    eal.save_directory(hedef, only_if_is_dirty=False, recursive=True)
    bs = eal.load_asset(D + "/Anim/BS_Cocuk2_Hareket2"); ornek = list(bs.get_editor_property("sample_data"))
    for i, s in enumerate(ornek):
        ad = s.get_editor_property("animation").get_name()
        if ad.endswith("_C3"):
            s.set_editor_property("animation", eal.load_asset(f"{hedef}/{ad[:-3]}_C4")); ornek[i] = s
    bs.set_editor_property("sample_data", ornek); eal.save_loaded_asset(bs, only_if_is_dirty=False)
    log("BS anim", sorted(set(s.get_editor_property("animation").get_name() for s in bs.get_editor_property("sample_data"))))
    sil = [f"{D}/Anim/MCO3/{a}_C3" for a in ADLAR] + [f"{TD}/RTG_V{i}" for i in (1, 2, 3)] + [f"{TD}/MOB1_Stand_Relaxed_Idle_v2_IPC_V{i}" for i in (1, 2, 3)]
    for p in sil:
        if not eal.does_asset_exist(p): continue
        ref = [str(r) for r in eal.find_package_referencers_for_asset(p, False) if not str(r).startswith(D + "/Anim/Test")]
        if ref: log("silinmedi (başvuru var)", p, ref)
        else: log("silindi" if eal.delete_asset(p) else "SİLİNEMEDİ", p.split("/")[-1])
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_uygula_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
