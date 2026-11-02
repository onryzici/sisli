# Sisli — "Sisli Rıhtım" ortamı: ara sokak → rıhtım → sise uzanan iskele.
# REANIMAL ışık dili (RE: REANIMAL-RE/analiz/atmosfer_presetleri.txt): soğuk 9500K ay, camgöbeği gökyüzü ışığı (B6EAFF),
# tek sokak lambası ışık havuzu, uzakta tek sıcak pencere, yoğun hacimsel sis, yüksek açılı uzun lens kamera.
# kullanım: blender -b -P sahne.py -- --blend sahne.blend [--render out.png --w 1920 --h 1080 --spp 128] [--json yerlesim.json]
import bpy, bmesh, sys, os, math, json, glob, random
from mathutils import Vector, Matrix, Euler
argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
def opt(k, d=None): return argv[argv.index(k)+1] if k in argv else d
random.seed(7)
PH = "C:/Users/Onur/Sisli/Indir/polyhaven"
CHAR = "C:/Users/Onur/Sisli/Blender/cocuk_v2.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; col = sc.collection
PLACE = []   # Unreal'e aktarım: {"mesh":ad, "loc":[], "rot":[], "scale":[]}

# ---------------- malzemeler ----------------
MATS = {}
def pbr(tex_id, scale=1.0, tint=(1, 1, 1), rough_mul=1.0, puddles=False):
    key = f"{tex_id}_{scale}_{tint}_{puddles}"
    if key in MATS: return MATS[key]
    d = f"{PH}/textures/{tex_id}"
    m = bpy.data.materials.new("M_" + tex_id + ("_islak" if puddles else "")); N = m.node_tree.nodes; L = m.node_tree.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(tc.outputs["UV"], mp.inputs["Vector"])
    def img(name, nonc=False):
        f = (glob.glob(f"{d}/{name}.*") or [None])[0]
        if not f: return None
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(f, check_existing=True)
        if nonc: t.image.colorspace_settings.name = 'Non-Color'
        L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    dif = img("Diffuse"); nor = img("nor_gl", True); rgh = img("Rough", True); arm = img("arm", True)
    if dif:
        mix = N.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs["Factor"].default_value = 1
        L.new(dif.outputs["Color"], mix.inputs[6]); mix.inputs[7].default_value = (*tint, 1); L.new(mix.outputs[2], b.inputs["Base Color"])
    if nor:
        nm = N.new("ShaderNodeNormalMap"); L.new(nor.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    rsrc = rgh.outputs["Color"] if rgh else None
    if not rsrc and arm:
        sp = N.new("ShaderNodeSeparateColor"); L.new(arm.outputs["Color"], sp.inputs["Color"]); rsrc = sp.outputs["Green"]
    if rsrc:
        mul = N.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = rough_mul; L.new(rsrc, mul.inputs[0]); rsrc = mul.outputs[0]
        if puddles:   # su birikintisi: dünya uzayı gürültü maskesi → düşük pürüz + koyu taban
            tc2 = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 6
            L.new(tc2.outputs["Object"], nz.inputs["Vector"])
            cr = N.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = 0.52; cr.inputs["From Max"].default_value = 0.58
            L.new(nz.outputs["Fac"], cr.inputs["Value"])
            mr = N.new("ShaderNodeMix"); mr.data_type = 'FLOAT'; L.new(cr.outputs["Result"], mr.inputs["Factor"]); L.new(rsrc, mr.inputs[2]); mr.inputs[3].default_value = 0.04
            rsrc = mr.outputs[0]
            dk = N.new("ShaderNodeMix"); dk.data_type = 'RGBA'; dk.blend_type = 'MULTIPLY'
            L.new(cr.outputs["Result"], dk.inputs["Factor"]); L.new(b.inputs["Base Color"].links[0].from_socket, dk.inputs[6]); dk.inputs[7].default_value = (0.45, 0.45, 0.45, 1)
            L.new(dk.outputs[2], b.inputs["Base Color"])
            m["puddle"] = True
        L.new(rsrc, b.inputs["Roughness"])
    m["tex"] = tex_id; m["scale"] = scale; m["tint"] = list(tint)
    MATS[key] = m; return m
def flat(name, col, rough=0.8, emit=None, estr=0.0):
    m = bpy.data.materials.new(name); b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    if emit: b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = estr
    return m

M_ASF = pbr("asphalt_03", 1.0, (0.40, 0.42, 0.46), 1.0, puddles=True)
M_KALD = pbr("cobblestone_floor_05", 1.0, (0.36, 0.38, 0.42), 1.0, puddles=True)
M_DUVAR = [pbr("brick_4", 1.0, (0.55, 0.52, 0.5)), pbr("blue_plaster_weathered", 1.0, (0.55, 0.6, 0.65)),
           pbr("black_painted_planks", 1.0, (0.9, 0.9, 0.9)), pbr("concrete_layers", 1.0, (0.5, 0.52, 0.55))]
M_CATI = pbr("ceramic_roof_01", 1.0, (0.35, 0.33, 0.33))
M_BETON = pbr("concrete_layers", 1.0, (0.4, 0.42, 0.45))
M_CAM = flat("M_Cam", (0.01, 0.012, 0.015), 0.08)
M_CERCEVE = flat("M_Cerceve", (0.05, 0.05, 0.05), 0.6)
M_SICAKCAM = flat("M_SicakCam", (0.2, 0.1, 0.04), 0.3, (1.0, 0.45, 0.15), 1.6)
M_SU = flat("M_Su", (0.004, 0.006, 0.008), 0.06)
M_TEL = flat("M_Tel", (0.01, 0.01, 0.01), 0.5)
M_SILUET = flat("M_Siluet", (0.02, 0.022, 0.025), 0.9)

def uv_cube(o, size=2.0):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=size, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode='OBJECT')

