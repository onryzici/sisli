# Pil bekçisi: pil üzerinde %8'de işaret dosyası (yeni iş başlatma), %5'te: başsız UE/Blender işlerini kısa bekle,
# editörü düzgün kapatmayı dene, Sisli'yi git'e işle + GitHub'a it, sonra bilgisayarı kapat. Fişe takılırsa hiçbir şey yapmaz.
$log = "C:\Users\Onur\Sisli\Araclar\pil_bekci.log"
$flag = "C:\Users\Onur\Sisli\Araclar\pil_dusuk.flag"
function L($m) { $t = "$(Get-Date -Format 'HH:mm:ss') $m"; Add-Content -Path $log -Value $t -Encoding utf8; Write-Output $t }
Remove-Item $flag -ErrorAction SilentlyContinue
L "basladi"
$son = -1
while ($true) {
  $b = Get-CimInstance Win32_Battery
  $c = [int]$b.EstimatedChargeRemaining; $s = [int]$b.BatteryStatus
  $pilde = ($s -eq 1 -or $s -eq 4 -or $s -eq 5)
  if ($c -ne $son) { L "pil %$c durum $s"; $son = $c }
  if ($pilde -and $c -le 8) { New-Item -ItemType File -Path $flag -Force | Out-Null }
  if ($pilde -and $c -le 5) {
    L "ESIK: %$c - kapatma basliyor"
    $bitis = (Get-Date).AddSeconds(120)
    while ((Get-Date) -lt $bitis -and (Get-Process UnrealEditor-Cmd, blender -ErrorAction SilentlyContinue)) { Start-Sleep 5 }
    Get-Process UnrealEditor-Cmd, UnrealEditor, blender -ErrorAction SilentlyContinue | ForEach-Object {
      if ($_.Name -eq 'UnrealEditor' -and $_.MainWindowHandle -ne 0) { L "editor kapatiliyor $($_.Id)"; $_.CloseMainWindow() | Out-Null }
      else { L "bitiriliyor $($_.Name) $($_.Id)"; Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue } }
    Start-Sleep 20
    # git: yarım kalan iş de olsa kaydet ve it (en fazla 4 dk)
    $g = Start-Process -FilePath "C:\Program Files\Git\bin\bash.exe" -ArgumentList '-lc "cd /c/Users/Onur/Sisli && git add -A && git commit -q -m \"Pil %5: otomatik kayit (is yarim kalmis olabilir)\" ; git push -q origin main"' -PassThru -WindowStyle Hidden
    if (-not $g.WaitForExit(240000)) { L "git push zaman asimi"; Stop-Process -Id $g.Id -Force -ErrorAction SilentlyContinue } else { L "git cikis $($g.ExitCode)" }
    L "shutdown /s /f /t 15"
    shutdown /s /f /t 15 /c "Sisli: pil %5 - kayit tamam, kapatiliyor"
    L "shutdown cikis $LASTEXITCODE"
    if ($LASTEXITCODE -ne 0) { Stop-Computer -Force }
    break
  }
  Start-Sleep 30
}
