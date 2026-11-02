# L_Uyanis — açılış: "Yalnız uyanış". Bölüm 1: Yatakhane (distopik megayapının beton koğuşu).
# Kurallar (kullanıcı geri bildirimi): her model sınır kutusundan zemine oturtulur (havada/gömük yok), görünür eş düzlemli yüzey yok,
# yürüme yolunda çarpışmalı moloz yok (yığınların altında gizli düz basamak), set kapalı: pencereden görünen yalnız sis/ışık.
import unreal, json, math, os, random, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary; at = unreal.AssetToolsHelpers.get_asset_tools()
MAP = "/Game/Uyanis/Maps/L_Uyanis"; FAB = "/Game/Uyanis/Fab"; SMI = "/Game/Uyanis/Sahne"
V = lambda x, y, z: unreal.Vector(x, y, z)
R = lambda pitch=0, yaw=0, roll=0: unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)
def sset(o, k, v):
    try: o.set_editor_property(k, v)
    except Exception as e: OUT.append("ÖZELLİK YOK %s.%s: %s" % (type(o).__name__, k, str(e)[:90]))

try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if eal.does_asset_exist(MAP): eal.delete_asset(MAP)
    if not les.new_level(MAP): raise RuntimeError("new_level başarısız")
    KUP = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    M_MS = eal.load_asset("/Game/Uyanis/Malzeme/M_MS")
    def bpcls(n): a = eal.load_asset("/Game/Sisli/Mekanik/" + n); return a.generated_class() if a else None

    # ---------- malzeme örnekleri (sahneye özel ton/ölçek) ----------
    MIC = {}
    def smi(ad, ebeveyn, skal=None, vek=None):
        if ad in MIC: return MIC[ad]
        p = f"{SMI}/MI_{ad}"
        if eal.does_asset_exist(p): eal.delete_asset(p)
        m = at.create_asset("MI_" + ad, SMI, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(m, ebeveyn)
        for k, v in (skal or {}).items(): mel.set_material_instance_scalar_parameter_value(m, k, v)
        for k, v in (vek or {}).items(): mel.set_material_instance_vector_parameter_value(m, k, unreal.LinearColor(*v, 1) if len(v) == 3 else unreal.LinearColor(*v))
        eal.save_loaded_asset(m); MIC[ad] = m; return m
    def yz(ad): return eal.load_asset(f"{FAB}/Yuzey/{ad}/MI_{ad}")
    ZEMIN = smi("Yat_Zemin", yz("Zemin_Tozlu"), {"Olcek": 260.0, "PuruzCarpan": 1.0}, {"Ton": (0.42, 0.43, 0.45)})
    DUVAR = smi("Yat_Duvar", yz("Beton_Akinti_B"), {"Olcek": 320.0}, {"Ton": (0.40, 0.42, 0.44)})
    BANT = smi("Yat_Bant", yz("Beton_Boya"), {"Olcek": 220.0}, {"Ton": (0.20, 0.27, 0.26)})       # kurum yeşili-gri alt bant
    TAVAN = smi("Yat_Tavan", yz("Beton_Kalip"), {"Olcek": 300.0}, {"Ton": (0.30, 0.31, 0.33)})
    KIRISM = smi("Yat_Kiris", yz("Beton_Panel"), {"Olcek": 200.0}, {"Ton": (0.33, 0.34, 0.36)})
    METAL = smi("Metal_Koyu", M_MS, {"Metal": 0.7, "PuruzCarpan": 0.45}, {"Ton": (0.035, 0.036, 0.04)})
    FLOR_OLU = smi("Floresan_Olu", M_MS, {"PuruzCarpan": 0.3}, {"Ton": (0.25, 0.27, 0.28)})
    FLOR_CANLI = smi("Floresan_Canli", M_MS, {"PuruzCarpan": 0.3}, {"Ton": (0.8, 0.85, 0.85), "Isima": (5.5, 7.0, 7.4)})
    # ranza: glTF dokulari (0 renk, 1 metal/puruz, 2 normal - glTF normali OpenGL -> cevir), kendi MI'miz
    RD = "/Game/Uyanis/Fab/Ranza/bunk_bed/Textures/bunk_bed_texture_"
    t2 = eal.load_asset(RD + "2")
    if not t2.get_editor_property("flip_green_channel"): t2.set_editor_property("flip_green_channel", True); eal.save_loaded_asset(t2)
    RANZA = smi("Ranza", M_MS, {"PuruzCarpan": 0.62, "AOGuc": 0.0}, {"Ton": (0.62, 0.63, 0.65)})
    mel.set_material_instance_texture_parameter_value(RANZA, "Renk", eal.load_asset(RD + "0")); mel.set_material_instance_texture_parameter_value(RANZA, "Normal", t2); eal.save_loaded_asset(RANZA)
    GOK = smi("Pencere_Sis", M_MS, {"PuruzCarpan": 1.0}, {"Ton": (0, 0, 0), "Isima": (0.05, 0.11, 0.14)})

    # ---------- yerleştirme yardımcıları ----------
    KATILAR = []   # (ad, min, max) — mimari kutular (çakışma denetimi için)
    def spawn(cls, loc=V(0, 0, 0), rot=R(), etiket=None):
        a = eas.spawn_actor_from_class(cls, loc, rot)
        if a is None: raise RuntimeError("spawn başarısız %s" % cls)
        if etiket: a.set_actor_label(etiket)
        return a
    def kutu(etiket, x0, x1, y0, y1, z0, z1, mt, golge=True, carpisma=True, gizli=False):
        a = spawn(unreal.StaticMeshActor, V((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), R(), etiket)
        c = a.static_mesh_component; c.set_static_mesh(KUP); c.set_material(0, mt)
        a.set_actor_scale3d(V((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0))
        sset(c, "cast_shadow", golge)
        if not carpisma: c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        if gizli:
            a.set_actor_hidden_in_game(True); sset(c, "cast_shadow", False)
            c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA, unreal.CollisionResponseType.ECR_IGNORE)
            c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY, unreal.CollisionResponseType.ECR_IGNORE)
        else:
            KATILAR.append((etiket, (min(x0, x1), min(y0, y1), min(z0, z1)), (max(x0, x1), max(y0, y1), max(z0, z1))))
        return a
    SMC = {}
    def mesh(ad):
        if ad not in SMC:
            for p in (f"{FAB}/UB/{ad}/SM_{ad}", f"{FAB}/Oyuncak/{ad}", f"{FAB}/Ranza/bunk_bed/StaticMeshes/{ad}"):
                if eal.does_asset_exist(p): SMC[ad] = eal.load_asset(p); break
            else: raise RuntimeError("mesh yok " + ad)
        return SMC[ad]
    PROPS = []
    def koy(ad, x, y, yaw=0.0, zemin=0.0, gomme=1.0, olcek=1.0, carpisma="karmasik", etiket=None, pitch=0.0, roll=0.0, malzeme=None):
        """Sınır kutusunun tabanı zemine (zemin - gomme cm) oturur. carpisma: karmasik | yok | engel"""
        sm = mesh(ad); bb = sm.get_bounding_box()
        s = olcek if isinstance(olcek, (tuple, list)) else (olcek, olcek, olcek)
        z = zemin - bb.min.z * s[2] - gomme
        a = spawn(unreal.StaticMeshActor, V(x, y, z), R(pitch=pitch, yaw=yaw, roll=roll), etiket or ad)
        c = a.static_mesh_component; c.set_static_mesh(sm); a.set_actor_scale3d(V(*s))
        if ad == "bunk_bed":
            for i in range(c.get_num_materials()): c.set_material(i, RANZA)
        if malzeme is not None:
            for i in range(c.get_num_materials()): c.set_material(i, malzeme)
        if carpisma == "yok": c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA, unreal.CollisionResponseType.ECR_IGNORE)
        # dönmüş sınır (XY) — çakışma denetimi için
        cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)); xs, ys = [], []
        for bx in (bb.min.x * s[0], bb.max.x * s[0]):
            for by in (bb.min.y * s[1], bb.max.y * s[1]):
                xs.append(x + bx * cy - by * sy); ys.append(y + bx * sy + by * cy)
        PROPS.append((etiket or ad, (min(xs), min(ys), z + bb.min.z * s[2]), (max(xs), max(ys), z + bb.max.z * s[2]), carpisma))
        return a
    def moloz_yigini(ad, x, y, yaw=0.0, olcek=1.0, zemin=0.0):
        """Görünen yığın çarpışmasız; altında gizli, düz üstlü basamak (çocuk takılmadan çıkar/iner)."""
        a = koy(ad, x, y, yaw, zemin, 3.0, olcek, "yok")
        sm = mesh(ad); bb = sm.get_bounding_box(); s = olcek
        h = (bb.max.z - bb.min.z) * s * 0.55
        w = (bb.max.x - bb.min.x) * s * 0.55; d = (bb.max.y - bb.min.y) * s * 0.55
        b = spawn(unreal.StaticMeshActor, V(x, y, zemin + h / 2), R(yaw=yaw), ad + "_Basamak")
        bc = b.static_mesh_component; bc.set_static_mesh(KUP); b.set_actor_scale3d(V(w / 100, d / 100, h / 100))
        b.set_actor_hidden_in_game(True); sset(bc, "cast_shadow", False)
        bc.set_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA, unreal.CollisionResponseType.ECR_IGNORE)
        # projektör siperi: yığının %85 yüksekliğinde, yalnız görünürlük kanalını keser (yürümeyi etkilemez)
        sh = (bb.max.z - bb.min.z) * s * 0.85
        g_ = spawn(unreal.StaticMeshActor, V(x, y, zemin + sh / 2), R(yaw=yaw), ad + "_Siper")
        gc = g_.static_mesh_component; gc.set_static_mesh(KUP); g_.set_actor_scale3d(V(w * 0.9 / 100, d * 0.9 / 100, sh / 100))
        g_.set_actor_hidden_in_game(True); sset(gc, "cast_shadow", False)
        gc.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
        gc.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_IGNORE)
        gc.set_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY, unreal.CollisionResponseType.ECR_BLOCK)
        return a
    def dekal(ad, x, y, z, boyut, yaw=0.0, zemin=True, guc=1.0):
        mt = eal.load_asset(f"{FAB}/Dekal/{ad}/MI_{ad}")
        if guc != 1.0: mt = smi(f"Dekal_{ad}_{int(guc * 100)}", mt, {"OpaklikGuc": guc})
        d = spawn(unreal.DecalActor, V(x, y, z), R(pitch=-90, yaw=yaw) if zemin else R(yaw=yaw), "Dekal_" + ad)
        dc = d.decal; dc.set_decal_material(mt); sset(dc, "decal_size", V(*boyut))
        return d
    def isik(cls, etiket, loc, rot=R(), **kw):
        a = spawn(cls, loc, rot, etiket); c = a.get_component_by_class(unreal.LightComponent)
        sset(c, "intensity_units", unreal.LightUnits.CANDELAS) if cls is not unreal.DirectionalLight else None
        for k, v in kw.items(): sset(c, k, v)
        return a

    # ================= BÖLÜM 1: YATAKHANE =================
    W, LEN, H = 900.0, 2600.0, 340.0
    kutu("Zemin", -30, W + 30, -30, LEN + 30, -30, 0, ZEMIN)
    kutu("Tavan", -30, W + 30, -30, LEN + 30, H, H + 40, TAVAN)
    kutu("SolDuvar", -30, 0, 0, LEN, 0, H + 20, DUVAR)
    kutu("ArkaDuvar", -30, W + 30, -30, 0, 0, H + 20, DUVAR)
    # sağ duvar: yüksek şerit pencereler (parmaklıklı) — ay ışığı buradan girer
    PEN = [(430.0, 870.0), (1230.0, 1670.0), (2030.0, 2470.0)]; PZ0, PZ1 = 225.0, 305.0
    kutu("SagDuvar_Alt", W, W + 30, 0, LEN, 0, PZ0, DUVAR)
    kutu("SagDuvar_Ust", W, W + 30, 0, LEN, PZ1, H + 20, DUVAR)
    y = 0.0
    for i, (a0, a1) in enumerate(PEN + [(LEN, LEN)]):
        if a0 > y: kutu(f"SagDuvar_Ayak{i}", W, W + 30, y, a0, PZ0, PZ1, DUVAR)
        y = a1
    for (a0, a1) in PEN:
        yy = a0 + 10
        while yy < a1 - 5:
            kutu("Parmaklik", W + 12, W + 16, yy, yy + 3, PZ0, PZ1, METAL); yy += 22
        kutu("PencereSis", W + 600, W + 602, a0 - 400, a1 + 400, PZ0 - 300, PZ1 + 400, GOK, golge=False, carpisma=False)   # dışarıda aydınlık sis
    # kâğıt dokuları (kurallar, Ela'nın çizimi): SourceArt/Kagit → /Game/Uyanis/Kagit
    for fn in ("T_Kurallar", "T_ElaCizim"):
        if not eal.does_asset_exist(f"/Game/Uyanis/Kagit/{fn}"):
            t = unreal.AssetImportTask(); t.filename = f"C:/Users/Onur/Sisli/Unreal/SourceArt/Kagit/{fn}.png"; t.destination_path = "/Game/Uyanis/Kagit"
            t.automated = True; t.save = True; t.replace_existing = True; at.import_asset_tasks([t])
    # ---------- yatakhane eşyaları (Megascans 4K) ----------
    YAT = "/Game/Uyanis/Fab/Yat"
    def ym(ad): return eal.load_asset(f"{YAT}/{ad}/" + {"Floresan": "Fluorescent_Ceiling_Lamp_vidrear_High", "Sarkit": "Metal_Pendant_Light_vgyide1aw_High",
                                                       "Defter": "Old_Book_wldocam_High", "Tabure": "Old_Metal_Stool_ukknbeyaw_High", "Sandalye": "Dirty_Metal_Chair_ukikdggbw_High",
                                                       "Dolap": "Rusty_Metal_Cabinet_vjhledeaw_High", "Masa": "Wooden_Table_With_Drawer_vfvndhsga_High",
                                                       "KafesLamba": "Rusty_Bulkhead_Light_vgyidfpaw_High", "Anahtarlik": "Keys"}[ad])
    for k_ in ("Floresan", "Sarkit", "Defter", "Tabure", "Sandalye", "Dolap", "Masa", "KafesLamba", "Anahtarlik"): SMC[k_] = ym(k_)
    def mesh_at(ad, x, y, z, rot=R(), olcek=1.0, etiket=None, carpisma=True, golge=True):
        """Sınır kutusu hesabı olmadan, verilen dönüş/konumda (asılı/yatık eşyalar)."""
        a = spawn(unreal.StaticMeshActor, V(x, y, z), rot, etiket or ad); c = a.static_mesh_component; c.set_static_mesh(mesh(ad))
        a.set_actor_scale3d(V(olcek, olcek, olcek) if not isinstance(olcek, tuple) else V(*olcek)); sset(c, "cast_shadow", golge)
        if not carpisma: c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA, unreal.CollisionResponseType.ECR_IGNORE)
        return a
    def kagit(et, doku_yol, x, y, z, nx, ny, gen, yuk):
        """Duvara/dolap kapağına kâğıt: normal (nx, ny) yönüne bakar, görüntü dik ve okunur."""
        t = eal.load_asset(doku_yol)
        m = smi("Kagit_" + et, M_MS, {"PuruzCarpan": 0.85, "AOGuc": 0.0}, {"Ton": (0.6, 0.58, 0.55)}); mel.set_material_instance_texture_parameter_value(m, "Renk", t); eal.save_loaded_asset(m)
        n = V(nx, ny, 0); sag = V(ny, -nx, 0) * -1.0   # bakan kişinin sağı = (-n) × yukarı
        rot = unreal.MathLibrary.make_rotation_from_axes(sag * -1.0, V(0, 0, -1), n)   # (sag, yukarı) 180° ters çıkıyordu
        a = spawn(unreal.StaticMeshActor, V(x, y, z), rot, et); c = a.static_mesh_component
        c.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Plane.Plane")); c.set_material(0, m); a.set_actor_scale3d(V(gen / 100.0, yuk / 100.0, 1.0))
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); sset(c, "cast_shadow", False)
        return a
    def incele(et, x, y, z, satirlar, yaricap=140.0, sureler=(4.5, 5.0), al=None):
        b = spawn(bpcls("BP_Incele"), V(x, y, z), R(), "Incele_" + et)
        for i, k in enumerate(satirlar[:3]): sset(b, f"Satir{i + 1}", eal.load_asset(f"/Game/Uyanis/Yazi/SW_{k}"))
        sset(b, "Yaricap", yaricap); sset(b, "Sure1", sureler[0]); sset(b, "Sure2", sureler[1])
        if al is not None: sset(b, "Al", True); sset(b, "AlinanAktor", al)
        if os.environ.get("UY_YURU"): sset(b, "TestOto", True)
        return b
    # cam (bakıcı odası pencereleri): ince, yarı saydam, parlak
    cp = SMI + "/M_Cam"
    if eal.does_asset_exist(cp): eal.delete_asset(cp)
    CAMM = at.create_asset("M_Cam", SMI, unreal.Material, unreal.MaterialFactoryNew())
    CAMM.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    for (prop, val) in ((unreal.MaterialProperty.MP_BASE_COLOR, unreal.LinearColor(0.02, 0.025, 0.03, 1)),):
        e_ = mel.create_material_expression(CAMM, unreal.MaterialExpressionConstant3Vector, -300, 0); e_.set_editor_property("constant", val); mel.connect_material_property(e_, "", prop)
    for (prop, val, yy_) in ((unreal.MaterialProperty.MP_OPACITY, 0.16, 120), (unreal.MaterialProperty.MP_ROUGHNESS, 0.06, 220), (unreal.MaterialProperty.MP_SPECULAR, 0.6, 320)):
        e_ = mel.create_material_expression(CAMM, unreal.MaterialExpressionConstant, -300, yy_); e_.set_editor_property("r", val); mel.connect_material_property(e_, "", prop)
    mel.recompile_material(CAMM); eal.save_loaded_asset(CAMM)
    SIVA = smi("Bakici_Duvar", yz("Beton_Boya"), {"Olcek": 180.0}, {"Ton": (0.30, 0.36, 0.34)})

    # ---------- ön duvar: çift kanatlı kapı (Megascans), üstünde kafesli kırmızı lamba ----------
    KX0, KX1, KZ = 413.0, 567.0, 223.0
    kutu("OnDuvar_Sol", -30, KX0, LEN, LEN + 30, 0, H + 20, DUVAR)
    kutu("OnDuvar_Sag", KX1, W + 30, LEN, LEN + 30, 0, H + 20, DUVAR)
    kutu("OnDuvar_Ust", KX0, KX1, LEN, LEN + 30, KZ, H + 20, DUVAR)
    # alt bant (2 cm önde: eş düzlemli değil)
    for (et, x0, x1, y0, y1) in (("Bant_Sol", 0, 2, 0, LEN), ("Bant_Sag", W - 2, W, 0, LEN), ("Bant_Arka", 0, W, 0, 2),
                                 ("Bant_OnSol", 0, KX0 - 6, LEN - 2, LEN), ("Bant_OnSag", KX1 + 6, 605, LEN - 2, LEN)):
        kutu(et, x0, x1, y0, y1, 0, 115, BANT)
    # tavan kirişleri (üstü döşemeye gömülü → görünür ek yeri yok)
    yy = 160.0
    while yy < LEN:
        kutu("TavanKiris", 0, W, yy - 18, yy + 18, H - 38, H + 6, KIRISM); yy += 325.0
    # ---------- ranzalar (sağda biri eksik: sökülmüş yatak izi; sağ öndeki yerine bakıcı odası) ----------
    RY = [270.0, 610.0, 950.0, 1290.0, 1630.0, 1970.0, 2310.0]
    for i, ry in enumerate(RY):
        koy("bunk_bed", 104.0, ry, 0.0, 0.0, 0.5, etiket=f"Ranza_Sol{i}")
        if i not in (4, 6):
            koy("bunk_bed", W - (114.0 if i == 2 else 104.0), ry + (35.0 if i == 2 else 0.0), 180.0 + (7.0 if i == 2 else 0.0), 0.0, 0.5, etiket=f"Ranza_Sag{i}")
    dekal("Leke_C", W - 110, RY[4], 2, (4, 120, 90), 0.0, guc=0.8)   # eksik yatağın izi
    # ---------- dolaplar: ranza aralarında, sırtı duvarda ----------
    DOL_YAW = float(os.environ.get("UY_DOLAPYAW", "-90"))
    for i, gy in enumerate((440.0, 780.0, 1120.0, 1460.0, 1800.0, 2140.0)):
        koy("Dolap", 32.0, gy, DOL_YAW + (2.5 if i % 2 else -1.5), 0.0, 0.3, etiket=f"Dolap_Sol{i}")
    for i, gy in enumerate((440.0, 1120.0)):
        koy("Dolap", W - 32.0, gy, DOL_YAW + 180.0 + (1.5 if i else -2.0), 0.0, 0.3, etiket=f"Dolap_Sag{i}")
    # Ela'nın dolabı (Sol0, y=440): kapağında çizimi
    kagit("Ela_Cizim", "/Game/Uyanis/Kagit/T_ElaCizim", 60.5, 440.0, 128.0, 1.0, 0.0, 34.0, 24.0)
    # ---------- kardeşinin ve çocuğun köşesi ----------
    BX, BY = 230.0, 470.0   # tavşan: Ela'nın ranzası (Sol1) ile Sol0 arası, sarkıt lambanın ışık havuzunda
    tb = mesh("SM_ToyBunny").get_bounding_box()
    spawn(bpcls("BP_Oyuncak"), V(BX, BY, -tb.min.z - 0.3), R(yaw=205), "Tavsan")   # alınabilir (BP_Oyuncak)
    koy("SM_ToyCube_01a", 205.0, 540.0, 20.0, 0.0, 0.2, carpisma="yok"); koy("SM_ToyCube_02a", 262.0, 418.0, -35.0, 0.0, 0.2, carpisma="yok")
    koy("SM_Ball", 150.0, 760.0, 0.0, 0.0, 0.3, carpisma="yok")
    koy("Tabure", 265.0, 1150.0, 25.0, 0.0, 0.3, etiket="Tabure_Yat")
    koy("Sandalye", 250.0, 1800.0, 200.0, 0.0, 0.3, etiket="Sandalye_Yat")
    koy("Palet", 800.0, 70.0, 3.0, 0.0, 0.5, etiket="Palet_Arka")
    koy("Karton_A", 430.0, 95.0, -20.0, 0.0, 0.3, carpisma="yok")
    dekal("Leke_E", 450, 1500, 2, (4, 220, 300), 0.0, guc=0.7)
    dekal("Akinti_A", 2.5, 1100, 200, (6, 140, 220), 90.0, zemin=False)
    dekal("Leke_A", 470, 2420, 2, (4, 200, 160), 20.0, guc=0.6)
    # arka duvarda kurallar
    kagit("Kurallar", "/Game/Uyanis/Kagit/T_Kurallar", 600.0, 2.6, 165.0, 0.0, 1.0, 44.0, 62.0)

    # ---------- bakıcı odası (sağ ön köşe): camlı bölme, masa, defter, anahtarlar, dolap, sıcak sarkıt lamba ----------
    BX0, BY0, BZ = 605.0, 2140.0, 255.0
    for (et, x0, x1, y0, y1, z0, z1) in (("Bak_Bati1", BX0, BX0 + 12, BY0 + 12, 2265, 0, BZ), ("Bak_Bati2", BX0, BX0 + 12, 2265, 2465, 0, 100), ("Bak_Bati3", BX0, BX0 + 12, 2265, 2465, 195, BZ),
                                         ("Bak_Bati4", BX0, BX0 + 12, 2465, 2495, 0, BZ), ("Bak_Bati5", BX0, BX0 + 12, 2495, 2590, 212, BZ), ("Bak_Bati6", BX0, BX0 + 12, 2590, LEN, 0, BZ),
                                         ("Bak_Guney1", BX0, 690, BY0, BY0 + 12, 0, BZ), ("Bak_Guney2", 690, 860, BY0, BY0 + 12, 0, 100), ("Bak_Guney3", 690, 860, BY0, BY0 + 12, 195, BZ),
                                         ("Bak_Guney4", 860, W, BY0, BY0 + 12, 0, BZ)):
        kutu(et, x0, x1, y0, y1, z0, z1, SIVA)
    kutu("Bak_Tavan", BX0, W, BY0, LEN, BZ, BZ + 14, SIVA)
    # pencere camları + ince metal kasalar
    kutu("Bak_CamBati", BX0 + 5.5, BX0 + 6.5, 2265, 2465, 100, 195, CAMM, golge=False)
    kutu("Bak_CamGuney", 690, 860, BY0 + 5.5, BY0 + 6.5, 100, 195, CAMM, golge=False)
    for (et, x0, x1, y0, y1, z0, z1) in (("Kasa_B_Alt", BX0 - 1, BX0 + 13, 2265, 2465, 97, 100), ("Kasa_B_Ust", BX0 - 1, BX0 + 13, 2265, 2465, 195, 198), ("Kasa_B_Orta", BX0 - 1, BX0 + 13, 2363, 2367, 100, 195),
                                         ("Kasa_G_Alt", 690, 860, BY0 - 1, BY0 + 13, 97, 100), ("Kasa_G_Ust", 690, 860, BY0 - 1, BY0 + 13, 195, 198), ("Kasa_G_Orta", 773, 777, BY0 - 1, BY0 + 13, 100, 195)):
        kutu(et, x0, x1, y0, y1, z0, z1, METAL, carpisma=False)
    MZ = 81.5   # masa üstü
    koy("Masa", W - 33.0, 2400.0, 90.0, 0.0, 0.3, etiket="Bak_Masa")
    koy("Sandalye", 805.0, 2400.0, float(os.environ.get("UY_SANDYAW", "90")), 0.0, 0.3, etiket="Bak_Sandalye")
    mesh_at("Defter", 858.0, 2372.0, MZ + 1.1, R(pitch=90.0, yaw=12.0), etiket="Bak_Defter", carpisma=False)
    anah = mesh_at("Anahtarlik", 872.0, 2440.0, MZ + 0.4, R(yaw=35.0), etiket="Bak_Anahtarlar", carpisma=False)
    koy("Dolap", 652.0, 2190.0, DOL_YAW + 90.0, 0.0, 0.3, etiket="Bak_Dolap")
    koy("Tabure", 700.0, 2290.0, -15.0, 0.0, 0.3, etiket="Bak_Tabure")
    dekal("Leke_B", 780, 2380, 2, (4, 160, 130), 40.0, guc=0.6)
    # sarkıt lamba: masanın üstünde, sıcak — yatakhanedeki tek sıcak ışık (camın ardından görünür)
    mesh_at("Sarkit", 858.0, 2400.0, BZ - 1.5, R(), etiket="Bak_Sarkit", carpisma=False)
    isik(unreal.SpotLight, "Bak_Isik", V(858.0, 2400.0, BZ - 24.0), R(pitch=-90), intensity=9.0, attenuation_radius=520.0, inner_cone_angle=20.0, outer_cone_angle=58.0,
         source_radius=3.0, use_temperature=True, temperature=2700.0, volumetric_scattering_intensity=1.8)
    isik(unreal.PointLight, "Bak_Dolgu", V(800.0, 2380.0, 180.0), intensity=0.8, attenuation_radius=300.0, use_temperature=True, temperature=2600.0, cast_shadows=False)

    # ---------- ışıklar ----------
    # floresan armatürler (Megascans): iki sıra, tavan kirişlerinin arasında; çoğu ölü.
    FLT = SMI + "/MI_Floresan_Tup_Canli"
    FL = [(300.0, 320.0, "olu"), (600.0, 320.0, "olu"), (300.0, 970.0, "bp"), (600.0, 970.0, "olu"), (300.0, 1620.0, "olu"), (600.0, 1620.0, "canli"), (300.0, 2270.0, "olu")]
    for i, (fx, fy, tur) in enumerate(FL):
        mesh_at("Floresan", fx, fy, H, R(), etiket=f"Floresan{i}", carpisma=False)
        if tur == "canli":
            kutu(f"Floresan{i}_Tup", fx - 1.5, fx + 1.5, fy - 23, fy + 23, H - 7.5, H - 4.5, FLOR_CANLI, golge=False, carpisma=False)
            isik(unreal.RectLight, f"Floresan{i}_Isik", V(fx, fy, H - 9), R(pitch=-90),
                 intensity=22.0, attenuation_radius=950.0, source_width=10.0, source_height=46.0, barn_door_angle=80.0,
                 use_temperature=True, temperature=7200.0, volumetric_scattering_intensity=1.0)
        elif tur == "bp":
            fb = spawn(bpcls("BP_Floresan"), V(fx, fy, H), R(yaw=90.0), f"Floresan{i}_BP")
            for c in fb.get_components_by_class(unreal.StaticMeshComponent):
                if c.get_name().startswith("Govde"): c.set_visibility(False)
                if c.get_name().startswith("Tup"): c.set_relative_scale3d(V(0.46, 0.03, 0.03)); c.set_relative_location(V(0, 0, -6.0), False, False)
            rl = fb.get_component_by_class(unreal.RectLightComponent)
            if rl: sset(rl, "source_width", 46.0); sset(rl, "source_height", 10.0); rl.set_relative_location(V(0, 0, -9.0), False, False)
            sset(fb, "TemelSiddet", 22.0)
    # tavşanın üstünde sarkıt lamba (kablosu tavandan) → tek ışık havuzu
    mesh_at("Sarkit", BX, BY, 232.0, R(yaw=20.0), etiket="Sarkit_Tavsan", carpisma=False)
    kutu("Sarkit_Kablo", BX - 0.6, BX + 0.6, BY - 0.6, BY + 0.6, 233, H - 38, METAL, golge=False, carpisma=False)
    isik(unreal.SpotLight, "Tavsan_Isik", V(BX, BY, 208), R(pitch=-90),
         intensity=20.0, attenuation_radius=650.0, inner_cone_angle=4.0, outer_cone_angle=40.0, source_radius=2.0,
         use_temperature=True, temperature=6400.0, volumetric_scattering_intensity=2.5)
    # kırmızı dil: kapının üstünde kafesli lambada nabız atan acil ışık (yolu gösterir)
    def kirmizi(et, x, y, z, yaw=0.0, siddet=6.0, faz=0.0, yaricap=750.0, kafes=False):
        k_ = spawn(bpcls("BP_KirmiziLamba"), V(x, y, z), R(yaw=yaw), et)
        sset(k_, "TemelSiddet", siddet); sset(k_, "Faz", faz)
        sset(k_.get_component_by_class(unreal.PointLightComponent), "attenuation_radius", yaricap)
        if kafes:
            for c in k_.get_components_by_class(unreal.StaticMeshComponent):
                if c.get_name().startswith("Kasa"): c.set_visibility(False)
                if c.get_name().startswith("Cam"): c.set_relative_scale3d(V(0.06, 0.05, 0.09)); c.set_relative_location(V(0, -6.0, 0), False, False)
        return k_
    mesh_at("KafesLamba", 490.0, LEN, 262.0, R(yaw=180.0), etiket="Kapi_KafesLamba", carpisma=False)
    kirmizi("Kirmizi_Kapi", 490.0, LEN, 262.0, 0.0, 7.0, 0.0, 900.0, kafes=True)
    # ---------- kapı + inceleme noktaları ----------
    defter = incele("Defter", 855.0, 2395.0, 95.0, ["defter1", "defter2", "defter3"], 130.0, (5.5, 6.5), al=anah)
    kp_ = spawn(bpcls("BP_YatakhaneKapisi"), V(490.0, LEN + 15.0, 0.0), R(), "YatakhaneKapisi")
    sset(kp_, "Anahtar", anah); sset(kp_, "AcilmaYonu", -1.0)
    if os.environ.get("UY_YURU"): sset(kp_, "TestOto", True)
    incele("Ela_Yatak", 150.0, 690.0, 60.0, ["yatak_ela"], 120.0)
    incele("Ben_Yatak", 150.0, 1010.0, 60.0, ["yatak_ben"], 120.0)
    incele("Ela_Dolap", 75.0, 440.0, 110.0, ["dolap_ela", "cizim1", "cizim2"], 125.0, (4.5, 4.0))
    incele("Kurallar", 600.0, 70.0, 120.0, ["kurallar1", "kurallar2"], 150.0, (5.0, 5.0))
    incele("Pencere", 860.0, 1630.0, 120.0, ["pencere"], 190.0)
    incele("Bak_Dolap", 690.0, 2235.0, 100.0, ["dolap_bakici"], 110.0)
    # ay: pencerelerden, yüksekten ve çapraz — koğuşun içinde ışık sütunları
    ay = isik(unreal.DirectionalLight, "Ay", V(0, 0, 2000), R(pitch=-30, yaw=225),
              intensity=float(os.environ.get("UY_AY", "2.6")), use_temperature=True, temperature=9500.0, volumetric_scattering_intensity=float(os.environ.get("UY_AYHAC", "2.4")), light_source_angle=0.4)
    sset(ay.light_component, "atmosphere_sun_light", False)
    sky = spawn(unreal.SkyLight, V(0, 0, 600), R(), "GokIsigi"); s = sky.light_component
    sset(s, "source_type", unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP); sset(s, "cubemap", unreal.load_asset("/Engine/EngineResources/GrayDarkTextureCube.GrayDarkTextureCube"))
    sset(s, "intensity", float(os.environ.get("UY_GOK", "1.6"))); sset(s, "light_color", unreal.Color(r=0xB6, g=0xEA, b=0xFF, a=255)); sset(s, "lower_hemisphere_is_black", False); sset(s, "mobility", unreal.ComponentMobility.MOVABLE)
    # sis: içeride hafif ama hacimli (ışık sütunları görünsün)
    fog = spawn(unreal.ExponentialHeightFog, V(0, 0, -100), R(), "Sis"); fc = fog.component
    sset(fc, "fog_density", float(os.environ.get("UY_SIS", "0.032"))); sset(fc, "fog_height_falloff", 0.06)
    sset(fc, "fog_inscattering_luminance", unreal.LinearColor(0.0035, 0.007, 0.0095, 1))
    sset(fc, "enable_volumetric_fog", True); sset(fc, "volumetric_fog_albedo", unreal.Color(r=118, g=146, b=160, a=255))
    sset(fc, "directional_inscattering_exponent", 6.0); sset(fc, "directional_inscattering_start_distance", 2500.0)
    sset(fc, "directional_inscattering_luminance", unreal.LinearColor(0.012, 0.024, 0.03, 1))
    sset(fc, "volumetric_fog_extinction_scale", float(os.environ.get("UY_SONUM", "1.15"))); sset(fc, "volumetric_fog_distance", float(os.environ.get("UY_HACMESAFE", "32000"))); sset(fc, "volumetric_fog_static_lighting_scattering_intensity", 0.0)
    # post-process (REANIMAL presetleri: sabit pozlama, bloom eşik 0, gren .25, kuvvetli vinyet, soğuk gölgeler)
    ppv = spawn(unreal.PostProcessVolume, V(0, 0, 0), R(), "PostProcess"); ppv.set_editor_property("unbound", True)
    ps = ppv.get_editor_property("settings")
    def pp(k, v):
        try: ps.set_editor_property("override_" + k, True)
        except Exception: pass
        sset(ps, k, v)
    EXP = float(os.environ.get("UY_EXP", "2.4"))
    pp("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM); pp("auto_exposure_min_brightness", 1.0); pp("auto_exposure_max_brightness", 1.0)
    pp("auto_exposure_bias", EXP); pp("bloom_intensity", 0.7); pp("bloom_threshold", 0.0); pp("film_grain_intensity", float(os.environ.get("UY_GREN", "0.42"))); pp("film_grain_intensity_shadows", 1.0); pp("film_grain_intensity_midtones", 0.9); pp("film_grain_intensity_highlights", 0.5); pp("vignette_intensity", 0.75)
    pp("scene_fringe_intensity", 0.25); pp("color_contrast_shadows", unreal.Vector4(1.15, 1.15, 1.15, 1.0)); pp("color_saturation", unreal.Vector4(0.82, 0.82, 0.82, 1.0))
    pp("color_offset_shadows", unreal.Vector4(0.0, 0.004, 0.009, 0.0)); pp("color_gain_highlights", unreal.Vector4(0.92, 1.0, 1.04, 1.0))
    pp("depth_of_field_fstop", float(os.environ.get("UY_FSTOP", "3.2"))); pp("depth_of_field_focal_distance", float(os.environ.get("UY_ODAK", "420"))); pp("motion_blur_amount", 0.0)
    pp("dynamic_global_illumination_method", unreal.DynamicGlobalIlluminationMethod.NONE); pp("reflection_method", unreal.ReflectionMethod.SCREEN_SPACE)
    pp("ambient_occlusion_intensity", 0.9); pp("ambient_occlusion_radius", 120.0)
    ppv.set_editor_property("settings", ps)
    # ================= BÖLÜM 2: GEÇİT (yıkık servis koridoru) =================
    ZEMIN2 = smi("Gec_Zemin", yz("Zemin_Kaba"), {"Olcek": 240.0}, {"Ton": (0.36, 0.37, 0.38)})
    DUVAR2 = smi("Gec_Duvar", yz("Beton_Kalip"), {"Olcek": 260.0}, {"Ton": (0.34, 0.36, 0.37)})
    TAVAN2 = smi("Gec_Tavan", yz("Beton_Koyu"), {"Olcek": 260.0}, {"Ton": (0.35, 0.35, 0.36)})
    BORU = smi("Boru", yz("Beton_Boya"), {"Olcek": 120.0, "Metal": 0.35, "PuruzCarpan": 0.75}, {"Ton": (0.10, 0.13, 0.12)})
    KIRMIZI = smi("Uyari_Kirmizi", M_MS, {"PuruzCarpan": 0.4}, {"Ton": (0.05, 0, 0), "Isima": (18.0, 0.6, 0.3)})
    CX0, CX1, CY0, CY1, CH = 380.0, 640.0, LEN + 30, 3800.0, 300.0
    DX0, DX1 = 3150.0, 3450.0   # tavanda çökük delik (x 380..560): ay ışığı molozun üstüne düşer
    kutu("Gec_Zemin", 300, 700, CY0, 4100, -30, 0, ZEMIN2)
    kutu("Gec_SolDuvar", 300, CX0, CY0, CY1, 0, CH + 20, DUVAR2)
    kutu("Gec_SagDuvar", CX1, 700, CY0, CY1, 0, CH + 20, DUVAR2)
    kutu("Gec_Tavan_A", 300, 700, CY0, DX0, CH, CH + 40, TAVAN2)
    kutu("Gec_Tavan_B", 300, 700, DX1, CY1, CH, CH + 40, TAVAN2)
    kutu("Gec_Tavan_Kenar", 560, 700, DX0, DX1, CH, CH + 40, TAVAN2)
    SIL = unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")
    def boru(et, x, z, cap, y0, y1):
        a = spawn(unreal.StaticMeshActor, V(x, (y0 + y1) / 2, z), R(roll=90), et)
        c = a.static_mesh_component; c.set_static_mesh(SIL); c.set_material(0, BORU); a.set_actor_scale3d(V(cap / 100, cap / 100, (y1 - y0) / 100))
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    boru("Boru_Kalin", CX0 + 16, 245, 16, CY0, CY1); boru("Boru_Ince", CX0 + 12, 218, 9, CY0, CY1); boru("Boru_Sag", CX1 - 14, 262, 12, CY0, DX0 - 40)
    yy = CY0 + 120
    while yy < CY1:
        kutu("Boru_Kelepce", CX0, CX0 + 22, yy - 3, yy + 3, 205, 256, METAL, carpisma=False); yy += 240
    for i, fy in enumerate((2900.0, 3650.0)):   # ölü lambalar
        kutu(f"Gec_Lamba{i}", 490, 530, fy - 12, fy + 12, CH - 10, CH, FLOR_OLU, carpisma=False)
    moloz_yigini("Moloz_Yigin_B", 455.0, 3300.0, 15.0, 0.42)
    for (ad, x, y_, yw) in (("Beton_Parca_D", 600, 3180, 40), ("Beton_Parca_F", 420, 3520, 160), ("Moloz_Duz_B", 590, 3420, 80),
                            ("Karton_C", 600, 2850, -30), ("Briket_A", 410, 2960, 12), ("Beton_Parca_C", 520, 3060, 250)):
        koy(ad, x, y_, yw, 0.0, 1.0, carpisma="yok")
    CAMUR = smi("Camur_Koyu", eal.load_asset(f"{FAB}/UB/Camur_Leke/MI_Camur_Leke"), {"PuruzCarpan": 0.55}, {"Ton": (0.30, 0.31, 0.33)})
    koy("Camur_Leke", 520, 3650, 90.0, 0.0, 1.5, olcek=(0.6, 0.85, 0.4), carpisma="yok", malzeme=CAMUR)
    dekal("Akinti_B", CX1 - 1, 3000, 180, (6, 160, 240), -90.0, zemin=False)
    dekal("Akinti_C", CX0 + 1, 3560, 190, (6, 140, 220), 90.0, zemin=False)
    dekal("Leke_B", 500, 3300, 2, (4, 220, 160), 70.0)
    # acil durum ışığı: merdivenin üstünde kırmızı
    kutu("Acil_Govde", 495, 525, CY1 - 14, CY1 - 2, 258, 272, KIRMIZI, golge=False, carpisma=False)
    isik(unreal.PointLight, "Acil_Isik", V(510, CY1 - 30, 262), intensity=4.5, attenuation_radius=650.0, source_radius=2.0,
         light_color=unreal.Color(r=255, g=40, b=25, a=255), volumetric_scattering_intensity=2.0)
    kirmizi("Kirmizi_Gecit", CX1 - 10, 3020.0, 250.0, -90.0, 3.5, 1.9, 600.0)
    # merdiven: geçit boşluğunda (y 3800..4100) zemin 0 → teras 125
    TZ = 125.0
    mer = koy("Merdiven_A", 510.0, 3803.0, 180.0, 0.0, 0.0, etiket="Merdiven")   # mesh -Y yönünde alçalır → 180° (yüksek uç terasta)
    kutu("Mer_Yan_Sol", 380, 427, 3800, 4100, 0, TZ, DUVAR2); kutu("Mer_Yan_Sag", 593, 640, 3800, 4100, 0, TZ, DUVAR2)

    # ================= BÖLÜM 3: TERAS (megayapının yarım kalmış katı, kenarı boşluğa açık) =================
    ZEMIN3 = smi("Ter_Zemin", yz("Zemin_Kahve"), {"Olcek": 320.0}, {"Ton": (0.34, 0.34, 0.35)})
    DUVAR3 = smi("Ter_Duvar", yz("Beton_Akinti_C"), {"Olcek": 420.0}, {"Ton": (0.30, 0.32, 0.33)})
    TAVAN3 = smi("Ter_Tavan", yz("Beton_Kalip"), {"Olcek": 380.0}, {"Ton": (0.26, 0.27, 0.29)})
    TX0, TX1, TY0, TY1, TH = -1700.0, 2700.0, 4100.0, 7700.0, 1325.0
    kutu("Ter_Zemin", TX0, TX1, TY0, TY1, -80, TZ, ZEMIN3)
    kutu("Ter_Arka_Sol", TX0 - 40, 380, 3800, TY0, 0, TH + 140, DUVAR3)
    kutu("Ter_Arka_Sag", 640, TX1 + 40, 3800, TY0, 0, TH + 140, DUVAR3)
    kutu("Ter_Arka_Ust", 380, 640, 3800, TY0, 420, TH + 140, DUVAR3)
    kutu("Ter_Tavan", TX0 - 40, TX1 + 40, TY0 - 20, TY1 - 700, TH, TH + 120, TAVAN3)
    kutu("Ter_SolDuvar", TX0 - 40, TX0, TY0, TY1, -80, TH + 140, DUVAR3)
    kutu("Ter_SagDuvar", TX1, TX1 + 40, TY0, TY1, -80, TH + 140, DUVAR3)
    kutu("Ter_KenarSinir", TX0, TX1, TY1 - 30, TY1 - 10, TZ, TZ + 400, DUVAR3, gizli=True)   # düşmesin
    # dev kolonlar (tabanı terasa, tepesi tavana gömülü)
    KS = (TH + 8 - TZ) / 249.6
    for ky in (5000.0, 5900.0, 6800.0):
        for kx in (-1150.0, -200.0, 1250.0, 2150.0):
            ad = "Kolon_A" if (kx + ky) % 1800 < 900 else "Kolon_C"
            koy(ad, kx, ky, (kx * 7 + ky) % 90, TZ, 0.5, olcek=(1.9, 1.9, KS), etiket=f"Kolon_{int(kx)}_{int(ky)}")
    for (lx, ly, yw, fz) in ((-200 + 50, 5000.0, 90.0, 0.7), (1250 - 50, 5900.0, -90.0, 2.6), (-200 + 50, 6800.0, 90.0, 4.4)):
        kirmizi(f"Kirmizi_Kolon_{int(ly)}", lx, ly, TZ + 270.0, yw, 9.0, fz, 1100.0)
    # siperler (projektörden saklanma): rıhtım yolu x ~300..720
    random.seed(11)
    def briket_yigini(x0, y0, sira, kat, yaw=0.0):
        for k in range(kat):
            for i in range(sira):
                for j in range(2):
                    koy("Briket_A" if (i + j + k) % 3 else "Briket_B", x0 + i * 41 + random.uniform(-1.5, 1.5), y0 + j * 21, yaw + random.uniform(-3, 3), TZ + k * 20.2, 0.0, etiket=f"Briket_{int(x0)}_{int(y0)}_{k}{i}{j}")
    koy("Moloz_Torba", 340, 4750, 25, TZ, 1.0); koy("Palet", 700, 4820, 80, TZ, 0.5); koy("Palet", 705, 4826, 84, TZ + 13.5, 0.0, etiket="Palet_Ust")
    briket_yigini(210, 5450, 4, 6)
    # siper adaları: yol boyunca 4-5 m'de bir (taramayı kollayıp siperden sipere geç)
    if not os.environ.get("UY_YURU"):
      briket_yigini(395, 5020, 4, 7)
      briket_yigini(430, 5820, 3, 7, 8.0)
      koy("Moloz_Torba", 400, 6480, 40, TZ, 1.0, etiket="Torba_Siper_A"); koy("Moloz_Torba", 235, 6630, -10, TZ, 1.0, etiket="Torba_Siper_B")
      for k in range(5): koy("Palet", 330, 7180, 6 + k * 3, TZ + k * 13.5, 0.0 if k else 0.5, etiket=f"Palet_Yigin_{k}")
    moloz_yigini("Moloz_Yigin_B", 720, 6150, 200, 0.9, zemin=TZ)
    koy("Varil", 300, 6820, 0, TZ, 0.5); koy("Varil", 382, 6862, 40, TZ, 0.5); koy("Moloz_Torba", 515, 6755, -15, TZ, 1.0)
    koy("Kiris_B", -600, 5600, 75, TZ, 1.0, olcek=(1.6, 1.6, 1.6)); koy("Kiris_D", 1700, 6400, 15, TZ, 1.0, olcek=(1.5, 1.5, 1.5))
    moloz_yigini("Moloz_Yigin_A", -900, 6500, 30, 1.3, zemin=TZ)
    for (ad, x, y_, yw, s) in (("Beton_Parca_A", 560, 5300, 20, 2.2), ("Beton_Parca_E", 905, 5740, 140, 2.5), ("Moloz_Duz_A", 650, 5180, 0, 1.4),
                               ("Moloz_Duz_B", 650, 6500, 60, 1.6), ("Beton_Parca_B", 330, 7040, 300, 2.0), ("Karton_A", 520, 6300, 15, 1.0)):
        koy(ad, x, y_, yw, TZ, 1.0, olcek=s, carpisma="yok")
    dekal("Leke_D", 500, 5800, TZ + 2, (4, 500, 380), 10.0); dekal("Leke_E", 1100, 6900, TZ + 2, (4, 600, 500), 70.0, guc=0.8)
    # projektörlü dron: kenarın ötesinde havada, terası tarar (yakalanınca terasın başına)
    don = spawn(unreal.TargetPoint, V(510, 4320, TZ + 95), R(yaw=90), "Donus_Teras")
    YURU = os.environ.get("UY_YURU")   # "x1 y1 x2 y2 x3 y3": otomatik yürüyüş testi (dron kapalı)
    pj = spawn(bpcls("BP_Projektor") if not YURU else unreal.TargetPoint, V(520, 8300, 1150), R(), "Dron_Projektor")
    if not YURU: sset(pj, "Merkez", V(500, 5900, TZ)); sset(pj, "Donus", don); sset(pj, "Genlik", 32.0); sset(pj, "Hiz", 0.35); sset(pj, "AlgiSure", 0.9)
    pl_ = pj.get_component_by_class(unreal.SpotLightComponent)
    if pl_: sset(pl_, "volumetric_scattering_intensity", 14.0); sset(pl_, "intensity", 1400.0)
    if YURU:
        t_ = [float(v) for v in YURU.split()]; tw = spawn(bpcls("BP_TestYuru"), V(0, 0, 0), R(), "TestYuru")
        for i in range(len(t_) // 2): sset(tw, f"H{i + 1}", V(t_[2 * i], t_[2 * i + 1], 0))
        sset(tw, "Son", float(len(t_) // 2))
    DRON = smi("Dron_Govde", M_MS, {"Metal": 0.8, "PuruzCarpan": 0.35}, {"Ton": (0.02, 0.022, 0.025)})
    for (et, dx, dy, dz, sx, sy, sz) in (("Dron_Govde", 0, 0, 25, 90, 70, 34), ("Dron_KolA", 0, 0, 40, 190, 10, 6), ("Dron_KolB", 0, 0, 40, 10, 190, 6)):
        kutu(et, 520 + dx - sx / 2, 520 + dx + sx / 2, 8300 + dy - sy / 2, 8300 + dy + sy / 2, 1150 + dz - sz / 2, 1150 + dz + sz / 2, DRON, carpisma=False)
    tk_ = eal.load_asset("/Game/Sisli/Mekanik/BP_Titrek")
    if tk_:
        dk = spawn(tk_.generated_class(), V(520, 8300, 1120), R(), "Dron_Uyari")
        dl = dk.get_component_by_class(unreal.PointLightComponent); sset(dl, "light_color", unreal.Color(r=255, g=30, b=20, a=255)); sset(dl, "attenuation_radius", 400.0)
        sset(dk, "TemelSiddet", 6.0); sset(dk, "Sans", 0.5)
    bt = spawn(bpcls("BP_Bitis"), V(500, TY1 - 260, TZ + 150), R(), "Bitis")
    bt.get_component_by_class(unreal.BoxComponent).set_box_extent(V(700, 160, 200), False)
    # uzak megayapı siluetleri (sisin içinde): dev kuleler, köprüler, seyrek pencere ışıkları, tepe uyarı ışıkları
    SILUET = smi("Siluet", M_MS, {"PuruzCarpan": 1.0}, {"Ton": (0.012, 0.014, 0.017)})
    PS = smi("Uzak_Pencere_Sicak", M_MS, {}, {"Ton": (0, 0, 0), "Isima": (9.0, 4.6, 1.6)})
    PK = smi("Uzak_Pencere_Soguk", M_MS, {}, {"Ton": (0, 0, 0), "Isima": (3.0, 6.0, 7.5)})
    random.seed(5); nk = 0
    def kule(i, x, y, w, d, h):
        """Kademeli megayapı kulesi: 2-4 gövde (yukarı daralan), dikey kanatlar, yatay pencere bantları, tepe ışığı."""
        global nk
        z = -40000.0; kat = random.randint(2, 4); ww, dd = w, d
        for k in range(kat):
            zt = z + (h + 40000.0) * (0.55 if k == 0 else 0.25 / max(1, kat - 1) + 0.12) if k < kat - 1 else h
            zt = min(zt, h)
            kutu(f"Kule{i}_{k}", x - ww / 2, x + ww / 2, y, y + dd, z, zt, SILUET, golge=False, carpisma=False)
            # cepheye dikey kanatlar (gölge çizgisi → ölçek)
            for f_ in range(random.randint(2, 5)):
                fx = x - ww / 2 + ww * (f_ + 0.5) / 5.0
                kutu(f"Kule{i}_{k}_Kanat", fx - 60, fx + 60, y - 160, y, z, zt, SILUET, golge=False, carpisma=False)
            # yatay pencere bantları (bazı katlar yanık)
            nb = random.randint(1, 4)
            for b in range(nb):
                bz = random.uniform(max(z, -8000.0), zt - 600)
                if bz > zt - 600: continue
                x0 = random.uniform(x - ww / 2 + 100, x); x1 = min(x + ww / 2 - 100, x0 + random.uniform(ww * 0.2, ww * 0.7))
                mt = PS if random.random() < 0.55 else PK
                px = x0
                while px < x1:
                    if random.random() < 0.55:
                        kutu(f"Kule{i}_Pen", px, px + 180, y - 30, y - 12, bz, bz + 140, mt, golge=False, carpisma=False); nk += 1
                    px += 260
            z = zt; ww *= random.uniform(0.6, 0.85); dd *= random.uniform(0.7, 0.9)
        kutu(f"Kule{i}_Tepe", x - 100, x + 100, y + 40, y + 240, h, h + 220, KIRMIZI, golge=False, carpisma=False)
    for i in range(16):
        x = random.uniform(-32000, 36000); y = random.uniform(9500, 30000); w = random.uniform(2500, 8000); d = random.uniform(2500, 7000)
        h = random.uniform(5000, 26000)
        if abs(x - 500) < 4500 and y < 16000: x += 8000 * (1 if x > 500 else -1)   # tam karşı boş: sis derinliği okunsun
        kule(i, x, y, w, d, h)
    for (y, z, x0, x1, kal) in ((16000, 3500, -30000, 22000, 1100), (26000, 11000, -12000, 38000, 1600)):
        kutu("Kopru", x0, x1, y, y + kal, z, z + kal * 0.8, SILUET, golge=False, carpisma=False)
    log("uzak kule pencere", nk)
    # kulelerin arkasında hafif aydınlık sis perdesi: siluetler koyu okunur (REANIMAL: koyu yapı, açık sis)
    PERDE = smi("Sis_Perdesi", M_MS, {"PuruzCarpan": 1.0}, {"Ton": (0, 0, 0), "Isima": (0.018, 0.036, 0.046)})
    kutu("SisPerdesi", -150000, 150000, 45000, 45200, -60000, 90000, PERDE, golge=False, carpisma=False)
    # teras zemini: daha fazla kir, ıslaklık, küçük moloz (düz/boş görünmesin)
    for (ad, x, y_, yw, s_) in (("Moloz_Duz_A", -300, 4700, 40, 1.8), ("Moloz_Duz_B", 1500, 5200, 110, 2.0), ("Moloz_Duz_A", 900, 6900, 200, 1.6),
                                ("Beton_Parca_C", 1000, 4900, 30, 2.4), ("Beton_Parca_F", -500, 6100, 80, 2.0), ("Beton_Parca_D", 250, 6000, 10, 2.2),
                                ("Moloz_Duz_B", -1300, 5400, 0, 2.2), ("Beton_Parca_A", 1900, 7200, 60, 2.6), ("Karton_C", 700, 5050, 75, 1.0)):
        koy(ad, x, y_, yw, TZ, 1.0, olcek=s_, carpisma="yok")
    for (x, y_, yw, s_) in ((640, 5560, 30, 0.9), (1250, 6150, 100, 1.3), (-700, 5000, 10, 1.2), (40, 7430, 80, 1.0)):
        koy("Camur_Leke", x, y_, yw, TZ, 2.0, olcek=(s_, s_, 0.5), carpisma="yok", malzeme=CAMUR)
    for (ad, x, y_, sz, yw) in (("Leke_A", -400, 5300, 450, 30), ("Leke_B", 1200, 5600, 400, 120), ("Leke_C", 600, 6600, 380, 200), ("Leke_E", -1000, 7000, 500, 60)):
        dekal(ad, x, y_, TZ + 2, (4, sz, sz * 0.8), yw)
    # bölüm ambiyansı
    w_ = eal.load_asset("/Game/Sisli/Ses/Sisli_Ambiyans")
    if w_:
        muz = spawn(unreal.AmbientSound, V(450, 1000, 200), R(), "Ambiyans"); ac = muz.get_component_by_class(unreal.AudioComponent)
        ac.set_sound(w_); sset(ac, "allow_spatialization", False); sset(ac, "volume_multiplier", 0.6)
    # isteğe bağlı sinema kameraları (C tuşu): bölüm başına bir alçak, geniş kadraj
    def sinema(et, kam, hedef, alan_a, alan_b, fov, takip, bakis, maxk):
        dx, dy, dz = hedef[0] - kam[0], hedef[1] - kam[1], hedef[2] - kam[2]
        yaw = math.degrees(math.atan2(dy, dx)); pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
        c = spawn(bpcls("BP_SinemaKamera"), V(*kam), R(pitch=pitch, yaw=yaw), et)
        c.get_component_by_class(unreal.CameraComponent).set_editor_property("field_of_view", fov)
        for kk, vv in (("FOV", fov), ("Odak", V(hedef[0], hedef[1], 0)), ("Takip", V(*takip)), ("Bakis", bakis), ("MaxKayma", maxk)): sset(c, kk, vv)
        mn = [min(alan_a[j], alan_b[j]) for j in range(3)]; mx = [max(alan_a[j], alan_b[j]) for j in range(3)]
        e = V(*[(mx[j] - mn[j]) / 2 for j in range(3)])
        z_ = spawn(bpcls("BP_KameraAlani"), V(*[(mn[j] + mx[j]) / 2 for j in range(3)]), R(), et + "_Alan")
        z_.get_component_by_class(unreal.BoxComponent).set_box_extent(e, False)
        for kk, vv in (("Kamera", c), ("Boyut", e), ("Basta", False)): sset(z_, kk, vv)
    if not os.environ.get("UY_KAMERA"):
        sinema("Sinema_Yatakhane", (840, 2480, 290), (300, 500, 60), (0, 0, -50), (W, LEN - 10, H), 62.0, (0.12, 0.1, 0), 0.3, 140.0)
        sinema("Sinema_Gecit", (590, 3760, 250), (470, 2750, 40), (CX0, LEN, -50), (CX1, 4090, CH), 58.0, (0.2, 0.25, 0), 0.35, 120.0)
        sinema("Sinema_Teras", (-1350, 4350, 420), (900, 7300, 125), (TX0, 4100, -50), (TX1, TY1, TH), 55.0, (0.15, 0.2, 0.05), 0.3, 300.0)
    # ---------- mekanikler ----------
    def bpcls(n): a = eal.load_asset("/Game/Sisli/Mekanik/" + n); return a.generated_class() if a else None
    fe = bpcls("BP_Fener")
    if fe:
        fen = spawn(fe, V(0, 0, 0), R(), "Fener")
        if os.environ.get("UY_COMELTEST"): sset(fen, "TestComel", True)
    if not os.environ.get("UY_KAMERA"): spawn(bpcls("BP_Giris"), V(0, 0, 0), R(), "Giris")
    # ---------- test kamerası (UY_KAMERA="x y z pitch yaw fov"): sabit sinema kamerası + alanı ----------
    tk = os.environ.get("UY_KAMERA")
    if tk:
        k = [float(v) for v in tk.split()]
        cam = spawn(bpcls("BP_SinemaKamera"), V(k[0], k[1], k[2]), R(pitch=k[3], yaw=k[4]), "TestKamera")
        for kk, vv in (("FOV", k[5]), ("Takip", V(0, 0, 0)), ("MaxKayma", 0.0), ("Bakis", 0.0), ("Odak", V(k[0], k[1], 0))): sset(cam, kk, vv)
        cam.get_component_by_class(unreal.CameraComponent).set_editor_property("field_of_view", k[5])
        z_ = spawn(bpcls("BP_KameraAlani"), V(450, 1300, 150), R(), "TestKameraAlani")
        z_.get_component_by_class(unreal.BoxComponent).set_box_extent(V(3000, 3000, 1000), False)
        for kk, vv in (("Kamera", cam), ("Boyut", V(3000, 3000, 1000)), ("Basta", True), ("Gecis", 0.0)): sset(z_, kk, vv)
    for i, sat in enumerate(t for t in os.environ.get("UY_ANIMTEST", "").split(";") if t.strip()):   # "mesh,anim,x,y,yaw,ölçek;..." poz karşılaştırma
        ms, an, ax, ay, ayaw, aol = sat.split(",")
        a_ = spawn(unreal.SkeletalMeshActor, V(float(ax), float(ay), 0.0), R(yaw=float(ayaw)), "AnimTest%d" % i)
        c_ = a_.get_editor_property("skeletal_mesh_component"); c_.set_skeletal_mesh_asset(eal.load_asset(ms))
        c_.set_editor_property("relative_scale3d", V(float(aol), float(aol), float(aol)))
        c_.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE); c_.override_animation_data(eal.load_asset(an), True, True, 0.0, 1.0)
        log("animtest", i, ms.split("/")[-1], an.split("/")[-1])
    ti = os.environ.get("UY_TESTISIK")   # "x y z cd": test için dolgu ışığı (yüz yakın çekimi)
    if ti:
        t_ = [float(v) for v in ti.replace("_", " ").split()]
        isik(unreal.PointLight, "TestIsik", V(t_[0], t_[1], t_[2]), intensity=t_[3], attenuation_radius=400.0, source_radius=8.0, use_temperature=True, temperature=5600.0)
    # ---------- başlangıç ----------
    b = [float(v) for v in os.environ.get("UY_BASLA", "330 900 257").split()]
    spawn(unreal.PlayerStart, V(b[0], b[1], 95.0), R(yaw=b[2]), "Baslangic")
    # ---------- çakışma denetimi: prop ↔ mimari / prop ↔ prop (2 cm tolerans) ----------
    def kesisim(a0, a1, b0, b1, tol=2.0):
        return all(min(a1[i], b1[i]) - max(a0[i], b0[i]) > tol for i in range(3))
    nc = 0
    for (pa, p0, p1, pc) in PROPS:
        for (ka, k0, k1) in KATILAR:
            if ka in ("Zemin",) or pa.startswith(("Kolon", "Moloz_Yigin", "Merdiven")): continue   # kolon tavana, yığın duvara, merdiven yan duvarlara bilerek gömülü
            if kesisim(p0, p1, k0, k1): log("ÇAKIŞMA mimari", pa, "↔", ka); nc += 1
    for i in range(len(PROPS)):
        for j in range(i + 1, len(PROPS)):
            if PROPS[i][0].startswith("Briket") and PROPS[j][0].startswith("Briket"): continue
            if kesisim(PROPS[i][1], PROPS[i][2], PROPS[j][1], PROPS[j][2], 4.0): log("ÇAKIŞMA prop", PROPS[i][0], "↔", PROPS[j][0]); nc += 1
    log("çakışma sayısı", nc, "prop", len(PROPS), "kutu", len(KATILAR))
    les.save_current_level(); log("kaydedildi", MAP)
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/kur_uyanis_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
