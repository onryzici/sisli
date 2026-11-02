# Yatakhane eşyaları (Megascans 4K + anahtarlık) → /Game/Uyanis/Fab/Yat/<Ad>; tüm Fab dokularında boyut sınırı kaldırılır (4K); oyuncaklar 4K.
import unreal, os, glob, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary
KOK = "D:/Sisli-Fab/yatakhane"; HD = "/Game/Uyanis/Fab/Yat"
M = eal.load_asset("/Game/Uyanis/Malzeme/M_MS")
ESYA = {"Kapi": ("painted_wooden_door_vmqifgedw_high", False), "Floresan": ("fluorescent_ceiling_lamp_vidrear_high", True),
        "Sarkit": ("metal_pendant_light_vgyide1aw_high", True), "Defter": ("old_book_wldocam_high", True), "Tabure": ("old_metal_stool_ukknbeyaw_high", True),
        "Sandalye": ("dirty_metal_chair_ukikdggbw_high", True), "Dolap": ("rusty_metal_cabinet_vjhledeaw_high", True), "Masa": ("wooden_table_with_drawer_vfvndhsga_high", True),
        "KafesLamba": ("rusty_bulkhead_light_vgyidfpaw_high", True)}
def doku(dosya, hedef, ad, tur):
    if not dosya or not os.path.exists(dosya): return None
    ap = f"{hedef}/{ad}"
    if not eal.does_asset_exist(ap):
        t = unreal.AssetImportTask(); t.filename = dosya; t.destination_path = hedef; t.destination_name = ad; t.automated = True; t.save = False; t.replace_existing = True
        at.import_asset_tasks([t])
    a = eal.load_asset(ap)
    if a is None: return None
    if tur == "n":
        a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP); a.set_editor_property("srgb", False); a.set_editor_property("flip_green_channel", True)
    elif tur == "l":
        a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS); a.set_editor_property("srgb", False)
    a.set_editor_property("max_texture_size", 0); eal.save_loaded_asset(a); return a
def mi(ad, hedef, d, skal):
    p = f"{hedef}/{ad}"
    if eal.does_asset_exist(p): eal.delete_asset(p)
    m = at.create_asset(ad, hedef, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew()); mel.set_material_instance_parent(m, M)
    for k, v in d.items():
        if v: mel.set_material_instance_texture_parameter_value(m, k, v)
    for k, v in skal.items(): mel.set_material_instance_scalar_parameter_value(m, k, v)
    eal.save_loaded_asset(m); return m
def fbx_al(dosya, hedef, birlestir):
    t = unreal.AssetImportTask(); t.filename = dosya; t.destination_path = hedef; t.automated = True; t.save = False; t.replace_existing = True
    ui = unreal.FbxImportUI(); ui.import_mesh = True; ui.import_as_skeletal = False; ui.import_materials = False; ui.import_textures = False
    ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH; ui.static_mesh_import_data.combine_meshes = birlestir
    ui.static_mesh_import_data.auto_generate_collision = False; ui.static_mesh_import_data.generate_lightmap_u_vs = False
    t.options = ui; at.import_asset_tasks([t]); return [eal.load_asset(p) for p in t.imported_object_paths]
