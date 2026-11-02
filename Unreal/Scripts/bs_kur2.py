# Geçerli ızgaralı şablon BS'i (BS_Idle_Walk_Run_Cocuk2: X yön -180..180, Y hız 0..600) kopyala; konumlara dokunmadan animasyonları değiştir.
# Yön ekseni boşta (karakter hareket yönüne döner) → X=45 ayakta, X=90 çömelik. Y: 0 bekleme, 300 yürüme, 600 koşu.
# (Başsız modda sıfırdan kurulan BS'in ızgarası hesaplanmıyor → çalışma anında boş, bağlama pozu.)
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
D = "/Game/Sisli/Cocuk2/Anim"; HED = D + "/BS_Cocuk2_Hareket2"
try:
    if not eal.does_asset_exist(HED): OUT.append("kopya " + str(bool(eal.duplicate_asset(D + "/BS_Idle_Walk_Run_Cocuk2", HED))))
    bs = eal.load_asset(HED)
    A = lambda n: eal.load_asset(f"{D}/MCO/{n}_Cocuk2")
    AYAK = {0: A("MOB1_Stand_Relaxed_Idle_v2_IPC"), 300: A("MOB1_Walk_F_IPC"), 600: A("MOB1_Jog_F_IPC")}
    COMEL = {0: A("MOB1_Crouch_Idle_V2_IPC"), 300: A("MOB1_CrouchWalk_F_IPC"), 600: A("MOB1_CrouchWalk_F_IPC")}
    ornek = list(bs.get_editor_property("sample_data"))
    for i, s in enumerate(ornek):
        v = s.get_editor_property("sample_value"); y = int(round(v.y)); x = abs(int(round(v.x)))
        hedef = (COMEL if x >= 90 else AYAK).get(y)
        if hedef: s.set_editor_property("animation", hedef); ornek[i] = s
        OUT.append("x=%4d y=%3d → %s" % (int(round(v.x)), y, hedef.get_name() if hedef else "-"))
    bs.set_editor_property("sample_data", ornek)
    eal.save_loaded_asset(bs, only_if_is_dirty=False); OUT.append("TAMAM")
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/bs_kur2_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
