# Blend space'i çocuğun doğal hızlarına ölçekle (×0.65), yürüme hızı 200, kamera: kontrolcü yaw'ı (fare kapalı) + sabit eğim
import unreal
out = []
eal = unreal.EditorAssetLibrary
K = 0.65
bs = eal.load_asset("/Game/Sisli/Cocuk/Anim/BS_Idle_Walk_Run_Cocuk")
bp_ = bs.get_editor_property("blend_parameters")
out.append("eksen ızgara: %s" % bp_[1].get_editor_property("grid_num"))
bp_[1].set_editor_property("max", 600 * K)
bs.set_editor_property("blend_parameters", bp_)
samples = bs.get_editor_property("sample_data")
new = []
for s in samples:
    v = s.get_editor_property("sample_value")
    if v.y > 1: s.set_editor_property("sample_value", unreal.Vector(v.x, v.y * K, v.z))
    new.append(s)
bs.set_editor_property("sample_data", new)
eal.save_loaded_asset(bs)
out.append("BS örnek hızları: %s" % sorted(set(round(s.get_editor_property("sample_value").y) for s in bs.get_editor_property("sample_data"))))
bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
cdo = unreal.get_default_object(bp.generated_class())
mv = cdo.get_editor_property("character_movement"); mv.set_editor_property("max_walk_speed", 200.0)
# kamera ayarı BURADA YAPILMAZ (eski tepeden kamera -32° kilidi kaldırıldı, 2026-11-02): tek kaynak kamera_ayar.py
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
import importlib, kamera_ayar; importlib.reload(kamera_ayar); kamera_ayar.uygula(bp, lambda *a: out.append(" ".join(str(x) for x in a)))
unreal.BlueprintEditorLibrary.compile_blueprint(bp); eal.save_loaded_asset(bp)
open("C:/Users/Onur/Sisli/Unreal/Scripts/yuruyus_duzelt_out.txt", "w", encoding="utf-8").write("\n".join(out))
