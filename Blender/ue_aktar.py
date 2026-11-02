# sahne.blend → Unreal: dünya uzayında birleşik FBX'ler + ışık/karakter JSON.
#  - Poly Haven örnekleri: varlık türüne göre birleşik (SM_PH_<ad>.fbx)
#  - mimari (static=True): malzemeye göre birleşik (SM_Mim_<malzeme>.fbx)
# kullanım: blender -b sahne.blend -P ue_aktar.py -- --out C:/Users/Onur/Sisli/Unreal/SourceArt/Ortam
import bpy, sys, os, json, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--")+1:]
OUT = argv[argv.index("--out")+1]; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene

def join_export(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    copies = []
    for o in objs:
        c = o.copy(); c.data = o.data.copy(); sc.collection.objects.link(c); copies.append(c)
    for c in copies: c.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    if any(c.type == 'CURVE' for c in copies): bpy.ops.object.convert(target='MESH')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if len(copies) > 1: bpy.ops.object.join()
    j = bpy.context.view_layer.objects.active; j.name = name
    bpy.ops.object.select_all(action='DESELECT'); j.select_set(True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + ".fbx"), use_selection=True, object_types={'MESH'},
                             apply_scale_options='FBX_SCALE_ALL', axis_forward='-Y', axis_up='Z', path_mode='COPY',
                             embed_textures=False, mesh_smooth_type='FACE', use_mesh_modifiers=True)
    n = len(j.data.vertices); bpy.data.objects.remove(j); return n

# 1) Poly Haven örnekleri (ad sonu "_i", paylaşılan mesh verisi)
groups = {}
for o in sc.objects:
    if o.type == 'MESH' and o.name.split(".")[0].endswith("_i"):
        groups.setdefault(o.name.split(".")[0][:-2], []).append(o)
for k, objs in groups.items():
    print("PH", k, len(objs), join_export(objs, "SM_PH_" + k))

# 1b) dinamik parçalar: her biri ayrı FBX, kendi orijininde (pivot korunur); konum/yaw JSON a
DYNOUT = {}
for o in list(sc.objects):
    if o.get("dinamik"):
        nm = o["dinamik"]; loc = o.location.copy(); rz = o.rotation_euler.z; scl = o.scale.copy()
        c = o.copy(); c.data = o.data.copy(); sc.collection.objects.link(c)
        c.location = (0, 0, 0); c.rotation_euler = (0, 0, 0)
        bpy.ops.object.select_all(action="DESELECT"); c.select_set(True); bpy.context.view_layer.objects.active = c
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "SM_Dyn_" + nm + ".fbx"), use_selection=True, object_types={"MESH"},
                                 apply_scale_options="FBX_SCALE_ALL", axis_forward="-Y", axis_up="Z", path_mode="COPY", embed_textures=False, mesh_smooth_type="FACE")
        bpy.data.objects.remove(c)
        DYNOUT[nm] = {"loc": [loc.x * 100, -loc.y * 100, loc.z * 100], "yaw": -math.degrees(rz)}
        print("DİNAMİK", nm)

# 2) mimari: malzemeye göre
mats = {}
for o in sc.objects:
    if o.get("static") and not o.get("dinamik") and o.type in ('MESH', 'CURVE') and o.name != "Sis":
        m = o.data.materials[0].name if o.data.materials else "yok"
        mats.setdefault((o.get("grup", ""), m), []).append(o)
for (grp, m), objs in mats.items():
    safe = "".join(ch if ch.isalnum() else "_" for ch in m)
    print("MIM", grp, m, len(objs), join_export(objs, "SM_Mim_" + (grp + "_" if grp else "") + safe))

# 3) ışıklar / karakter (UE: cm, Y ters)
def ue(v): return [v[0] * 100, -v[1] * 100, v[2] * 100]
L = {}
for o in sc.objects:
    if o.type == 'LIGHT':
        L[o.name] = {"type": o.data.type, "loc": ue(o.location), "energy": o.data.energy, "color": list(o.data.color)}
arm = next((o for o in sc.objects if o.type == 'ARMATURE'), None)
cam = sc.objects.get("Kamera")
YER = argv[argv.index("--yer") + 1] if "--yer" in argv else "C:/Users/Onur/Sisli/Blender/yerlesim.json"
yer = json.load(open(YER))
isr = {}
for k, v in yer.get("isaret", {}).items():
    if isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) for x in v): isr[k] = ue(v)
    elif k == "lambalar_ek": isr[k] = [ue(p) for p in v]
    elif k == "ic_mekan_kutu": isr[k] = {"x": [v[0][0] * 100, v[0][1] * 100], "y": [-v[1][1] * 100, -v[1][0] * 100], "z": [v[2][0] * 100, v[2][1] * 100]}
    elif k == "su_olum_kutusu": isr[k] = {"x": [v[0][0] * 100, v[0][1] * 100], "y": [-v[1][1] * 100, -v[1][0] * 100], "z": [v[2][0] * 100, v[2][1] * 100]}
    else: isr[k] = v
json.dump({"lights": L, "char": ue(arm.location) if arm else None, "cam": ue(cam.location) if cam else None, "dinamik": DYNOUT, "isaret": isr}, open(os.path.join(OUT, "sahne_ue.json"), "w"), indent=1)
# 4) malzeme bilgisi (Unreal malzeme ataması için)
MB = {}
for m in bpy.data.materials:
    if not m.node_tree: continue
    safe = "".join(ch if ch.isalnum() else "_" for ch in m.name)
    b = m.node_tree.nodes.get("Principled BSDF")
    if m.get("tex"):
        MB[safe] = {"tex": m["tex"], "tint": list(m["tint"]), "puddle": bool(m.get("puddle", False))}
    elif b and not b.inputs["Base Color"].links:
        MB[safe] = {"flat": list(b.inputs["Base Color"].default_value)[:3], "rough": b.inputs["Roughness"].default_value,
                    "emis": [c * b.inputs["Emission Strength"].default_value for c in list(b.inputs["Emission Color"].default_value)[:3]]}
json.dump(MB, open(os.path.join(OUT, "malzeme_bilgi.json"), "w"), indent=1)
print("TAMAM", len(MB), "malzeme")
