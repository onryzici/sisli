#!/bin/bash
# Otomatik yürüyüş testi: yuru_test.sh <önek> <başlangıç 1|2|3> "x1 y1 x2 y2 x3 y3" [saniye]
# seviyeyi test yürütücüsüyle kurar, oyunu ekran dışı çalıştırır, karelerden 4'ünü (çeyrekler) alır, SISLI log satırlarını yazar
P=$1; A=/c/Users/Onur/Sisli/Araclar; U=/c/Users/Onur/Sisli/Unreal
ODA_TEST_BASLA=$2 ODA_TEST_YURU="$3" $A/oda_kur.sh >/dev/null
cd $U && rm -rf Saved/Screenshots
powershell -c "\$p = Start-Process 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList '\"C:/Users/Onur/Sisli/Unreal/Sisli.uproject\" /Game/Sisli/Maps/L_Oda1 -game -RenderOffscreen -ResX=1280 -ResY=720 -nosound -unattended -dumpmovie -ExecCmds=\"t.MaxFPS 6\"' -PassThru; \$p.PriorityClass = 'BelowNormal'; Start-Sleep ${4:-70}; Stop-Process -Id \$p.Id -Force -ErrorAction SilentlyContinue"
sleep 3
F=($(ls Saved/Screenshots/WindowsEditor/*.png)); N=${#F[@]}
for q in 1 2 3 4; do i=$(( N * q / 4 - 1 )); [ $i -lt 0 ] && i=0; cp "${F[$i]}" Saved/Test/${P}_$q.png; done
echo "kare: $N"; grep -a "SISLI" Saved/Logs/Sisli.log | sed 's/.*\] //' | cut -c1-120
