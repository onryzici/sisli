# Sisli — oda1.py'nin dışı: avlu → dar sokak (kilitli kapı) → rıhtım + iskele (projektör, su). oda1.py içinden exec edilir.
# Blender koordinatı: oda x 0..11, y -1..8, arka duvar y 8..8.32; yol +Y yönünde ilerler.
M_TAS = pbr("cobblestone_floor_05", 1.0, (0.5, 0.52, 0.55), 1.0, puddles=True)
M_CATI = pbr("ceramic_roof_01", 1.0, (0.3, 0.29, 0.29))
M_SIVA2 = pbr("blue_plaster_weathered", 1.0, (0.42, 0.46, 0.5))
M_BETON = pbr("concrete_floor_worn_001", 1.0, (0.4, 0.41, 0.43))
M_CAM = flat("M_Cam", (0.01, 0.012, 0.015), 0.08)
M_SICAK = flat("M_SicakCam", (0.2, 0.1, 0.04), 0.3, (1.0, 0.45, 0.15), 3.0)
M_SU = flat("M_Su", (0.004, 0.006, 0.008), 0.05)
SX0, SX1 = 3.5, 9.5          # sokak genişliği
Y_AVLU, Y_RIHTIM, Y_SU = 11.5, 44.0, 48.0
# ---------------- zeminler ----------------
box("DisZemin", -40, 50, RY + 0.3, Y_SU, -0.15, -0.02, M_CAMUR, 4.0)
box("SokakTas", SX0, SX1, Y_AVLU - 1.5, Y_RIHTIM, -0.05, 0.0, M_TAS, 2.0)
box("Rihtim", -12, 26, Y_RIHTIM, Y_SU, -1.7, 0.0, M_BETON, 2.0)
box("Su", -80, 90, Y_SU, 130, -2.4, -1.0, M_SU, 0)
# odanın önü ve yanları: zemin + karanlık harabe siluetleri (kadraj kenarında boşluk görünmesin)
box("OnZemin", -40, 50, -14.0, RY + 0.3, -0.15, -0.02, M_CAMUR, 4.0)
random.seed(41)
for (xa, xb) in ((-7.0, -0.35), (RX + 0.35, RX + 7.0)):
    yy = -12.0
    while yy < RY + 0.3:
        w = random.uniform(0.8, 2.2); box("YanHarabe", xa, xb, yy, min(RY + 0.3, yy + w), 0, random.uniform(3.0, 7.5), M_KOYU, 0); yy += w
# avlu duvarları (odadan sokağa kapalı geçit)
for (x0, x1) in ((-0.3, 0.0), (RX, RX + 0.3)):
    yy = RY + 0.3
    while yy < Y_AVLU:
        w = random.uniform(0.7, 1.3); box("AvluDuvar", x0, x1, yy, min(Y_AVLU, yy + w), 0, random.uniform(2.2, 3.4), M_TUGLA, 2.0); yy += w
box("AvluArka", -0.3, SX0, Y_AVLU - 0.3, Y_AVLU, 0, 3.0, M_TUGLA, 2.0); box("AvluArka", SX1, RX + 0.3, Y_AVLU - 0.3, Y_AVLU, 0, 3.0, M_TUGLA, 2.0)
# ---------------- ev sıraları ----------------
def cati(name, x0, x1, y0, y1, h, rh):
    bm = bmesh.new(); xm = (x0 + x1) / 2
    v = [bm.verts.new(p) for p in ((x0 - 0.35, y0, h), (x1 + 0.35, y0, h), (xm, y0, h + rh), (x0 - 0.35, y1, h), (x1 + 0.35, y1, h), (xm, y1, h + rh))]
    for f in ((0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)): bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col.objects.link(o); me.materials.append(M_CATI); uv_cube(o, 2.0); o["static"] = True