def quad(name, axis, coord, nsign, a0, a1, z0, z1, mat):
    """Tek yüzlü düzlem (pencere camı/çerçeve): axis düzleminde coord da, normal nsign yönüne bakar; içeriden görünmez."""
    if axis == "x": P = [(coord, a0, z0), (coord, a1, z0), (coord, a1, z1), (coord, a0, z1)]
    else: P = [(a0, coord, z0), (a1, coord, z0), (a1, coord, z1), (a0, coord, z1)]
    flip = (axis == "x" and nsign < 0) or (axis == "y" and nsign > 0)
    if flip: P = P[::-1]
    me = bpy.data.meshes.new(name); me.from_pydata(P, [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new(name="UVMap")
    for li, uv in zip(me.polygons[0].loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))): uvl.data[li].uv = uv
    o = bpy.data.objects.new(name, me); col.objects.link(o); me.materials.append(mat); o["static"] = True; return o

def box(name, x0, x1, y0, y1, z0, z1, mat, uv=2.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector(((v.co.x + .5) * (x1 - x0) + x0, (v.co.y + .5) * (y1 - y0) + y0, (v.co.z + .5) * (z1 - z0) + z0))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col.objects.link(o); me.materials.append(mat)
    if uv: uv_cube(o, uv)
    o["static"] = True; return o

# ---------------- zemin ----------------
Y0, Y1 = -18.0, 15.5
road = box("Yol", -2.6, 2.6, Y0, Y1, -0.05, 0.0, M_ASF, 4.0)
for s in (-1, 1):
    box(f"Kaldirim_{s}", min(s*2.6, s*4.2), max(s*2.6, s*4.2), Y0, Y1, -0.05, 0.14, M_KALD, 2.0)
# rıhtım duvarı + iskele önü platform
box("Rihtim", -9, 9, Y1, Y1 + 0.8, -2.2, 0.14, M_BETON, 2.0)
box("Su", -60, 60, Y1 + 0.8, 120, -1.95, -1.9, M_SU, 0)

# ---------------- evler ----------------
WIN_LIGHT = None
def house(side, y0, y1, h, mat, idx):
    global WIN_LIGHT
    xf = side * 4.2; xb = side * 11.0
    o = box(f"Ev_{side}_{idx}", min(xf, xb), max(xf, xb), y0, y1, 0.0, h, mat, 2.0)
    # beşik çatı (y boyunca mahya)
    bm = bmesh.new()
    ov = 0.35; rh = 2.4
    xa, xc = xf - side * ov, xb + side * ov; xm = (xa + xc) / 2
    pts = [(xa, y0 - ov, h), (xc, y0 - ov, h), (xm, y0 - ov, h + rh), (xa, y1 + ov, h), (xc, y1 + ov, h), (xm, y1 + ov, h + rh)]
    vs = [bm.verts.new(p) for p in pts]
    for f in [(0, 2, 1), (3, 4, 5), (0, 3, 5, 2), (1, 2, 5, 4), (0, 1, 4, 3)]: bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(f"Cati_{side}_{idx}"); bm.to_mesh(me); bm.free()
    r = bpy.data.objects.new(me.name, me); col.objects.link(r); me.materials.append(M_CATI); uv_cube(r, 2.0); r["static"] = True
    # pencereler (her kat 2-3)
    floors = int(h // 3.0)
    w = y1 - y0
    for fl in range(1, floors):
        n = max(1, int(w // 2.4))
        for k in range(n):
            yc = y0 + (k + 0.5) * w / n + random.uniform(-0.2, 0.2)
            zc = fl * 3.0 + 1.5
            xw = xf - side * 0.0
            lit = (WIN_LIGHT is None and side == 1 and fl == 2 and y0 > 6)
            quad(f"Cam_{side}_{idx}_{fl}_{k}", "x", xw - side * 0.01, -side, yc - 0.45, yc + 0.45, zc - 0.7, zc + 0.7, M_SICAKCAM if lit else M_CAM)
            for (a0, a1, b0, b1) in [(-0.52, 0.52, 0.68, 0.78), (-0.52, 0.52, -0.78, -0.68), (-0.52, -0.42, -0.78, 0.78), (0.42, 0.52, -0.78, 0.78), (-0.05, 0.05, -0.7, 0.7)]:
                quad(f"Cerceve_{side}_{idx}_{fl}_{k}", "x", xw - side * 0.02, -side, yc + a0, yc + a1, zc + b0, zc + b1, M_CERCEVE)
            if lit: WIN_LIGHT = (xw, yc, zc, side)
    return o
for side in (-1, 1):
    y = Y0 - 2; idx = 0
    while y < Y1 - 1:
        w = random.uniform(5.0, 7.5); w = min(w, Y1 - y)
        h = random.choice([6.0, 7.5, 9.0, 9.0, 10.5])
        house(side, y, y + w, h, random.choice(M_DUVAR), idx)
        y += w + random.choice([0.0, 0.0, 0.6]); idx += 1

# ---------------- Poly Haven modelleri ----------------
LIB = {}
def load_ph(asset, names=None, prefix=None, join_name=None):
    key = (asset, tuple(names or []), prefix)
    if key in LIB: return LIB[key]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glob.glob(f"{PH}/models/{asset}/*.gltf")[0])
    new = [o for o in bpy.data.objects if o not in before]
    keep = [o for o in new if o.type == 'MESH' and ((names and o.name in names) or (prefix and o.name.startswith(prefix)) or (not names and not prefix))]
    for o in new:
        if o not in keep: bpy.data.objects.remove(o)
    for o in keep:
        o.matrix_world = o.matrix_world.copy()
        o.parent = None
    # birleştir ve kaynağı sahneden kaldır (kopyalarla yerleştirilecek)
    bpy.ops.object.select_all(action='DESELECT')
    for o in keep: o.select_set(True)
    bpy.context.view_layer.objects.active = keep[0]
    if len(keep) > 1: bpy.ops.object.join()
    src = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    src.name = join_name or asset
    # orijini tabana-merkeze al
    bpy.context.view_layer.update()
    vs = [src.matrix_world @ v.co for v in src.data.vertices]
    cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2; cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2; cz = min(v.z for v in vs)
    src.data.transform(Matrix.Translation(-(Vector((cx, cy, cz)) - src.matrix_world.translation)))
    src.matrix_world = Matrix.Identity(4)
    col.objects.unlink(src)
    LIB[key] = src; return src
def put(src, loc, rotz=0.0, rotx=0.0, roty=0.0, s=1.0):
    o = bpy.data.objects.new(src.name + "_i", src.data); col.objects.link(o)
    o.location = loc; o.rotation_euler = Euler((math.radians(rotx), math.radians(roty), math.radians(rotz))); o.scale = (s, s, s)
    PLACE.append({"mesh": src.name, "loc": list(loc), "rot": [rotx, roty, rotz], "scale": s}); return o

lamp = load_ph("street_lamp_01")
car = load_ph("covered_car")
barrier = load_ph("concrete_road_barrier")
can = load_ph("metal_trash_can", prefix="metal_trash_can_rust", join_name="metal_trash_can_rust")
bag = load_ph("trashbag")
barrel = load_ph("Barrel_01")
crate = load_ph("old_military_crate", prefix="old_military_crate", join_name="old_military_crate")
wcrate = load_ph("wooden_crate_01")
tyre = load_ph("old_tyre")
ubox = load_ph("utility_box_01")
trunk = load_ph("dead_tree_trunk")
buoy = load_ph("lifebuoy")
rat = load_ph("street_rat")
pole = load_ph("modular_electricity_poles", prefix="preset_02", join_name="elektrik_diregi")
pier = load_ph("modular_wooden_pier", names=["modular_wooden_pier_section_01", "modular_wooden_pier_section_02", "modular_wooden_pier_section_03", "modular_wooden_pier_section_04"], join_name="iskele")
fence = load_ph("modular_chainlink_fence", names=["modular_chainlink_fence_double"], join_name="cit")
fgate = load_ph("modular_chainlink_fence", names=["modular_chainlink_fence_door_frame"], join_name="cit_kapi")
shutter = load_ph("rollershutter_door", names=["rollershutter_door_graffiti"], join_name="kepenk_kapi")
shutw = load_ph("rollershutter_window_01", names=["rollershutter_window_01"], join_name="kepenk_pencere")

# sokak lambası: direk sağ kaldırımda, kol yola uzanır
LAMP_POS = Vector((3.35, 4.6, 0.14))
put(lamp, LAMP_POS, rotz=float(opt("--lamprot", "180")))
put(car, (-1.55, 9.6, 0), rotz=7)
put(barrier, (1.6, 13.4, 0), rotz=16); put(barrier, (-0.4, 14.0, 0), rotz=-6)
put(can, (3.55, 0.9, 0.14), rotz=20); put(bag, (3.7, 0.1, 0.14), rotz=40); put(bag, (3.1, 1.7, 0.14), rotz=-30, s=0.85)
put(barrel, (-3.3, 14.2, 0.14)); put(barrel, (-2.7, 14.7, 0.14), rotz=40); put(barrel, (-2.1, 13.6, 0.32), rotx=90, rotz=70)
put(crate, (3.2, 14.6, 0.14), rotz=-12); put(wcrate, (3.6, 13.6, 0.14), rotz=25); put(wcrate, (3.5, 13.7, 0.47), rotz=10, s=0.9)
put(tyre, (2.0, -2.8, 0.08), rotx=90, rotz=30)
put(ubox, (-3.95, 2.6, 0.14), rotz=90)
put(trunk, (-1.2, -5.0, 0.12), rotz=28)
put(rat, (3.0, 1.5, 0.14), rotz=-60, s=1.2)
for y in (-11.0, 0.0, 11.0): put(pole, (-3.5, y, 0.14), rotz=90)
put(pier, (1.0, Y1 + 0.8 - 0.9, -2.62))
put(buoy, (2.4, Y1 + 4.0, 0.25), rotz=90)
for x in (-8.0, -6.0): put(fence, (x, Y1 + 0.35, 0.14))
put(fgate, (-4.0, Y1 + 0.35, 0.14))
# kepenkler: evlerin zemin katına
for side in (-1, 1):
    for k, y in enumerate([-9.0, -2.5, 3.5, 10.0]):
        src = shutter if (k + (side > 0)) % 2 == 0 else shutw
        put(src, (side * 4.13, y + (0.6 if side > 0 else 0), 0.14 if src is shutter else 0.9), rotz=90 if side < 0 else -90)

# elektrik telleri: direk tepeleri arasında sarkık eğri (+ sise kaybolan uçlar)
def wire(p0, p1, sag, name):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.008; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); n = 24; sp.points.add(n - 1)
    for i in range(n):
        t = i / (n - 1); p = p0.lerp(p1, t); p.z -= sag * 4 * t * (1 - t)
        sp.points[i].co = (*p, 1)
    o = bpy.data.objects.new(name, cu); col.objects.link(o); cu.materials.append(M_TEL); o["static"] = True; return o
ys = [-24.0, -11.0, 0.0, 11.0, 26.0]
for i in range(len(ys) - 1):
    for dz, dx in ((5.55, -0.6), (5.55, 0.6), (5.05, 0.0)):
        wire(Vector((-3.5 + dx, ys[i], dz)), Vector((-3.5 + dx, ys[i + 1], dz)), 0.55, f"Tel_{i}_{dz}_{dx}")
for k, (dz, dx) in enumerate(((5.55, -0.6), (5.05, 0.0))):   # sokağı çaprazlayan teller
    wire(Vector((-3.5 + dx, 0.0, dz)), Vector((4.2, 6.5 + k, 6.6)), 0.7, f"TelCapraz_{k}")

# uzak siluetler (sisin içinde): depolar, baca, vinç
box("Siluet_Depo1", -30, -14, 38, 52, -2, 12, M_SILUET, 0)
box("Siluet_Depo2", 12, 34, 44, 60, -2, 16, M_SILUET, 0)
box("Siluet_Baca", 18, 19.6, 40, 41.6, -2, 30, M_SILUET, 0)
box("Siluet_Vinc", -6, -5.4, 48, 48.6, -2, 22, M_SILUET, 0); box("Siluet_VincKol", -6, 8, 48, 48.6, 20.5, 21.5, M_SILUET, 0)

# ---------------- şehir genişletmesi ----------------
ISARET = {}; DYN = []
exec(open("C:/Users/Onur/Sisli/Blender/sahne_genis.py", encoding="utf-8").read())

# ---------------- karakter ----------------
with bpy.data.libraries.load(CHAR, link=False) as (src, dst):
    dst.objects = [n for n in src.objects]
for o in dst.objects:
    if o is not None and o.name not in ("Kas",): col.objects.link(o)
arm = next(o for o in dst.objects if o and o.type == 'ARMATURE')
CHAR_POS = Vector((float(opt("--cx", "1.1")), float(opt("--cy", "3.3")), 0.0))
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='POSE')
def rot_world(bn, axis, deg):
    pb = arm.pose.bones[bn]; bpy.context.view_layer.update()
    h = pb.head.copy(); R = Matrix.Rotation(math.radians(deg), 4, axis)
    pb.matrix = Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ pb.matrix; bpy.context.view_layer.update()
rot_world("LeftArm", 'Y', 72); rot_world("RightArm", 'Y', -72)
rot_world("LeftArm", 'X', 14); rot_world("RightArm", 'X', -18)        # kollar yürüyüşte karşıt sallanır
rot_world("LeftForeArm", 'X', -12); rot_world("RightForeArm", 'X', -18)
rot_world("LeftUpLeg", 'X', 16); rot_world("RightUpLeg", 'X', -20)     # sol bacak geride, sağ önde (yön -Y)
rot_world("LeftLeg", 'X', -22)
rot_world("Spine", 'X', -5); rot_world("Head", 'X', 8); rot_world("Head", 'Z', -12)
bpy.ops.object.mode_set(mode='OBJECT')
arm.location = CHAR_POS; arm.rotation_euler = (0, 0, math.radians(180 + float(opt("--cyaw", "-8"))))
# yerde dur: en alçak noktayı z=0'a getir
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
zmin = min((o.evaluated_get(dg).matrix_world @ v.co).z for o in arm.children if o.type == 'MESH' for v in o.evaluated_get(dg).to_mesh().vertices)
arm.location.z -= zmin

# ---------------- ışık ----------------
w = bpy.data.worlds.new("Gece"); sc.world = w
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.010, 0.020, 0.030, 1); bg.inputs[1].default_value = float(opt("--sky", "1.0"))
def K2RGB(k):   # kaba Kelvin → RGB (doğrusal)
    t = k / 100.0
    r = 1.0 if t <= 66 else min(1, 1.292936 * ((t - 60) ** -0.1332047592))
    g = (0.39008157 * math.log(t) - 0.63184144) if t <= 66 else 1.129890861 * ((t - 60) ** -0.0755148492)
    b = 1.0 if t >= 66 else (0 if t <= 19 else 0.543206789 * math.log(t - 10) - 1.19625408)
    return tuple(max(0, min(1, c)) ** 2.2 for c in (r, g, b))
