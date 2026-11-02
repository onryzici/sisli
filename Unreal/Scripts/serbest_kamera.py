# Yalnız kamera ayarını uygula (karakteri yeniden kurmadan): Araclar/ue_py.sh serbest_kamera.py
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
import unreal, traceback, importlib, kamera_ayar
importlib.reload(kamera_ayar)
eal = unreal.EditorAssetLibrary
LOG = []
def log(*a): LOG.append(" ".join(str(x) for x in a))
try:
    bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
    kamera_ayar.uygula(bp, log)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("use_controller_rotation_yaw", False)
    cdo.get_editor_property("character_movement").set_editor_property("orient_rotation_to_movement", True)
    cdo.get_editor_property("mesh").set_editor_property("receives_decals", False); log("mesh dekal almaz")   # zemin lekeleri ayakkabıya basılmasın
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    log("kaydet", eal.save_loaded_asset(bp, only_if_is_dirty=False))
    # fareyle bakış eşlemesi duruyor mu (şablon: IA_MouseLook ← Mouse XY 2D)
    for p in ("/Game/Input/IMC_Default", "/Game/Input/IMC_MouseLook"):
        imc = eal.load_asset(p)
        try: ms = imc.get_editor_property("default_key_mappings").get_editor_property("mappings")
        except Exception:
            try: ms = imc.get_editor_property("mappings")
            except Exception as e: log("ESLEME okunamadı", p, e); continue
        for m in ms:
            log("ESLEME", p.split("/")[-1], m.get_editor_property("action").get_name(), m.get_editor_property("key").get_editor_property("key_name"))
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/serbest_kamera_out.txt", "w", encoding="utf-8").write("\n".join(LOG))
