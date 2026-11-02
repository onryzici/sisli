# Karakteri Unreal için dışa aktarır:
#  - HSV renk ayarlı doku → numpy ile yeni PNG (FBX node ağacını taşımaz)
#  - prosedürel maske malzemesi → Cycles ile Base Color pişirme (UV: smart project)
#  - FBX (iskelet + mesh), dokular SourceArt klasörüne
# kullanım: blender -b cocuk_v2.blend -P disa_aktar.py -- --out C:/Users/Onur/Sisli/Unreal/SourceArt/Cocuk
import bpy, sys, os, numpy as np
argv = sys.argv[sys.argv.index("--")+1:]
OUT = argv[argv.index("--out")+1]; os.makedirs(OUT, exist_ok=True)
MASKESIZ = "--maskesiz" in argv     # maske + kayış atılır, kaşlar kalır (2026-11-02: maske kaldırıldı)
sc = bpy.context.scene
if MASKESIZ:
    for ad in ("Maske", "Kayis"):
        if ad in sc.objects: bpy.data.objects.remove(sc.objects[ad]); print("ATILDI", ad)

# şaşılık: çocuk hedefleri göz yuvalarını dışa kaydırmış, göz küreleri yerinde kalmış → iris kapak aralığının burun ucunda.
# goz_ortak: önden ortografik çekimde iris ↔ kapak aralığı ortası farkını ölçer, gözü kendi merkezi etrafında dışa çevirir (yinelemeli).
if MASKESIZ and "Gozler" in sc.objects:
    sys.path.append("C:/Users/Onur/Sisli/Blender"); import goz_ortak
    kk = os.path.join(OUT, "goz_kontrol"); os.makedirs(kk, exist_ok=True)
    goz_ortak.duzelt(sc, sc.objects["Gozler"], kk)
    if "GozKam" in sc.objects: bpy.data.objects.remove(sc.objects["GozKam"])

def rgb_to_hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a[..., :3].max(-1); mn = a[..., :3].min(-1); d = mx - mn
    h = np.zeros_like(mx); s = np.where(mx > 0, d / np.maximum(mx, 1e-8), 0); v = mx
    m = d > 1e-8
    rc = np.where(m, (mx - r) / np.maximum(d, 1e-8), 0); gc = np.where(m, (mx - g) / np.maximum(d, 1e-8), 0); bc = np.where(m, (mx - b) / np.maximum(d, 1e-8), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2 + rc - bc, 4 + gc - rc)); h = (h / 6.0) % 1.0
    return h, s, v
def hsv_to_rgb(h, s, v):
    i = np.floor(h * 6).astype(int) % 6; f = h * 6 - np.floor(h * 6)
    p = v * (1 - s); q = v * (1 - s * f); t = v * (1 - s * (1 - f))
    r = np.choose(i, [v, q, p, p, t, v]); g = np.choose(i, [t, v, v, q, p, p]); b = np.choose(i, [p, p, t, v, v, q])
    return np.stack([r, g, b], -1)

def tinted_image(img, hue, sat, val, name):
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    # pixels doğrusal değil, görüntü sRGB kodlu ise Blender pixels'i görüntü uzayında döndürür; HSV düğümü doğrusal uzayda çalışır → yaklaşık eşdeğer
    H, S, V = rgb_to_hsv(px)
    H = (H + hue - 0.5) % 1.0; S = np.clip(S * sat, 0, 1); V = V * val
    out = np.concatenate([hsv_to_rgb(H, S, V), px[..., 3:4]], -1)
    new = bpy.data.images.new(name, w, h, alpha=True); new.pixels = out.ravel().tolist()
    new.filepath_raw = os.path.join(OUT, name + ".png"); new.file_format = 'PNG'; new.save()
    return new

