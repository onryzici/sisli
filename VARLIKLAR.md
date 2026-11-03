# Sisli / Uyanış — repoda olmayan varlıklar

Bu repo herkese açık (public). Aşağıdaki paketler Fab lisansları gereği burada paylaşılamaz. Hepsi Fab hesabının
kütüphanesinde (fab.com → My Library) duruyor ve yeni bilgisayara oradan yeniden indirilebilir.

| Proje yolu | Kaynak | Nasıl geri gelir |
|---|---|---|
| `Unreal/Content/child_test_2/` | Fab: NoEdge "Realistic 3D Child Character" (kişisel lisans) | Fab → Add to Project (UE 5.x) → `/Game/child_test_2`. Eksik 37 doku: indirilen `textures.zip` → `D:/Sisli-Fab/cocuk_noedge/textures/...` → `Scripts/karakter2_doku.py`, sonra `karakter2_renk.py`, `karakter2_olcek.py` |
| `Unreal/Content/MCO_Mocap_Basics/` + `Unreal/Source/` | Fab: "MoCap Online Free Animation Pack" | Fab → Add to Project → `/Game/MCO_Mocap_Basics`. Sonra `Scripts/uyumlu_iskelet.py` (çocuk iskeleti ↔ MCO iskeleti uyumlu) |
| `Unreal/Content/Uyanis/Fab/UB`, `Yuzey`, `Dekal` | Fab/Megascans: "Unfinished Building" (_high.zip, 4K) | `D:/Sisli-Fab/unfinished_building_high/` → `Scripts/fab_aktar.py` |
| `Unreal/Content/Uyanis/Fab/Yat/*` | Fab/Megascans 4K: boyalı çift kanatlı kapı, floresan, sarkıt lamba, defter, tabure, sandalye, dolap, masa, kafes lamba; anahtarlık (plaggy, **CC BY — jenerikte an**) | `D:/Sisli-Fab/yatakhane/` → `Scripts/yat_aktar.py` |
| `Unreal/Content/Uyanis/Fab/Oyuncak` | Fab: "Old Children's Toys Pack" (peluş tavşan) | `D:/Sisli-Fab/oldchildrenstoysfbx/` → `Scripts/fab_aktar.py` |
| `Unreal/Content/Uyanis/Fab/Ranza` | Fab: "Bunk Bed" (GLB) | `D:/Sisli-Fab/bunk_bed/` → `Scripts/fab_aktar.py` |
| `Unreal/Content/Sisli/Cocuk2/Anim/MCO*` | MCO animasyonlarının çocuğa aktarılmış kopyaları | `Scripts/karakter2_kur.py`, `bs_kur.py`, ardından `rtg_ayar.py` (duruş varyantları) + `rtg_uygula.py` (seçilen varyant → `MCO4/*_C4`, BS güncellenir) yeniden üretir |
| `Indir/` | Poly Haven + MakeHuman (CC0) | betiklerdeki indirme adımları |

Unreal: 5.8. Başsız betik çalıştırma: `Araclar/ue_py.sh <betik.py>`; seviye: `Araclar/uy_kur.sh` (editör kapalıyken).
Ayrıntılı durum ve sıradaki işler: `NOTLAR.md`.

## Epic Game Animation Sample (GASP) — yalnız Unreal Engine ürünlerinde kullanım lisansı, repoda YOK
- Fab: https://fab.com/s/46a85e1ef0c5 → Add to My Library → Epic Launcher → Library → Fab Library → Game Animation Sample → Create Project (5.8), örn. `D:\GASP`.
- Kopyala: `GameAnimationSample/Content/Characters/UEFN_Mannequin/{Meshes,Rigs,Materials,Textures}` + seçili animasyonlar (`gasp_kur.py` içindeki `SECIM`) → `Unreal/Content/Characters/UEFN_Mannequin/` (aynı göreli yollar).
- Sonra: `gasp_kur.py` (RTG_GASP_Cocuk2 + `Anim/GASP/*_C`), `mco_kur.py` (RTG_MCO_Cocuk2 + `Anim/MCOK/*_C`), `el_burulma.py` (yürüyüşte avuç yere dönmesin), `gasp_uygula.py` (BS + karakter hızları).
