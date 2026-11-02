import bpy, json, math, sys
from mathutils import Vector
argv = sys.argv[sys.argv.index("--")+1:]
J = json.load(open(argv[0]))["isaret"]; OUT = argv[1]
sc = bpy.context.scene
w = bpy.data.worlds.new("W"); sc.world = w; bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.02, 0.035, 0.05, 1); bg.inputs[1].default_value = 1.0
s = bpy.data.lights.new("Ay", 'SUN'); s.energy = 0.6; s.color = (0.7, 0.82, 1.0); s.angle = 0.05
so = bpy.data.objects.new("Ay", s); sc.collection.objects.link(so); so.rotation_euler = (math.radians(-62), 0, math.radians(180))  # arkadan (+Y) kameraya doğru
f = bpy.data.lights.new("Fener", 'POINT'); f.energy = 25; f.color = (1.0, 0.6, 0.3); f.shadow_soft_size = 0.05
fo = bpy.data.objects.new("Fener", f); sc.collection.objects.link(fo); fo.location = J["fener"]
# çocuk vekili
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.28, location=(J["baslangic"][0] + 1.0, J["baslangic"][1] + 2.0, 0.64))
# sis hacmi
bpy.ops.mesh.primitive_cube_add(size=1, location=(5, 40, 8)); fog = bpy.context.object; fog.scale = (120, 110, 18)
m = bpy.data.materials.new("Sis"); N = m.node_tree.nodes; N.remove(N["Principled BSDF"]); v = N.new("ShaderNodeVolumePrincipled")
v.inputs["Density"].default_value = 0.035; v.inputs["Color"].default_value = (0.7, 0.8, 0.9, 1); v.inputs["Anisotropy"].default_value = 0.5
m.node_tree.links.new(v.outputs[0], N["Material Output"].inputs["Volume"]); fog.data.materials.append(m)
cd = bpy.data.cameras.new("K"); cd.lens_unit = 'FOV'; cd.angle = math.radians(60); c = bpy.data.objects.new("K", cd); sc.collection.objects.link(c); sc.camera = c
c.location = J["kamera"]; c.rotation_euler = (Vector(J["kamera_hedef"]) - Vector(J["kamera"])).to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = 'CYCLES'; sc.cycles.device = 'GPU'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
try:
    p = bpy.context.preferences.addons["cycles"].preferences; p.compute_device_type = 'OPTIX'; p.get_devices()
    for d in p.devices: d.use = d.type != 'CPU'
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1280, 720; sc.view_settings.view_transform = 'AgX'
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
