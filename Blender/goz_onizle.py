# Yüz/göz önizlemesi (şaşılık teşhisi): blender -b cocuk_v2_export.blend -P goz_onizle.py -- <çıktı.png>
import bpy, sys, math
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1]
sc = bpy.context.scene
arm = next(o for o in sc.objects if o.type == 'ARMATURE')
bpy.context.view_layer.update()
for o in sc.objects:
    if o.type == 'MESH': print("MESH", o.name, [m.name for m in o.data.materials][:3], "boyut", tuple(round(x, 1) for x in o.dimensions))
gz = sc.objects.get("Gozler")
if gz:
    vs = [gz.matrix_world @ v.co for v in gz.data.vertices]
    sol = [v for v in vs if v.x > 0]; sag = [v for v in vs if v.x < 0]
    def ort(a): return sum(a, Vector()) / len(a)
    print("GOZ merkez sol", tuple(round(c, 2) for c in ort(sol)), "sag", tuple(round(c, 2) for c in ort(sag)))
    # göz bebeği yönü: her gözde iris (en önde, -Y) köşelerinin ortalaması - göz merkezi
    for ad, g in (("sol", sol), ("sag", sag)):
        c = ort(g); on = sorted(g, key=lambda v: v.y)[:max(4, len(g) // 12)]
        d = (ort(on) - c).normalized(); print("GOZ yon", ad, tuple(round(x, 3) for x in d), "sapma_x_derece", round(math.degrees(math.atan2(d.x, -d.y)), 1))
head = arm.matrix_world @ arm.data.bones["Head"].head_local
eye_z = ort(vs).z if gz else head.z + 8
target = Vector((0.0, ort(vs).y if gz else head.y, eye_z))
cam = bpy.data.objects.new("K", bpy.data.cameras.new("K")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = target + Vector((0, -55, 1)); cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 85; cam.data.clip_start = 1; cam.data.clip_end = 5000
sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'TEXTURE'
sc.render.resolution_x = 800; sc.render.resolution_y = 500; sc.render.filepath = out
bpy.ops.render.render(write_still=True); print("GOZ TAMAM", out)
