# Uyanış — durum notları (2026-11-03)

## Oyun
REANIMAL tarzı karanlık, sisli, sinematik; distopik megayapıda kız kardeşi **Ela**'yı (yer tutucu ad) arayan çocuk.
Açılış "Yalnız uyanış": yetimhane yatakhanesi. Kullanıcı kararı: **yatakhane "tamam" denene kadar yalnız yatakhane geliştirilir.**

Yatakhanedeki akış (otomatik testle doğrulandı): tavşan oyuncak → kilitli kapı → bakıcı odasında defter (E) + anahtar → kapı açılır → koridor.
İncelenebilirler: Ela'nın yatağı, kendi yatağı, Ela'nın dolabı ve çizimi, kurallar kâğıdı, pencere, bakıcı dolabı, defter.

## Bu oturumda yapılanlar
- **Kambur bekleme pozu düzeldi.** Kök: IK Retargeter'ın otomatik hizalaması hedef pozda `spine_01` −13°, `spine_02` +20° bükmüştü. `RTG_UE4_Cocuk2` hedef pozu tamamen, `RTG_Manny_Cocuk2` gövde kemikleri sıfırlandı. "Run IK Rig" (FBIK) kapalı: IK Chains işlemi olmadığından hedefleri yanlış yerdeydi. Betik: `Unreal/Scripts/rtg_son.py`. Animasyonlar `Anim/MCO3/*_C3`, zıplama `Anim/Ziplama/*_G`.
- **Zıplama:** BP_Fener tek düğüm kipinde durum makinesi kullanıyor. Havaya kalkınca MM_Jump, 0.8 sn sonra MM_Fall_Loop; yere değince MM_Land, ardından blend space. Zıplama 400 cm/s, yerçekimi 1.4: yaklaşık 58 cm (`ziplama_ayar.py`).
- **Göz kırpma + mikro ifade:** 2.2–5.8 sn'de bir kırpma, %18 ihtimalle çift kırpma. Kaş, ağız ve burun yavaş sinüslerle oynuyor; nefes de var. Çömelince korku artıyor (kaş iç uç ve göz açıklığı).
- **Altyazılar kapalı:** `Config/DefaultEngine.ini` içinde `bSubtitlesEnabled=False` ve `bSubtitlesForcedOff=True`. Geri açmak için bu iki satırı silmek yeterli; altyazı sistemi (`yazi_kur.py`) duruyor.
- Test aracı: `UY_ANIMTEST="mesh,anim,x,y,yaw,ölçek;..."` sahneye poz karşılaştırma mankenleri koyar. `UY_ZIPLATEST=1` çocuğu 2.6 sn'de bir zıplatır.

## Sıradaki
- 4K çekim serisi: `Araclar/uy_cekim.sh`.
- Kullanıcı geri bildirimi: duruş, zıplama ve mimik nasıl hissettiriyor?
- Tek düğüm kipinde geçişler karışımsız (zıplama başlangıcı ve inişte küçük sıçrama olabilir). Gerekirse ABP'ye geçilir.

## Yeni bilgisayarda
- Betiklerdeki yollar `C:/Users/Onur/Sisli` olarak sabit. Repoyu aynı yola klonla ya da yolları değiştir.
- UE 5.8, Git Bash. Başsız çalıştırma: `Araclar/ue_py.sh`; seviye: `Araclar/uy_kur.sh` (editör kapalıyken).
- Lisanslı paketler repoda yok. Geri kurma: `VARLIKLAR.md`.
