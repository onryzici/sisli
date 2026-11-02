#!/bin/bash
# Yakın animasyon testi: ue_animtest.sh <anim> <yaw> <önek> [kol] [eğim]   (sonra BP'yi geri alır)
S=C:/Users/Onur/Sisli/Unreal/Scripts; A=/c/Users/Onur/Sisli/Araclar
echo "test $1 $2 ${4:-300} ${5:--8}" > $S/test_anim_mod.txt && $A/ue_py.sh $S/test_anim.py && $A/ue_kare.sh 50 $3 >/dev/null; sleep 10
echo "geri" > $S/test_anim_mod.txt && $A/ue_py.sh $S/test_anim.py
