# L_Sisli: ortam + REANIMAL ışık/sis/post-process değerleri (REANIMAL-RE/analiz/atmosfer_presetleri.txt).
import unreal, json, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal = unreal.EditorAssetLibrary
MAP = "/Game/Sisli/Maps/L_Sisli"
J = json.load(open("C:/Users/Onur/Sisli/Unreal/SourceArt/Ortam/sahne_ue.json"))
V = lambda x, y, z: unreal.Vector(x, y, z)
R = lambda pitch=0, yaw=0, roll=0: unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)
def sset(obj, name, val):
    try: obj.set_editor_property(name, val)
    except Exception as e: OUT.append("ÖZELLİK YOK %s.%s: %s" % (obj.get_class().get_name(), name, str(e)[:120]))
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if eal.does_asset_exist(MAP): eal.delete_asset(MAP)
    ok = les.new_level(MAP); log("yeni seviye", ok)
    def spawn(cls, loc=V(0, 0, 0), rot=R(), label=None):
        a = eas.spawn_actor_from_class(cls, loc, rot)
        if a is None: raise RuntimeError("spawn başarısız: %s" % cls)
        if label: a.set_actor_label(label)
        return a
    # --- ortam mesh'leri (dünya uzayında, orijinde) ---
    n = 0
    for p in eal.list_assets("/Game/Sisli/Ortam", recursive=True):
        a = eal.load_asset(p)
        if isinstance(a, unreal.StaticMesh) and not a.get_name().startswith("SM_Dyn_"):
            act = eas.spawn_actor_from_class(unreal.StaticMeshActor, V(0, 0, 0), R())
            if act is None: log("SPAWN YOK", a.get_name()); continue
            act.static_mesh_component.set_static_mesh(a); act.set_actor_label(a.get_name()); n += 1
            if a.get_name().startswith("SM_PH_") or "Cerceve" in a.get_name() or "Tel" in a.get_name():   # küçük eşyalar kamerayı itmesin
                act.static_mesh_component.set_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA, unreal.CollisionResponseType.ECR_IGNORE)
            if "EvKesit" in a.get_name():
                act.tags = [unreal.Name("EvKesit")]; act.static_mesh_component.set_editor_property("cast_hidden_shadow", True)
                act.static_mesh_component.set_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA, unreal.CollisionResponseType.ECR_IGNORE)
            if "Tel" in a.get_name() or "Siluet" in a.get_name():
                act.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    log("mesh aktörü", n)
    # --- ay (REANIMAL Overworld: 9500K, 1.2 lux, hacimsel saçılım .25) ---
    ay = spawn(unreal.DirectionalLight, V(0, 0, 1000), R(pitch=-38, yaw=70), "Ay")
    c = ay.light_component
    sset(c, "intensity", 0.6); sset(c, "use_temperature", True); sset(c, "temperature", 9500.0)
    sset(c, "volumetric_scattering_intensity", 0.25); sset(c, "light_source_angle", 1.0)
    sset(c, "atmosphere_sun_light", False)
    # --- gökyüzü ışığı (B6EAFF tonlu, belirtilen küp doku) ---
    sky = spawn(unreal.SkyLight, V(0, 0, 500), R(), "GokIsigi")
    s = sky.light_component
    cube = unreal.load_asset("/Engine/EngineResources/GrayDarkTextureCube.GrayDarkTextureCube")
    sset(s, "source_type", unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
    if cube: sset(s, "cubemap", cube)
    sset(s, "intensity", 1.6)
    sset(s, "light_color", unreal.Color(r=182, g=234, b=255, a=255))
    sset(s, "lower_hemisphere_is_black", False)
    sset(s, "volumetric_scattering_intensity", 0.05)
    sset(s, "mobility", unreal.ComponentMobility.MOVABLE)
    log("küp doku", cube)
    # --- sokak lambası ---
    L = J["lights"]
    lp = L["Lamba"]["loc"]
    sp = spawn(unreal.SpotLight, V(*lp), R(pitch=-90), "SokakLambasi")
    k = sp.spot_light_component
    sset(k, "intensity_units", unreal.LightUnits.CANDELAS); sset(k, "intensity", 90.0)
    sset(k, "light_color", unreal.Color(r=205, g=228, b=255, a=255))
    sset(k, "attenuation_radius", 1600.0); sset(k, "outer_cone_angle", 52.0); sset(k, "inner_cone_angle", 12.0)
    sset(k, "source_radius", 6.0); sset(k, "volumetric_scattering_intensity", 2.0)
    sset(k, "mobility", unreal.ComponentMobility.MOVABLE)
    gp = L["LambaCam"]["loc"]
    pl = spawn(unreal.PointLight, V(*gp), R(), "LambaCami")
    q = pl.point_light_component
    sset(q, "intensity_units", unreal.LightUnits.CANDELAS); sset(q, "intensity", 6.0)
    sset(q, "light_color", unreal.Color(r=205, g=228, b=255, a=255)); sset(q, "attenuation_radius", 300.0)
    sset(q, "cast_shadows", False); sset(q, "volumetric_scattering_intensity", 4.0)
    # --- sıcak pencere ---
    if "SicakPencere" in L:
        wl = L["SicakPencere"]["loc"]
        side = 1 if wl[0] > 0 else -1
        rl = spawn(unreal.RectLight, V(wl[0], wl[1], wl[2]), R(yaw=180 if side > 0 else 0), "SicakPencere")
        r = rl.rect_light_component
        sset(r, "intensity_units", unreal.LightUnits.CANDELAS); sset(r, "intensity", 25.0)
        sset(r, "use_temperature", True); sset(r, "temperature", 2400.0)
        sset(r, "source_width", 90.0); sset(r, "source_height", 130.0)
        sset(r, "attenuation_radius", 900.0); sset(r, "volumetric_scattering_intensity", 3.0)
    # --- yükseklik sisi (hacimsel) ---
    fog = spawn(unreal.ExponentialHeightFog, V(0, 0, -150), R(), "Sis")
    f = fog.component
    sset(f, "fog_density", 0.08); sset(f, "fog_height_falloff", 0.22)
    sset(f, "fog_inscattering_luminance", unreal.LinearColor(0.03, 0.05, 0.07, 1))
    sset(f, "enable_volumetric_fog", True)
    sset(f, "volumetric_fog_albedo", unreal.Color(r=180, g=200, b=225, a=255))
    sset(f, "volumetric_fog_extinction_scale", 1.5)
    sset(f, "volumetric_fog_distance", 6000.0)
    sset(f, "volumetric_fog_scattering_distribution", 0.35)
    sset(f, "volumetric_fog_static_lighting_scattering_intensity", 0.0)
    # --- post-process (sınırsız) ---
    ppv = spawn(unreal.PostProcessVolume, V(0, 0, 0), R(), "PostProcess")
    sset(ppv, "unbound", True)
    ps = ppv.get_editor_property("settings")
    def pp(name, val):
        try:
            sset(ps, "override_" + name, True)
        except Exception: pass
        sset(ps, name, val)
    pp("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM)
    pp("auto_exposure_min_brightness", 1.0); pp("auto_exposure_max_brightness", 1.0)
    pp("auto_exposure_bias", 1.8)
    pp("bloom_intensity", 1.0); pp("bloom_threshold", 0.0)
    pp("film_grain_intensity", 0.25)
    pp("vignette_intensity", 0.6)
    pp("scene_fringe_intensity", 0.2)
    pp("color_contrast_shadows", unreal.Vector4(1.2, 1.2, 1.2, 1.0))
    pp("color_offset_shadows", unreal.Vector4(0.006, 0.012, 0.02, 0.0))
    pp("color_gain_midtones", unreal.Vector4(1.99, 2.0, 1.87, 1.0))
    pp("film_slope", 0.63); pp("film_toe", 0.726)
    pp("depth_of_field_fstop", 5.6); pp("depth_of_field_focal_distance", 1250.0)
    pp("motion_blur_amount", 0.0)
    pp("dynamic_global_illumination_method", unreal.DynamicGlobalIlluminationMethod.NONE)
    pp("reflection_method", unreal.ReflectionMethod.SCREEN_SPACE)
    pp("ambient_occlusion_intensity", 0.75)
    sset(ppv, "settings", ps)
    # --- ses: müzik (konumsuz döngü) + lamba vızıltısı (3B) ---
    at = unreal.AssetToolsHelpers.get_asset_tools()
    def wav(fn):
        ap = "/Game/Sisli/Ses/" + fn
        if not eal.does_asset_exist(ap):
            t = unreal.AssetImportTask(); t.filename = "C:/Users/Onur/Sisli/Ses/" + fn + ".wav"; t.destination_path = "/Game/Sisli/Ses"
            t.automated = True; t.save = True; t.replace_existing = True; at.import_asset_tasks([t])
        w = eal.load_asset(ap); sset(w, "looping", True); eal.save_loaded_asset(w); return w
    muz = spawn(unreal.AmbientSound, V(0, 0, 300), R(), "Muzik")
    ac = muz.get_component_by_class(unreal.AudioComponent)
    ac.set_sound(wav("Sisli_Ambiyans")); sset(ac, "allow_spatialization", False); sset(ac, "volume_multiplier", 0.7); sset(ac, "auto_activate", True)
    vz = spawn(unreal.AmbientSound, V(*lp), R(), "LambaVizilti")
    vc = vz.get_component_by_class(unreal.AudioComponent)
    vc.set_sound(wav("Lamba_Vizilti")); sset(vc, "volume_multiplier", 0.35); sset(vc, "auto_activate", True)
    sset(vc, "override_attenuation", True)
    att = vc.get_editor_property("attenuation_overrides")
    sset(att, "attenuation_shape_extents", V(150, 0, 0)); sset(att, "falloff_distance", 1300.0)
    sset(vc, "attenuation_overrides", att)
    log("ses eklendi")
    # --- genişletme: mekanikler, ek ışıklar, fizik ---
    D = J.get("dinamik", {}); I = J.get("isaret", {})
    def bpcls(n): return eal.load_asset("/Game/Sisli/Mekanik/" + n).generated_class()
    def spawn_bp(n, loc, yaw=0.0, label=None):
        a = eas.spawn_actor_from_class(bpcls(n), V(*loc), R(yaw=yaw))
        if a is None: raise RuntimeError("BP yerleşmedi " + n)
        a.set_actor_label(label or n); return a
    def nokta(loc, label):
        return spawn(unreal.TargetPoint, V(loc[0], loc[1], loc[2] + 90), R(yaw=-90), label)
    don_meydan = nokta(I["donus_meydan"], "Donus_Meydan"); don_iskele = nokta(I["donus_iskele"], "Donus_Iskele")
    anahtar = spawn_bp("BP_Anahtar", D["Anahtar"]["loc"], D["Anahtar"]["yaw"], "Anahtar")
    kapi = spawn_bp("BP_Kapi", D["CitKapisi"]["loc"], D["CitKapisi"]["yaw"], "CitKapisi"); sset(kapi, "Anahtar", anahtar)
    spawn_bp("BP_EvKapisi", D["EvKapisi"]["loc"], D["EvKapisi"]["yaw"], "EvKapisi")
    pj = spawn_bp("BP_Projektor", I["projektor"], 0.0, "Projektor")
    m = I["projektor_hedef_merkez"]; sset(pj, "Merkez", V(m[0], m[1], 0.0)); sset(pj, "Donus", don_meydan)
    sk = I["su_olum_kutusu"]
    ol = spawn_bp("BP_Olum", [(sk["x"][0] + sk["x"][1]) / 2, (sk["y"][0] + sk["y"][1]) / 2, (sk["z"][0] + sk["z"][1]) / 2], 0.0, "SuOlum")
    obx = V((sk["x"][1] - sk["x"][0]) / 2, (sk["y"][1] - sk["y"][0]) / 2, (sk["z"][1] - sk["z"][0]) / 2)
    ol.get_component_by_class(unreal.BoxComponent).set_box_extent(obx); sset(ol, "Boyut", obx)
    sset(ol, "Donus", don_iskele)
    spawn_bp("BP_Son", I["son_tetik"], 0.0, "Son")
    spawn_bp("BP_Fener", [0, 0, 0], 0.0, "Fener")
    ik = I.get("ic_mekan_kutu")
    if ik:
        im = spawn_bp("BP_IcMekan", [(ik["x"][0] + ik["x"][1]) / 2, (ik["y"][0] + ik["y"][1]) / 2, 150.0], 0.0, "IcMekan")
        bx = V((ik["x"][1] - ik["x"][0]) / 2 - 10, (ik["y"][1] - ik["y"][0]) / 2 - 10, 170.0)
        im.get_component_by_class(unreal.BoxComponent).set_box_extent(bx); sset(im, "Boyut", bx)
    # ek sokak lambaları (biri titrek)
    for i, p in enumerate(I.get("lambalar_ek", [])):
        if i == I.get("titrek_lamba", -1):
            t = spawn_bp("BP_Titrek", p, 0.0, f"Lamba_Titrek{i}")
            ic = t.get_component_by_class(unreal.PointLightComponent)
            ic.set_light_color(unreal.LinearColor(0.8, 0.9, 1.0, 1.0)); ic.set_attenuation_radius(1500.0)
            sset(t, "TemelSiddet", 60.0); sset(t, "Sans", 0.05)
        else:
            s2 = spawn(unreal.SpotLight, V(*p), R(pitch=-90), f"Lamba_Ek{i}")
            k2 = s2.spot_light_component
            sset(k2, "intensity_units", unreal.LightUnits.CANDELAS); sset(k2, "intensity", 80.0)
            sset(k2, "light_color", unreal.Color(r=205, g=228, b=255, a=255)); sset(k2, "attenuation_radius", 1500.0)
            sset(k2, "outer_cone_angle", 50.0); sset(k2, "inner_cone_angle", 12.0); sset(k2, "volumetric_scattering_intensity", 2.0)
    # iç mekân: masadaki fener (sıcak, loş) + arka odada titreyen asılı ampul
    fm = I["fener_masa"]
    fl = spawn(unreal.PointLight, V(fm[0], fm[1], fm[2] + 8), R(), "MasaFeneri")
    q2 = fl.point_light_component
    sset(q2, "intensity_units", unreal.LightUnits.CANDELAS); sset(q2, "intensity", 3.0); sset(q2, "attenuation_radius", 450.0)
    sset(q2, "use_temperature", True); sset(q2, "temperature", 2100.0); sset(q2, "source_radius", 2.0)
    al = spawn_bp("BP_Titrek", I["arka_oda_lamba"], 0.0, "ArkaOdaAmpul")
    sset(al, "TemelSiddet", 3.0); sset(al, "Sans", 0.07)
    # itilebilir sandıklar (fizik)
    for n in ("Sandik0", "Sandik1"):
        if n not in D: continue
        a = spawn(unreal.StaticMeshActor, V(*D[n]["loc"]), R(yaw=D[n]["yaw"]), n)
        c = a.static_mesh_component
        c.set_mobility(unreal.ComponentMobility.MOVABLE)
        c.set_static_mesh(eal.load_asset(f"/Game/Sisli/Ortam/SM_Dyn_{n}/SM_Dyn_{n}"))
        c.set_simulate_physics(True); c.set_mass_override_in_kg("", 22.0, True); c.set_linear_damping(1.5); c.set_angular_damping(2.0)
    log("mekanikler yerleşti")
    # --- başlangıç: meydanın güneyi, kuzeye bakar ---
    bs = I.get("baslangic", J["char"])
    spawn(unreal.PlayerStart, V(bs[0], bs[1], 90.0), R(yaw=-90), "Baslangic")
    les.save_current_level()
    log("kaydedildi", MAP)
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/kur_seviye_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
