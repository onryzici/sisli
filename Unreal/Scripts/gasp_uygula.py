# Seçilen hazır animasyonları oyuna uygular (ayak kaymasın diye hızlar animasyonların doğal adım hızına eşit):
# ayakta: bekleme GASP Neutral Stand Idle, yürüme MCO "Walk_06_Look_Around" (98 cm/s → karakter 100, BS Y=300'de oran 1.02)
# Ctrl:   bekleme GASP Neutral Crouch Idle, yürüme MCO "SCR_Walk_Scared_Fwd_Look_Right" (48 cm/s → karakter 50)
# ABP_Cocuk: BsY = HizY * (3 + 3*ComelA)  (abp_kur.py)
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
def log(*a): OUT.append(" ".join(str(x) for x in a))
D = "/Game/Sisli/Cocuk2/Anim"; G2 = D + "/GASP"; K = D + "/MCOK"
YURU, COMEL = 100.0, 50.0; V_YURU, V_COMEL = 98.0, 48.0
try:
    idle = eal.load_asset(f"{G2}/M_Neutral_Stand_Idle_Loop_C"); cidle = eal.load_asset(f"{G2}/M_Neutral_Crouch_Idle_Loop_C")
    yuru = eal.load_asset(f"{K}/Walk_06_Look_Around_Loop_IP_C"); korku = eal.load_asset(f"{K}/SCR_Walk_Scared_Fwd_Look_Right_Loop_IP_C")
    # koşu (Shift, kullanıcı seçimi "2"): GASP Relaxed Run, doğal 266 cm/s → karakter koşu hızı 266 (BP_Fener), BS Y=600 örneği oran 1.0
    kosu = eal.load_asset(f"{G2}/M_Relaxed_Run_Loop_F_C")
    AYAK = {0: (idle, 1.0), 300: (yuru, YURU / V_YURU), 600: (kosu, 1.0)}
    COML = {0: (cidle, 1.0), 300: (korku, COMEL / V_COMEL), 600: (korku, 2 * COMEL / V_COMEL)}
    bs = eal.load_asset(D + "/BS_Cocuk2_Hareket2"); ornek = list(bs.get_editor_property("sample_data"))
    for i, s in enumerate(ornek):
        v = s.get_editor_property("sample_value"); h = (COML if abs(round(v.x)) >= 90 else AYAK).get(int(round(v.y)))
        if h: s.set_editor_property("animation", h[0]); s.set_editor_property("rate_scale", h[1]); ornek[i] = s
    bs.set_editor_property("sample_data", ornek); eal.save_loaded_asset(bs, only_if_is_dirty=False)
    log("BS", sorted(set((s.get_editor_property("animation").get_name(), round(s.get_editor_property("rate_scale"), 2)) for s in bs.get_editor_property("sample_data"))))
    bpc = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"); cdo = unreal.get_default_object(bpc.generated_class())
    mv = cdo.get_editor_property("character_movement"); mv.set_editor_property("max_walk_speed", YURU); mv.set_editor_property("max_walk_speed_crouched", COMEL)
    unreal.BlueprintEditorLibrary.compile_blueprint(bpc); eal.save_loaded_asset(bpc, only_if_is_dirty=False)
    log("hız", mv.get_editor_property("max_walk_speed"), mv.get_editor_property("max_walk_speed_crouched"))
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/gasp_uygula_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
