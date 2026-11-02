# Yalnız çocuk karakterinin malzemeleri (ortam MI'lerine dokunmaz). Ana malzemeler M_Sisli / M_Sisli_Maskeli var olmalı.
# Maskesiz sürüm (2026-11-02): Kas_Mat (kaşlar, alfa maskeli) eklendi; M_Maske/M_Kayis artık yok.
import unreal, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary
MDIR = "/Game/Sisli/Malzeme"; C = "/Game/Sisli/Cocuk"; SRC = "C:/Users/Onur/Sisli/Unreal/SourceArt/Cocuk"

def tex(fn, normal=False):
    ap = f"{C}/{fn}"
    if not eal.does_asset_exist(ap):
        t = unreal.AssetImportTask(); t.filename = f"{SRC}/{fn}.png"; t.destination_path = C; t.destination_name = fn
        t.automated = True; t.save = True; t.replace_existing = True; at.import_asset_tasks([t])
    a = eal.load_asset(ap)
    if a and normal:
        a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP); a.set_editor_property("srgb", False); eal.save_loaded_asset(a)
    return a

def mi(name, master, base=None, nor=None, ton=(1, 1, 1), rmul=1.0, maskealfa=None, maskerenk=None):
    path = f"{MDIR}/MI/{name}"
    if eal.does_asset_exist(path): eal.delete_asset(path)
    m = at.create_asset(name, f"{MDIR}/MI", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(m, master)
    if base: mel.set_material_instance_texture_parameter_value(m, "BaseColor", base)
    if nor: mel.set_material_instance_texture_parameter_value(m, "Normal", nor)
    mel.set_material_instance_vector_parameter_value(m, "Ton", unreal.LinearColor(*ton, 1))
    mel.set_material_instance_scalar_parameter_value(m, "PuruzCarpan", rmul)
    mel.set_material_instance_scalar_parameter_value(m, "MetalCarpan", 0.0)
    if maskealfa is not None: mel.set_material_instance_scalar_parameter_value(m, "MaskeAlfa", maskealfa)
    if maskerenk is not None: mel.set_material_instance_scalar_parameter_value(m, "MaskeRenk", maskerenk)
    eal.save_loaded_asset(m); return m

try:
    M = eal.load_asset(f"{MDIR}/M_Sisli"); MM = eal.load_asset(f"{MDIR}/M_Sisli_Maskeli")
    assert M and MM, "ana malzemeler yok"
    sk = eal.load_asset(C + "/SK_Cocuk")
    CH = {
        "Ten_Mat": lambda: mi("MI_Cocuk_Ten", M, None, None, (0.58, 0.47, 0.42), 0.55),
        "male_worksuit01_Mat": lambda: mi("MI_Cocuk_Tulum", M, tex("T_male_worksuit01_Mat_D"), tex("male_worksuit01_normal", True), (1, 1, 1), 0.88),
        "shoes03_Mat": lambda: mi("MI_Cocuk_Bot", M, tex("shoes03_diffuse"), None, (0.8, 0.8, 0.8), 0.45),
        "Sac_Mat": lambda: mi("MI_Cocuk_Sac", MM, tex("T_Sac_Mat_D"), None, (1, 1, 1), 0.6, maskealfa=1.0, maskerenk=0.0),
        "Goz_Mat": lambda: mi("MI_Cocuk_Goz", M, tex("brown_eye"), None, (0.6, 0.6, 0.6), 0.15),
        "Kas_Mat": lambda: mi("MI_Cocuk_Kas", MM, tex("eyebrow001"), None, (0.35, 0.28, 0.24), 0.7, maskealfa=1.0, maskerenk=0.0),
    }
    mats = sk.get_editor_property("materials")
    for s in mats:
        slot = str(s.get_editor_property("material_slot_name"))
        f = CH.get(slot)
        log("karakter slot", slot, "atandı" if f else "ATLANDI")
        if f: s.set_editor_property("material_interface", f())
    sk.set_editor_property("materials", mats)
    eal.save_loaded_asset(sk)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/cocuk_malzeme_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
