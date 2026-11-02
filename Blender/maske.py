# Sisli karakteri: yüze oturan kartonpiyer karga maskesi + kayış + soluk/kirli kıyafet tonları
# Maske kabuğu karakterin kendi yüz yüzeyinden türetilir (yumuşatılıp dışarı itilir), gaga ayrı modellenir.
# kullanım: blender -b cocuk_v1.blend -P maske.py -- --blend cocuk_v2.blend
import bpy, bmesh, sys, math
from mathutils import Vector
from mathutils.kdtree import KDTree
argv = sys.argv[sys.argv.index("--")+1:]
def opt(k, d=None): return argv[argv.index(k)+1] if k in argv else d
sc = bpy.context.scene; col = sc.collection
arm = next(o for o in sc.objects if o.type == 'ARMATURE')
ten = sc.objects["Ten"]; goz = sc.objects["Gozler"]; sac = sc.objects["Sac"]
bpy.context.view_layer.update()

# --- kafa ölçüleri ---
gi = ten.vertex_groups["Head"].index
def headw(v): return max([g.weight for g in v.groups if g.group == gi] or [0])
hv = [ten.matrix_world @ v.co for v in ten.data.vertices if headw(v) > .6]
mn = Vector([min(v[i] for v in hv) for i in range(3)]); mx = Vector([max(v[i] for v in hv) for i in range(3)])
c = (mn + mx) / 2; size = mx - mn
ev = [goz.matrix_world @ v.co for v in goz.data.vertices]
def avg(vs): return sum(vs, Vector()) / max(1, len(vs))
eL = avg([v for v in ev if v.x > 0]); eR = avg([v for v in ev if v.x < 0])
eye_z = (eL.z + eR.z) / 2; front_y = mn.y
eye_r = size.x * 0.095
print("KAFA merkez", tuple(round(x, 3) for x in c), "boyut", tuple(round(x, 3) for x in size), "göz z", round(eye_z, 3))

def apply_mods(o):
    with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o]):
        for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)

# --- 1) yüz kabuğu: önden bakışta oval yarım maske, yüze ışınla oturtulmuş kutupsal ızgara ---
from mathutils.bvhtree import BVHTree
dg = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(ten, dg)          # nesne uzayı (ten'in matrisi birim varsayımıyla kontrol)
tm = ten.matrix_world; tmi = tm.inverted()
ZC = eye_z + size.z * 0.02
AX = size.x * float(opt("--ax", "0.46"))
AZ_UP = size.z * float(opt("--ust", "0.22")); AZ_DN = size.z * float(opt("--alt", "0.27"))
RINGS, SEGS = 36, 96
grid = []   # [halka][dilim] -> Vector
for i in range(RINGS + 1):
    r = i / RINGS
    row = []
    for j in range(SEGS):
        th = 2 * math.pi * j / SEGS
        s = math.sin(th)
        x = AX * r * math.cos(th)
        z = ZC + (AZ_UP if s > 0 else AZ_DN) * r * s
        o = tmi @ Vector((x, front_y - 0.3, z)); d = (tmi.to_3x3() @ Vector((0, 1, 0))).normalized()
        hit = bvh.ray_cast(o, d, 1.0)
        y = (tm @ hit[0]).y if hit[0] is not None else c.y
        row.append(Vector((x, y, z)))
    grid.append(row)
# derinlik alanını yumuşat (burun/dudak izleri kaybolsun, kafatası hatları kalsın)
for it in range(60):
    new = [[p.copy() for p in row] for row in grid]
    for i in range(1, RINGS):
        for j in range(SEGS):
            nb = [grid[i - 1][j], grid[i + 1][j], grid[i][(j - 1) % SEGS], grid[i][(j + 1) % SEGS]]
            new[i][j].y = grid[i][j].y * 0.4 + 0.6 * sum(p.y for p in nb) / 4
    cy0 = sum(grid[1][j].y for j in range(SEGS)) / SEGS
    for j in range(SEGS): new[0][j].y = cy0
    grid = new
front_y = min(p.y for row in grid for p in row) - 0.011
print("ÖN YÜZ y", round(front_y, 3))
bm = bmesh.new()
ctr = bm.verts.new(grid[0][0])
V = [None] + [[bm.verts.new(p) for p in row] for row in grid[1:]]
for j in range(SEGS):
    bm.faces.new((V[1][(j + 1) % SEGS], V[1][j], ctr))
for i in range(1, RINGS):
    for j in range(SEGS):
        bm.faces.new((V[i + 1][(j + 1) % SEGS], V[i + 1][j], V[i][j], V[i][(j + 1) % SEGS]))
print("KABUK ham", len(bm.verts), len(bm.faces))
bm.normal_update()
for f in bm.faces:
    if f.normal.y > 0: f.normal_flip()
bm.normal_update()
for v in bm.verts:
    n = v.normal.copy()
    if n.y > -0.2: n = Vector((n.x, -0.2, n.z)).normalized()
    v.co += n * 0.011
