#!/bin/bash
# Çocuk karakterini Unreal'de baştan kur (editör KAPALI): FBX içe aktar → IK/RTG/ABP → kol düzeltmeleri → yalnız karakter malzemeleri.
# Önce Blender: blender -b cocuk_v2.blend -P disa_aktar.py -- --out .../SourceArt/Cocuk --maskesiz
S=C:/Users/Onur/Sisli/Unreal/Scripts; A=/c/Users/Onur/Sisli/Araclar/ue_py.sh
rm -rf /c/Users/Onur/Sisli/Unreal/Content/Sisli/Cocuk
for s in kur_karakter duzelt_egim duzelt_el duzelt_burulma yuruyus_duzelt cocuk_malzeme; do
  $A $S/$s.py; r=$?
  echo "== $s çıkış $r: $(grep -c HATA $S/${s}_out.txt 2>/dev/null) hata satırı"
done
