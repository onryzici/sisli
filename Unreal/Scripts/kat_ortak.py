# Kule katları için ortak seviye yardımcıları (kur_uyanis.py'nin kuralları: model sınır kutusundan zemine oturur, görünür eş düzlemli yüzey yok,
# set kapalı; atmosfer REANIMAL presetleri: sabit pozlama, bloom eşik 0, gren, vinyet, hacimsel sis, Lumen yok).
# Kullanım: from kat_ortak import Kat; k = Kat("/Game/Uyanis/Maps/L_Kat01"); ... k.atmosfer(); k.kaydet()
import unreal, math, os
eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary; at = unreal.AssetToolsHelpers.get_asset_tools()
V = lambda x, y, z: unreal.Vector(x, y, z)
R = lambda pitch=0, yaw=0, roll=0: unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)
FAB = "/Game/Uyanis/Fab"; SMI = "/Game/Uyanis/Sahne"; YAT = f"{FAB}/Yat"
YAT_AD = {"Floresan": "Fluorescent_Ceiling_Lamp_vidrear_High", "Sarkit": "Metal_Pendant_Light_vgyide1aw_High", "Defter": "Old_Book_wldocam_High",
          "Tabure": "Old_Metal_Stool_ukknbeyaw_High", "Sandalye": "Dirty_Metal_Chair_ukikdggbw_High", "Dolap": "Rusty_Metal_Cabinet_vjhledeaw_High",
          "Masa": "Wooden_Table_With_Drawer_vfvndhsga_High", "KafesLamba": "Rusty_Bulkhead_Light_vgyidfpaw_High", "Anahtarlik": "Keys"}

