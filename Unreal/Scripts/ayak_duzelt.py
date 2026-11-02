# Ayak teması: CharacterMovement kapsülü zeminden ~2 cm yukarıda tutar → mesh'i 2.5 cm indir
import unreal
eal = unreal.EditorAssetLibrary
bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
cdo = unreal.get_default_object(bp.generated_class())
sk = cdo.get_editor_property("mesh")
sk.set_editor_property("relative_location", unreal.Vector(0, 0, -66.5))
unreal.BlueprintEditorLibrary.compile_blueprint(bp); eal.save_loaded_asset(bp)
open("C:/Users/Onur/Sisli/Unreal/Scripts/ayak_duzelt_out.txt", "w").write("ok %s" % unreal.get_default_object(bp.generated_class()).get_editor_property("mesh").get_editor_property("relative_location"))