ay = bpy.data.lights.new("Ay", 'SUN'); ay.energy = float(opt("--ay", "0.12")); ay.color = K2RGB(9500); ay.angle = math.radians(1.5)
ayo = bpy.data.objects.new("Ay", ay); col.objects.link(ayo); ayo.rotation_euler = Euler((math.radians(35), math.radians(-10), math.radians(200)))
# sokak lambası: başın altından aşağı spot
sp = bpy.data.lights.new("Lamba", 'SPOT'); sp.energy = float(opt("--lamba", "900")); sp.color = (0.80, 0.90, 1.0)
sp.spot_size = math.radians(95); sp.spot_blend = 0.65; sp.shadow_soft_size = 0.12
LAMP_HEAD = LAMP_POS + Vector((float(opt("--lhx", "-1.15")), 0, 3.62))
spo = bpy.data.objects.new("Lamba", sp); col.objects.link(spo); spo.location = LAMP_HEAD; spo.rotation_euler = (0, 0, 0)
# lamba camı parlak
glow = bpy.data.lights.new("LambaCam", 'POINT'); glow.energy = 15; glow.color = (0.8, 0.9, 1.0); glow.shadow_soft_size = 0.05
go = bpy.data.objects.new("LambaCam", glow); col.objects.link(go); go.location = LAMP_HEAD + Vector((0, 0, 0.06))
# sıcak pencere
if WIN_LIGHT:
    xw, yc, zc, side = WIN_LIGHT
    ar = bpy.data.lights.new("SicakPencere", 'AREA'); ar.energy = 60; ar.color = (1.0, 0.5, 0.2); ar.size = 0.9; ar.size_y = 1.3; ar.shape = 'RECTANGLE'
    ao = bpy.data.objects.new("SicakPencere", ar); col.objects.link(ao); ao.location = (xw + 0.15 * side, yc, zc); ao.rotation_euler = (0, math.radians(-90 * side), 0)
