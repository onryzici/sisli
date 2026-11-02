# Sessiz WAV üret (altyazı taşıyıcı sesler için): sessiz_wav.ps1 <klasör>  → sessiz_2s.wav ... sessiz_9s.wav
param([string]$Dir)
New-Item -ItemType Directory -Force $Dir | Out-Null
$rate = 22050
foreach ($s in 2..9) {
  $n = $rate * $s; $data = $n * 2
  $ms = New-Object System.IO.MemoryStream; $w = New-Object System.IO.BinaryWriter($ms)
  $w.Write([Text.Encoding]::ASCII.GetBytes("RIFF")); $w.Write([int](36 + $data)); $w.Write([Text.Encoding]::ASCII.GetBytes("WAVEfmt "))
  $w.Write([int]16); $w.Write([int16]1); $w.Write([int16]1); $w.Write([int]$rate); $w.Write([int]($rate * 2)); $w.Write([int16]2); $w.Write([int16]16)
  $w.Write([Text.Encoding]::ASCII.GetBytes("data")); $w.Write([int]$data); $w.Write((New-Object byte[] $data))
  [IO.File]::WriteAllBytes((Join-Path $Dir "sessiz_${s}s.wav"), $ms.ToArray()); $w.Dispose()
}
"tamam"
