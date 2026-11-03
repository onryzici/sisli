# BS ayakta örnek hız ölçekleri: Epic yürüyüş çocuk mesh'inde 238 cm/s, aktör ölçeği 0.86 → 205 cm/s; karakter 150 cm/s → 0.73
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
try:
    R = {"MF_Unarmed_Walk_Fwd_H": 150.0 / (238.0 * 0.86), "MF_Unarmed_Jog_Fwd_H": 300.0 / (467.6 * 0.86)}
    bs = eal.load_asset("/Game/Sisli/Cocuk2/Anim/BS_Cocuk2_Hareket2"); ornek = list(bs.get_editor_property("sample_data"))
    for i, s in enumerate(ornek):
        n = s.get_editor_property("animation").get_name()
        if n in R: s.set_editor_property("rate_scale", R[n]); ornek[i] = s
    bs.set_editor_property("sample_data", ornek); eal.save_loaded_asset(bs, only_if_is_dirty=False)
    OUT.append(str(sorted(set((s.get_editor_property("animation").get_name(), round(s.get_editor_property("rate_scale"), 2)) for s in bs.get_editor_property("sample_data")))))
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/hazir_hiz_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
