#!/bin/bash
# Kule katı kur + (isteğe bağlı) ekran dışı kare: kat_kur.sh <kat no, örn. 01> [önek] [saniye]   (editör KAPALI). Ortam: UY_KAMERA, UY_BASLA, UY_YURU, UY_SAKLAN, UY_KAT_OTO, UY_BEKCI_KOR
K=$1; A=/c/Users/Onur/Sisli/Araclar; rm -f /c/Users/Onur/Sisli/Unreal/Content/Uyanis/Maps/L_Kat$K.umap
$A/ue_py.sh C:/Users/Onur/Sisli/Unreal/Scripts/kur_kat$K.py >/dev/null
grep -E "HATA|TAMAM|UYARI|ÖZELLİK YOK" /c/Users/Onur/Sisli/Unreal/Scripts/kur_kat${K}_out.txt | head -8
[ -n "$2" ] || exit 0
cd /c/Users/Onur/Sisli && UE_MAP=/Game/Uyanis/Maps/L_Kat$K MSYS2_ARG_CONV_EXCL="*" ./Araclar/ue_kare.sh ${3:-45} $2 >/dev/null 2>&1
node Araclar/parlaklik.js Unreal/Saved/Test/$2_3.png
