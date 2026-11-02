#!/bin/bash
# Blender sahnesi → Unreal ortamı + malzeme + seviye (editör KAPALI olmalı)
B="/c/Program Files/Blender Foundation/Blender 5.1/blender.exe"; S=C:/Users/Onur/Sisli/Unreal/Scripts; A=/c/Users/Onur/Sisli/Araclar/ue_py.sh
cd /c/Users/Onur/Sisli/Blender
echo "== blender sahne"; "$B" -b --python sahne.py -- --blend C:/Users/Onur/Sisli/Blender/sahne.blend --json C:/Users/Onur/Sisli/Blender/yerlesim.json 2>&1 | grep "GENİŞLETME\|Traceback\|Error:" | head -5
echo "== blender → fbx"; rm -rf /c/Users/Onur/Sisli/Unreal/SourceArt/Ortam
powershell -c '$p = Start-Process "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -ArgumentList "-b C:/Users/Onur/Sisli/Blender/sahne.blend --python C:/Users/Onur/Sisli/Blender/ue_aktar.py -- --out C:/Users/Onur/Sisli/Unreal/SourceArt/Ortam" -PassThru -WindowStyle Hidden -RedirectStandardOutput C:/Users/Onur/Sisli/Blender/ue_aktar_log.txt; $p.PriorityClass = "BelowNormal"; $p.WaitForExit()'
grep "TAMAM\|Error" ue_aktar_log.txt | head -3
rm -rf /c/Users/Onur/Sisli/Unreal/Content/Sisli/Ortam
echo "== ue içe aktar"; $A $S/ice_aktar_ortam.py
echo "== malzeme"; $A $S/malzeme_kur.py; tail -1 $S/malzeme_kur_out.txt
rm -f /c/Users/Onur/Sisli/Unreal/Content/Sisli/Maps/L_Sisli.umap
echo "== seviye"; $A $S/kur_seviye.py; cat $S/kur_seviye_out.txt | tail -3