def ev(name, x0, x1, y0, y1, h, mat, yuz, sicak=False, kapi=True):
    box(name, x0, x1, y0, y1, 0, h, mat, 2.0)
    if random.random() < 0.8: cati(name + "Cati", x0, x1, y0, y1, h, random.uniform(1.4, 2.4))
    fx = x1 + 0.012 if yuz > 0 else x0 - 0.012
    katlar = int((h - 0.6) // 2.6)
    for k in range(katlar):
        z0 = 0.9 + k * 2.6 if k else 1.0
        ny = max(1, int((y1 - y0 - 0.8) // 2.0))
        for j in range(ny):
            a = y0 + 0.6 + j * (y1 - y0 - 1.2) / ny + 0.3
            if k == 0 and kapi and j == ny // 2:
                quad(name + "Kapi", "x", fx, yuz, a - 0.1, a + 0.95, 0.0, 2.1, M_CAM); continue
            m = M_SICAK if (sicak and k == katlar - 1 and j == 0) else M_CAM
            quad(name + "Pen", "x", fx, yuz, a, a + 0.85, z0, z0 + 1.3, m)
def sira(x0, x1, yuz, seed):
    random.seed(seed); y = Y_AVLU; i = 0
    while y < Y_RIHTIM - 0.1:
        w = min(random.uniform(4.5, 7.0), Y_RIHTIM - y)
        if Y_RIHTIM - (y + w) < 2.5: w = Y_RIHTIM - y
        ev(f"Ev{seed}_{i}", x0, x1, y, y + w, random.uniform(4.6, 7.6), random.choice((M_SIVA, M_SIVA2, M_TUGLA)), yuz, sicak=(i == 3))
        y += w; i += 1
sira(-3.0, SX0, +1, 5); sira(SX1, 16.0, -1, 9)
# ---------------- sokak eşyaları ----------------
fence = load_ph("modular_chainlink_fence", names=["modular_chainlink_fence_double"], join_name="cit")
lamp = load_ph("street_lamp_01"); barrier = load_ph("concrete_road_barrier"); can = load_ph("metal_trash_can")
car = load_ph("covered_car"); ubox = load_ph("utility_box_01"); buoy = load_ph("lifebuoy")
GATE_Y = 30.0; GX0, GX1 = 5.45, 7.55   # kapı kanadı (Unreal'de BP_Kapi, menteşe GX0)
for (xa, xb) in ((SX0, GX0), (GX1, SX1)):
    o = put(fence, ((xa + xb) / 2, GATE_Y, 0.0), rotz=0, s=1.0)
    o.scale = ((xb - xa) / 1.91, 1.0, 1.0); PLACE[-1]["scale_xyz"] = [(xb - xa) / 1.91, 1.0, 1.0]
ISARET["kapi_mentese"] = [GX0, GATE_Y, 0.0]
put(barrier, (4.4, 26.5, 0), rotz=14); put(barrier, (8.6, 33.8, 0), rotz=-8)
put(car, (8.3, 18.5, 0), rotz=4); put(can, (4.0, 22.5, 0), rotz=30); put(bag, (3.9, 23.2, 0), rotz=10); put(bag, (9.1, 37.5, 0), rotz=60)
put(barrel, (4.0, 36.5, 0)); put(barrel, (4.5, 37.1, 0), rotz=40); put(ubox, (9.3, 24.0, 0), rotz=-90)
put(crate, (8.9, 40.5, 0), rotz=8); put(wcrate, (4.2, 41.5, 0), rotz=-25); put(tyre, (6.8, 15.0, 0.08), rotx=90, rotz=20)
put(lamp, (9.15, 27.2, 0.0), rotz=180); ISARET["lamba1"] = [9.15 - 1.15, 27.2, 3.55]
put(lamp, (3.85, 45.6, 0.0), rotz=0); ISARET["lamba2"] = [3.85 + 1.15, 45.6, 3.55]
# eğik elektrik direği avluda + sokağın üstünden teller
put(pole, (10.0, 10.6, 0.0), rotz=80, roty=-9)
wire(Vector((8.9, 10.8, 5.3)), Vector((2.6, 25.0, 6.4)), 0.9, "TelA"); wire(Vector((11.1, 10.5, 5.4)), Vector((15.5, 31.0, 7.2)), 1.2, "TelB")
wire(Vector((3.0, 33.0, 5.8)), Vector((10.0, 36.0, 6.1)), 0.6, "TelC")
# su kulesi doğu evlerin arkasında (çatıların üstünden görünür)
kul.location = (19.0, 36.0, 0.0)
# ---------------- iskele ----------------
PX0, PX1, PY1 = 5.3, 7.7, 70.0
y = Y_SU - 0.4
while y < PY1:
    box("IskeleTahta", PX0, PX1, y, y + 0.24, -0.08, 0.0, M_KIRIS, 1.0); y += 0.27
yy = Y_SU + 0.6
while yy < PY1 + 0.1:
    for xx in (PX0 + 0.1, PX1 - 0.1):
        box("IskeleDirek", xx - 0.1, xx + 0.1, yy - 0.1, yy + 0.1, -2.4, 0.5 if random.random() < 0.6 else 0.9, M_KIRIS, 1.0)
    box("IskeleKiris", PX0, PX1, yy - 0.08, yy + 0.08, -0.3, -0.08, M_KIRIS, 1.0)
    yy += 2.4
# siper sandık yığınları (projektörden saklanma) — kule tarafı (doğu)
M_SANDIK = pbr("brown_planks_05", 1.0, (0.36, 0.33, 0.3))
for sy in (54.2, 59.6, 65.0):   # üç katlı eski sandık yığını (çocuğu projektörden saklar)
    z = 0.0
    for kk, (sz, h) in enumerate(((1.0, 0.62), (0.92, 0.6), (0.8, 0.6))):
        rot_box("Siper", (PX1 - 0.55 + random.uniform(-0.05, 0.05), sy + 0.55 + random.uniform(-0.08, 0.08), z + h / 2), (sz * 0.95, sz, h), (0, 0, random.uniform(-9, 9)), M_SANDIK, 1.0)
        z += h
put(buoy, (PX0 + 0.05, 52.0, 0.55), rotz=90, rotx=90)
put(lamp, (PX0 + 0.25, PY1 - 0.4, 0.0), rotz=0); ISARET["lamba3"] = [PX0 + 0.25 + 1.15, PY1 - 0.4, 3.55]
# gözetleme kulesi (suyun içinde, iskelenin doğusunda) — projektör
TX, TY, TH = 14.5, 62.0, 4.6
for dx in (-1.0, 1.0):
    for dy in (-1.0, 1.0):
        rot_box("KuleDirek", (TX + dx, TY + dy, (TH - 2.4) / 2), (0.22, 0.22, TH + 2.4), (dy * 4, -dx * 4, 0), M_KOYU, 0)
box("KulePlatform", TX - 1.4, TX + 1.4, TY - 1.4, TY + 1.4, TH, TH + 0.18, M_KIRIS, 1.0)
box("KuleKulube", TX - 0.9, TX + 0.9, TY - 0.6, TY + 1.2, TH + 0.18, TH + 2.2, M_KOYU, 0)
ISARET["projektor"] = [TX - 0.9, TY - 0.7, TH + 1.0]; ISARET["projektor_merkez"] = [6.5, 60.0, 0.0]
# karşı kıyı siluetleri + vinç
random.seed(77)
for k in range(16):
    x0 = random.uniform(-45, 55); y0 = random.uniform(84, 92); w = random.uniform(4, 11); h0 = random.uniform(3, 13)
    h0 = random.uniform(2.5, 8.5); y1 = y0 + random.uniform(3, 8)
    box(f"Kiyi{k}", x0, x0 + w, y0, y1, -1.2, h0, M_KOYU, 0)
    if random.random() < 0.6: cati(f"KiyiCati{k}", x0, x0 + w, y0, y1, h0, random.uniform(1.2, 3.0))
rot_box("Vinc", (-8.0, 86.0, 9.0), (0.6, 0.6, 20.0), (0, 0, 0), M_KOYU, 0); rot_box("VincKol", (-1.0, 86.0, 18.0), (16.0, 0.5, 0.6), (0, -6, 0), M_KOYU, 0)
rot_box("VincIp", (5.5, 86.0, 13.0), (0.04, 0.04, 9.0), (0, 0, 0), M_KOYU, 0)
trunk = load_ph("dead_tree_trunk_02"); put(trunk, (22.5, 45.6, -0.1), roty=-84, rotz=8)
# gök kartı: karşı kıyının arkasında aydınlık sis
quad("GokKarti", "y", 100.0, -1, -90, 100, -5, 60, M_GOK)
# ---------------- oyun işaretleri ----------------
ISARET["kamera2"] = [4.9, 9.4, 2.5]; ISARET["kamera2_hedef"] = [6.5, 28.0, 0.9]; ISARET["odak2"] = [6.5, 15.5, 0.0]
ISARET["kamera3"] = [5.4, 40.2, 2.6]; ISARET["kamera3_hedef"] = [7.4, 66.0, 0.0]; ISARET["odak3"] = [6.4, 47.5, 0.0]
ISARET["alan1_a"] = [-0.3, -1.0, -0.5]; ISARET["alan1_b"] = [RX + 0.3, RY + 0.2, H]
ISARET["alan2_a"] = [-3.0, RY + 0.4, -0.5]; ISARET["alan2_b"] = [16.0, Y_RIHTIM - 0.6, 7.0]
ISARET["alan3_a"] = [-12.0, Y_RIHTIM - 0.5, -3.0]; ISARET["alan3_b"] = [26.0, 100.0, 7.0]
ISARET["donus_iskele"] = [6.5, 46.2, 0.1]
ISARET["su_a"] = [-60.0, Y_SU + 0.05, -4.0]; ISARET["su_b"] = [80.0, 120.0, -0.5]
ISARET["son"] = [6.5, PY1 - 0.6, 1.0]
ISARET["anahtar"] = [3.2, 5.0, 0.05]
# görünmez sınırlar (Unreal'de gizli çarpışma kutusu): oda önü, kapalı kapı boşluğu, rıhtım uçları ve arkası
SINIR = [((0, -1.35, 0), (RX, -1.0, 3.0)), ((-0.65, 2.6, 0), (-0.3, 3.8, 2.4)),
         ((-12.35, Y_RIHTIM - 0.3, 0), (-12.0, Y_SU, 3)), ((26.0, Y_RIHTIM - 0.3, 0), (26.35, Y_SU, 3)),
         ((-12.0, Y_RIHTIM - 0.35, 0), (-3.0, Y_RIHTIM, 3)), ((16.0, Y_RIHTIM - 0.35, 0), (26.0, Y_RIHTIM, 3))]
for i, (a, b) in enumerate(SINIR): ISARET[f"sinir{i}_a"] = list(a); ISARET[f"sinir{i}_b"] = list(b)
