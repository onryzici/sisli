# Sisli — şehir genişletmesi (sahne.py içinden exec ile çalışır; box/pbr/load_ph/put/PLACE/flat yardımcılarını kullanır)
# Meydan + gözetleme kulesi + kilitli çit kapısı + iç mekânlı ev + itilebilir sandıklar + ek sokak lambaları.
# Hareketli parçalar o["dinamik"] ile işaretlenir (Unreal'de Blueprint olacak), oyun noktaları ISARET sözlüğüne yazılır.
import bmesh, math
from mathutils import Vector, Euler, Matrix
ISARET = {}
DYN = []

M_PARKE = pbr("brown_planks_05", 1.0, (0.55, 0.5, 0.45))
M_SIVA = pbr("clay_plaster", 1.0, (0.45, 0.47, 0.5))
M_ICBETON = pbr("concrete_floor_worn_001", 1.0, (0.4, 0.4, 0.42))
M_KULE = pbr("black_painted_planks", 1.0, (0.7, 0.7, 0.7))
M_TAS = pbr("concrete_layers", 1.0, (0.45, 0.46, 0.5))

def dyn(o, name):
    o["dinamik"] = name; o["static"] = False
    DYN.append(o); return o

# ---------- zemin: meydan ----------
SQ = (-16.0, 16.0, -48.0, -18.0)
box("Meydan", SQ[0], SQ[1], SQ[2], SQ[3], -0.05, 0.0, M_KALD, 2.0)

