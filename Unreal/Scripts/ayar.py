# L_Sisli ışık/sis/PP ince ayarı (seviyeyi yeniden kurmadan): Scripts/ayar.json okunur
import unreal, json, traceback
OUT = []
try:
    A = json.load(open("C:/Users/Onur/Sisli/Unreal/Scripts/ayar.json"))
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les.load_level("/Game/Sisli/Maps/L_Sisli")
    by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
    if "pozlama" in A:
        ppv = by["PostProcess"]; ps = ppv.get_editor_property("settings")
        ps.set_editor_property("override_auto_exposure_bias", True); ps.set_editor_property("auto_exposure_bias", A["pozlama"])
        if "golge_ofset" in A:
            ps.set_editor_property("override_color_offset_shadows", True); ps.set_editor_property("color_offset_shadows", unreal.Vector4(*A["golge_ofset"], 0.0))
        ppv.set_editor_property("settings", ps)
    if "gok" in A: by["GokIsigi"].light_component.set_editor_property("intensity", A["gok"])
    if "ay" in A: by["Ay"].light_component.set_editor_property("intensity", A["ay"])
    if "sis_isik" in A or "sis_yogun" in A:
        f = by["Sis"].component
        if "sis_isik" in A: f.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(*A["sis_isik"], 1))
        if "sis_yogun" in A: f.set_editor_property("fog_density", A["sis_yogun"])
    if "lamba" in A:
        for lb, a in by.items():
            if lb.startswith("SokakLambasi") or lb.startswith("Lamba_Ek"):
                a.get_component_by_class(unreal.SpotLightComponent).set_editor_property("intensity", A["lamba"])
    les.save_current_level(); OUT.append("ayar uygulandı %s" % A)
except Exception:
    OUT.append(traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/ayar_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