def ilk(desen): f = glob.glob(desen); return f[0] if f else None
try:
    for ad, (kl, birlestir) in ESYA.items():
        d = f"{KOK}/{kl}"; h = f"{HD}/{ad}"
        fbx = ilk(d + "/*.fbx")
        sms = [a for a in fbx_al(fbx, h, birlestir) if isinstance(a, unreal.StaticMesh)]
        tx = lambda k: ilk(f"{d}/*_4K_{k}.jpg")
        metal = tx("Metalness")
        m = mi("MI_" + ad, h, {"Renk": doku(tx("BaseColor"), h, f"T_{ad}_R", "c"), "Normal": doku(tx("Normal"), h, f"T_{ad}_N", "n"),
                                "Puruz": doku(tx("Roughness"), h, f"T_{ad}_P", "l"), "AO": doku(tx("AO"), h, f"T_{ad}_AO", "l"),
                                "MetalDoku": doku(metal, h, f"T_{ad}_M", "l")}, {"Metal": 1.0 if metal else 0.0})
        for i, sm in enumerate(sms):
            for k in range(len(sm.get_editor_property("static_materials"))): sm.set_material(k, m)
            bs = sm.get_editor_property("body_setup")
            if bs: bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            bb = sm.get_bounding_box(); eal.save_loaded_asset(sm)
            log("ESYA", ad, sm.get_path_name().split(".")[0], "min", [round(v, 1) for v in (bb.min.x, bb.min.y, bb.min.z)], "max", [round(v, 1) for v in (bb.max.x, bb.max.y, bb.max.z)])
    # anahtarlık (parça başına doku seti)
    d = f"{KOK}/cc0-keys"; h = f"{HD}/Anahtarlik"
    sms = [a for a in fbx_al(ilk(d + "/**/*.fbx") or ilk(d + "/*.fbx"), h, True) if isinstance(a, unreal.StaticMesh)]
    tf = lambda n: ilk(f"{d}/**/{n}.*") or ilk(f"{d}/{n}.*")
    for sm in sms:
        for k, s in enumerate(sm.get_editor_property("static_materials")):
            slot = str(s.get_editor_property("material_slot_name"))
            p_ = "KeyRing" if "ring" in slot.lower() else ("Key1" if "1" in slot else "Key2" if "2" in slot else "Key3" if "3" in slot else "Key1")
            m = mi(f"MI_Anahtar_{p_}", h, {"Renk": doku(tf(p_ + "Albedo"), h, f"T_{p_}_R", "c"), "Normal": doku(tf(p_ + "Normal"), h, f"T_{p_}_N", "n"),
                                          "Puruz": doku(tf(p_ + "Rough"), h, f"T_{p_}_P", "l"), "MetalDoku": doku(tf(p_ + "Metal"), h, f"T_{p_}_M", "l")}, {"Metal": 1.0})
            sm.set_material(k, m); log("anahtar slot", slot, "→", p_)
        bb = sm.get_bounding_box(); eal.save_loaded_asset(sm)
        log("ESYA Anahtarlik", sm.get_path_name().split(".")[0], "boyut", [round(v, 1) for v in (bb.max.x - bb.min.x, bb.max.y - bb.min.y, bb.max.z - bb.min.z)], "minz", round(bb.min.z, 1))
    # 4K: önceki Fab dokularında 2048 sınırını kaldır
    n = 0
    for p in eal.list_assets("/Game/Uyanis/Fab", recursive=True):
        a = eal.load_asset(p)
        if isinstance(a, unreal.Texture2D) and a.get_editor_property("max_texture_size") != 0:
            a.set_editor_property("max_texture_size", 0); eal.save_loaded_asset(a); n += 1
    log("4K'ya açılan doku", n)
    # oyuncaklar: 4K atlas
    TD = "D:/Sisli-Fab/oldchildrenstoysfbx/OldChildrensToysFbx/textures/4k"; h = "/Game/Uyanis/Fab/Oyuncak"
    mo = eal.load_asset(h + "/MI_Oyuncak")
    for par, fn, tur, ad in (("BaseColor", "T_Toys_BaseColor.tga", "c", "T_Oyuncak4K_R"), ("Normal", "T_Toys_Normal.tga", "n", "T_Oyuncak4K_N"), ("ARM", "T_Toys_ORM.tga", "l", "T_Oyuncak4K_ORM")):
        t = doku(f"{TD}/{fn}", h, ad, tur)
        if tur == "n": t.set_editor_property("flip_green_channel", False); eal.save_loaded_asset(t)
        mel.set_material_instance_texture_parameter_value(mo, par, t)
    eal.save_loaded_asset(mo); log("oyuncak 4K")
    eal.save_directory("/Game/Uyanis", only_if_is_dirty=True, recursive=True); log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/yat_aktar_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
