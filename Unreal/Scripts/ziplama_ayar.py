# Çocuk zıplaması: şablon 500 cm/s, yerçekimi 1.0 → ~1.3 m süzülme; çocuk için 400 cm/s + yerçekimi 1.4 → ~58 cm, 0.58 sn
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
try:
    bpc = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"); mv = unreal.get_default_object(bpc.generated_class()).get_editor_property("character_movement")
    OUT.append("önce jump %.0f gravity %.2f air %.2f" % (mv.get_editor_property("jump_z_velocity"), mv.get_editor_property("gravity_scale"), mv.get_editor_property("air_control")))
    mv.set_editor_property("jump_z_velocity", float(__import__("os").environ.get("ZIPLA_HIZ", "400"))); mv.set_editor_property("air_control", 0.2); mv.set_editor_property("gravity_scale", 1.4)
    unreal.BlueprintEditorLibrary.compile_blueprint(bpc); eal.save_loaded_asset(bpc)
    g = 980.0 * mv.get_editor_property("gravity_scale"); v = mv.get_editor_property("jump_z_velocity")
    OUT.append("sonra jump %.0f → yükseklik %.0f cm, havada %.2f sn" % (v, v * v / (2 * g), 2 * v / g))
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/ziplama_ayar_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
