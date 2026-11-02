#!/bin/bash
# L_Oda1'i baştan kur + test karesi: oda_kur.sh <önek> [saniye]   (editör KAPALI olmalı)
rm -f /c/Users/Onur/Sisli/Unreal/Content/Sisli/Maps/L_Oda1.umap
/c/Users/Onur/Sisli/Araclar/ue_py.sh C:/Users/Onur/Sisli/Unreal/Scripts/kur_oda.py >/dev/null
cat /c/Users/Onur/Sisli/Unreal/Scripts/kur_oda_out.txt; echo
[ -n "$1" ] || exit 0
cd /c/Users/Onur/Sisli && UE_MAP=/Game/Sisli/Maps/L_Oda1 MSYS2_ARG_CONV_EXCL="*" ./Araclar/ue_kare.sh ${2:-60} $1 >/dev/null 2>&1
node Araclar/parlaklik.js Unreal/Saved/Test/$1_3.png
