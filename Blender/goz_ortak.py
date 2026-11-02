# Şaşılık düzeltme — görüntüden ölçüm: yüzün önden ORTOGRAFİK çekimi (perspektif yanılgısı yok) → her gözde
# göz akı (parlak) ve iris (koyu) ağırlık merkezleri → iris akın ortasında değilse göz küresi kendi merkezi etrafında çevrilir.
# disa_aktar.py ve goz_test.py ortak kullanır.
import bpy, math, os, numpy as np
from mathutils import Matrix, Vector

def _goz_kumeleri(gz):
    mw = gz.matrix_world; vs = [mw @ v.co for v in gz.data.vertices]; r = {}
    for sol in (True, False):
        idx = [i for i, v in enumerate(vs) if (v.x > 0) == sol]
        mn = Vector([min(vs[i][k] for i in idx) for k in range(3)]); mx = Vector([max(vs[i][k] for i in idx) for k in range(3)])
        r[sol] = (idx, (mn + mx) / 2, (mx.x - mn.x) / 2)
    return r, vs

def _cek(sc, gz, yol, genislik):
    kume, vs = _goz_kumeleri(gz)
    m = (kume[True][1] + kume[False][1]) / 2
    cam = sc.objects.get("GozKam")
    if cam is None:
        cam = bpy.data.objects.new("GozKam", bpy.data.cameras.new("GozKam")); sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = genislik; cam.data.clip_start = genislik * 0.01; cam.data.clip_end = genislik * 200
    cam.location = m + Vector((0, -genislik * 4, 0)); cam.rotation_euler = (0.5 * math.pi, 0, 0)   # +Y'ye bakar, sağ = +X
    sc.camera = cam; sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'TEXTURE'
    sc.render.resolution_x = 1200; sc.render.resolution_y = 400; sc.render.filepath = yol
    # yalnız göz + cilt; cilt saf yeşil (göz akıyla karışmasın), kaş/saç/kıyafet gizli
    eski = []
    for o in sc.objects:
        if o.type != 'MESH' or o == gz: continue
        if o.name == "Ten":
            for m in o.data.materials: eski.append((m, tuple(m.diffuse_color))); m.diffuse_color = (0, 1, 0, 1)
        else: eski.append((o, o.hide_render)); o.hide_render = True
    bpy.ops.render.render(write_still=True)
    for a, v in eski:
        if isinstance(a, bpy.types.Material): a.diffuse_color = v
        else: a.hide_render = v
    im = bpy.data.images.load(yol, check_existing=False); w, h = im.size
    px = np.empty(w * h * 4, dtype=np.float32); im.pixels.foreach_get(px); bpy.data.images.remove(im)
    return px.reshape(h, w, 4), genislik / w

def olc(sc, gz, yol, genislik):
    """{sol: (iris - göz akı) yatay fark metre} — + = görüntüde sağa (+X)"""
    px, mpp = _cek(sc, gz, yol, genislik); h, w = px.shape[:2]
    lum = px[..., 0] * 0.3 + px[..., 1] * 0.59 + px[..., 2] * 0.11
    sat = px[..., :3].max(-1) - px[..., :3].min(-1)
    r = {}
    for sol, (x0, x1) in ((True, (w // 2, w)), (False, (0, w // 2))):
        L = lum[:, x0:x1]; S = sat[:, x0:x1]
        G_ = px[:, x0:x1, 1]; R_ = px[:, x0:x1, 0]
        ak = (L > 0.6) & (S < 0.18) & ~((G_ > 0.8) & (R_ < 0.3))   # göz akı: parlak, doygun değil, yeşil cilt değil
        if ak.sum() < 50: r[sol] = None; continue
        ys, xs = np.nonzero(ak); y0, y1 = ys.min(), ys.max()
        yesil = (G_ > 0.8) & (R_ < 0.3)
        koyu = (L < 0.35) & ~yesil
        bant = np.zeros_like(ak); bant[y0:y1 + 1, :] = True
        acik = (ak | koyu) & bant                       # göz kapağı aralığında görünen her şey (ak + iris)
        xs2 = np.nonzero(acik)[1]; xa, xb = xs2.min(), xs2.max()
        iris = koyu & bant
        if iris.sum() < 20: r[sol] = None; continue
        akx = (xa + xb) / 2.0; ix = np.nonzero(iris)[1].mean()   # aralığın ortası vs iris ağırlık merkezi
        r[sol] = (ix - akx) * mpp
    return r

def duzelt(sc, gz, klasor, yineleme=3):
    kume, _ = _goz_kumeleri(gz); genislik = (kume[True][1].x - kume[False][1].x) * 2.2
    for it in range(yineleme):
        f = olc(sc, gz, os.path.join(klasor, f"goz_{it}.png"), genislik)
        print("GOZ ölçüm", it, {("sol" if k else "sag"): (None if v is None else round(v * 1000, 2)) for k, v in f.items()}, "mm")
        kume, vs = _goz_kumeleri(gz); mwi = gz.matrix_world.inverted(); hepsi_iyi = True
        for sol, fark in f.items():
            if fark is None: continue
            idx, c, rr = kume[sol]
            th = -math.asin(max(-0.9, min(0.9, fark / rr)))
            if abs(math.degrees(th)) < 0.3: continue
            hepsi_iyi = False; rz = Matrix.Rotation(th, 3, 'Z')
            for i in idx: gz.data.vertices[i].co = mwi @ (c + rz @ (vs[i] - c))
            print("GOZ çevrildi", "sol" if sol else "sag", "%.2f°" % math.degrees(th))
        gz.data.update(); bpy.context.view_layer.update()
        if hepsi_iyi: break
    son = olc(sc, gz, os.path.join(klasor, "goz_son.png"), genislik)
    print("GOZ son", {("sol" if k else "sag"): (None if v is None else round(v * 1000, 2)) for k, v in son.items()}, "mm")
