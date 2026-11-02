# Fab/Megascans paketini tanı: her mesh için ölçü + tri sayısı + küçük önizleme; her yüzey için doku küçük resmi.
# kullanım: blender -b -P fab_onizle.py -- --kok D:/Sisli-Fab/unfinished_building_high --cikti D:/Sisli-Fab/_onizleme/ub
import bpy, sys, os, glob, json, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
def opt(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
KOK = opt("--kok"); CIK = opt("--cikti"); os.makedirs(CIK, exist_ok=True)
bilgi = {}
def temizle():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'TEXTURE'
    sc.display.shading.show_shadows = True; sc.display.shading.show_cavity = True
    sc.render.resolution_x = 320; sc.render.resolution_y = 240; sc.render.film_transparent = False
    sc.world = bpy.data.worlds.new("W"); sc.world.color = (0.08, 0.08, 0.09)
    return sc
def ilk(desen):
    f = glob.glob(desen); return f[0] if f else None
for d in sorted(glob.glob(os.path.join(KOK, "*"))):
    if not os.path.isdir(d): continue
    ad = os.path.basename(d); fbx = ilk(os.path.join(d, "*.fbx"))
    renk = ilk(os.path.join(d, "*_BaseColor.jpg")) or ilk(os.path.join(d, "*_Albedo.jpg"))
    if not fbx:
        if renk:
            im = bpy.data.images.load(renk); im.scale(256, 256); im.filepath_raw = os.path.join(CIK, "S_" + ad + ".png"); im.file_format = 'PNG'; im.save()
            bilgi[ad] = {"tur": "yuzey", "opak": bool(ilk(os.path.join(d, "*_Opacity.jpg"))), "dosyalar": sorted(os.path.basename(x).split("_4K_")[-1] for x in glob.glob(d + "/*.jpg"))}
            bpy.data.images.remove(im)
        continue
    sc = temizle()
    bpy.ops.import_scene.fbx(filepath=fbx)
    obs = [o for o in sc.objects if o.type == 'MESH']
    if renk:
        im = bpy.data.images.load(renk)
        m = bpy.data.materials.new("M"); m.use_nodes = True; t = m.node_tree.nodes.new("ShaderNodeTexImage"); t.image = im
        m.node_tree.links.new(t.outputs["Color"], m.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
        for o in obs:
            o.data.materials.clear(); o.data.materials.append(m)
    bpy.context.view_layer.update()
    vs = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    mn = Vector([min(v[i] for v in vs) for i in range(3)]); mx = Vector([max(v[i] for v in vs) for i in range(3)])
    boy = mx - mn; mer = (mn + mx) / 2
    tri = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs)
    cam = bpy.data.objects.new("K", bpy.data.cameras.new("K")); sc.collection.objects.link(cam); sc.camera = cam
    r = max(boy.length, 0.01)
    cam.location = mer + Vector((r * 0.75, -r * 0.95, r * 0.6))
    cam.rotation_euler = (mer - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 50; cam.data.clip_end = r * 20
    sc.render.filepath = os.path.join(CIK, "M_" + ad + ".png"); bpy.ops.render.render(write_still=True)
    bilgi[ad] = {"tur": "mesh", "boyut_m": [round(x, 2) for x in boy], "taban_z": round(mn.z, 3), "tri": tri, "parca": len(obs), "lod": sorted(o.name for o in obs)[:6]}
    print("ONIZLE", ad, bilgi[ad]["boyut_m"], tri)
json.dump(bilgi, open(os.path.join(CIK, "bilgi.json"), "w"), indent=1)
print("ONIZLE TAMAM", len(bilgi))
