# Yatakhane kâğıtları: kurallar (daktilo, sararmış, mühür) + Ela'nın pastel boya çizimi. kagitlar.ps1 <çıktı klasörü>
param([string]$Out)
Add-Type -AssemblyName System.Drawing
New-Item -ItemType Directory -Force $Out | Out-Null
$R = New-Object System.Random 7
function Kagit([int]$w, [int]$h, $taban) {
  $b = New-Object System.Drawing.Bitmap $w, $h; $g = [System.Drawing.Graphics]::FromImage($b); $g.SmoothingMode = 'AntiAlias'; $g.Clear($taban)
  # lif + leke: yarı saydam benekler ve büyük sararma lekeleri
  for ($i = 0; $i -lt 9000; $i++) { $c = [System.Drawing.Color]::FromArgb($R.Next(6, 22), $R.Next(60, 120), $R.Next(50, 100), $R.Next(30, 70)); $x = $R.Next($w); $y = $R.Next($h); $g.FillRectangle((New-Object System.Drawing.SolidBrush $c), $x, $y, $R.Next(1, 4), $R.Next(1, 3)) }
  for ($i = 0; $i -lt 14; $i++) { $s = $R.Next(80, 360); $c = [System.Drawing.Color]::FromArgb($R.Next(10, 28), 120, 90, 40); $g.FillEllipse((New-Object System.Drawing.SolidBrush $c), $R.Next(-100, $w), $R.Next(-100, $h), $s, $s * (0.6 + $R.NextDouble())) }
  # kenar kararması
  for ($k = 0; $k -lt 40; $k++) { $p = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(5, 70, 50, 20)), 6; $g.DrawRectangle($p, $k * 3, $k * 3, $w - $k * 6, $h - $k * 6) }
  return @($b, $g)
}
# ---------- 1) kurallar ----------
$kb = Kagit 1024 1448 ([System.Drawing.Color]::FromArgb(255, 214, 202, 170)); $b = $kb[0]; $g = $kb[1]
$m = [System.Drawing.Color]::FromArgb(235, 38, 34, 32); $f1 = New-Object System.Drawing.Font 'Courier New', 38, ([System.Drawing.FontStyle]::Bold); $f2 = New-Object System.Drawing.Font 'Courier New', 25
$br = New-Object System.Drawing.SolidBrush $m
$g.DrawString("4. YATAKHANE", $f2, $br, 90, 110); $g.DrawString("YATAKHANE KURALLARI", $f1, $br, 90, 170)
$g.DrawLine((New-Object System.Drawing.Pen $m, 3), 90, 240, 934, 240)
$satir = @("1. Işıklar saat 21.00'de söner.", "2. Gece sayımında herkes yatağında olur.", "3. Yatakhanede konuşmak yasaktır.", "4. Bakıcının izni olmadan kapıdan", "   çıkılmaz.", "5. Kardeşler ayrı ranzalarda yatar.", "6. Kural dışı hareket eden çocuk", "   ayrılır.")
$y = 300; foreach ($s in $satir) { $g.DrawString($s, $f2, $br, 90 + $R.Next(-2, 3), $y + $R.Next(-2, 3)); $y += 62 }
$g.DrawString("Müdürlük", $f2, $br, 640, 1010)
# mühür: mor halka + yazı, eğik
$g.TranslateTransform(300, 1120); $g.RotateTransform(-14)
$mp = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(150, 92, 40, 110)), 7; $g.DrawEllipse($mp, -120, -120, 240, 240); $g.DrawEllipse((New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(120, 92, 40, 110)), 3), -95, -95, 190, 190)
$g.DrawString("ONAYLI", (New-Object System.Drawing.Font 'Arial Black', 30), (New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(140, 92, 40, 110))), -82, -26)
$g.ResetTransform()
# biri "6"nın altını tırnakla kazımış
$g.DrawLine((New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(90, 120, 30, 20)), 2), 120, 798, 690, 806)
$b.Save("$Out\T_Kurallar.png"); $g.Dispose(); $b.Dispose()
# ---------- 2) Ela'nın çizimi (pastel boya) ----------
$kb = Kagit 1448 1024 ([System.Drawing.Color]::FromArgb(255, 226, 222, 208)); $b = $kb[0]; $g = $kb[1]
function Pastel($g, $renk, [double[]]$pts, [int]$kat = 5, [double]$kal = 7) {
  for ($k = 0; $k -lt $kat; $k++) {
    $p = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb($R.Next(110, 190), $renk.R, $renk.G, $renk.B)), ($kal * (0.6 + $R.NextDouble() * 0.6))
    $p.StartCap = 'Round'; $p.EndCap = 'Round'; $p.LineJoin = 'Round'
    $arr = New-Object 'System.Drawing.PointF[]' ($pts.Length / 2)
    for ($i = 0; $i -lt $pts.Length; $i += 2) { $arr[$i / 2] = New-Object System.Drawing.PointF ($pts[$i] + $R.Next(-4, 5)), ($pts[$i + 1] + $R.Next(-4, 5)) }
    $g.DrawCurve($p, $arr, 0.35)
  }
}
function Tara($g, $renk, $x0, $y0, $x1, $y1, $adim) {  # pastel boya dolgusu: çapraz, düzensiz çizgiler
  for ($x = $x0; $x -lt $x1; $x += $adim) { Pastel $g $renk @($x, $y1, ($x + $adim * 2), $y0) 1 5 }
}
$gri = [System.Drawing.Color]::FromArgb(255, 95, 98, 104); $siyah = [System.Drawing.Color]::FromArgb(255, 35, 32, 36)
$kir = [System.Drawing.Color]::FromArgb(255, 205, 32, 28); $kah = [System.Drawing.Color]::FromArgb(255, 110, 70, 40); $pem = [System.Drawing.Color]::FromArgb(255, 220, 120, 150)
$mavi = [System.Drawing.Color]::FromArgb(255, 70, 100, 170); $sari = [System.Drawing.Color]::FromArgb(255, 220, 190, 90)
# dev bina (sağda), üstü sayfadan taşıyor, minik pencereler
Pastel $g $siyah @(800, 980, 800, 120, 1380, 60, 1400, 980) 4 6
Tara $g $gri 810 90 1390 970 18
for ($sat = 0; $sat -lt 7; $sat++) { for ($sut = 0; $sut -lt 6; $sut++) { $x = 850 + $sut * 88; $y = 170 + $sat * 110; Pastel $g $siyah @($x, $y, ($x + 40), $y, ($x + 40), ($y + 45), $x, ($y + 45), $x, $y) 2 4 } }
# kırmızı ışık: bina tepesinde, ışınlarıyla
for ($i = 0; $i -lt 3; $i++) { Pastel $g $kir @(1080, 40, 1150, 20, 1200, 60, 1150, 100, 1090, 90, 1080, 40) 2 9 }
foreach ($a in 0..11) { $t = $a * [math]::PI / 6; Pastel $g $kir @((1140 + 80 * [math]::Cos($t)), (60 + 80 * [math]::Sin($t)), (1140 + 140 * [math]::Cos($t)), (60 + 140 * [math]::Sin($t))) 2 6 }
# yer çizgisi
Pastel $g $kah @(40, 900, 400, 890, 790, 905) 3 8
# abi (uzun): kahverengi saç, mavi tulum
$ax = 300; Pastel $g $siyah @(($ax - 45), 470, ($ax - 30), 420, $ax, 405, ($ax + 32), 420, ($ax + 45), 470, ($ax + 30), 515, $ax, 525, ($ax - 32), 512, ($ax - 45), 470) 3 6
Tara $g $kah ($ax - 50) 390 ($ax + 50) 440 12
Pastel $g $mavi @($ax, 525, $ax, 720) 4 12; Pastel $g $mavi @($ax, 720, ($ax - 45), 880) 3 10; Pastel $g $mavi @($ax, 720, ($ax + 45), 880) 3 10
Pastel $g $mavi @(($ax - 70), 650, $ax, 580, ($ax + 110), 640) 3 9
Pastel $g $siyah @(($ax - 18), 465, ($ax - 12), 468) 2 6; Pastel $g $siyah @(($ax + 14), 465, ($ax + 20), 468) 2 6; Pastel $g $siyah @(($ax - 15), 492, $ax, 500, ($ax + 16), 492) 2 4
# Ela (küçük): örgülü saç, pembe elbise, tavşan
$ex = 500; Pastel $g $siyah @(($ex - 38), 600, ($ex - 25), 560, $ex, 548, ($ex + 27), 560, ($ex + 38), 600, ($ex + 25), 638, $ex, 645, ($ex - 27), 636, ($ex - 38), 600) 3 6
Pastel $g $kah @(($ex - 40), 575, ($ex - 75), 640) 3 8; Pastel $g $kah @(($ex + 40), 575, ($ex + 75), 640) 3 8
Tara $g $pem ($ex - 55) 650 ($ex + 55) 790 12; Pastel $g $pem @(($ex - 55), 790, $ex, 645, ($ex + 55), 790, ($ex - 55), 790) 3 7
Pastel $g $pem @(($ex - 20), 790, ($ex - 25), 880) 3 8; Pastel $g $pem @(($ex + 20), 790, ($ex + 25), 880) 3 8
Pastel $g $pem @(($ex - 50), 690, ($ax + 110), 640) 3 8   # el ele
Pastel $g $sari @(($ex + 50), 690, ($ex + 110), 700) 2 7
Pastel $g $siyah @(($ex + 105), 640, ($ex + 140), 640, ($ex + 150), 690, ($ex + 140), 740, ($ex + 110), 740, ($ex + 100), 690, ($ex + 105), 640) 2 5   # tavşan
Pastel $g $siyah @(($ex + 112), 640, ($ex + 108), 590) 2 5; Pastel $g $siyah @(($ex + 132), 640, ($ex + 140), 592) 2 5
Pastel $g $siyah @(($ex - 12), 597, ($ex - 8), 600) 2 5; Pastel $g $siyah @(($ex + 10), 597, ($ex + 14), 600) 2 5; Pastel $g $kir @(($ex - 12), 620, $ex, 627, ($ex + 13), 620) 2 4
# yazı: ABİM VE BEN (titrek büyük harfler)
$fnt = New-Object System.Drawing.Font 'Segoe Print', 64, ([System.Drawing.FontStyle]::Bold)
$x = 70; foreach ($ch in "ABİM VE BEN".ToCharArray()) {
  $g.TranslateTransform($x, 130 + $R.Next(-14, 14)); $g.RotateTransform($R.Next(-12, 12))
  $g.DrawString([string]$ch, $fnt, (New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(200, 70, 100, 170))), 0, 0); $g.ResetTransform(); $x += ($(if ($ch -eq ' ') { 40 } else { 62 }))
}
# köşelerde bant
foreach ($c in @(@(-20, -10, 14), @(1360, -10, -10), @(-20, 950, -12), @(1370, 950, 9))) { $g.TranslateTransform($c[0] + 55, $c[1] + 35); $g.RotateTransform($c[2]); $g.FillRectangle((New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(120, 235, 225, 190))), -60, -22, 120, 44); $g.ResetTransform() }
$b.Save("$Out\T_ElaCizim.png"); $g.Dispose(); $b.Dispose()
"tamam"
