import unreal
eal = unreal.EditorAssetLibrary
bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
cdo = unreal.get_default_object(bp.generated_class())
sk = cdo.get_editor_property("mesh")
sk.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
data = sk.get_editor_property("animation_data")
data.set_editor_property("anim_to_play", eal.load_asset("/Game/Sisli/Cocuk/Anim/MM_Idle_Cocuk"))
data.set_editor_property("saved_looping", True); data.set_editor_property("saved_playing", True)
sk.set_editor_property("animation_data", data)
unreal.BlueprintEditorLibrary.compile_blueprint(bp); eal.save_loaded_asset(bp)
open("C:/Users/Onur/Sisli/Unreal/Scripts/test_tekanim_out.txt", "w").write("ok %s" % sk.get_editor_property("animation_mode"))
