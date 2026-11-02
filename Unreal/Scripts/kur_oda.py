# L_Oda1 — "Yarık Oda" diorama: sabit alçak sinematik kamera, arkadan ay ışığı + sis, sarkan fener.
import unreal, json, math, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal = unreal.EditorAssetLibrary
MAP = "/Game/Sisli/Maps/L_Oda1"; DST = "/Game/Sisli/Oda1"
J = json.load(open("C:/Users/Onur/Sisli/Unreal/SourceArt/Oda1/sahne_ue.json")); I = J["isaret"]
V = lambda x, y, z: unreal.Vector(x, y, z)
R = lambda pitch=0, yaw=0, roll=0: unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)
def sset(o, k, v):
    try: o.set_editor_property(k, v)
    except Exception as e: OUT.append("ÖZELLİK YOK %s.%s: %s" % (o.get_class().get_name(), k, str(e)[:100]))
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if eal.does_asset_exist(MAP): eal.delete_asset(MAP)
    if not les.new_level(MAP): raise RuntimeError("new_level başarısız")
    # koyu su malzemesi: Specular ~0 (yatay bakışta sisi ayna gibi yansıtmasın), hafif pürüz
    mel = unreal.MaterialEditingLibrary; at_ = unreal.AssetToolsHelpers.get_asset_tools()
    sup = DST + "/M_SuKoyu"
    if eal.does_asset_exist(sup): eal.delete_asset(sup)
    smat = at_.create_asset("M_SuKoyu", DST, unreal.Material, unreal.MaterialFactoryNew())
    def sx(cls, x, y, **kw):
        e = mel.create_material_expression(smat, cls, x, y)
        for kk, vv in kw.items(): e.set_editor_property(kk, vv)
        return e
    bcx = sx(unreal.MaterialExpressionConstant3Vector, -400, 0, constant=unreal.LinearColor(0.006, 0.013, 0.015, 1))
    mel.connect_material_property(bcx, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(sx(unreal.MaterialExpressionConstant, -400, 200, r=0.12), "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(sx(unreal.MaterialExpressionConstant, -400, 300, r=0.06), "", unreal.MaterialProperty.MP_SPECULAR)
    mel.recompile_material(smat); eal.save_loaded_asset(smat)
    for p in eal.list_assets(DST, recursive=True):
        a = eal.load_asset(p)
        if isinstance(a, unreal.StaticMesh) and a.get_name().endswith("M_Su"):
            for si in range(len(a.get_editor_property("static_materials"))): a.set_material(si, smat)
            eal.save_loaded_asset(a); log("su malzemesi", a.get_name())
    def spawn(cls, loc=V(0, 0, 0), rot=R(), label=None):
        a = eas.spawn_actor_from_class(cls, loc, rot)
        if a is None: raise RuntimeError("spawn başarısız %s" % cls)
        if label: a.set_actor_label(label)
        return a
    n = 0
    for p in eal.list_assets(DST, recursive=True):
        a = eal.load_asset(p)
        if isinstance(a, unreal.StaticMesh):
            act = spawn(unreal.StaticMeshActor, V(0, 0, 0), R(), a.get_name()); act.static_mesh_component.set_static_mesh(a); n += 1
            if a.get_name().startswith("SM_PH_") or "Tel" in a.get_name() or "GokKarti" in a.get_name():
                act.static_mesh_component.set_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA, unreal.CollisionResponseType.ECR_IGNORE)
            if "GokKarti" in a.get_name():
                act.static_mesh_component.set_editor_property("cast_shadow", False); act.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    log("mesh", n)
    # ay: dışarıdan (UE -Y) içeri, kameraya doğru, alçak
    ay = spawn(unreal.DirectionalLight, V(0, 0, 1000), R(pitch=-24, yaw=78), "Ay"); c = ay.light_component
    sset(c, "intensity", 2.4); sset(c, "light_color", unreal.Color(r=120, g=205, b=225, a=255)); sset(c, "volumetric_scattering_intensity", 1.1); sset(c, "specular_scale", 0.7)
    sset(c, "light_source_angle", 0.6); sset(c, "atmosphere_sun_light", False)
    sky = spawn(unreal.SkyLight, V(0, 0, 500), R(), "GokIsigi"); s = sky.light_component
    sset(s, "source_type", unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP); sset(s, "cubemap", unreal.load_asset("/Engine/EngineResources/GrayDarkTextureCube.GrayDarkTextureCube"))
    sset(s, "intensity", 2.2); sset(s, "light_color", unreal.Color(r=150, g=215, b=225, a=255)); sset(s, "lower_hemisphere_is_black", False); sset(s, "specular_scale", 0.3); sset(s, "mobility", unreal.ComponentMobility.MOVABLE)
    # sarkan fener: sıcak, loş, gölgeli
    f = I["fener"]
    pl = spawn(unreal.PointLight, V(*f), R(), "Fener_Isik"); q = pl.point_light_component
    sset(q, "intensity_units", unreal.LightUnits.CANDELAS); sset(q, "intensity", 22.0); sset(q, "attenuation_radius", 950.0)
    sset(q, "use_temperature", True); sset(q, "temperature", 2000.0); sset(q, "source_radius", 3.0); sset(q, "volumetric_scattering_intensity", 2.5)
    # yarıktan sızan dolgu (açıklığın sekmesi): içeriye bakan yumuşak alan ışığı
    ym = I["yarik_merkez"]
    rl = spawn(unreal.RectLight, V(ym[0], ym[1] + 60, ym[2]), R(yaw=90), "Yarik_Dolgu"); rc = rl.rect_light_component
    sset(rc, "intensity_units", unreal.LightUnits.CANDELAS); sset(rc, "intensity", 30.0); sset(rc, "attenuation_radius", 2200.0)
    sset(rc, "source_width", 500.0); sset(rc, "source_height", 380.0); sset(rc, "barn_door_angle", 70.0)
    sset(rc, "light_color", unreal.Color(r=150, g=210, b=230, a=255)); sset(rc, "volumetric_scattering_intensity", 0.0)
    # gök kartı ışıması: camgöbeği, beyaz değil
    gm = eal.load_asset("/Game/Sisli/Malzeme/MI/MI_Oda1_M_GokKarti")
    if gm:
        unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(gm, "Isima", unreal.LinearColor(0.09, 0.2, 0.23, 1)); eal.save_loaded_asset(gm)
    else: log("GokKarti MI YOK")
    # sis: içeride hafif, dışarıda yoğun ve aydınlık (yarık parlasın)
    fog = spawn(unreal.ExponentialHeightFog, V(0, 0, -100), R(), "Sis"); fc = fog.component
    sset(fc, "fog_density", 0.032); sset(fc, "fog_height_falloff", 0.1)
    sset(fc, "fog_inscattering_luminance", unreal.LinearColor(0.018, 0.05, 0.06, 1))
    sset(fc, "enable_volumetric_fog", True); sset(fc, "volumetric_fog_albedo", unreal.Color(r=180, g=225, b=235, a=255))
    sset(fc, "volumetric_fog_extinction_scale", 1.3); sset(fc, "volumetric_fog_distance", 9000.0); sset(fc, "volumetric_fog_scattering_distribution", 0.4)
    sset(fc, "volumetric_fog_static_lighting_scattering_intensity", 0.0)
    # post-process (REANIMAL presetleri)
    ppv = spawn(unreal.PostProcessVolume, V(0, 0, 0), R(), "PostProcess"); ppv.set_editor_property("unbound", True)
    ps = ppv.get_editor_property("settings")
    def pp(k, v):
        try: ps.set_editor_property("override_" + k, True)
        except Exception: pass
        sset(ps, k, v)
    pp("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM); pp("auto_exposure_min_brightness", 1.0); pp("auto_exposure_max_brightness", 1.0)
    pp("auto_exposure_bias", 1.6); pp("bloom_intensity", 0.8); pp("bloom_threshold", 0.0); pp("film_grain_intensity", 0.25); pp("vignette_intensity", 0.7)
    pp("scene_fringe_intensity", 0.2); pp("color_contrast_shadows", unreal.Vector4(1.2, 1.2, 1.2, 1.0)); pp("color_gain_midtones", unreal.Vector4(1.99, 2.0, 1.87, 1.0))
    pp("color_offset_shadows", unreal.Vector4(0.005, 0.01, 0.018, 0.0)); pp("film_slope", 0.63); pp("film_toe", 0.726)
    pp("depth_of_field_fstop", 4.0); pp("depth_of_field_focal_distance", 1100.0); pp("motion_blur_amount", 0.0)
    pp("dynamic_global_illumination_method", unreal.DynamicGlobalIlluminationMethod.NONE); pp("reflection_method", unreal.ReflectionMethod.SCREEN_SPACE)
    pp("ambient_occlusion_intensity", 0.8)
    ppv.set_editor_property("settings", ps)
    # ---- sinematik kameralar + kamera alanları (oda → sokak → iskele) ----
    import os
    def bpcls(n): return eal.load_asset("/Game/Sisli/Mekanik/" + n).generated_class()
    def P(n): return V(*I[n])
    def bp_spawn(n, loc, yaw=0.0, label=None):
        a = eas.spawn_actor_from_class(bpcls(n), loc, R(yaw=yaw))
        if a is None: raise RuntimeError("bp spawn başarısız " + n)
        if label: a.set_actor_label(label)
        return a
    def kutu(an):
        a, b = I[an + "_a"], I[an + "_b"]
        mn = [min(a[j], b[j]) for j in range(3)]; mx = [max(a[j], b[j]) for j in range(3)]
        return V(*[(mn[j] + mx[j]) / 2 for j in range(3)]), V(*[(mx[j] - mn[j]) / 2 for j in range(3)])
    bl = os.environ.get("ODA_TEST_BASLA", "1")
    oda_odak = [(I["baslangic"][0] + I["yarik_merkez"][0]) / 2, (I["baslangic"][1] + I["yarik_merkez"][1]) / 2, 0.0]
    KAM = [("kamera", "kamera_hedef", oda_odak, "alan1", 58.0, (0.12, 0.1, 0.0), 90.0, 0.25),
           ("kamera2", "kamera2_hedef", I["odak2"], "alan2", 55.0, (0.2, 0.9, 0.05), 3200.0, 0.35),
           ("kamera3", "kamera3_hedef", I["odak3"], "alan3", 55.0, (0.22, 0.4, 0.05), 1000.0, 0.35)]
    yaw0 = 0.0
    for i, (kn, hn, odak, an, fov, takip, maxk, bakis) in enumerate(KAM):
        k = I[kn]; h = I[hn]
        dx, dy, dz = h[0] - k[0], h[1] - k[1], h[2] - k[2]
        yaw = math.degrees(math.atan2(dy, dx)); pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
        if i == 0: yaw0 = yaw
        cam = bp_spawn("BP_SinemaKamera", V(*k), 0.0, f"Kamera{i + 1}")
        cam.set_actor_rotation(R(pitch=pitch, yaw=yaw), False)
        cam.get_component_by_class(unreal.CameraComponent).set_editor_property("field_of_view", fov)
        sset(cam, "FOV", fov); sset(cam, "Odak", V(*odak)); sset(cam, "Takip", V(*takip)); sset(cam, "Bakis", bakis); sset(cam, "MaxKayma", maxk)
        c, e = kutu(an)
        z = bp_spawn("BP_KameraAlani", c, 0.0, f"KameraAlani{i + 1}")
        z.get_component_by_class(unreal.BoxComponent).set_box_extent(e, False)
        sset(z, "Kamera", cam); sset(z, "Boyut", e); sset(z, "Basta", str(i + 1) == bl and os.environ.get("ODA_SINEMA") == "1")   # varsayılan serbest kamera; test karesi için ODA_SINEMA=1
        log("kamera%d yaw %.1f pitch %.1f" % (i + 1, yaw, pitch))
    fe = eas.spawn_actor_from_class(bpcls("BP_Fener"), V(0, 0, 0), R()); fe.set_actor_label("Fener")
    # ---- mekanikler: anahtar → kapı, projektör, su, son ----
    an_ = bp_spawn("BP_Anahtar", P("anahtar") + V(0, 0, 6), 0.0, "Anahtar")
    kp = bp_spawn("BP_Kapi", P("kapi_mentese"), 0.0, "CitKapisi"); sset(kp, "Anahtar", an_)
    don = spawn(unreal.TargetPoint, P("donus_iskele") + V(0, 0, 95), R(yaw=-90), "Donus_Iskele")
    pj = bp_spawn("BP_Projektor", P("projektor"), 0.0, "Projektor"); m_ = I["projektor_merkez"]
    sset(pj, "Merkez", V(m_[0], m_[1], 0.0)); sset(pj, "Donus", don)
    c, e = kutu("su"); ol = bp_spawn("BP_Olum", c, 0.0, "SuOlum")
    ol.get_component_by_class(unreal.BoxComponent).set_box_extent(e, False); sset(ol, "Boyut", e); sset(ol, "Donus", don)
    bp_spawn("BP_Son", P("son"), 0.0, "Son")
    ty = os.environ.get("ODA_TEST_YURU")   # "x1 y1 x2 y2 x3 y3" (UE cm) — otomatik yürüyüş testi
    if ty:
        t_ = [float(v) for v in ty.split()]
        tw = bp_spawn("BP_TestYuru", V(0, 0, 0), 0.0, "TestYuru")
        sset(tw, "H1", V(t_[0], t_[1], 0)); sset(tw, "H2", V(t_[2], t_[3], 0)); sset(tw, "H3", V(t_[4], t_[5], 0))
    # ---- sokak lambaları (sıcak, loş) ----
    for ln in ("lamba1", "lamba2", "lamba3"):
        la = spawn(unreal.PointLight, P(ln) + V(0, 0, -12), R(), ln); q2 = la.point_light_component
        sset(q2, "intensity_units", unreal.LightUnits.CANDELAS); sset(q2, "intensity", 14.0); sset(q2, "attenuation_radius", 1100.0)
        sset(q2, "use_temperature", True); sset(q2, "temperature", 2300.0); sset(q2, "source_radius", 6.0); sset(q2, "volumetric_scattering_intensity", 2.0)
    # ---- görünmez sınırlar ----
    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    i = 0
    while f"sinir{i}_a" in I:
        c, e = kutu(f"sinir{i}")
        s_ = spawn(unreal.StaticMeshActor, c, R(), f"Sinir{i}"); smc = s_.static_mesh_component; smc.set_static_mesh(cube)
        s_.set_actor_scale3d(V(e.x / 50.0, e.y / 50.0, e.z / 50.0)); s_.set_actor_hidden_in_game(True)
        smc.set_editor_property("cast_shadow", False)
        smc.set_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA, unreal.CollisionResponseType.ECR_IGNORE)
        smc.set_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY, unreal.CollisionResponseType.ECR_IGNORE)
        i += 1
    log("sınır", i)
    # müzik
    muz = spawn(unreal.AmbientSound, V(0, 0, 300), R(), "Muzik"); ac = muz.get_component_by_class(unreal.AudioComponent)
    w = eal.load_asset("/Game/Sisli/Ses/Sisli_Ambiyans")
    if w: ac.set_sound(w); sset(ac, "allow_spatialization", False); sset(ac, "volume_multiplier", 0.7)
    b = {"1": I["baslangic"], "2": I["odak2"], "3": I["donus_iskele"]}[bl]
    spawn(unreal.PlayerStart, V(b[0], b[1], 95.0), R(yaw=yaw0 if bl == "1" else -90.0), "Baslangic")
    les.save_current_level(); log("kaydedildi", MAP)
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/kur_oda_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
