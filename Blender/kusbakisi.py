import bpy, math, sys
sc = bpy.context.scene
for o in sc.objects:
    if o.name == "Sis" or o.type == 'LIGHT': o.hide_render = True
    if o.name.startswith(("EvUst", "EvTavan")) or "_Cati" in o.name or o.name.startswith("Cati_") or o.name == "KuleCati": o.hide_render = True
w = sc.world; w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.62, 0.65, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
s = bpy.data.lights.new("UstGunes", 'SUN'); s.energy = 3.0; so = bpy.data.objects.new("UstGunes", s); sc.collection.objects.link(so); so.rotation_euler = (math.radians(25), math.radians(10), 0)
cd = bpy.data.cameras.new("Ust"); cd.type = 'ORTHO'; cd.ortho_scale = float(sys.argv[-1]) if sys.argv[-1].replace(".", "").isdigit() else 95
c = bpy.data.objects.new("Ust", cd); sc.collection.objects.link(c); c.location = (0, -15, 80); c.rotation_euler = (0, 0, 0); sc.camera = c
sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = 1400; sc.render.resolution_y = 1400
sc.view_settings.view_transform = 'Standard'
sc.render.filepath = "C:/Users/Onur/Sisli/Blender/render/kusbakisi.png"; bpy.ops.render.render(write_still=True)
