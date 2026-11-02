#!/bin/bash
# Uyanış 4K çekim serisi: her satır = önek | çocuk "x y yaw" | kamera "x y z pitch yaw fov" | odak cm | f | ek env
# Kareler: Unreal/Saved/Test/<önek>_3.png  → sonra seviye normal haliyle yeniden kurulur
A=/c/Users/Onur/Sisli/Araclar
export UE_RX=${UE_RX:-3840} UE_RY=${UE_RY:-2160}
while IFS='|' read -r ad cocuk kam odak fs ek; do
  [ -z "$ad" ] && continue
  env UY_BASLA="$cocuk" UY_KAMERA="$kam" UY_ODAK="$odak" UY_FSTOP="$fs" $ek $A/uy_kur.sh "$ad" 70 | tail -1
done <<'LISTE'
cek_kahraman|450 1880 90|395 1460 112 0.5 85 46|430|2.8|
cek_dolap|175 455 180|285 585 128 -3 211 44|180|2.4|
cek_bakici|800 2448 0|588 2372 150 -8 10 46|230|3.2|
cek_comel|300 600 222|205 395 66 6 66 40|215|2.2|UY_COMELTEST=1
cek_yuz|330 900 257|300 785 119 -1 77 25|108|5.6|UY_TESTISIK=262_752_160_0.5
cek_genis|450 1300 90|860 45 300 -15 103 70|1300|5.6|
LISTE
$A/uy_kur.sh >/dev/null; echo "seviye normal"