# ---------- ev sıraları (meydanı çevreler; arada boşluk yok) ----------
def house_block(name, x0, x1, y0, y1, h, mat, ridge_along_y=True, windows_face=None):
    o = box(name, x0, x1, y0, y1, 0.0, h, mat, 2.0)
    ov = 0.35; rh = 2.2
    bm = bmesh.new()
    if ridge_along_y:
        xm = (x0 + x1) / 2
        pts = [(x0 - ov, y0 - ov, h), (x1 + ov, y0 - ov, h), (xm, y0 - ov, h + rh), (x0 - ov, y1 + ov, h), (x1 + ov, y1 + ov, h), (xm, y1 + ov, h + rh)]
    else:
        ym = (y0 + y1) / 2
        pts = [(x0 - ov, y0 - ov, h), (x0 - ov, y1 + ov, h), (x0 - ov, ym, h + rh), (x1 + ov, y0 - ov, h), (x1 + ov, y1 + ov, h), (x1 + ov, ym, h + rh)]
    vs = [bm.verts.new(p) for p in pts]
    for f in [(0, 2, 1), (3, 4, 5), (0, 3, 5, 2), (1, 2, 5, 4), (0, 1, 4, 3)]: bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name + "_Cati"); bm.to_mesh(me); bm.free()
    r = bpy.data.objects.new(me.name, me); col.objects.link(r); me.materials.append(M_CATI); uv_cube(r, 2.0); r["static"] = True
    # cephe pencereleri (karanlık cam + çerçeve)
    if windows_face:
        axis, coord, sgn, a0, a1 = windows_face
        floors = int(h // 3.0)
        for fl in range(1, floors):
            n = max(1, int((a1 - a0) // 2.6))
            for k in range(n):
                c = a0 + (k + 0.5) * (a1 - a0) / n; zc = fl * 3.0 + 1.5
                ctr = (x0 + x1) / 2 if axis == 'x' else (y0 + y1) / 2
                ns = 1 if coord > ctr else -1   # dışa bakan normal
                quad(f"{name}_Cam{fl}{k}", axis, coord + ns * 0.01, ns, c - 0.45, c + 0.45, zc - 0.7, zc + 0.7, M_CAM)
    return o
random.seed(11)
# batı sırası (meydana bakan cephe x=-16)
y = -48.0; i = 0
while y < -18.0:
    w = min(random.uniform(5.5, 8.0), -18.0 - y)
    house_block(f"BatiEv{i}", -27, -16, y, y + w, random.choice([7.5, 9.0, 10.5]), random.choice(M_DUVAR), True, ('x', -16, -1, y, y + w)); y += w; i += 1
# güney sırası (cephe y=-48)
x = -27.0; i = 0
while x < 27.0:
    w = min(random.uniform(6.0, 9.0), 27.0 - x)
    house_block(f"GuneyEv{i}", x, x + w, -60, -48, random.choice([3.8, 4.4, 5.0]), random.choice(M_DUVAR), False, ('y', -48, -1, x, x + w)); x += w; i += 1
# doğu sırası: iç mekânlı evin güneyi ve kuzeyi
house_block("DoguEvG", 16, 27, -48, -40, 4.6, M_DUVAR[0], True, ('x', 16, 1, -48, -40))
house_block("DoguEvK", 16, 27, -28, -18, 10.5, M_DUVAR[3], True, ('x', 16, 1, -28, -18))
# kuzey köşe blokları (sokak evleriyle meydan arası boşlukları kapatır)
house_block("KuzeyBatiEv", -27, -11, -18, -8, 9.0, M_DUVAR[1] if len(M_DUVAR) > 1 else M_DUVAR[0], False, ('y', -18, -1, -27, -11))
house_block("KuzeyDoguEv", 11, 27, -18, -8, 7.5, M_DUVAR[2], False, ('y', -18, -1, 11, 27))

# ---------- iç mekânlı ev ----------
HX0, HX1, HY0, HY1 = 16.0, 26.0, -40.0, -28.0
T = 0.25; CEIL = 3.4; HTOP = 7.2
def wall_y(name, xc, y0, y1, z0, z1, opens, mat, t=T):
    """x=xc düzleminde, y boyunca duvar; opens=[(ya,yb,za,zb)] boşluklar"""
    cuts = sorted(opens); y = y0; k = 0
    for (ya, yb, za, zb) in cuts:
        if ya > y: box(f"{name}_{k}", xc - t / 2, xc + t / 2, y, ya, z0, z1, mat, 2.0); k += 1
        if za > z0: box(f"{name}_{k}", xc - t / 2, xc + t / 2, ya, yb, z0, za, mat, 2.0); k += 1
        if zb < z1: box(f"{name}_{k}", xc - t / 2, xc + t / 2, ya, yb, zb, z1, mat, 2.0); k += 1
        y = yb
    if y < y1: box(f"{name}_{k}", xc - t / 2, xc + t / 2, y, y1, z0, z1, mat, 2.0)
def wall_x(name, yc, x0, x1, z0, z1, opens, mat, t=T):
    cuts = sorted(opens); x = x0; k = 0
    for (xa, xb, za, zb) in cuts:
        if xa > x: box(f"{name}_{k}", x, xa, yc - t / 2, yc + t / 2, z0, z1, mat, 2.0); k += 1
        if za > z0: box(f"{name}_{k}", xa, xb, yc - t / 2, yc + t / 2, z0, za, mat, 2.0); k += 1
        if zb < z1: box(f"{name}_{k}", xa, xb, yc - t / 2, yc + t / 2, zb, z1, mat, 2.0); k += 1
        x = xb
    if x < x1: box(f"{name}_{k}", x, x1, yc - t / 2, yc + t / 2, z0, z1, mat, 2.0)
DOOR = (-34.6, -33.4, 0.0, 2.25)
WIN1 = (-38.4, -37.2, 1.0, 2.4); WIN2 = (-30.8, -29.6, 1.0, 2.4)
# dış kabuk (tuğla) — batı cephe kapı + 2 pencere
wall_y("EvDisBati", HX0, HY0, HY1, 0, HTOP, [DOOR, WIN1, WIN2], M_DUVAR[0])
wall_y("EvDisDogu", HX1, HY0, HY1, 0, HTOP, [], M_DUVAR[0])
wall_x("EvDisGuney", HY0, HX0 - T / 2, HX1 + T / 2, 0, 1.0, [], M_DUVAR[0])
wall_x("EvKesitGuney", HY0, HX0 - T / 2, HX1 + T / 2, 1.0, HTOP, [], M_DUVAR[0])   # kesit: içerideyken gizlenir
wall_x("EvDisKuzey", HY1, HX0 - T / 2, HX1 + T / 2, 0, HTOP, [], M_DUVAR[0])
# iç sıva kaplaması (iç yüzler) — aynı boşluklarla
ti = 0.04
wall_y("EvIcBati", HX0 + T / 2 + ti / 2, HY0 + T / 2, HY1 - T / 2, 0, CEIL, [DOOR, WIN1, WIN2], M_SIVA, ti)
wall_y("EvIcDogu", HX1 - T / 2 - ti / 2, HY0 + T / 2, HY1 - T / 2, 0, CEIL, [], M_SIVA, ti)
wall_x("EvIcGuney", HY0 + T / 2 + ti / 2, HX0 + T / 2, HX1 - T / 2, 0, 1.0, [], M_SIVA, ti)
wall_x("EvKesitIcGuney", HY0 + T / 2 + ti / 2, HX0 + T / 2, HX1 - T / 2, 1.0, CEIL, [], M_SIVA, ti)
wall_x("EvIcKuzey", HY1 - T / 2 - ti / 2, HX0 + T / 2, HX1 - T / 2, 0, CEIL, [], M_SIVA, ti)
# ara duvar (iki oda), kapı boşluğu
INNER_X = 22.3; INDOOR = (-32.7, -31.5, 0.0, 2.2)
wall_y("EvAraDuvar", INNER_X, HY0 + T / 2, HY1 - T / 2, 0, CEIL, [INDOOR], M_SIVA, 0.18)
# zemin, tavan, çatı
box("EvZemin", HX0, HX1, HY0, HY1, -0.02, 0.06, M_PARKE, 2.0)
box("EvTavan", HX0, HX1, HY0, HY1, CEIL, CEIL + 0.2, M_ICBETON, 2.0)
house_block("EvUst", HX0 - T / 2, HX1 + T / 2, HY0 - T / 2, HY1 + T / 2, HTOP, M_DUVAR[0], True, ('x', HX0 - T / 2, -1, HY0, HY1))
# (EvUst kutusu dış duvarları kaplar; iç hacmi boşaltmak için yalnız üst kısmını bırak)
ev_ust = bpy.data.objects["EvUst"]
for v in ev_ust.data.vertices:
    if v.co.z < 0.1: v.co.z = CEIL + 0.2
# kesit grubu: tavan, üst blok + çatısı, güney duvarı üst kısmı → Unreal da ayrı mesh, içerideyken gizlenir
for o in bpy.data.objects:
    if o.name.startswith(("EvTavan", "EvUst", "EvKesit")): o["grup"] = "EvKesit"
ISARET["ic_mekan_kutu"] = [[HX0, HX1], [HY0, HY1], [0.0, CEIL]]
# pencere çerçeveleri (kırık camsız; içeri ay ışığı girer)
for nm, (ya, yb, za, zb) in (("Pen1", WIN1), ("Pen2", WIN2)):
    for (a0, a1, b0, b1) in [(ya - 0.06, yb + 0.06, zb, zb + 0.08), (ya - 0.06, yb + 0.06, za - 0.08, za), (ya - 0.06, ya, za, zb), (yb, yb + 0.06, za, zb), ((ya + yb) / 2 - 0.025, (ya + yb) / 2 + 0.025, za, zb)]:
        box(f"{nm}_Cerceve", HX0 - 0.16, HX0 - 0.1, a0, a1, b0, b1, M_CERCEVE, 0)
# kapı kanadı (dinamik: menteşe kapının güney kenarında; pivot = menteşe)
kb = box("EvKapisi", 0, 0.06, 0, DOOR[1] - DOOR[0] - 0.02, 0, DOOR[3] - 0.03, M_KULE, 1.0)
kb.location = (HX0 - 0.03, DOOR[0] + 0.01, 0.02)
dyn(kb, "EvKapisi")
ISARET["ev_kapi_tetik"] = [HX0 - 1.0, (DOOR[0] + DOOR[1]) / 2, 1.0]

# iç eşyalar
table = load_ph("WoodenTable_01"); rock = load_ph("Rockingchair_01"); cab = load_ph("GothicCabinet_01", prefix="GothicCabinet_01", join_name="GothicCabinet_01")
drw = load_ph("drawer_cabinet", prefix="drawer_cabinet", join_name="drawer_cabinet"); box_ = load_ph("cardboard_box_01"); stable = load_ph("small_wooden_table_01")
shelf = load_ph("painted_wooden_shelves"); hlamp = load_ph("hanging_industrial_lamp"); lantern = load_ph("Lantern_01", prefix="Lantern_01", join_name="Lantern_01")
put(table, (19.2, -35.6, 0.06), rotz=90)
put(rock, (18.4, -30.0, 0.06), rotz=130)
put(cab, (20.0, -28.85, 0.06), rotz=180)
put(drw, (17.0, -39.4, 0.06), rotz=0)
put(box_, (21.4, -39.2, 0.06), rotz=15); put(box_, (21.6, -38.6, 0.06), rotz=-20); put(box_, (21.5, -39.0, 0.40), rotz=40)
put(shelf, (25.55, -36.5, 0.06), rotz=-90)
put(stable, (24.6, -34.2, 0.06), rotz=-90)
put(lantern, (19.5, -35.9, 0.61), rotz=30)
put(hlamp, (24.0, -32.0, CEIL - 1.36), rotz=0)
ISARET["arka_oda_lamba"] = [24.0, -32.0, CEIL - 1.25]
ISARET["fener_masa"] = [19.5, -35.9, 0.78]
# anahtar (dinamik): basit eski tip anahtar — halka + gövde + diş
def make_key():
    parts = []
    bpy.ops.mesh.primitive_torus_add(major_radius=0.028, minor_radius=0.006, location=(0, 0, 0), rotation=(math.radians(90), 0, 0)); parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0045, depth=0.09, location=(0.072, 0, 0), rotation=(0, math.radians(90), 0)); parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.105, 0, -0.012)); c = bpy.context.object; c.scale = (0.012, 0.004, 0.022); parts.append(c)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.088, 0, -0.008)); c = bpy.context.object; c.scale = (0.008, 0.004, 0.014); parts.append(c)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.transform_apply(location=False, rotation=True, scale=True); bpy.ops.object.join()
    k = bpy.context.object; k.name = "Anahtar"
    k.data.materials.clear(); k.data.materials.append(flat("M_Anahtar", (0.42, 0.3, 0.12), 0.35))
    bpy.ops.object.shade_smooth(); return k
