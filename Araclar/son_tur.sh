#!/bin/bash
A=/c/Users/Onur/Sisli/Araclar
$A/oda_hepsi.sh f 2>&1 | grep "png\|PIL\|HATA"
[ -f $A/pil_dusuk.flag ] && exit 1
$A/yuru_test.sh yt6 1 "320 -500 630 -990 650 -3400" 80
ODA_TEST_BASLA=1 $A/oda_kur.sh | tail -1
