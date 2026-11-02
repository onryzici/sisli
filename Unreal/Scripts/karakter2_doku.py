# NoEdge "clean" projesinde eksik ana dokular (Diffuse/Normal/Opacity/Specular/Bump) → malzemelerin beklediği yollara
import unreal, os, glob, traceback
OUT = []
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary
KAY = "D:/Sisli-Fab/cocuk_noedge/textures/textures/maya file.fbm"; HED = "/Game/child_test_2/textures/unreal_file"
ISTENEN = [l.strip() for l in open("C:/Users/Onur/AppData/Local/Temp/claude/C--Users-Onur/c05057a4-94ba-4cf9-b28d-6d4149e5668e/scratchpad/istenen_doku.txt", encoding="utf-8") if l.strip()]
NORMAL_CEVIR = os.environ.get("NORMAL_CEVIR", "1") == "1"
try:
    n = 0
    for p in ISTENEN:
        ad = p.split("/")[-1]
        if eal.does_asset_exist(f"{HED}/{ad}"): continue
        f = [x for x in glob.glob(f"{KAY}/{ad}.*") if not x.endswith(".swatch")]
        if not f: OUT.append("KAYNAK YOK " + ad); continue
        t = unreal.AssetImportTask(); t.filename = f[0]; t.destination_path = HED; t.destination_name = ad; t.automated = True; t.save = False; t.replace_existing = True
        at.import_asset_tasks([t]); a = eal.load_asset(f"{HED}/{ad}")
        if a is None: OUT.append("ALINAMADI " + ad); continue
        if ad.endswith("_Normal"):
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP); a.set_editor_property("srgb", False); a.set_editor_property("flip_green_channel", NORMAL_CEVIR)
        elif ad.endswith(("_Opacity", "_Specular", "_Bump")):
            a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS); a.set_editor_property("srgb", False)
        a.set_editor_property("max_texture_size", 0); eal.save_loaded_asset(a); n += 1
    OUT.append("aktarılan %d" % n)
    # malzemeleri yeniden yükleyip kaydet (artık dokuları buluyorlar)
    for p in eal.list_assets("/Game/child_test_2/Materials/unreal_file", recursive=False):
        m = eal.load_asset(p)
        if isinstance(m, unreal.MaterialInstanceConstant):
            bos = [str(v.get_editor_property("parameter_info").get_editor_property("name")) for v in m.get_editor_property("texture_parameter_values") if not v.get_editor_property("parameter_value")]
            if bos: OUT.append("BOŞ PARAMETRE " + m.get_name() + " " + ",".join(bos))
            eal.save_loaded_asset(m, only_if_is_dirty=False)
    OUT.append("TAMAM")
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/karakter2_doku_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
