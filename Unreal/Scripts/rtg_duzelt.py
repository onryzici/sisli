# Kamburluk düzeltmesi: RTG'lerde "Run IK Rig" (FBIK) işlemi kapalı — IK Chains işlemi olmadığından hedefler yanlış yerde kalıyor,
# FBIK eli/ayağı oraya çekerken omurgayı büküyordu. Animasyonlar yeni klasöre yeniden aktarılır, BS örnekleri yerinde değiştirilir.
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2"; SK = "/Game/child_test_2/mesh/unreal_file"
MCO = "/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/"; MANNY_J = "/Game/Characters/Mannequins/Anims/Unarmed/Jump/"
def ik_kapat(ad):
    r = eal.load_asset(f"{D}/{ad}"); rc = unreal.IKRetargeterController.get_controller(r)
    for i in range(rc.get_num_retarget_ops()):
        if str(rc.get_op_name(i)) == "Run IK Rig": rc.set_retarget_op_enabled(i, False)
    log(ad, [(str(rc.get_op_name(i)), rc.get_retarget_op_enabled(i)) for i in range(rc.get_num_retarget_ops())])
    eal.save_loaded_asset(r, only_if_is_dirty=False); return r
def aktar(kaynaklar, src_mesh, rtg, hedef):
    gerek = [a for a in kaynaklar if not eal.does_asset_exist(f"{hedef}/{a.split('/')[-1]}_C2")]
    if gerek:
        res = unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(a) for a in gerek], src_mesh, eal.load_asset(SK), rtg,
              search="", replace="", prefix="", suffix="_C2", target_path=hedef, include_referenced_assets=False)
        log("aktarılan", [str(r.package_name).split("/")[-1] for r in res])
    eal.save_directory(hedef, only_if_is_dirty=False, recursive=True)
try:
    r_ue4 = ik_kapat("RTG_UE4_Cocuk2"); r_manny = ik_kapat("RTG_Manny_Cocuk2")
    ue4 = eal.load_asset("/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin"); manny = eal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
    aktar([MCO + n for n in ("MOB1_Stand_Relaxed_Idle_v2_IPC", "MOB1_Walk_F_IPC", "MOB1_Jog_F_IPC", "MOB1_Crouch_Idle_V2_IPC", "MOB1_CrouchWalk_F_IPC")], ue4, r_ue4, D + "/Anim/MCO2")
    aktar([MANNY_J + n for n in ("MM_Jump", "MM_Fall_Loop", "MM_Land")], manny, r_manny, D + "/Anim/Ziplama")
    for n in ("MM_Jump", "MM_Fall_Loop", "MM_Land"):
        a = eal.load_asset(f"{D}/Anim/Ziplama/{n}_C2"); log(n, "süre %.3f" % a.get_play_length())
    bs = eal.load_asset(D + "/Anim/BS_Cocuk2_Hareket2")
    A = lambda n: eal.load_asset(f"{D}/Anim/MCO2/{n}_C2")
    AYAK = {0: A("MOB1_Stand_Relaxed_Idle_v2_IPC"), 300: A("MOB1_Walk_F_IPC"), 600: A("MOB1_Jog_F_IPC")}
    COMEL = {0: A("MOB1_Crouch_Idle_V2_IPC"), 300: A("MOB1_CrouchWalk_F_IPC"), 600: A("MOB1_CrouchWalk_F_IPC")}
    ornek = list(bs.get_editor_property("sample_data"))
    for i, s in enumerate(ornek):
        v = s.get_editor_property("sample_value"); y = int(round(v.y)); x = abs(int(round(v.x)))
        h = (COMEL if x >= 90 else AYAK).get(y)
        if h: s.set_editor_property("animation", h); ornek[i] = s
    bs.set_editor_property("sample_data", ornek); eal.save_loaded_asset(bs, only_if_is_dirty=False)
    log("BS", [(round(s.get_editor_property("sample_value").x), round(s.get_editor_property("sample_value").y), s.get_editor_property("animation").get_name()) for s in bs.get_editor_property("sample_data")])
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_duzelt_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
