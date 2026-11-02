import bpy, glob, os
root = "C:/Users/Onur/Sisli/Indir/polyhaven/models"
for d in sorted(os.listdir(root)):
    g = glob.glob(f"{root}/{d}/*.gltf")
    if not g: continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=g[0])
    obs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    print("##", d, len(obs))
    for o in obs[:14]:
        print("   %-40s dim=(%.2f, %.2f, %.2f) loc=(%.2f, %.2f, %.2f)" % (o.name, *o.dimensions, *o.matrix_world.translation))