key = make_key(); key.location = (24.55, -34.25, 0.60); key.rotation_euler = (0, 0, math.radians(35)); key.scale = (2.2, 2.2, 2.2)
dyn(key, "Anahtar")

# ---------- kilitli çit kapısı (sokak girişi, y=-17.5) ----------
GATE_Y = -17.6
for (xa, xb) in ((-4.2, -1.05), (1.05, 4.2)):
    o = put(fence, ((xa + xb) / 2, GATE_Y, 0.0), rotz=0, s=1.0)
    o.scale = ((xb - xa) / 1.91, 1.0, 1.0); PLACE[-1]["scale_xyz"] = [(xb - xa) / 1.91, 1.0, 1.0]
# kanat: çit parçası kopyası, menteşe sol kenarda (pivot), 2.1 m
gk = bpy.data.objects.new("CitKapisi", fence.data.copy()); col.objects.link(gk)
gk.data.transform(Matrix.Translation(Vector((1.91 / 2, 0, 0))))   # sol kenar orijinde
gk.data.transform(Matrix.Diagonal(Vector((2.1 / 1.91, 1, 1, 1))))
gk.location = (-1.05, GATE_Y, 0.0)
dyn(gk, "CitKapisi")
ISARET["kapi_tetik"] = [0.0, GATE_Y - 0.8, 1.0]

