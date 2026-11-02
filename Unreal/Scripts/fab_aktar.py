# Fab paketlerini /Game/Uyanis/Fab altına aktar + ana malzemeler.
#  M_MS        : UV'li tarama malzemesi (Renk, Normal, Puruz, AO) — Megascans mesh'leri
#  M_MS_Dunya  : dünyaya hizalı üç düzlemli (triplanar) yüzey — ölçeklenmiş kutu mimari (dikiş/esneme yok); normal dünya uzayında
#  M_MS_Dekal  : ertelenmiş dekal (leke/akıntı), opaklık haritalı
# Megascans + Poly Haven normal haritaları OpenGL (normal_kip.py ile ölçüldü) → içe aktarırken yeşil kanal çevrilir.
import unreal, os, glob, json, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary
KOK = "/Game/Uyanis"; MD = KOK + "/Malzeme"; FAB = KOK + "/Fab"
UB = "D:/Sisli-Fab/unfinished_building_high"
SADECE = os.environ.get("FAB_SADECE", "")   # "ana" → yalnız ana malzemeler
E = unreal.MaterialProperty

MESH = {  # ad: megascans kimliği
    "Moloz_Duz_A": "riuvL", "Moloz_Duz_B": "rjgmQ", "Moloz_Yigin_A": "tfxteboda", "Moloz_Yigin_B": "tgdtfg0da",
    "Beton_Parca_A": "tl0kcdmiw", "Beton_Parca_B": "tl0mbbihw", "Beton_Parca_C": "tl1gdgyhw", "Beton_Parca_D": "tmclbcpiw",
    "Beton_Parca_E": "tmclcaeiw", "Beton_Parca_F": "tmjgderjw", "Varil": "uizhacnga",
    "Merdiven_A": "uiznce1ga", "Merdiven_B": "ujcgdgifa", "Merdiven_C": "uknjfevga",
    "Kolon_A": "ujikdbrva", "Kolon_B": "ujjleixga", "Kolon_C": "ujjmecwba", "Kolon_D": "ukigcctfa", "Kolon_Genis": "ujkgddqva",
    "Kiris_A": "ujlkbd1ga", "Kiris_B": "ujonbdmfa", "Kiris_C": "ujymbbdba", "Kiris_D": "ukmifdmva",
    "Camur_Leke": "ujriaadga", "Moloz_Torba": "ukxkbesqa", "Celik_Kiris": "vgyidebaw", "Palet": "vh1icei",
    "Karton_A": "vidkbho", "Karton_B": "vjwnfiz", "Karton_C": "vjwtbd1", "Briket_A": "vk2sdis", "Briket_B": "vk2vcdl",
}
YUZEY = {
    "Beton_Kalip": "uflnbcofw", "Beton_Akinti_A": "ug3sbcady", "Beton_Akinti_B": "ugtmdgvew", "Beton_Akinti_C": "ui1obbtew",
    "Beton_Panel": "ugkkedvlw", "Beton_Koyu": "ufgnagwew", "Beton_Koyu_B": "ueydffrdy", "Zemin_Tozlu": "ugtmehro",
    "Zemin_Kaba": "ugkjec3ew", "Zemin_Kahve": "uhriddhlw", "Briket_Duvar": "ugsifevlw", "Beton_Duz": "uirleimn",
    "Beton_Demir": "uigqcejdy", "Beton_Boya": "ugiscdsew", "Siva": "uhnlfbvn",
}
DEKAL = {"Leke_A": "tdfdfebc", "Leke_B": "tdfeddkc", "Leke_C": "tdfedjwc", "Leke_D": "tdfgahvc", "Leke_E": "tdlodebc",
         "Akinti_A": "tk3jefoc", "Akinti_B": "tk3jej1c", "Akinti_C": "tk3jfbec"}

# ---------------- malzeme düğümü yardımcıları ----------------
HATALI = []
def X(m, cls, x, y, **kw):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in kw.items(): e.set_editor_property(k, v)
    return e
def L(a, ao, b, bi):
    if not mel.connect_material_expressions(a, ao, b, bi): HATALI.append(f"{a.get_name()}.{ao} → {b.get_name()}.{bi}")
def P(m, e, ao, prop):
    if not mel.connect_material_property(e, ao, prop): HATALI.append(f"{e.get_name()}.{ao} → {prop}")
