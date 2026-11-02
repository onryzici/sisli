# Altyazı yazı tipi: motorun Roboto'su /Game/Uyanis/UI/F_Altyazi olarak kopyalanır, eski (Canvas) boyutu 4K için büyütülür.
# Motor altyazıları ekran ölçeğiyle büyümez; DefaultEngine.ini SubtitleFontName bu dosyayı gösterir.
import unreal, os, traceback
OUT = []; eal = unreal.EditorAssetLibrary
P = "/Game/Uyanis/UI/F_Altyazi"; BOY = int(os.environ.get("ALTYAZI_BOY", "46"))
try:
    if not eal.does_asset_exist(P):
        ok = eal.duplicate_asset("/Engine/EngineFonts/Roboto", P); OUT.append("kopya " + str(bool(ok)))
    f = eal.load_asset(P)
    OUT.append("önce " + str(f.get_editor_property("legacy_font_size")) + " " + str(f.get_editor_property("font_cache_type")))
    f.set_editor_property("legacy_font_size", BOY)
    eal.save_loaded_asset(f, only_if_is_dirty=False); OUT.append("sonra " + str(f.get_editor_property("legacy_font_size")))
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/altyazi_font_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
