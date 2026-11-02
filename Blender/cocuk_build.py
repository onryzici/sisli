# MakeHuman CC0 verisinden özgün karakter: taban mesh + vücut hedefleri + kıyafet giydirme (mhclo) + sade humanoid iskelet + T-poz.
# MakeHuman uygulaması ÇALIŞTIRILMAZ; yalnız veri dosyaları okunur.
# kullanım: blender -b -P mh_build.py -- --out <Character.fbx> [--clothes a,b,...] [--hair short02] [--skin young_caucasian_male]
#           [--height 0.3] [--blend <kayıt.blend>]
import bpy, json, math, os, sys, glob
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def opt(k, d=None):
    return argv[argv.index(k) + 1] if k in argv else d
OUT = opt("--out"); BLEND = opt("--blend")
CLOTHES = [c for c in opt("--clothes", "").split(",") if c]
HAIR = opt("--hair"); SKIN = opt("--skin"); EYES = opt("--eyes", "low-poly")
HEIGHT = float(opt("--height", "0.0"))
MH = "C:/Users/Onur/BoyaRPG/Indir/makehuman"
DATA = MH + "/data"; SYS = MH + "/system/x"
S = 0.1   # MH birimi (dm) → m

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; col = sc.collection

def mh2b(v):   # MH (Y yukarı, Z öne) → Blender (Z yukarı, -Y öne)
    return Vector((v[0] * S, -v[2] * S, v[1] * S))

# ---------------- OBJ / hedef okuyucular ----------------
def load_obj(path):
    V, VT, F = [], [], []
    grp = None
    for ln in open(path, encoding="utf-8", errors="ignore"):
        if ln.startswith("v "): V.append([float(x) for x in ln.split()[1:4]])
        elif ln.startswith("vt "): VT.append([float(x) for x in ln.split()[1:3]])
        elif ln.startswith("g "): grp = ln.split(None, 1)[1].strip()
        elif ln.startswith("f "):
            vs, ts = [], []
            for tok in ln.split()[1:]:
                p = tok.split("/"); vs.append(int(p[0]) - 1); ts.append(int(p[1]) - 1 if len(p) > 1 and p[1] else -1)
            F.append((vs, ts, grp))
    return V, VT, F

def load_target(path, V, w):
    for ln in open(path, encoding="utf-8"):
        if not ln.strip() or ln.startswith("#"): continue
        p = ln.split(); i = int(p[0])
        V[i][0] += w * float(p[1]); V[i][1] += w * float(p[2]); V[i][2] += w * float(p[3])

def find(pattern):
    g = glob.glob(pattern, recursive=True); return g[0] if g else None

# ---------------- taban + hedefler ----------------
V, VT, F = load_obj(DATA + "/3dobjs/base.obj")
# --- Sisli: çocuk gövdesi (MakeHuman CC0 çocuk makro hedefleri, Sisli/Indir/mh_targets) ---
CT = "C:/Users/Onur/Sisli/Indir/mh_targets/"
MALE = float(opt("--male", "0.6")); THIN = float(opt("--thin", "0.7")); SHORT = float(opt("--short", "0.4"))
load_target(CT + "caucasian-male-child.target", V, MALE)
load_target(CT + "caucasian-female-child.target", V, 1 - MALE)
load_target(CT + "universal-male-child-averagemuscle-minweight.target", V, THIN * MALE)
load_target(CT + "universal-female-child-averagemuscle-minweight.target", V, THIN * (1 - MALE))
load_target(CT + "male-child-averagemuscle-averageweight-minheight.target", V, SHORT * MALE)
load_target(CT + "female-child-averagemuscle-averageweight-minheight.target", V, SHORT * (1 - MALE))
for spec in [x for x in opt("--targets", "").split(",") if x]:
    tp, tw = spec.rsplit(":", 1)
    load_target(f"{DATA}/targets/{tp}.target", V, float(tw))
print("taban köşe", len(V), "yüz", len(F))

# ---------------- iskelet (MH default) → sade humanoid ----------------
skel = json.load(open(DATA + "/rigs/default.mhskel"))
def joint(name):
    idx = skel["joints"][name]; n = len(idx)
    return [sum(V[i][k] for i in idx) / n for k in range(3)]
MB = {b: (mh2b(joint(d["head"])), mh2b(joint(d["tail"])), d["parent"]) for b, d in skel["bones"].items()}

