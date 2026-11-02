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
| `Unreal/Content/Sisli/Cocuk2/Anim/MCO*` | MCO animasyonlarının çocuğa aktarılmış kopyaları | `Scripts/karakter2_kur.py`, `bs_kur.py`, `rtg_duzelt.py` yeniden üretir |
| `Indir/` | Poly Haven + MakeHuman (CC0) | betiklerdeki indirme adımları |

Unreal: 5.8. Başsız betik çalıştırma: `Araclar/ue_py.sh <betik.py>`; seviye: `Araclar/uy_kur.sh` (editör kapalıyken).
Ayrıntılı durum ve sıradaki işler: `NOTLAR.md`.