def yeni(ad):
    """Var olan ana malzemeyi SILMEDEN bosaltip yeniden kurar (bagli MI'ler ebeveynini kaybetmesin)."""
    p = f"{MD}/{ad}"
    if eal.does_asset_exist(p):
        m = eal.load_asset(p); mel.delete_all_material_expressions(m)
    else:
        m = at.create_asset(ad, MD, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("used_with_nanite", True)
    return m
T2 = unreal.MaterialExpressionTextureSampleParameter2D; ST = unreal.MaterialSamplerType
def beyaz(): return unreal.load_asset("/Engine/EngineResources/WhiteSquareTexture.WhiteSquareTexture")
def beyaz_maske(): return unreal.load_asset("/Game/Sisli/Doku/T_BeyazMaske")   # dogrusal (Masks ornekleyici sRGB beyazla derlenmez)
def duznormal(): return unreal.load_asset("/Engine/EngineMaterials/DefaultNormal.DefaultNormal")
def skaler(m, ad, v, x, y): return X(m, unreal.MaterialExpressionScalarParameter, x, y, parameter_name=ad, default_value=v)
def vektor(m, ad, v, x, y): return X(m, unreal.MaterialExpressionVectorParameter, x, y, parameter_name=ad, default_value=unreal.LinearColor(*v))

def ana_ms():
    m = yeni("M_MS")
    uv = X(m, unreal.MaterialExpressionTextureCoordinate, -1700, 0)
    ol = skaler(m, "UVOlcek", 1.0, -1700, 120); uvm = X(m, unreal.MaterialExpressionMultiply, -1500, 40); L(uv, "", uvm, "A"); L(ol, "", uvm, "B")
    rk = X(m, T2, -1200, -400, parameter_name="Renk", texture=beyaz(), sampler_type=ST.SAMPLERTYPE_COLOR); L(uvm, "", rk, "UVs")
    nr = X(m, T2, -1200, 0, parameter_name="Normal", texture=duznormal(), sampler_type=ST.SAMPLERTYPE_NORMAL); L(uvm, "", nr, "UVs")
    pu = X(m, T2, -1200, 400, parameter_name="Puruz", texture=beyaz_maske(), sampler_type=ST.SAMPLERTYPE_MASKS); L(uvm, "", pu, "UVs")
    ao = X(m, T2, -1200, 800, parameter_name="AO", texture=beyaz_maske(), sampler_type=ST.SAMPLERTYPE_MASKS); L(uvm, "", ao, "UVs")
    ton = vektor(m, "Ton", (1, 1, 1, 1), -900, -550)
    aog = skaler(m, "AOGuc", 0.6, -900, 950)
    c1 = X(m, unreal.MaterialExpressionMultiply, -700, -400); L(rk, "RGB", c1, "A"); L(ton, "", c1, "B")
    aol = X(m, unreal.MaterialExpressionLinearInterpolate, -700, 850, const_a=1.0); L(ao, "R", aol, "B"); L(aog, "", aol, "Alpha")
    c2 = X(m, unreal.MaterialExpressionMultiply, -450, -350); L(c1, "", c2, "A"); L(aol, "", c2, "B")
    P(m, c2, "", E.MP_BASE_COLOR)
    pc = skaler(m, "PuruzCarpan", 1.0, -900, 500); r1 = X(m, unreal.MaterialExpressionMultiply, -700, 420); L(pu, "R", r1, "A"); L(pc, "", r1, "B")
    P(m, r1, "", E.MP_ROUGHNESS); P(m, ao, "R", E.MP_AMBIENT_OCCLUSION)
    md = X(m, T2, -1200, 1200, parameter_name="MetalDoku", texture=beyaz_maske(), sampler_type=ST.SAMPLERTYPE_MASKS); L(uvm, "", md, "UVs")
    mtl = X(m, unreal.MaterialExpressionMultiply, -700, 650); L(md, "R", mtl, "A"); L(skaler(m, "Metal", 0.0, -900, 700), "", mtl, "B")
    P(m, mtl, "", E.MP_METALLIC)   # metalik = MetalDoku.R × Metal (Megascans Metalness haritası olan eşyalar için)
    ng = skaler(m, "NormalGuc", 1.0, -900, 150)
    up = X(m, unreal.MaterialExpressionConstant3Vector, -900, 250, constant=unreal.LinearColor(0, 0, 1, 1))
    nl = X(m, unreal.MaterialExpressionLinearInterpolate, -600, 100); L(up, "", nl, "A"); L(nr, "RGB", nl, "B"); L(ng, "", nl, "Alpha")
    P(m, nl, "", E.MP_NORMAL)
    P(m, vektor(m, "Isima", (0, 0, 0, 1), -450, 1100), "", E.MP_EMISSIVE_COLOR)
    mel.recompile_material(m); eal.save_loaded_asset(m); return m

def ana_dunya():
    """Üç düzlemli dünya hizalı yüzey. Duvarda görüntü üstü = yukarı (akıntılar aşağı akar)."""
    m = yeni("M_MS_Dunya"); m.set_editor_property("tangent_space_normal", False)
    wp = X(m, unreal.MaterialExpressionWorldPosition, -2600, 0)
    ol = skaler(m, "Olcek", 300.0, -2600, 150)
    pw = X(m, unreal.MaterialExpressionDivide, -2400, 40); L(wp, "", pw, "A"); L(ol, "", pw, "B")
    def maske(src, r, g, b, x, y):
        e = X(m, unreal.MaterialExpressionComponentMask, x, y, r=r, g=g, b=b, a=False); L(src, "", e, ""); return e
    px = maske(pw, True, False, False, -2200, -200); py = maske(pw, False, True, False, -2200, 0); pz = maske(pw, False, False, True, -2200, 200)
    nz = X(m, unreal.MaterialExpressionMultiply, -2000, 200, const_b=-1.0); L(pz, "", nz, "A")   # -z: görüntü üstü yukarı
    def ekle(a, b, x, y):
        e = X(m, unreal.MaterialExpressionAppendVector, x, y); L(a, "", e, "A"); L(b, "", e, "B"); return e
    uvX = ekle(py, nz, -1800, -300); uvY = ekle(px, nz, -1800, 0); uvZ = ekle(px, py, -1800, 300)
    # ağırlıklar: |N|^4 normalize
    vn = X(m, unreal.MaterialExpressionVertexNormalWS, -2200, 600)
    ab = X(m, unreal.MaterialExpressionAbs, -2000, 600); L(vn, "", ab, "")
    pw4 = X(m, unreal.MaterialExpressionPower, -1850, 600, const_exponent=4.0); L(ab, "", pw4, "Base")
    bir = X(m, unreal.MaterialExpressionConstant3Vector, -1850, 750, constant=unreal.LinearColor(1, 1, 1, 1))
    top = X(m, unreal.MaterialExpressionDotProduct, -1700, 700); L(pw4, "", top, "A"); L(bir, "", top, "B")
    w = X(m, unreal.MaterialExpressionDivide, -1550, 620); L(pw4, "", w, "A"); L(top, "", w, "B")
    wx = maske(w, True, False, False, -1400, 560); wy = maske(w, False, True, False, -1400, 640); wz = maske(w, False, False, True, -1400, 720)
    def uc(par, tex, styp, y0, kanal):
        s = []
        for i, uv in enumerate((uvX, uvY, uvZ)):
            e = X(m, T2, -1500, y0 + i * 260, parameter_name=par, texture=tex, sampler_type=styp); L(uv, "", e, "UVs"); s.append(e)
        return s
    def karis(s, kanal, x, y):   # s[0]*wx + s[1]*wy + s[2]*wz
        terimler = []
        for i, ww in enumerate((wx, wy, wz)):
            e = X(m, unreal.MaterialExpressionMultiply, x, y + i * 80); L(s[i], kanal, e, "A"); L(ww, "", e, "B"); terimler.append(e)
        a1 = X(m, unreal.MaterialExpressionAdd, x + 150, y); L(terimler[0], "", a1, "A"); L(terimler[1], "", a1, "B")
        a2 = X(m, unreal.MaterialExpressionAdd, x + 300, y); L(a1, "", a2, "A"); L(terimler[2], "", a2, "B")
        return a2
    rk = uc("Renk", beyaz(), ST.SAMPLERTYPE_COLOR, -1400, "RGB")
    rgb = karis(rk, "RGB", -1100, -1300)
    ton = vektor(m, "Ton", (1, 1, 1, 1), -800, -1450)
    # büyük ölçekli kir/ton oynaması (tekrar desenini kırar)
    kir = X(m, unreal.MaterialExpressionNoise, -1100, -1550, scale=0.0012, levels=3, output_min=0.72, output_max=1.08, quality=1)   # Position boş → mutlak dünya konumu
    c1 = X(m, unreal.MaterialExpressionMultiply, -650, -1350); L(rgb, "", c1, "A"); L(ton, "", c1, "B")
    c2 = X(m, unreal.MaterialExpressionMultiply, -500, -1350); L(c1, "", c2, "A"); L(kir, "", c2, "B")
    P(m, c2, "", E.MP_BASE_COLOR)
    pu = uc("Puruz", beyaz_maske(), ST.SAMPLERTYPE_MASKS, -600, "R")
    pr = karis(pu, "R", -1100, -600)
    pc = skaler(m, "PuruzCarpan", 1.0, -800, -500); r1 = X(m, unreal.MaterialExpressionMultiply, -650, -600); L(pr, "", r1, "A"); L(pc, "", r1, "B")
    P(m, r1, "", E.MP_ROUGHNESS)
    P(m, skaler(m, "Metal", 0.0, -650, -420), "", E.MP_METALLIC)
    # normal: N + wx*(0, nx, -ny) + wy*(nx, 0, -ny) + wz*(nx, ny, 0)   (DirectX: +y = görüntüde aşağı = v yönü)
    nm = uc("Normal", duznormal(), ST.SAMPLERTYPE_NORMAL, 200, "RGB")
    ng = skaler(m, "NormalGuc", 1.0, -1300, 1000)
    sifir = X(m, unreal.MaterialExpressionConstant, -1300, 1100, r=0.0)
    parca = []
    for i, (s, ww) in enumerate(zip(nm, (wx, wy, wz))):
        x_ = maske(s, True, False, False, -1250, 200 + i * 260); y_ = maske(s, False, True, False, -1250, 260 + i * 260)
        xg = X(m, unreal.MaterialExpressionMultiply, -1100, 200 + i * 260); L(x_, "", xg, "A"); L(ng, "", xg, "B")
        yg = X(m, unreal.MaterialExpressionMultiply, -1100, 260 + i * 260); L(y_, "", yg, "A"); L(ng, "", yg, "B")
        yn = X(m, unreal.MaterialExpressionMultiply, -980, 260 + i * 260, const_b=-1.0); L(yg, "", yn, "A")
        if i == 0: v = ekle(ekle(sifir, xg, -900, 200), yn, -800, 200)       # (0, nx, -ny)
        elif i == 1: v = ekle(ekle(xg, sifir, -900, 460), yn, -800, 460)     # (nx, 0, -ny)
        else: v = ekle(ekle(xg, yg, -900, 720), sifir, -800, 720)            # (nx, ny, 0)
        t = X(m, unreal.MaterialExpressionMultiply, -650, 200 + i * 260); L(v, "", t, "A"); L(ww, "", t, "B"); parca.append(t)
    s1 = X(m, unreal.MaterialExpressionAdd, -500, 300); L(vn, "", s1, "A"); L(parca[0], "", s1, "B")
    s2 = X(m, unreal.MaterialExpressionAdd, -400, 400); L(s1, "", s2, "A"); L(parca[1], "", s2, "B")
    s3 = X(m, unreal.MaterialExpressionAdd, -300, 500); L(s2, "", s3, "A"); L(parca[2], "", s3, "B")
    nn = X(m, unreal.MaterialExpressionNormalize, -150, 500); L(s3, "", nn, "")
    P(m, nn, "", E.MP_NORMAL)
    P(m, vektor(m, "Isima", (0, 0, 0, 1), -300, 900), "", E.MP_EMISSIVE_COLOR)
    mel.recompile_material(m); eal.save_loaded_asset(m); return m

def ana_dekal():
    m = yeni("M_MS_Dekal")
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    rk = X(m, T2, -900, -300, parameter_name="Renk", texture=beyaz(), sampler_type=ST.SAMPLERTYPE_COLOR)
    op = X(m, T2, -900, 100, parameter_name="Opaklik", texture=beyaz_maske(), sampler_type=ST.SAMPLERTYPE_MASKS)
    ton = vektor(m, "Ton", (1, 1, 1, 1), -600, -450)
    c1 = X(m, unreal.MaterialExpressionMultiply, -400, -300); L(rk, "RGB", c1, "A"); L(ton, "", c1, "B")
    P(m, c1, "", E.MP_BASE_COLOR)
    og = skaler(m, "OpaklikGuc", 1.0, -600, 250); o1 = X(m, unreal.MaterialExpressionMultiply, -400, 120); L(op, "R", o1, "A"); L(og, "", o1, "B")
    P(m, o1, "", E.MP_OPACITY)
    P(m, skaler(m, "Puruz", 0.7, -400, 350), "", E.MP_ROUGHNESS)
    mel.recompile_material(m); eal.save_loaded_asset(m); return m

# ---------------- içe aktarma ----------------
TEXC = {}
def doku(dosya, hedef, ad, tur):
    """tur: c=renk(sRGB), n=normal(OpenGL→çevir), l=doğrusal maske"""
    if not dosya or not os.path.exists(dosya): return None
    ap = f"{hedef}/{ad}"
    if ap in TEXC: return TEXC[ap]
    if not eal.does_asset_exist(ap):
        t = unreal.AssetImportTask(); t.filename = dosya; t.destination_path = hedef; t.destination_name = ad
        t.automated = True; t.save = False; t.replace_existing = True; at.import_asset_tasks([t])
    a = eal.load_asset(ap)
    if a is None: log("DOKU YOK", dosya); return None
    if tur == "n":
        a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP); a.set_editor_property("srgb", False)
        a.set_editor_property("flip_green_channel", True)
    elif tur == "l":
        a.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS); a.set_editor_property("srgb", False)
    a.set_editor_property("max_texture_size", 0)   # 4K (sınırsız) — kullanıcı: "4k olsun"
    eal.save_loaded_asset(a); TEXC[ap] = a; return a

