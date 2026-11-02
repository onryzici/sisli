# Yeni çocuk için hareket: MoCap (UE4) bekleme/yürüme/koşu/çömelik → RTG_UE4_Cocuk2 → 2B blend space (X hız, Y çömelme 0..1).
# ABP kullanılmaz (Manny ayak IK'sı UE4 iskeletinde çocuğu kamburlaştırıyordu); BP_Fener tek düğüm kipinde BS konumunu sürer.
import unreal, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary
D = "/Game/Sisli/Cocuk2/Anim"; MCO = "/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/"
YURU_HIZ, KOSU_HIZ, COMEL_HIZ = 150.0, 320.0, 95.0
try:
    sk = eal.load_asset("/Game/child_test_2/mesh/unreal_file"); ue4 = eal.load_asset("/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin")
    rtg = eal.load_asset("/Game/Sisli/Cocuk2/RTG_UE4_Cocuk2")
    gerek = [a for a in ("MOB1_Stand_Relaxed_Idle_v2_IPC", "MOB1_Walk_F_IPC", "MOB1_Jog_F_IPC") if not eal.does_asset_exist(f"{D}/MCO/{a}_Cocuk2")]
    if gerek:
        res = unreal.IKRetargetBatchOperation.duplicate_and_retarget([eal.find_asset_data(MCO + a) for a in gerek], ue4, sk, rtg, search="", replace="", prefix="",
              suffix="_Cocuk2", target_path=D + "/MCO", include_referenced_assets=False)
        log("aktarılan", [str(r.package_name).split("/")[-1] for r in res])
        eal.save_directory(D + "/MCO", only_if_is_dirty=False, recursive=True)   # kaydetmezsen BS örnekleri bir sonraki açılışta boşalır
    A = lambda n: eal.load_asset(f"{D}/MCO/{n}_Cocuk2")
    p = f"{D}/BS_Cocuk2_Hareket"
    if eal.does_asset_exist(p): bs = eal.load_asset(p)   # SİLME: BP_Fener'e bağlı; yerinde güncelle
    else:
        f = unreal.BlendSpaceFactoryNew(); f.set_editor_property("target_skeleton", sk.get_editor_property("skeleton"))
        bs = at.create_asset("BS_Cocuk2_Hareket", D, unreal.BlendSpace, f)
    bp = list(bs.get_editor_property("blend_parameters"))
    for i, (ad, mn, mx, g) in enumerate((("Hiz", 0.0, KOSU_HIZ, 8), ("Comel", 0.0, 1.0, 1))):
        bp[i].set_editor_property("display_name", ad); bp[i].set_editor_property("min", mn); bp[i].set_editor_property("max", mx); bp[i].set_editor_property("grid_num", g)
    bs.set_editor_property("blend_parameters", bp)
    ornek = []
    for (n, x, y) in (("MOB1_Stand_Relaxed_Idle_v2_IPC", 0.0, 0.0), ("MOB1_Walk_F_IPC", YURU_HIZ, 0.0), ("MOB1_Jog_F_IPC", KOSU_HIZ, 0.0),
                      ("MOB1_Crouch_Idle_V2_IPC", 0.0, 1.0), ("MOB1_CrouchWalk_F_IPC", COMEL_HIZ, 1.0), ("MOB1_CrouchWalk_F_IPC", KOSU_HIZ, 1.0)):
        s = unreal.BlendSample(); s.set_editor_property("animation", A(n)); s.set_editor_property("sample_value", unreal.Vector(x, y, 0)); s.set_editor_property("rate_scale", 1.0)
        ornek.append(s)
    bs.set_editor_property("sample_data", ornek)
    # örneklerden SONRA eksenleri yeniden yaz → PostEditChange ızgarayı yeniden örnekler (yoksa çalışma zamanında karışım boş → bağlama pozu)
    bp2 = list(bs.get_editor_property("blend_parameters")); bs.set_editor_property("blend_parameters", bp2)
    try: bs.modify(); bs.post_edit_change()
    except Exception as e: log("post_edit_change yok", str(e)[:80])
    try: bs.set_editor_property("interpolation_param", bs.get_editor_property("interpolation_param"))
    except Exception: pass
    eal.save_loaded_asset(bs)
    log("BS örnek", len(bs.get_editor_property("sample_data")), "eksenler", [(str(b.get_editor_property("display_name")), b.get_editor_property("min"), b.get_editor_property("max")) for b in bs.get_editor_property("blend_parameters")][:2])
    for n in ("MOB1_Walk_F_IPC", "MOB1_Jog_F_IPC", "MOB1_CrouchWalk_F_IPC"):
        a = A(n); log(n, "süre %.2f" % a.get_play_length())
    # karakter: yürüme hızı = yürüme örneği (ayak kayması olmasın), çömelik hız = çömelik örnek
    bpc = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"); cdo = unreal.get_default_object(bpc.generated_class())
    mv = cdo.get_editor_property("character_movement"); mv.set_editor_property("max_walk_speed", YURU_HIZ); mv.set_editor_property("max_walk_speed_crouched", COMEL_HIZ)
    unreal.BlueprintEditorLibrary.compile_blueprint(bpc); eal.save_loaded_asset(bpc)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/bs_kur_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
