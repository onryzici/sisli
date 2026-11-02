#!/bin/bash
# Mekanik BP kur: mek.sh <betik_adı> <BP_adları...>   (BP dosyalarını diskten silip başsız UE'de betiği çalıştırır)
B=$1; shift
for n in "$@"; do rm -f "/c/Users/Onur/Sisli/Unreal/Content/Sisli/Mekanik/$n.uasset"; done
/c/Users/Onur/Sisli/Araclar/ue_py.sh "C:/Users/Onur/Sisli/Unreal/Scripts/$B.py"
cat "/c/Users/Onur/Sisli/Unreal/Scripts/${B}_out.txt" | cut -c1-400