def mi(ad, ana, hedef, doku_par, skal=None, vek=None):
    p = f"{hedef}/{ad}"
    if eal.does_asset_exist(p): eal.delete_asset(p)
    m = at.create_asset(ad, hedef, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(m, ana)
    for k, v in doku_par.items():
        if v: mel.set_material_instance_texture_parameter_value(m, k, v)
    for k, v in (skal or {}).items(): mel.set_material_instance_scalar_parameter_value(m, k, v)
    for k, v in (vek or {}).items(): mel.set_material_instance_vector_parameter_value(m, k, unreal.LinearColor(*v))
    eal.save_loaded_asset(m); return m

def nanite_ac(sm):
    try:
        ses = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        ns = sm.get_editor_property("nanite_settings"); ns.set_editor_property("enabled", True)
        ses.set_nanite_settings(sm, ns, apply_changes=True); return True
    except Exception as e:
        log("nanite ayarlanamadı", sm.get_name(), str(e)[:120]); return False

def fbx_al(dosya, hedef, ad=None, birlestir=True):
    t = unreal.AssetImportTask(); t.filename = dosya; t.destination_path = hedef; t.automated = True; t.save = False; t.replace_existing = True
    if ad: t.destination_name = ad
    ui = unreal.FbxImportUI(); ui.import_mesh = True; ui.import_as_skeletal = False; ui.import_materials = False; ui.import_textures = False
    ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    ui.static_mesh_import_data.combine_meshes = birlestir; ui.static_mesh_import_data.auto_generate_collision = False
    ui.static_mesh_import_data.generate_lightmap_u_vs = False
    t.options = ui; at.import_asset_tasks([t])
    return [eal.load_asset(p) for p in t.imported_object_paths]

def karmasik_carpisma(sm):
    bs = sm.get_editor_property("body_setup")
    if bs: bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)