FNAMES = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
def target_of(b):
    side = "Left" if b.endswith(".L") else ("Right" if b.endswith(".R") else "")
    n = b[:-2] if side else b
    if n in ("root", "spine05") or n == "pelvis": return "Hips"
    if n in ("spine04", "spine03"): return "Spine"
    if n == "spine02": return "Spine1"
    if n in ("spine01", "breast"): return "Spine2"
    if n.startswith("neck"): return "Neck"
    if n in ("clavicle", "shoulder01"): return side + "Shoulder"
    if n.startswith("upperarm"): return side + "Arm"
    if n.startswith("lowerarm"): return side + "ForeArm"
    if n.startswith("finger"):   # parmaklar: Mixamo adları (LeftHandIndex1 ...), UE IK Rig otomatik tanır
        k, j = n[6:].split("-"); return side + "Hand" + FNAMES[int(k) - 1] + j
    if n in ("wrist",) or n.startswith("metacarpal"): return side + "Hand"
    if n.startswith("upperleg"): return side + "UpLeg"
    if n.startswith("lowerleg"): return side + "Leg"
    if n == "foot": return side + "Foot"
    if n.startswith("toe"): return side + "ToeBase"
    return "Head"   # baş, çene, göz, dil, yüz kasları

H = lambda b: MB[b][0]; T = lambda b: MB[b][1]
BONES = {   # ad: (baş, kuyruk, ebeveyn)
    "Hips": (H("spine05"), H("spine04"), None),
    "Spine": (H("spine04"), H("spine02"), "Hips"),
    "Spine1": (H("spine02"), H("spine01"), "Spine"),
    "Spine2": (H("spine01"), H("neck01"), "Spine1"),
    "Neck": (H("neck01"), H("head"), "Spine2"),
    "Head": (H("head"), T("head"), "Neck"),
}
for s, side in (("L", "Left"), ("R", "Right")):
    BONES.update({
        f"{side}Shoulder": (H(f"clavicle.{s}"), H(f"upperarm01.{s}"), "Spine2"),
        f"{side}Arm": (H(f"upperarm01.{s}"), H(f"lowerarm01.{s}"), f"{side}Shoulder"),
        f"{side}ForeArm": (H(f"lowerarm01.{s}"), H(f"wrist.{s}"), f"{side}Arm"),
        f"{side}Hand": (H(f"wrist.{s}"), H(f"finger3-1.{s}"), f"{side}ForeArm"),
        f"{side}UpLeg": (H(f"upperleg01.{s}"), H(f"lowerleg01.{s}"), "Hips"),
        f"{side}Leg": (H(f"lowerleg01.{s}"), H(f"foot.{s}"), f"{side}UpLeg"),
        f"{side}Foot": (H(f"foot.{s}"), H(f"toe1-1.{s}") if f"toe1-1.{s}" in MB else T(f"foot.{s}"), f"{side}Leg"),
        f"{side}ToeBase": (H(f"toe1-1.{s}") if f"toe1-1.{s}" in MB else T(f"foot.{s}"),
                           (T(f"toe1-1.{s}") if f"toe1-1.{s}" in MB else T(f"foot.{s}") + Vector((0, -0.05, 0))), f"{side}Foot"),
    })

for s_, side in (("L", "Left"), ("R", "Right")):
    for k in range(1, 6):
        for j in range(1, 4):
            mb = f"finger{k}-{j}.{s_}"
            if mb not in MB: continue
            par = f"{side}Hand" if j == 1 else f"{side}Hand{FNAMES[k-1]}{j-1}"
            BONES[f"{side}Hand{FNAMES[k-1]}{j}"] = (H(mb), T(mb), par)
arm_d = bpy.data.armatures.new("Armature"); arm = bpy.data.objects.new("Armature", arm_d); col.objects.link(arm)
bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for name, (h, t, p) in BONES.items():
    b = arm_d.edit_bones.new(name); b.head = h; b.tail = t if (t - h).length > 1e-3 else h + Vector((0, 0, 0.05))
for name, (h, t, p) in BONES.items():
    if p: arm_d.edit_bones[name].parent = arm_d.edit_bones[p]
bpy.ops.object.mode_set(mode='OBJECT')

# ---------------- ağırlıklar (taban köşesi başına sade kemik ağırlığı) ----------------
mhw = json.load(open(DATA + "/rigs/default_weights.mhw"))["weights"]
VW = [dict() for _ in V]
for b, lst in mhw.items():
    tb = target_of(b)
    for vi, w in lst:
        VW[vi][tb] = VW[vi].get(tb, 0) + w
for d in VW:
    s = sum(d.values())
    if s > 0:
        for k in d: d[k] /= s

# ---------------- mesh oluşturucu ----------------
def build_mesh(name, verts_b, faces, uvs_per_face, weights, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts_b], [], [f for f in faces])
    if uvs_per_face:
        uvl = me.uv_layers.new(name="UVMap")
        k = 0
        for p, fu in zip(me.polygons, uvs_per_face):
            for li, uv in zip(p.loop_indices, fu): uvl.data[li].uv = uv
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    if mat: me.materials.append(mat)
    for vi, d in enumerate(weights):
        for bn, w in d.items():
            if w <= 1e-4: continue
            g = ob.vertex_groups.get(bn) or ob.vertex_groups.new(name=bn)
            g.add([vi], w, 'REPLACE')
    ob.parent = arm
    md = ob.modifiers.new("Armature", 'ARMATURE'); md.object = arm
    return ob

