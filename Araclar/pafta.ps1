# Önizleme klasöründen etiketli pafta: pafta.ps1 <klasör> <önek M_|S_> <çıktı.png> [sütun] [hücre genişliği]
param([string]$Dir, [string]$Prefix, [string]$Out, [int]$Cols = 8, [int]$W = 240)
Add-Type -AssemblyName System.Drawing
$info = Get-Content (Join-Path $Dir 'bilgi.json') -Raw | ConvertFrom-Json
$files = Get-ChildItem $Dir -Filter "$Prefix*.png" | Sort-Object Name
$H = [int]($W * 0.75); $LH = 30
$rows = [math]::Ceiling($files.Count / $Cols)
$bmp = New-Object System.Drawing.Bitmap ($Cols * $W), ($rows * ($H + $LH))
$g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::FromArgb(20, 20, 22))
$font = New-Object System.Drawing.Font 'Consolas', 9; $br = [System.Drawing.Brushes]::Gainsboro
$i = 0
foreach ($f in $files) {
  $id = $f.BaseName.Substring($Prefix.Length); $x = ($i % $Cols) * $W; $y = [math]::Floor($i / $Cols) * ($H + $LH)
  $im = [System.Drawing.Image]::FromFile($f.FullName); $g.DrawImage($im, $x, $y, $W, $H); $im.Dispose()
  $b = $info.$id; $t = $id
  if ($b.tur -eq 'mesh') { $t += "  " + ($b.boyut_m -join 'x') + "m`n" + [math]::Round($b.tri / 1000) + "k tri" } elseif ($b.opak) { $t += "  (dekal)" }
  $g.DrawString($t, $font, $br, $x + 3, $y + $H + 1); $i++
}
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose(); "pafta: $Out ($($files.Count))"
