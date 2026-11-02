#!/bin/bash
# Mekanikleri + seviyeyi sırayla yeniden kur (editör KAPALI)
unset MEK
/c/Users/Onur/Sisli/Araclar/mek.sh mek_titrek BP_Titrek | grep "TAMAM\|HATA"
/c/Users/Onur/Sisli/Araclar/mek.sh mek_hepsi BP_Kapi BP_EvKapisi BP_Anahtar BP_Projektor BP_Olum BP_Son BP_Fener BP_IcMekan | grep "OK\|HATA\|in:"
rm -f /c/Users/Onur/Sisli/Unreal/Content/Sisli/Maps/L_Sisli.umap
/c/Users/Onur/Sisli/Araclar/ue_py.sh C:/Users/Onur/Sisli/Unreal/Scripts/kur_seviye.py; tail -1 /c/Users/Onur/Sisli/Unreal/Scripts/kur_seviye_out.txt