# hacimsel sis: yükseklikle azalan yoğunluk
fog = box("Sis", -40, 40, -40, 90, -2.0, 20.0, flat("tmp", (1, 1, 1)), 0); fog["static"] = False
fm = bpy.data.materials.new("M_Sis"); N = fm.node_tree.nodes; L = fm.node_tree.links
N.remove(N["Principled BSDF"]); vol = N.new("ShaderNodeVolumePrincipled")
vol.inputs["Color"].default_value = (0.70, 0.80, 0.90, 1); vol.inputs["Anisotropy"].default_value = 0.45
tc = N.new("ShaderNodeTexCoord"); sepz = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sepz.inputs["Vector"])
ex = N.new("ShaderNodeMath"); ex.operation = 'MULTIPLY'; ex.inputs[1].default_value = -0.18; L.new(sepz.outputs["Z"], ex.inputs[0])
ex2 = N.new("ShaderNodeMath"); ex2.operation = 'EXPONENT'; L.new(ex.outputs[0], ex2.inputs[0])
dn = N.new("ShaderNodeMath"); dn.operation = 'MULTIPLY'; dn.inputs[1].default_value = float(opt("--sis", "0.045")); L.new(ex2.outputs[0], dn.inputs[0])
L.new(dn.outputs[0], vol.inputs["Density"])
L.new(vol.outputs[0], N["Material Output"].inputs["Volume"])
fog.data.materials.clear(); fog.data.materials.append(fm)

