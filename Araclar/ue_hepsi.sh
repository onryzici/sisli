#!/bin/bash
# Unreal tarafını sıfırdan kur (editör KAPALI olmalı). Sıra önemli.
S=C:/Users/Onur/Sisli/Unreal/Scripts; A=/c/Users/Onur/Sisli/Araclar/ue_py.sh
rm -rf /c/Users/Onur/Sisli/Unreal/Content/Sisli/Cocuk
for s in kur_karakter duzelt_egim duzelt_el duzelt_burulma yuruyus_duzelt malzeme_kur; do echo "== $s"; $A $S/$s.py; done
rm -f /c/Users/Onur/Sisli/Unreal/Content/Sisli/Maps/L_Sisli.umap; echo "== kur_seviye"; $A $S/kur_seviye.py
