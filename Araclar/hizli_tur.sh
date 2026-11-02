#!/bin/bash
# Kare almadan: Blender → FBX → UE → malzeme → yürüme testi → temiz seviye
A=/c/Users/Onur/Sisli/Araclar; S=C:/Users/Onur/Sisli/Unreal/Scripts
[ -f $A/pil_dusuk.flag ] && { echo "PIL DUSUK"; exit 1; }
cd /c/Users/Onur/Sisli/Blender
"/c/Program Files/Blender Foundation/Blender 5.1/blender.exe" -b --python oda1.py -- --blend C:/Users/Onur/Sisli/Blender/oda1.blend --json C:/Users/Onur/Sisli/Blender/oda1.json 2>&1 | grep -i "traceback\|ODA1 TAMAM" | head -3
rm -rf /c/Users/Onur/Sisli/Unreal/SourceArt/Oda1
powershell -c '$p = Start-Process "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -ArgumentList "-b C:/Users/Onur/Sisli/Blender/oda1.blend --python C:/Users/Onur/Sisli/Blender/ue_aktar.py -- --out C:/Users/Onur/Sisli/Unreal/SourceArt/Oda1 --yer C:/Users/Onur/Sisli/Blender/oda1.json" -PassThru -WindowStyle Hidden -RedirectStandardOutput C:/Users/Onur/Sisli/Blender/ue_aktar_oda_log.txt; $p.WaitForExit()'
rm -rf /c/Users/Onur/Sisli/Unreal/Content/Sisli/Oda1 /c/Users/Onur/Sisli/Unreal/Content/Sisli/Maps/L_Oda1.umap
export SISLI_SRC=C:/Users/Onur/Sisli/Unreal/SourceArt/Oda1 SISLI_DST=/Game/Sisli/Oda1 MSYS2_ENV_CONV_EXCL=SISLI_DST SISLI_ANA_KORU=1 SISLI_MIP=Oda1_
$A/ue_py.sh $S/ice_aktar_ortam.py >/dev/null; $A/ue_py.sh $S/malzeme_kur.py >/dev/null
unset SISLI_SRC SISLI_DST SISLI_ANA_KORU SISLI_MIP
[ -f $A/pil_dusuk.flag ] || $A/yuru_test.sh yt7 1 "320 -500 630 -990 650 -3400" 80
ODA_TEST_BASLA=1 $A/oda_kur.sh | tail -1
