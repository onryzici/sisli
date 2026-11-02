#!/bin/bash
# Ekran dışı oyun karesi: ue_kare.sh <saniye> <çıktı_önek>  (son 4 kareyi kopyalar)
cd /c/Users/Onur/Sisli/Unreal && rm -rf Saved/Screenshots
powershell -c "\$p = Start-Process 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList '\"C:/Users/Onur/Sisli/Unreal/Sisli.uproject\" ${UE_MAP:-/Game/Sisli/Maps/L_Sisli} -game -RenderOffscreen -ResX=${UE_RX:-1280} -ResY=${UE_RY:-720} ${UE_SES--nosound} -unattended -dumpmovie -ExecCmds=\"t.MaxFPS 6,${UE_EK:-r.Fog 1}\"' -PassThru; \$p.PriorityClass = 'BelowNormal'; Start-Sleep $1; Stop-Process -Id \$p.Id -Force -ErrorAction SilentlyContinue"
mkdir -p /c/Users/Onur/Sisli/Unreal/Saved/Test
i=0; for f in $(ls Saved/Screenshots/WindowsEditor/*.png | tail -12 | awk 'NR%3==0'); do cp $f Saved/Test/$2_$i.png; i=$((i+1)); done
ls Saved/Test/$2_*
