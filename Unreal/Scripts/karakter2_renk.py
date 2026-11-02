# Yeni çocuğun renkleri (ücretsiz sürümde renk dokuları gri yer tutucu → Base Color Tint ile): ten, saç, yetimhane kıyafeti
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary
D = "/Game/child_test_2/Materials/unreal_file/"
RENK = {
    "Std_Skin_Head_HQ_Inst": {"Base Color Tint": (0.86, 0.64, 0.54)}, "Std_Skin_Body_HQ_Inst": {"Base Color Tint": (0.84, 0.62, 0.52)},
    "Std_Skin_Arm_HQ_Inst": {"Base Color Tint": (0.84, 0.62, 0.52)}, "Std_Skin_Leg_HQ_Inst": {"Base Color Tint": (0.84, 0.62, 0.52)},
    "Std_Nails_HQ_Inst": {"Base Color Tint": (0.86, 0.66, 0.6)},
    "hair1_Transparency_LWHQ_Inst": {"Base Color Tint": (0.11, 0.072, 0.05), "Root Color": (0.06, 0.04, 0.03), "End Color": (0.13, 0.085, 0.06),
                                     "Highlight A Color": (0.35, 0.3, 0.26), "Highlight B Color": (0.3, 0.27, 0.24)},
    "Scalp1_Transparency_Inst": {"Base Color Tint": (0.16, 0.11, 0.08)},
    "Std_Eyelash_LWHQ_Inst": {"Base Color Tint": (0.09, 0.07, 0.06)},
    "Basic_T_shirts_Inst": {"Base Color Tint": (0.24, 0.26, 0.23)},
    "Waistband_Inst": {"Base Color Tint": (0.12, 0.12, 0.13)},
    "Basketball_Shoes_Inst": {"Base Color Tint": (0.22, 0.21, 0.2)},
}
try:
    for ad, vs in RENK.items():
        m = eal.load_asset(D + ad)
        if not m: OUT.append("YOK " + ad); continue
        liste = list(m.get_editor_property("vector_parameter_values")); bulunan = set()
        for i, pv in enumerate(liste):
            n = str(pv.get_editor_property("parameter_info").get_editor_property("name"))
            if n in vs:
                pv.set_editor_property("parameter_value", unreal.LinearColor(*vs[n], 1.0)); liste[i] = pv; bulunan.add(n)
        m.set_editor_property("vector_parameter_values", liste)
        for k in vs: OUT.append(f"{ad}.{k} {'ok' if k in bulunan else 'BULUNAMADI'}")
        unreal.MaterialEditingLibrary.update_material_instance(m); eal.save_loaded_asset(m, only_if_is_dirty=False)
    OUT.append("TAMAM")
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/karakter2_renk_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
