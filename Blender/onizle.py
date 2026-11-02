# Karakter ön izleme: blend aç, nötr stüdyo ışığı, ön/yan/3-4/arka görüş → tek PNG
# kullanım: blender -b <dosya.blend> -P onizle.py -- --out <png> [--h 1.3]
import bpy, sys, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--")+1:]
OUT = argv[argv.index("--out")+1]
sc = bpy.context.scene
H = max((o.matrix_world@v.co).z for o in sc.objects if o.type=='MESH' and o.visible_get() for v in o.data.vertices)
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 520, 900
sc.view_settings.view_transform = 'AgX'
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.32, 0.33, 0.35, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
def light(name, rot, e, col=(1,1,1)):
    d = bpy.data.lights.new(name, 'SUN'); d.energy = e; d.color = col; d.angle = 0.3
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.rotation_euler = [math.radians(a) for a in rot]
light("Key", (50, 0, 35), 3.0, (1, .96, .9)); light("Rim", (60, 0, 200), 2.0, (.8, .9, 1))
# zemin
bpy.ops.mesh.primitive_plane_add(size=20); g = bpy.context.object
m = bpy.data.materials.new("Zemin"); m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (.25,.25,.25,1); g.data.materials.append(m)
cam_d = bpy.data.cameras.new("C"); cam_d.lens = 85; cam = bpy.data.objects.new("C", cam_d); sc.collection.objects.link(cam); sc.camera = cam
ZC = float(argv[argv.index("--zc")+1]) if "--zc" in argv else 0.5
DF = float(argv[argv.index("--df")+1]) if "--df" in argv else 3.6
tgt = Vector((0, 0, H*ZC)); dist = H*DF
paths = []
for i, ang in enumerate([0, 45, 90, 180]):
    a = math.radians(ang)
    cam.location = tgt + Vector((math.sin(a)*dist, -math.cos(a)*dist, H*0.12))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    p = OUT.replace(".png", f"_{i}.png"); sc.render.filepath = p; bpy.ops.render.render(write_still=True); paths.append(p)
# yan yana birleştir
imgs = [bpy.data.images.load(p) for p in paths]
W, Hh = imgs[0].size; big = bpy.data.images.new("grid", W*len(imgs), Hh)
px = [0.0]*(W*len(imgs)*Hh*4)
for k, im in enumerate(imgs):
    src = list(im.pixels)
    for y in range(Hh):
        row = src[y*W*4:(y+1)*W*4]; s = (y*W*len(imgs) + k*W)*4; px[s:s+W*4] = row
big.pixels = px; big.filepath_raw = OUT; big.file_format = 'PNG'; big.save()
print("ONIZLEME", OUT, "H", H)
