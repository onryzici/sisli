# Normal map biçimi testi: yükseklik (displacement) haritasının dikey eğimi ile normal haritanın G kanalı arasındaki korelasyon.
# OpenGL (Y+): G, görüntüde YUKARI doğru yükselen yüzeyde negatif değil... → corr(G, -dh/dsatir) işaretine bakılır.
# kullanım: blender -b -P normal_kip.py -- <normal.jpg> <disp.jpg> [...]
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index("--") + 1:]
for i in range(0, len(a), 2):
    def yukle(p):
        im = bpy.data.images.load(p); im.scale(512, 512)
        px = np.empty(512 * 512 * 4, dtype=np.float32); im.pixels.foreach_get(px)
        return px.reshape(512, 512, 4)   # Blender: satır 0 = görüntünün ALTI
    n = yukle(a[i]); d = yukle(a[i + 1])[..., 0]
    g = n[..., 1] - 0.5; r = n[..., 0] - 0.5
    dy = np.gradient(d, axis=0)   # satır artınca görüntüde YUKARI (Blender pixels alttan başlar)
    dx = np.gradient(d, axis=1)
    cy = np.corrcoef(g.ravel(), -dy.ravel())[0, 1]; cx = np.corrcoef(r.ravel(), -dx.ravel())[0, 1]
    # normal, yüksekliğin arttığı yönün tersine eğilir: OpenGL'de G = -dh/d(yukarı) → cy > 0
    print("NORMALKIP", a[i].split("/")[-1], "corrR=%.3f corrG=%.3f" % (cx, cy), "→", "OpenGL" if cy > 0 else "DirectX")