def mhmat_textures(mhmat_path):
    tex = {}
    if not mhmat_path or not os.path.exists(mhmat_path): return tex
    base = os.path.dirname(mhmat_path)
    for ln in open(mhmat_path, encoding="utf-8", errors="ignore"):
        p = ln.split()
        if len(p) >= 2 and p[0] in ("diffuseTexture", "normalmapTexture", "diffuseColor"):
            if p[0] == "diffuseColor": tex["color"] = tuple(float(x) for x in p[1:4])
            else:
                f = os.path.join(base, os.path.basename(p[1]))
                if os.path.exists(f): tex[p[0]] = f
    return tex

def make_mat(name, tex, rough=0.75, fallback=(0.6, 0.6, 0.6)):
    m = bpy.data.materials.new(name); m.use_nodes = True
    N = m.node_tree.nodes; L = m.node_tree.links; b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    if "diffuseTexture" in tex:
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(tex["diffuseTexture"]); L.new(t.outputs["Color"], b.inputs["Base Color"])
        L.new(t.outputs["Alpha"], b.inputs["Alpha"])
    else:
        b.inputs["Base Color"].default_value = (*tex.get("color", fallback), 1)
    if "normalmapTexture" in tex:
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(tex["normalmapTexture"]); t.image.colorspace_settings.name = 'Non-Color'
        nm = N.new("ShaderNodeNormalMap"); L.new(t.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m

# ---------------- kıyafet giydirme (mhclo) ----------------
deleted = set()
def fit_proxy(mhclo_path, label):
    base = os.path.dirname(mhclo_path)
    obj_file = None; mat_file = None; scl = {}; refs = []; dels = []
    mode = None
    for ln in open(mhclo_path, encoding="utf-8", errors="ignore"):
        s = ln.strip()
        if not s or s.startswith("#"): continue
        p = s.split()
        if p[0] == "obj_file": obj_file = os.path.join(base, p[1]); continue
        if p[0] == "material": mat_file = os.path.join(base, p[1]); continue
        if p[0] in ("x_scale", "y_scale", "z_scale"): scl[p[0][0]] = (int(p[1]), int(p[2]), float(p[3])); continue
        if p[0] == "verts": mode = "v"; continue
        if p[0] == "delete_verts": mode = "d"; continue
        if p[0] in ("weights", "end"): mode = None; continue
        if mode == "v":
            if len(p) == 1: refs.append(((int(p[0]), 0, 0), (1.0, 0, 0), (0, 0, 0)))
            elif len(p) >= 9: refs.append(((int(p[0]), int(p[1]), int(p[2])), (float(p[3]), float(p[4]), float(p[5])), (float(p[6]), float(p[7]), float(p[8]))))
            else: mode = None
        elif mode == "d":
            # biçim: "a - b c d - e" (boşluklu aralıklar) veya "a-b"
            toks = " ".join(p).replace(" - ", "-").split()
            for tok in toks:
                if "-" in tok:
                    a, b = tok.split("-"); dels.extend(range(int(a), int(b) + 1))
                elif tok.isdigit(): dels.append(int(tok))
    def axscale(ax, k):
        if ax not in scl: return 1.0
        a, b, ref = scl[ax]; return abs(V[a][k] - V[b][k]) / ref if ref else 1.0
    sx, sy, sz = axscale("x", 0), axscale("y", 1), axscale("z", 2)
    CV, CVT, CF = load_obj(obj_file)
    verts = []; weights = []
    for (i0, i1, i2), (w0, w1, w2), (d0, d1, d2) in refs:
        pos = [w0 * V[i0][k] + w1 * V[i1][k] + w2 * V[i2][k] for k in range(3)]
        pos[0] += d0 * sx; pos[1] += d1 * sy; pos[2] += d2 * sz
        verts.append(mh2b(pos))
        d = {}
        for ii, ww in ((i0, w0), (i1, w1), (i2, w2)):
            if ww == 0: continue
            for bn, bw in VW[ii].items(): d[bn] = d.get(bn, 0) + ww * bw
        weights.append(d)
    faces = [f[0] for f in CF]; uvs = [[CVT[t] for t in f[1]] if CVT and f[1][0] >= 0 else None for f in CF]
    if any(u is None for u in uvs): uvs = None
    tex = mhmat_textures(mat_file)
    ob = build_mesh(label, verts, faces, uvs, weights, make_mat(label + "_Mat", tex))
    deleted.update(dels)
    print("GİYDİRİLDİ", label, len(verts), "köşe; gizlenen ten köşesi", len(dels), "doku", list(tex))
    return ob

for c in CLOTHES:
    f = find(f"{SYS}/**/clothes/{c}/*.mhclo"); fit_proxy(f, c) if f else print("YOK kıyafet", c)
if HAIR:
    f = find(f"{SYS}/**/hair/{HAIR}/*.mhclo"); fit_proxy(f, "Sac") if f else print("YOK saç", HAIR)
if EYES:
    f = find(f"{DATA}/eyes/{EYES}/*.mhclo")
    if f:
        e = fit_proxy(f, "Gozler")
        bt = DATA + "/eyes/materials/brown_eye.png"
        if os.path.exists(bt): e.data.materials[0] = make_mat("Goz_Mat", {"diffuseTexture": bt}, 0.2)
for extra in ("eyebrow001",):
    f = find(f"{SYS}/**/eyebrows/{extra}/*.mhclo"); fit_proxy(f, "Kas") if f else None

# ---------------- ten (yalnız 'body' grubu, gizlenen köşeler hariç) ----------------
body_faces = [(vs, ts) for vs, ts, g in F if g == "body" and not any(v in deleted for v in vs)]
used = sorted({v for vs, _ in body_faces for v in vs}); remap = {v: i for i, v in enumerate(used)}
skin_tex = {}
if SKIN:
    mf = find(f"{SYS}/**/skins/{SKIN}/*.mhmat") or find(f"{SYS}/**/skins/{SKIN}*.mhmat")
    skin_tex = mhmat_textures(mf)
build_mesh("Ten", [mh2b(V[v]) for v in used], [[remap[v] for v in vs] for vs, _ in body_faces],
           [[VT[t] for t in ts] for _, ts in body_faces], [VW[v] for v in used], make_mat("Ten_Mat", skin_tex, 0.55, (0.78, 0.6, 0.5)))
print("TEN", len(used), "köşe, doku", list(skin_tex))

# ---------------- A-poz → T-poz (kollar yatay) ----------------
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
for side, sx in (("Left", 1), ("Right", -1)):
    for bn in (f"{side}Arm", f"{side}ForeArm", f"{side}Hand"):
        pb = arm.pose.bones[bn]
        bpy.context.view_layer.update()
        head = pb.head.copy(); cur = (pb.tail - pb.head).normalized()
        want = Vector((sx, 0, 0))
        rot = cur.rotation_difference(want).to_matrix().to_4x4()
        pb.matrix = Matrix.Translation(head) @ rot @ Matrix.Translation(-head) @ pb.matrix
        bpy.context.view_layer.update()
# --- stilizasyon: büyük kafa (REANIMAL çocukları ~4.5 kafa boyu), hafif ince boyun ---
HEADS = float(opt("--heads", "1.22"))
pb = arm.pose.bones["Head"]; pb.scale = (HEADS, HEADS, HEADS)
for side in ("Left", "Right"):   # çocuksu: eller ve ayaklar biraz büyük
    arm.pose.bones[f"{side}Hand"].scale = (1.08, 1.08, 1.08)
bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode='OBJECT')
for ob in [o for o in col.objects if o.type == 'MESH']:
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier="Armature")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode='OBJECT')
for ob in [o for o in col.objects if o.type == 'MESH']:
    md = ob.modifiers.new("Armature", 'ARMATURE'); md.object = arm

