# Göz düzeltme doğrulaması (kaydetmez): blender -b cocuk_v2.blend -P goz_test.py -- <klasör>
import bpy, sys
sys.path.append("C:/Users/Onur/Sisli/Blender"); import goz_ortak as G
k = sys.argv[sys.argv.index("--") + 1]
G.duzelt(bpy.context.scene, bpy.context.scene.objects["Gozler"], k)