# ---------------- kamera ----------------
cam_d = bpy.data.cameras.new("Kamera"); cam_d.lens = float(opt("--lens", "50")); cam_d.sensor_width = 36
cam = bpy.data.objects.new("Kamera", cam_d); col.objects.link(cam); sc.camera = cam
cam.location = Vector(tuple(float(x) for x in opt("--campos", "8.5,-9.0,9.5").split(",")))
tgt = Vector(tuple(float(x) for x in opt("--camtgt", "0.6,6.5,0.4").split(",")))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_d.dof.use_dof = True; cam_d.dof.focus_distance = (CHAR_POS + Vector((0, 0, 0.7)) - cam.location).length
cam_d.dof.aperture_fstop = float(opt("--fstop", "2.0"))

# ---------------- render ----------------
sc.render.engine = 'CYCLES'; sc.cycles.device = 'GPU'
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = 'OPTIX'; prefs.get_devices()
    for d in prefs.devices: d.use = (d.type != 'CPU')
except Exception as e: print("GPU", e)
sc.cycles.samples = int(opt("--spp", "128")); sc.cycles.use_denoising = True
sc.cycles.volume_step_rate = 2.0; sc.cycles.volume_max_steps = 256
sc.render.resolution_x = int(opt("--w", "1920")); sc.render.resolution_y = int(opt("--h", "1080"))
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = opt("--look", "AgX - Base Contrast") if False else 'None'
sc.view_settings.exposure = float(opt("--exp", "0.0"))
if opt("--json"):
    json.dump({"place": PLACE, "lamp_head": list(LAMP_HEAD), "char": list(CHAR_POS), "win": list(WIN_LIGHT) if WIN_LIGHT else None, "isaret": ISARET}, open(opt("--json"), "w"), indent=1)
if opt("--blend"): bpy.ops.wm.save_as_mainfile(filepath=opt("--blend"))
if opt("--render"):
    sc.render.filepath = opt("--render"); bpy.ops.render.render(write_still=True); print("RENDER", opt("--render"))
