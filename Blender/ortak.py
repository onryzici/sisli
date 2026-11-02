# Sisli ortak Blender yardımcıları (sahne.py'den ayrıldı): pbr/flat malzeme, box/quad geometri, Poly Haven yükle/yerleştir, tel
import bpy, bmesh, sys, os, math, json, glob, random
from mathutils import Vector, Matrix, Euler
PH = "C:/Users/Onur/Sisli/Indir/polyhaven"
sc = bpy.context.scene; col = sc.collection
PLACE = []
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

def wire(p0, p1, sag, name):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.008; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); n = 24; sp.points.add(n - 1)
    for i in range(n):
        t = i / (n - 1); p = p0.lerp(p1, t); p.z -= sag * 4 * t * (1 - t)
        sp.points[i].co = (*p, 1)
    o = bpy.data.objects.new(name, cu); col.objects.link(o); cu.materials.append(flat("M_Tel", (0.01, 0.01, 0.01), 0.5)); o["static"] = True; return o