# 1) HSV düğümlerini pişir
for m in bpy.data.materials:
    if not m.node_tree: continue
    N = m.node_tree.nodes; L = m.node_tree.links
    for hsv in [n for n in N if n.type == 'HUE_SAT']:
        src = hsv.inputs["Color"].links[0].from_node if hsv.inputs["Color"].links else None
        if not src or src.type != 'TEX_IMAGE': continue
        img = tinted_image(src.image, hsv.inputs["Hue"].default_value, hsv.inputs["Saturation"].default_value, hsv.inputs["Value"].default_value, "T_" + m.name.replace(".", "_") + "_D")
        src.image = img
        out_sock = hsv.outputs["Color"].links[0].to_socket
        L.new(src.outputs["Color"], out_sock); N.remove(hsv)
        print("RENK PİŞTİ", m.name, img.size[:])

# 2) diğer doku görüntülerini kopyala (FBX yolu için)
for img in bpy.data.images:
    if img.source == 'FILE' and img.filepath and not img.filepath.startswith(OUT) and os.path.exists(bpy.path.abspath(img.filepath)):
        dst = os.path.join(OUT, os.path.basename(bpy.path.abspath(img.filepath)))
        if not os.path.exists(dst):
            import shutil; shutil.copy(bpy.path.abspath(img.filepath), dst)
        img.filepath = dst

# 3) maske: UV + Base Color pişir
mask = sc.objects.get("Maske")
def maske_pisir(mask):
    bpy.ops.object.select_all(action='DESELECT'); mask.select_set(True); bpy.context.view_layer.objects.active = mask
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.01); bpy.ops.object.mode_set(mode='OBJECT')
    mat = mask.data.materials[0]; N = mat.node_tree.nodes; L = mat.node_tree.links
    bake = bpy.data.images.new("T_Maske_D", 2048, 2048); tn = N.new("ShaderNodeTexImage"); tn.image = bake; N.active = tn
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 16; sc.cycles.device = 'GPU'
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = 'OPTIX'; prefs.get_devices()
        for d in prefs.devices: d.use = True
    except Exception as e: print("GPU ayarı", e)
    sc.render.bake.use_pass_direct = False; sc.render.bake.use_pass_indirect = False; sc.render.bake.margin = 8
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
    bake.filepath_raw = os.path.join(OUT, "T_Maske_D.png"); bake.file_format = 'PNG'; bake.save()
    # maske malzemesini sade dokulu hale getir
    b = N["Principled BSDF"]
    for l in list(b.inputs["Base Color"].links): L.remove(l)
    L.new(tn.outputs["Color"], b.inputs["Base Color"])
    for l in list(b.inputs["Normal"].links): L.remove(l)
    print("MASKE PİŞTİ")
if mask is not None:
    maske_pisir(mask)
    # 4) gereksiz: kaş (maske altında) — maskesiz kipte kaşlar kalır
    if "Kas" in sc.objects: bpy.data.objects.remove(sc.objects["Kas"])
else:
    print("MASKE YOK — pişirme atlandı, kaşlar korundu")

# 5) FBX — Unreal için santimetre: sahne birimi 0.01, armatür ×100 uygulanmış (kök kemikte ölçek kalmasın)
sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 0.01
arm = next(o for o in sc.objects if o.type == 'ARMATURE')
arm.scale = (100, 100, 100)
bpy.ops.object.select_all(action='DESELECT')
for o in sc.objects:
    if o.type in ('ARMATURE', 'MESH'): o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
print("ARMATÜR ölçek", tuple(arm.scale), "Head yerel", tuple(round(x, 2) for x in arm.data.bones["Head"].head_local))
bpy.ops.object.select_all(action='SELECT')
for o in sc.objects:
    if o.type not in ('ARMATURE', 'MESH'): o.select_set(False)
fbx = os.path.join(OUT, "SK_Cocuk.fbx")
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={'ARMATURE', 'MESH'}, apply_scale_options='FBX_SCALE_UNITS',
                         axis_forward='-Y', axis_up='Z', add_leaf_bones=False, bake_anim=False, path_mode='STRIP', embed_textures=False,
                         primary_bone_axis='Y', secondary_bone_axis='X', mesh_smooth_type='FACE', use_armature_deform_only=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath), "cocuk_v2_export.blend"))
print("FBX", fbx)
