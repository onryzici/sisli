#!/bin/bash
# L_Uyanis'i kur + ekran dışı kare: uy_kur.sh <önek> [saniye]   (editör KAPALI). Başlangıç: UY_BASLA="x y yaw"
A=/c/Users/Onur/Sisli/Araclar; rm -f /c/Users/Onur/Sisli/Unreal/Content/Uyanis/Maps/L_Uyanis.umap
/c/Users/Onur/Sisli/Araclar/ue_py.sh C:/Users/Onur/Sisli/Unreal/Scripts/kur_uyanis.py >/dev/null
grep -E "HATA|çakışma sayısı|ÇAKIŞMA|ÖZELLİK YOK|kaydedildi" /c/Users/Onur/Sisli/Unreal/Scripts/kur_uyanis_out.txt | head -30
[ -n "$1" ] || exit 0
cd /c/Users/Onur/Sisli && UE_MAP=/Game/Uyanis/Maps/L_Uyanis MSYS2_ARG_CONV_EXCL="*" ./Araclar/ue_kare.sh ${2:-50} $1 >/dev/null 2>&1
node Araclar/parlaklik.js Unreal/Saved/Test/$1_3.png