mn = min(v.co.z for o in col.objects if o.type == "MESH" for v in o.data.vertices)
arm.location.z -= mn
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
mx = max(v.co.z for o in col.objects if o.type == 'MESH' for v in o.data.vertices)
print(f"BOY {mx - mn:.3f} m, taban z={mn:.3f}")
# --- hedef boy (REANIMAL oyuncu çocukları ~1.30 m) ---
TH = float(opt("--tall", "1.28"))
def world_zmax():
    bpy.context.view_layer.update()
    return max((o.matrix_world @ v.co).z for o in col.objects if o.type == 'MESH' for v in o.data.vertices)
k = TH / world_zmax()
arm.scale = (k, k, k)
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
print(f"ÖLÇEK {k:.3f} → BOY {world_zmax():.3f} m")
# --- UE için kök kemik (orijinde, Hips'in ebeveyni) ---
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones
r = eb.new("root"); r.head = (0, 0, 0); r.tail = (0, 0.15, 0)
eb["Hips"].parent = r
bpy.ops.object.mode_set(mode='OBJECT')
if BLEND: bpy.ops.wm.save_as_mainfile(filepath=BLEND)
if OUT:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={'ARMATURE', 'MESH'}, apply_scale_options='FBX_SCALE_UNITS',
                             axis_forward='-Z', axis_up='Y', add_leaf_bones=False, bake_anim=False, path_mode='COPY', embed_textures=False,
                             primary_bone_axis='Y', secondary_bone_axis='X')
    print("YAZILDI", OUT)