try:
    M = ana_ms(); MW = ana_dunya(); MDk = ana_dekal()
    log("ana malzemeler", "bağlantı hataları:", HATALI if HATALI else "yok")
    if SADECE != "ana":
        boyut = {}
        for ad, kid in MESH.items():
            d = f"{UB}/{kid}"; h = f"{FAB}/UB/{ad}"
            sm = eal.load_asset(f"{h}/SM_{ad}") if eal.does_asset_exist(f"{h}/SM_{ad}") else None
            if sm is None:
                r = [a for a in fbx_al(f"{d}/{kid}.fbx", h, "SM_" + ad) if isinstance(a, unreal.StaticMesh)]
                sm = r[0] if r else None
            if sm is None: log("MESH ALINAMADI", ad); continue
            mt = mi("MI_" + ad, M, h, {"Renk": doku(f"{d}/{kid}_4K_BaseColor.jpg", h, "T_" + ad + "_R", "c"),
                                       "Normal": doku(f"{d}/{kid}_4K_Normal.jpg", h, "T_" + ad + "_N", "n"),
                                       "Puruz": doku(f"{d}/{kid}_4K_Roughness.jpg", h, "T_" + ad + "_P", "l"),
                                       "AO": doku(f"{d}/{kid}_4K_AO.jpg", h, "T_" + ad + "_AO", "l")})
            for i in range(len(sm.get_editor_property("static_materials"))): sm.set_material(i, mt)
            karmasik_carpisma(sm); nanite_ac(sm)
            bb = sm.get_bounding_box(); boyut[ad] = [round(bb.min.x, 1), round(bb.min.y, 1), round(bb.min.z, 1), round(bb.max.x, 1), round(bb.max.y, 1), round(bb.max.z, 1)]
            eal.save_loaded_asset(sm); log("MESH", ad, boyut[ad])
        for ad, kid in YUZEY.items():
            d = f"{UB}/{kid}"; h = f"{FAB}/Yuzey/{ad}"
            mi("MI_" + ad, MW, h, {"Renk": doku(f"{d}/{kid}_4K_Albedo.jpg", h, "T_" + ad + "_R", "c"),
                                   "Normal": doku(f"{d}/{kid}_4K_Normal.jpg", h, "T_" + ad + "_N", "n"),
                                   "Puruz": doku(f"{d}/{kid}_4K_Roughness.jpg", h, "T_" + ad + "_P", "l")})
            log("YUZEY", ad)
        for ad, kid in DEKAL.items():
            d = f"{UB}/{kid}"; h = f"{FAB}/Dekal/{ad}"
            mi("MI_" + ad, MDk, h, {"Renk": doku(f"{d}/{kid}_4K_Albedo.jpg", h, "T_" + ad + "_R", "c"),
                                    "Opaklik": doku(f"{d}/{kid}_4K_Opacity.jpg", h, "T_" + ad + "_O", "l")})
            log("DEKAL", ad)
        # oyuncaklar (tek doku atlası, ORM = AO/Pürüz/Metal → eski M_Sisli 'ARM' ile aynı düzen; normal UE biçiminde)
        TD = "D:/Sisli-Fab/oldchildrenstoysfbx/OldChildrensToysFbx"; h = f"{FAB}/Oyuncak"
        oy = [a for a in fbx_al(f"{TD}/meshes/ChildrensToys.fbx", h, None, birlestir=False) if isinstance(a, unreal.StaticMesh)]
        tr = doku(f"{TD}/textures/2k/T_Toys_BaseColor.tga", h, "T_Oyuncak_R", "c")
        tn = doku(f"{TD}/textures/2k/T_Toys_Normal.tga", h, "T_Oyuncak_N", "n")
        tn.set_editor_property("flip_green_channel", False); eal.save_loaded_asset(tn)   # oyun-hazır paket: DirectX
        to = doku(f"{TD}/textures/2k/T_Toys_ORM.tga", h, "T_Oyuncak_ORM", "l")
        MS = eal.load_asset("/Game/Sisli/Malzeme/M_Sisli")
        mo = mi("MI_Oyuncak", MS, h, {"BaseColor": tr, "Normal": tn, "ARM": to})
        for sm in oy:
            for i in range(len(sm.get_editor_property("static_materials"))): sm.set_material(i, mo)
            karmasik_carpisma(sm); bb = sm.get_bounding_box()
            eal.save_loaded_asset(sm); log("OYUNCAK", sm.get_name(), [round(v, 1) for v in (bb.max.x - bb.min.x, bb.max.y - bb.min.y, bb.max.z - bb.min.z)])
        # ranza (glTF, kendi malzemeleriyle)
        t = unreal.AssetImportTask(); t.filename = "D:/Sisli-Fab/bunk_bed/bunk_bed.glb"; t.destination_path = f"{FAB}/Ranza"; t.automated = True; t.save = False; t.replace_existing = True
        at.import_asset_tasks([t])
        for p in t.imported_object_paths:
            a = eal.load_asset(p)
            if isinstance(a, unreal.StaticMesh):
                karmasik_carpisma(a); bb = a.get_bounding_box(); eal.save_loaded_asset(a)
                log("RANZA", a.get_path_name(), [round(v, 1) for v in (bb.min.x, bb.min.y, bb.min.z, bb.max.x, bb.max.y, bb.max.z)])
            else: log("RANZA öğe", a.get_class().get_name() if a else None, p)
        json.dump(boyut, open("C:/Users/Onur/Sisli/Unreal/Scripts/fab_boyut.json", "w"), indent=1)
    eal.save_directory(KOK, only_if_is_dirty=True, recursive=True)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
log("bağlantı hataları:", HATALI)
open("C:/Users/Onur/Sisli/Unreal/Scripts/fab_aktar_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
