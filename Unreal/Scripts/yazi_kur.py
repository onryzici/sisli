# Altyazı satırları: her satır = sessiz SoundWave + Subtitles (motorun altyazı yöneticisi ekranın alt ortasında gösterir).
# /Game/Uyanis/Yazi/SW_<id>. Süre: metin uzunluğuna göre 2..9 sn (sessiz_Ns.wav).
import unreal, math, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
from metinler import SATIR
D = "/Game/Uyanis/Yazi"; WAV = "C:/Users/Onur/Sisli/Unreal/SourceArt/Ses/sessiz_{}s.wav"
try:
    for k, (metin, _tr) in SATIR.items():
        sure = max(2, min(9, int(math.ceil(len(metin) * 0.065 + 1.6))))
        ad = "SW_" + k; p = f"{D}/{ad}"
        if not eal.does_asset_exist(p):   # var olanı SİLME: BP'lerdeki referanslar kopar; yalnız altyazıyı güncelle
            t = unreal.AssetImportTask(); t.filename = WAV.format(sure); t.destination_path = D; t.destination_name = ad
            t.automated = True; t.save = False; t.replace_existing = True; at.import_asset_tasks([t])
        sw = eal.load_asset(p)
        cue = unreal.SubtitleCue(); cue.set_editor_property("text", metin); cue.set_editor_property("time", 0.0)
        sw.set_editor_property("subtitles", [cue])
        try: sw.set_editor_property("manual_word_wrap", False)
        except Exception: pass
        eal.save_loaded_asset(sw); log("YAZI", ad, f"{sure}s", metin)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/yazi_kur_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
