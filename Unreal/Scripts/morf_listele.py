# Yeni karakterin morph hedefleri (ifade) — gülümseme/kaş/ağız adlarını bul
import unreal
OUT = []
sk = unreal.EditorAssetLibrary.load_asset("/Game/child_test_2/mesh/unreal_file")
try:
    names = [str(n) for n in sk.get_all_morph_target_names()]
except Exception as e:
    names = []; OUT.append("get_all_morph_target_names yok: %s" % e)
    try: names = [m.get_name() for m in sk.get_editor_property("morph_targets")]
    except Exception as e2: OUT.append("morph_targets yok: %s" % e2)
OUT.append("toplam %d" % len(names))
OUT += [n for n in names if any(k in n.lower() for k in ("eye", "blink", "look", "nose", "jaw"))]
open("C:/Users/Onur/Sisli/Unreal/Scripts/morf_listele_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