class Kat:
    def __init__(self, harita, log):
        self.log = log; self.MAP = harita
        self.les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); self.eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        if eal.does_asset_exist(harita): eal.delete_asset(harita)
        if not self.les.new_level(harita): raise RuntimeError("new_level başarısız " + harita)
        self.KUP = unreal.load_asset("/Engine/BasicShapes/Cube.Cube"); self.SIL = unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")
        self.M_MS = eal.load_asset("/Game/Uyanis/Malzeme/M_MS"); self.MIC = {}; self.SMC = {}; self.KATILAR = []; self.PROPS = []
    def sset(self, o, k, v):
        try: o.set_editor_property(k, v)
        except Exception as e: self.log("ÖZELLİK YOK %s.%s: %s" % (type(o).__name__, k, str(e)[:90]))
    def bpcls(self, n): a = eal.load_asset("/Game/Sisli/Mekanik/" + n); return a.generated_class() if a else None
    def smi(self, ad, ebeveyn, skal=None, vek=None):
        if ad in self.MIC: return self.MIC[ad]
        p = f"{SMI}/MI_{ad}"
        if eal.does_asset_exist(p):
            m = eal.load_asset(p)
        else:
            m = at.create_asset("MI_" + ad, SMI, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(m, ebeveyn)
        for k, v in (skal or {}).items(): mel.set_material_instance_scalar_parameter_value(m, k, v)
        for k, v in (vek or {}).items(): mel.set_material_instance_vector_parameter_value(m, k, unreal.LinearColor(*v, 1) if len(v) == 3 else unreal.LinearColor(*v))
        eal.save_loaded_asset(m); self.MIC[ad] = m; return m
    def yz(self, ad): return eal.load_asset(f"{FAB}/Yuzey/{ad}/MI_{ad}")
    def spawn(self, cls, loc=V(0, 0, 0), rot=R(), etiket=None):
        a = self.eas.spawn_actor_from_class(cls, loc, rot)
        if a is None: raise RuntimeError("spawn başarısız %s" % cls)
        if etiket: a.set_actor_label(etiket)
        return a
    def kutu(self, etiket, x0, x1, y0, y1, z0, z1, mt, golge=True, carpisma=True, gizli=False):
        a = self.spawn(unreal.StaticMeshActor, V((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), R(), etiket)
        c = a.static_mesh_component; c.set_static_mesh(self.KUP); c.set_material(0, mt)
        a.set_actor_scale3d(V(abs(x1 - x0) / 100.0, abs(y1 - y0) / 100.0, abs(z1 - z0) / 100.0)); self.sset(c, "cast_shadow", golge)
        if not carpisma: c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        if gizli:
            a.set_actor_hidden_in_game(True); self.sset(c, "cast_shadow", False)
            c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA, unreal.CollisionResponseType.ECR_IGNORE)
            c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY, unreal.CollisionResponseType.ECR_IGNORE)
        else:
            self.KATILAR.append((etiket, (min(x0, x1), min(y0, y1), min(z0, z1)), (max(x0, x1), max(y0, y1), max(z0, z1))))
        return a
    def mesh(self, ad):
        if ad not in self.SMC:
            yollar = [f"{YAT}/{ad}/{YAT_AD[ad]}"] if ad in YAT_AD else []
            yollar += [f"{FAB}/UB/{ad}/SM_{ad}", f"{FAB}/Oyuncak/{ad}", f"{FAB}/Ranza/bunk_bed/StaticMeshes/{ad}"]
            for p in yollar:
                if eal.does_asset_exist(p): self.SMC[ad] = eal.load_asset(p); break
            else: raise RuntimeError("mesh yok " + ad)
        return self.SMC[ad]
    def koy(self, ad, x, y, yaw=0.0, zemin=0.0, gomme=1.0, olcek=1.0, carpisma="karmasik", etiket=None, malzeme=None):
        """Sınır kutusunun tabanı zemine oturur. carpisma: karmasik | yok"""
        sm = self.mesh(ad); bb = sm.get_bounding_box(); s = olcek if isinstance(olcek, (tuple, list)) else (olcek, olcek, olcek)
        z = zemin - bb.min.z * s[2] - gomme
        a = self.spawn(unreal.StaticMeshActor, V(x, y, z), R(yaw=yaw), etiket or ad)
        c = a.static_mesh_component; c.set_static_mesh(sm); a.set_actor_scale3d(V(*s))
        if malzeme is not None:
            for i in range(c.get_num_materials()): c.set_material(i, malzeme)
        if carpisma == "yok": c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA, unreal.CollisionResponseType.ECR_IGNORE)
        cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)); xs, ys = [], []
        for bx in (bb.min.x * s[0], bb.max.x * s[0]):
            for by in (bb.min.y * s[1], bb.max.y * s[1]):
                xs.append(x + bx * cy - by * sy); ys.append(y + bx * sy + by * cy)
        self.PROPS.append((etiket or ad, (min(xs), min(ys), z + bb.min.z * s[2]), (max(xs), max(ys), z + bb.max.z * s[2])))
        return a
    def boyut(self, ad):
        bb = self.mesh(ad).get_bounding_box(); return (bb.max.x - bb.min.x, bb.max.y - bb.min.y, bb.max.z - bb.min.z)
    def isik(self, cls, etiket, loc, rot=R(), **kw):
        a = self.spawn(cls, loc, rot, etiket); c = a.get_component_by_class(unreal.LightComponent)
        if cls is not unreal.DirectionalLight: self.sset(c, "intensity_units", unreal.LightUnits.CANDELAS)
        for k, v in kw.items(): self.sset(c, k, v)
        return a
    def atmosfer(self, gok=1.2, sis=0.03, exp=2.4, ay=None):
        """İç mekân: koyu gök ışığı (B6EAFF), hacimsel sis, REANIMAL post-process. ay=(şiddet, pitch, yaw) verilirse yönlü ışık."""
        if ay:
            d = self.isik(unreal.DirectionalLight, "Ay", V(0, 0, 2000), R(pitch=ay[1], yaw=ay[2]), intensity=ay[0], use_temperature=True, temperature=9500.0,
                          volumetric_scattering_intensity=2.4, light_source_angle=0.4)
            self.sset(d.light_component, "atmosphere_sun_light", False)
        sky = self.spawn(unreal.SkyLight, V(0, 0, 600), R(), "GokIsigi"); s = sky.light_component
        self.sset(s, "source_type", unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP); self.sset(s, "cubemap", unreal.load_asset("/Engine/EngineResources/GrayDarkTextureCube.GrayDarkTextureCube"))
        self.sset(s, "intensity", gok); self.sset(s, "light_color", unreal.Color(r=0xB6, g=0xEA, b=0xFF, a=255)); self.sset(s, "lower_hemisphere_is_black", False); self.sset(s, "mobility", unreal.ComponentMobility.MOVABLE)
        fog = self.spawn(unreal.ExponentialHeightFog, V(0, 0, -100), R(), "Sis"); fc = fog.component
        self.sset(fc, "fog_density", sis); self.sset(fc, "fog_height_falloff", 0.06); self.sset(fc, "fog_inscattering_luminance", unreal.LinearColor(0.0035, 0.007, 0.0095, 1))
        self.sset(fc, "enable_volumetric_fog", True); self.sset(fc, "volumetric_fog_albedo", unreal.Color(r=118, g=146, b=160, a=255))
        self.sset(fc, "volumetric_fog_extinction_scale", 1.15); self.sset(fc, "volumetric_fog_distance", 12000.0); self.sset(fc, "volumetric_fog_static_lighting_scattering_intensity", 0.0)
        ppv = self.spawn(unreal.PostProcessVolume, V(0, 0, 0), R(), "PostProcess"); ppv.set_editor_property("unbound", True); ps = ppv.get_editor_property("settings")
        def pp(k, v):
            try: ps.set_editor_property("override_" + k, True)
            except Exception: pass
            self.sset(ps, k, v)
        pp("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM); pp("auto_exposure_min_brightness", 1.0); pp("auto_exposure_max_brightness", 1.0)
        pp("auto_exposure_bias", exp); pp("bloom_intensity", 0.7); pp("bloom_threshold", 0.0); pp("film_grain_intensity", 0.42); pp("film_grain_intensity_shadows", 1.0)
        pp("film_grain_intensity_midtones", 0.9); pp("film_grain_intensity_highlights", 0.5); pp("vignette_intensity", 0.75); pp("scene_fringe_intensity", 0.25)
        pp("color_contrast_shadows", unreal.Vector4(1.15, 1.15, 1.15, 1.0)); pp("color_saturation", unreal.Vector4(0.82, 0.82, 0.82, 1.0))
        pp("color_offset_shadows", unreal.Vector4(0.0, 0.004, 0.009, 0.0)); pp("color_gain_highlights", unreal.Vector4(0.92, 1.0, 1.04, 1.0))
        pp("depth_of_field_fstop", float(os.environ.get("UY_FSTOP", "3.2"))); pp("depth_of_field_focal_distance", float(os.environ.get("UY_ODAK", "420"))); pp("motion_blur_amount", 0.0)
        pp("dynamic_global_illumination_method", unreal.DynamicGlobalIlluminationMethod.NONE); pp("reflection_method", unreal.ReflectionMethod.SCREEN_SPACE)
        pp("ambient_occlusion_intensity", 0.9); pp("ambient_occlusion_radius", 120.0)
        ppv.set_editor_property("settings", ps)
    def asansor_kabini(self, et, x, y, yon, mt_duvar, mt_metal, mt_zemin, H=320.0):
        """Ağzı (x, y)'de, yon=+1 ise +Y'ye, -1 ise -Y'ye açılan 200x240 kabin (içi yürünür). Dönüş: kabin iç merkezi."""
        y_ic = y - yon * 130.0
        y0, y1 = sorted((y, y - yon * 260.0))
        self.kutu(f"{et}_Zemin", x - 120, x + 120, y0, y1, -30, 0, mt_zemin)
        self.kutu(f"{et}_Tavan", x - 120, x + 120, y0, y1, H - 60, H - 30, mt_metal)
        self.kutu(f"{et}_SolDuvar", x - 135, x - 115, y0, y1, 0, H - 30, mt_metal)
        self.kutu(f"{et}_SagDuvar", x + 115, x + 135, y0, y1, 0, H - 30, mt_metal)
        yd = y - yon * 260.0
        self.kutu(f"{et}_ArkaDuvar", x - 135, x + 135, min(yd, yd - yon * 20.0), max(yd, yd - yon * 20.0), 0, H - 30, mt_metal)
        self.kutu(f"{et}_Lento", x - 135, x + 135, min(y, y + yon * 14), max(y, y + yon * 14), 230, H, mt_duvar)
        return V(x, y_ic, 0)
    def test_kamera(self):
        """UY_KAMERA="x y z pitch yaw fov": sabit sinema kamerası + her yeri kaplayan kamera alanı (kur_uyanis ile aynı)."""
        tk = os.environ.get("UY_KAMERA")
        if not tk: return
        kk = [float(v) for v in tk.split()]
        cam = self.spawn(self.bpcls("BP_SinemaKamera"), V(kk[0], kk[1], kk[2]), R(pitch=kk[3], yaw=kk[4]), "TestKamera")
        for a_, b_ in (("FOV", kk[5]), ("Takip", V(0, 0, 0)), ("MaxKayma", 0.0), ("Bakis", 0.0), ("Odak", V(kk[0], kk[1], 0))): self.sset(cam, a_, b_)
        cam.get_component_by_class(unreal.CameraComponent).set_editor_property("field_of_view", kk[5])
        z_ = self.spawn(self.bpcls("BP_KameraAlani"), V(1000, 1000, 150), R(), "TestKameraAlani")
        z_.get_component_by_class(unreal.BoxComponent).set_box_extent(V(5000, 5000, 1000), False)
        for a_, b_ in (("Kamera", cam), ("Boyut", V(5000, 5000, 1000)), ("Basta", True), ("Gecis", 0.0)): self.sset(z_, a_, b_)
    def baslangic(self, x, y, yaw, z=95.0):
        self.spawn(unreal.PlayerStart, V(x, y, z), R(yaw=yaw), "Baslangic")
    def kaydet(self):
        self.les.save_current_level(); self.log("kaydedildi", self.MAP)