me = bpy.data.meshes.new("Maske"); bm.to_mesh(me); bm.free()
plate = bpy.data.objects.new("Maske", me); col.objects.link(plate)
so = plate.modifiers.new("kal", 'SOLIDIFY'); so.thickness = 0.006; so.offset = -1.0; so.use_rim = True
cuts = []
for e in (eL, eR):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=eye_r, depth=0.3, location=(e.x * 1.04, e.y, e.z + 0.003), rotation=(math.radians(90), 0, 0))
    cut = bpy.context.object; cut.scale = (1.08, 0.80, 1); cuts.append(cut)
    b = plate.modifiers.new("b", 'BOOLEAN'); b.object = cut; b.operation = 'DIFFERENCE'; b.solver = opt('--solver', 'MANIFOLD')
plate.modifiers.new("sub", 'SUBSURF').levels = 1
print("KABUK önce", len(plate.data.vertices))
apply_mods(plate)
print("KABUK sonra", len(plate.data.vertices))
for cut in cuts: bpy.data.objects.remove(cut)

# --- 2) gaga: üst ve alt çene ayrı, gözlerin arasından başlar ---
def beak_part(name, L, W0, H0, z_c, z_top_bias, hook, lower):
    bm = bmesh.new(); segs, rings = 20, 26; rv = []
    for i in range(rings + 1):
        t = i / rings
        y = -L * t
        zc = z_c(t)
        h = 0.5 * H0 * (1 - t) ** (1.25 if not lower else 1.3) + 0.0008
        w = 0.5 * W0 * (1 - t) ** 1.35 + 0.0008
        ring = []
        for j in range(segs):
            a = 2 * math.pi * j / segs
            s, co = math.sin(a), math.cos(a)
            x = w * math.copysign(abs(co) ** 0.8, co)
            if s > 0: z = zc + h * z_top_bias * (abs(s) ** 0.75)    # üst sırt sivri
            else: z = zc - h * (2 - z_top_bias) * (abs(s) ** 1.3)    # alt yassı
            ring.append(bm.verts.new((x, y, z)))
        rv.append(ring)
    for i in range(rings):
        for j in range(segs):
            bm.faces.new((rv[i][j], rv[i][(j + 1) % segs], rv[i + 1][(j + 1) % segs], rv[i + 1][j]))
    tip = bm.verts.new((0, -L - 0.002, z_c(1.0) - hook))
    for j in range(segs): bm.faces.new((rv[-1][j], rv[-1][(j + 1) % segs], tip))
    bm.faces.new(list(reversed(rv[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col.objects.link(o)
    o.modifiers.new("sub", 'SUBSURF').levels = 1; apply_mods(o); return o
L = size.y * float(opt("--gaga", "1.05"))
W0 = (eL.x - eR.x) * 1.05
HU = size.z * 0.24; HL = size.z * 0.10
ust = beak_part("GagaUst", L, W0, HU, lambda t: -0.16 * L * t ** 2.2, 1.30, 0.012, False)
alt = beak_part("GagaAlt", L * 0.72, W0 * 0.82, HL, lambda t: -0.5 * HU * (1 - t) ** 0.75 - 0.003 - 0.06 * L * t ** 1.8, 1.0, 0.0, True)
root_y = front_y + size.y * 0.06
for o in (ust, alt):
    o.location = Vector((c.x, root_y, eye_z - eye_r * 0.15))
    o.rotation_euler = (math.radians(-4), 0, 0)
gaga = ust

# --- 3) göz halkaları: maske yüzeyine oturan boyalı kenar ---
rims = []
for e in (eL, eR):
    bpy.ops.mesh.primitive_torus_add(major_radius=eye_r, minor_radius=0.0032, major_segments=40, minor_segments=8,
                                     location=(e.x * 1.04, front_y - 0.05, e.z + 0.003), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object; t.scale = (1.08, 0.80, 1)
    sw = t.modifiers.new("sw", 'SHRINKWRAP'); sw.target = plate; sw.wrap_method = 'PROJECT'
    sw.use_project_y = True; sw.use_negative_direction = True; sw.use_positive_direction = True; sw.offset = 0.001
    apply_mods(t); rims.append(t)

# --- 4) kayış: saçın dış çeperine oturan temiz elips bant (yalnız arka) ---
sv = [sac.matrix_world @ v.co for v in sac.data.vertices]
band = [v for v in sv if abs(v.z - (eye_z + 0.015)) < 0.012]
bx = max(abs(v.x) for v in band) + 0.003; by_back = max(v.y for v in band) + 0.003
cy_band = c.y
ry = by_back - cy_band
bm = bmesh.new(); n = 64; top = []; bot = []
for j in range(n + 1):
    th = math.pi * j / n            # 0..pi → arka yarım
    x = bx * math.cos(th); y = cy_band + ry * math.sin(th)
    top.append(bm.verts.new((x, y, eye_z + 0.015 + 0.007))); bot.append(bm.verts.new((x, y, eye_z + 0.015 - 0.007)))
for j in range(n): bm.faces.new((top[j], top[j + 1], bot[j + 1], bot[j]))
me = bpy.data.meshes.new("Kayis"); bm.to_mesh(me); bm.free()
kay = bpy.data.objects.new("Kayis", me); col.objects.link(kay)
s2 = kay.modifiers.new("kal", 'SOLIDIFY'); s2.thickness = 0.003; apply_mods(kay)

# --- birleştir ---
bpy.ops.object.select_all(action='DESELECT')
for o in [plate, ust, alt] + rims: o.select_set(True)
bpy.context.view_layer.objects.active = plate
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.join()
mask = plate
for o in (mask, kay):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()
# --- malzemeler ---
def mat_mask():
    m = bpy.data.materials.new("M_Maske"); N = m.node_tree.nodes; Lk = m.node_tree.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    # büyük ölçekli leke + ince gren
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 9; n1.inputs["Detail"].default_value = 10; n1.inputs["Roughness"].default_value = 0.6
    Lk.new(tc.outputs["Object"], n1.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.30, 0.26, 0.20, 1); ramp.color_ramp.elements[0].position = 0.38
    ramp.color_ramp.elements[1].color = (0.66, 0.62, 0.54, 1); ramp.color_ramp.elements[1].position = 0.60
    Lk.new(n1.outputs["Fac"], ramp.inputs["Fac"])
    # ince kıl çatlaklar (gürültüyle bozulmuş voronoi kenarı)
    warp = N.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = 30
    Lk.new(tc.outputs["Object"], warp.inputs["Vector"])
    addv = N.new("ShaderNodeVectorMath"); addv.operation = 'SCALE'; addv.inputs["Scale"].default_value = 0.02
    Lk.new(warp.outputs["Color"], addv.inputs[0])
    add2 = N.new("ShaderNodeVectorMath"); add2.operation = 'ADD'
    Lk.new(tc.outputs["Object"], add2.inputs[0]); Lk.new(addv.outputs[0], add2.inputs[1])
    vor = N.new("ShaderNodeTexVoronoi"); vor.feature = 'DISTANCE_TO_EDGE'; vor.inputs["Scale"].default_value = 14
    Lk.new(add2.outputs[0], vor.inputs["Vector"])
    crack = N.new("ShaderNodeMapRange"); crack.inputs["From Min"].default_value = 0.0; crack.inputs["From Max"].default_value = 0.012
    crack.inputs["To Min"].default_value = 1.0; crack.inputs["To Max"].default_value = 0.0
    Lk.new(vor.outputs["Distance"], crack.inputs["Value"])
    # çatlaklar yalnız bazı bölgelerde (maske)
    cm = N.new("ShaderNodeTexNoise"); cm.inputs["Scale"].default_value = 4
    Lk.new(tc.outputs["Object"], cm.inputs["Vector"])
    cmr = N.new("ShaderNodeMapRange"); cmr.inputs["From Min"].default_value = 0.5; cmr.inputs["From Max"].default_value = 0.62
    Lk.new(cm.outputs["Fac"], cmr.inputs["Value"])
    cmul = N.new("ShaderNodeMath"); cmul.operation = 'MULTIPLY'
    Lk.new(crack.outputs["Result"], cmul.inputs[0]); Lk.new(cmr.outputs["Result"], cmul.inputs[1])
    mix = N.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    Lk.new(cmul.outputs[0], mix.inputs["Factor"]); Lk.new(ramp.outputs["Color"], mix.inputs[6]); mix.inputs[7].default_value = (0.35, 0.30, 0.24, 1)
    Lk.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.75
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.invert = True
    Lk.new(cmul.outputs[0], bump.inputs["Height"]); Lk.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m
def mat_plain(name, col, rough):
    m = bpy.data.materials.new(name); b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough; return m
mask.data.materials.clear(); mask.data.materials.append(mat_mask())
kay.data.materials.clear(); kay.data.materials.append(mat_plain("M_Kayis", (0.05, 0.035, 0.025), 0.55))

# --- kıyafet tonları ---
def retint(ob, sat, val, hue=0.5):
    for m in ob.data.materials:
        N = m.node_tree.nodes; Lk = m.node_tree.links; b = N["Principled BSDF"]
        link = next((l for l in Lk if l.to_socket == b.inputs["Base Color"]), None)
        if not link: continue
        hsv = N.new("ShaderNodeHueSaturation"); hsv.inputs["Hue"].default_value = hue
        hsv.inputs["Saturation"].default_value = sat; hsv.inputs["Value"].default_value = val
        Lk.new(link.from_socket, hsv.inputs["Color"]); Lk.new(hsv.outputs["Color"], b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = 0.88
        if "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = 0.2
retint(sc.objects["male_worksuit01"], float(opt("--sat", "0.40")), float(opt("--val", "0.38")), float(opt("--hue", "0.45")))
retint(sac, 0.6, 0.40)
ten.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.58, 0.47, 0.42, 1)

# --- kafaya bağla ---
for o in (mask, kay):
    o.parent = arm
    g = o.vertex_groups.new(name="Head"); g.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    md = o.modifiers.new("Armature", 'ARMATURE'); md.object = arm
bpy.ops.wm.save_as_mainfile(filepath=opt("--blend"))
print("MASKE TAMAM", len(mask.data.vertices), "kayis", len(kay.data.vertices))
