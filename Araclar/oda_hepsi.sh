#!/bin/bash
# Oda1+dış sahne tam yeniden kurulum (editör KAPALI): Blender → FBX → UE içe aktar → malzeme → [BP'ler] → seviye → 3 kamera karesi
# kullanım: oda_hepsi.sh <önek> [BP adları virgüllü]
P=$1; BPS=$2; A=/c/Users/Onur/Sisli/Araclar; S=C:/Users/Onur/Sisli/Unreal/Scripts
[ -f $A/pil_dusuk.flag ] && { echo "PIL DUSUK - iptal"; exit 1; }
cd /c/Users/Onur/Sisli/Blender
"/c/Program Files/Blender Foundation/Blender 5.1/blender.exe" -b --python oda1.py -- --blend C:/Users/Onur/Sisli/Blender/oda1.blend --json C:/Users/Onur/Sisli/Blender/oda1.json 2>&1 | grep -i "traceback\|error\|ODA1 TAMAM" | head -5
rm -rf /c/Users/Onur/Sisli/Unreal/SourceArt/Oda1
powershell -c '$p = Start-Process "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -ArgumentList "-b C:/Users/Onur/Sisli/Blender/oda1.blend --python C:/Users/Onur/Sisli/Blender/ue_aktar.py -- --out C:/Users/Onur/Sisli/Unreal/SourceArt/Oda1 --yer C:/Users/Onur/Sisli/Blender/oda1.json" -PassThru -WindowStyle Hidden -RedirectStandardOutput C:/Users/Onur/Sisli/Blender/ue_aktar_oda_log.txt; $p.WaitForExit()'
grep "TAMAM" ue_aktar_oda_log.txt | tail -1
rm -rf /c/Users/Onur/Sisli/Unreal/Content/Sisli/Oda1 /c/Users/Onur/Sisli/Unreal/Content/Sisli/Maps/L_Oda1.umap
export SISLI_SRC=C:/Users/Onur/Sisli/Unreal/SourceArt/Oda1 SISLI_DST=/Game/Sisli/Oda1 MSYS2_ENV_CONV_EXCL=SISLI_DST SISLI_ANA_KORU=1 SISLI_MIP=Oda1_
$A/ue_py.sh $S/ice_aktar_ortam.py >/dev/null; echo "ice: $(grep -c '^SM' /c/Users/Onur/Sisli/Unreal/Scripts/ice_aktar_ortam_out.txt) SM"
$A/ue_py.sh $S/malzeme_kur.py >/dev/null; grep "HATA\|TAMAM" /c/Users/Onur/Sisli/Unreal/Scripts/malzeme_kur_out.txt | head -2
unset SISLI_SRC SISLI_DST SISLI_ANA_KORU SISLI_MIP
if [ -n "$BPS" ]; then MEK=$BPS $A/mek.sh mek_hepsi ${BPS//,/ } | grep -v "^TAMAM"; fi
for b in 1 2 3; do
  [ -f $A/pil_dusuk.flag ] && { echo "PIL DUSUK - dur"; exit 1; }
  ODA_SINEMA=1 ODA_TEST_BASLA=$b $A/oda_kur.sh ${P}_$b 45 | grep -v "^kamera\|^mesh"
done
ODA_TEST_BASLA=1 $A/oda_kur.sh >/dev/null; echo "son: seviye başlangıç 1 ile kaydedildi"
