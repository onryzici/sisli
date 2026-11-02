#!/bin/bash
# ue_yer.sh "x y z yaw" <önek> [saniye]  — başlangıcı taşı, kare al
echo "$1" > /c/Users/Onur/Sisli/Unreal/Scripts/test_yer.txt
/c/Users/Onur/Sisli/Araclar/ue_py.sh C:/Users/Onur/Sisli/Unreal/Scripts/test_yer.py >/dev/null
/c/Users/Onur/Sisli/Araclar/ue_kare.sh ${3:-75} $2 >/dev/null; sleep 8