# ---------- gözetleme kulesi + projektör ----------
TX, TY = -12.0, -43.0; TH = 7.0
for dx in (-1.3, 1.3):
    for dy in (-1.3, 1.3):
        o = box("KuleBacak", TX + dx - 0.15, TX + dx + 0.15, TY + dy - 0.15, TY + dy + 0.15, 0, TH, M_KULE, 1.0)
box("KulePlatform", TX - 1.7, TX + 1.7, TY - 1.7, TY + 1.7, TH, TH + 0.2, M_KULE, 1.0)
for (x0, x1, y0, y1) in ((TX - 1.7, TX + 1.7, TY - 1.7, TY - 1.6), (TX - 1.7, TX + 1.7, TY + 1.6, TY + 1.7), (TX - 1.7, TX - 1.6, TY - 1.7, TY + 1.7), (TX + 1.6, TX + 1.7, TY - 1.7, TY + 1.7)):
    box("KuleKorkuluk", x0, x1, y0, y1, TH + 0.2, TH + 1.1, M_KULE, 1.0)
for z in (2.4, 4.8):   # çapraz kuşaklar
    box("KuleKusak", TX - 1.45, TX + 1.45, TY - 1.35, TY - 1.25, z, z + 0.15, M_KULE, 1.0)
    box("KuleKusak", TX - 1.45, TX + 1.45, TY + 1.25, TY + 1.35, z, z + 0.15, M_KULE, 1.0)
