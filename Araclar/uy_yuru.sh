#!/bin/bash
# Uyanış otomatik yürüyüş testi: uy_yuru.sh "x1 y1 x2 y2 x3 y3" [saniye]  — sonra seviyeyi normal haliyle yeniden kurar
A=/c/Users/Onur/Sisli/Araclar
UY_YURU="$1" $A/uy_kur.sh uyyuru ${2:-110} >/dev/null
grep -oE 'SISLI [A-Z_]+' /c/Users/Onur/Sisli/Unreal/Saved/Logs/Sisli.log | uniq -c
$A/uy_kur.sh >/dev/null; echo "seviye normal haliyle yeniden kuruldu"