house_block("KuleCati", TX - 1.9, TX + 1.9, TY - 1.9, TY + 1.9, TH + 2.6, M_KULE, True)
bpy.data.objects["KuleCati"].data.vertices.foreach_set("co", [c for v in bpy.data.objects["KuleCati"].data.vertices for c in (v.co.x, v.co.y, max(v.co.z, TH + 2.4))])
ISARET["projektor"] = [TX + 1.2, TY + 1.2, TH + 1.3]
ISARET["projektor_hedef_merkez"] = [0.0, -30.0, 0.0]

# ---------- meydan eşyaları (siper) ----------
# çeşme kaidesi + sütun
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.4, depth=0.65, location=(1.0, -33.0, 0.325)); c = bpy.context.object; c.name = "CesmeKaide"
c.data.materials.append(M_TAS); uv_cube(c, 2.0); c["static"] = True
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.45, depth=2.6, location=(1.0, -33.0, 1.3)); c = bpy.context.object; c.name = "CesmeSutun"
c.data.materials.append(M_TAS); uv_cube(c, 2.0); c["static"] = True
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.75, depth=0.3, location=(1.0, -33.0, 2.6)); c = bpy.context.object; c.name = "CesmeTas"
c.data.materials.append(M_TAS); uv_cube(c, 2.0); c["static"] = True
barrier2 = load_ph("concrete_road_barrier_02"); trunk2 = load_ph("dead_tree_trunk_02"); stump = load_ph("tree_stump_01")
put(car, (-8.5, -25.5, 0), rotz=68)
put(car, (9.5, -43.5, 0), rotz=-12)
put(barrier2, (-3.0, -20.0, 0), rotz=8); put(barrier2, (3.2, -20.4, 0), rotz=-14); put(barrier2, (12.5, -30.5, 0), rotz=80)
put(trunk2, (7.5, -24.5, 0.05), rotz=-35); put(stump, (-6.0, -36.0, 0), rotz=20)
put(barrel, (-10.2, -40.6, 0)); put(barrel, (-9.6, -41.3, 0), rotz=30); put(barrel, (-13.4, -39.8, 0.28), rotx=90, rotz=10)
put(wcrate, (-14.5, -30.0, 0), rotz=10); put(wcrate, (-14.4, -29.9, 0.33), rotz=-5); put(crate, (-14.2, -27.2, 0), rotz=80)
put(can, (14.8, -24.0, 0), rotz=20); put(bag, (15.2, -23.2, 0), rotz=60); put(bag, (14.6, -45.5, 0), rotz=-10)
put(tyre, (-4.5, -45.0, 0.08), rotx=90, rotz=-20); put(tyre, (-4.0, -44.6, 0.24), rotx=90, rotz=40)
# itilebilir sandıklar (dinamik, fizik)
for k, (sx, sy) in enumerate(((13.5, -38.5), (11.8, -46.0))):
    o = box(f"Sandik{k}", -0.45, 0.45, -0.45, 0.45, 0.0, 0.9, M_PARKE, 1.0)
    o.location = (sx, sy, 0.0); o.rotation_euler = (0, 0, math.radians(15 * k))
    dyn(o, f"Sandik{k}")
# ek sokak lambaları (meydan) — kafa konumu lamba dönüşüyle birlikte
EXTRA_LAMPS = []
for (lx, ly, rz) in ((-5.5, -41.0, 0), (10.5, -21.5, 180), (-2.6, -10.0, 0)):
    put(lamp, (lx, ly, 0.0), rotz=rz)
    off = Vector((-1.15, 0, 0)); off.rotate(Euler((0, 0, math.radians(rz - 180))))
    EXTRA_LAMPS.append([lx + off.x, ly + off.y, 3.62])
ISARET["lambalar_ek"] = EXTRA_LAMPS
ISARET["titrek_lamba"] = 1   # EXTRA_LAMPS[1] titreyecek

# ---------- oyun noktaları ----------
ISARET["baslangic"] = [13.5, -40.0, 0.0]
ISARET["donus_meydan"] = [13.5, -40.0, 0.0]
ISARET["donus_iskele"] = [1.0, 16.0, 0.0]
ISARET["su_olum_kutusu"] = [[-60, 60], [16.6, 120], [-3.0, -1.6]]
ISARET["son_tetik"] = [1.0, 25.0, 0.5]
print("GENİŞLETME: dinamik", [o["dinamik"] for o in DYN], "işaret", list(ISARET))
