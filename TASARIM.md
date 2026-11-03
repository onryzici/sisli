# UYANIŞ / AWAKENING — Tasarım belgesi / Design document

> Türkçe ve İngilizce eşzamanlı. Oyun içi metinlerin tek kaynağı `Unreal/Scripts/metinler.py` (oyunda **L** tuşu dili değiştirir).
> Turkish and English kept in sync. Single source for in-game text: `Unreal/Scripts/metinler.py` (press **L** in game to switch language).

## Hikâye / Story

**TR** — Distopik bir megayapının dibinde, bir yetimhanenin bodrum yatakhanesinde bir çocuk tek başına uyanır. Küçük kız kardeşi Ela gece götürülmüştür. Ela'nın çizdiği resimde uzun bir kule ve tepesinde kırmızı bir ışık vardır. Çocuğun ona bu ışıktan hiç bahsetmemiş olması tuhaftır. Kule, yetimhanenin ta kendisidir: 15 kat. Her katta "Müdürlük"ün başka bir yüzü, başka bir kural vardır. Çocuk kat kat yukarı çıkarak Ela'yı kırmızı ışığın altında bulmaya çalışır. Yolda saklanır, bulmacalar çözer ve yetişkinlerin dünyasının çocuklara ne yaptığını parça parça öğrenir.

**EN** — At the bottom of a dystopian megastructure, in the basement dormitory of an orphanage, a boy wakes up alone. His little sister Ela was taken in the night. In her drawing there is a tall tower with a red light on top. Strangely, he had never told her about that light. The tower is the orphanage itself: 15 floors. Each floor is another face of "the Directorate", another rule. The boy climbs floor by floor to find Ela under the red light, hiding, solving puzzles, and learning piece by piece what the adults' world does to children.

**Ton / Tone:** REANIMAL / Little Nightmares: az söz, çok ima; alçak sinematik kadrajlar, sis, soğuk ışık + kırmızı yol gösterici ışık. / Few words, much implication; low cinematic framing, fog, cold light + red guiding light.

## Katlar / Floors

| # | TR | EN | Konsept & mekanik / Concept & mechanic |
|---|----|----|----------------------------------------|
| B | **Yatakhane** (bodrum) | **Dormitory** (basement) | Uyanış, tavşan, kilitli kapı, bakıcının anahtarı. Avluda yukarı uzanan kule, asansör. / Waking, rabbit, locked door, caretaker's keys; courtyard looking up the tower, elevator. **(yapıldı / built)** |
| 1 | **Dolaplar Katı** (soyunma odaları) | **The Lockers** (changing rooms) | İlk düşman: Bekçi feneriyle devriye geziyor. **Dolaplarda saklanma**, görüş konisinden kaçma. Sigorta bul → asansöre güç ver. / First enemy: the Warden patrols with a lamp. **Hide in lockers**, avoid the vision cone. Find the fuse → power the elevator. **(oynanabilir, testli / playable, tested)** |
| 2 | **Mutfak** | **The Kitchen** | İri aşçılar; fırın/buzdolabında saklanma; **teneke atıp dikkat dağıtma** (REANIMAL: throwable tin can). / Hulking cooks; hide in oven/fridge; **throw tin cans to distract**. **(oynanabilir, testli / playable, tested:** iri aşçı sesi duyunca araştırır, anahtar ocağın yanında, asansör zincirli / the cook investigates noises, key by the stove, elevator chained**)** |
| 3 | **Sınıflar** | **Classrooms** | Tahtalardaki "dersler" = ipucu; **4 haneli şifre makinesi** (kod, çizimlerin tarihinde). / Lessons on blackboards are clues; **4-digit code machine** (code hidden in drawings' dates). *(yer tutucu / placeholder)* |
| 4 | **Revir** | **Infirmary** | Uyuyan hemşire; ses çıkarma = uyanır. **Krank çarkı** ile kepenk aç (bırakınca geri iner). / Sleeping nurse, noise wakes her. **Crank wheel** opens shutter (falls back when released). |
| 5 | **Arşiv** | **Records** | Sonsuz dosya dolapları; **raf itme/çekme** ile yol açma; Ela'nın dosyası. / Endless cabinets; **push/pull shelves** to open a path; Ela's file. |
| 6 | **Oyun Odası** | **Playroom** | Mankenler/oyuncaklar: **ışık altındayken donan, karanlıkta yaklaşan** figürler; fener mekaniği. / Mannequins that **freeze in light, creep in darkness**; flashlight mechanic. |
| 7 | **7. Blok** | **Block 7** | Ela'nın nakledildiği yer: boş, sessiz, gerilim. Hayalet ipuçları; Ela'nın kaçtığı anlaşılır. / Where Ela was transferred: empty, silent; clues show she escaped upward. |
| 8 | **Bakım** | **Maintenance** | Borular, buhar; **vana sırası bulmacası**, sıcak buhardan zamanlamayla geçme. / Pipes, steam; **valve-order puzzle**, timed passage through steam. |
| 9 | **Seralar** | **Greenhouses** | Sisli hidroponik tarlalar; **dron projektörleri** (bodrumdaki projektör mekaniği), uzun otlarda çömelerek saklanma. / Foggy hydroponic farms; **drone searchlights**, hide crouched in tall plants. |
| 10 | **Gözetleme** | **Surveillance** | Monitörlerde diğer katlar, bir ekranda Ela. **Kamera görüş alanları**, kameraları kapatan şalter. / Monitors show other floors, Ela on one screen. **Camera cones**, breaker that disables cameras. |
| 11 | **Koro Salonu** | **Choir Hall** | Uyurgezer gibi şarkı söyleyen çocuklar; **müzik durunca hareket etme** (kırmızı ışık–yeşil ışık). / Sleepwalking children singing; **don't move when the music stops**. |
| 12 | **Müdürlük** | **Directorate** | Ofisler, **kart kilitleri**, kâğıt izi; Müdür'ün kendisi. / Offices, **keycard locks**, paper trail; the Director. |
| 13 | **Makine Dairesi** | **Engine Room** | Asansör makineleri, dev dişliler; **dişli/krank zamanlama** bulmacası. / Elevator machinery, giant gears; **gear/crank timing** puzzle. |
| 14 | **Çatı Arası** | **The Attic** | Rüzgâr, kablolar; **merdiven indirme**, kenarlarda denge. / Wind, cables; **kick down ladders**, balance along edges. |
| 15 | **Kırmızı Işık** | **The Red Light** | Çatıdaki ışık makinesi. Ela. Final. / The light machine on the roof. Ela. Finale. |

## Mekanik kütüphanesi / Mechanic library

REANIMAL dosyalarından (`REANIMAL-RE/files.txt`) çıkarılan ve tek kişiye uyarlanan mekanikler. / Mechanics found in REANIMAL's files, adapted for single player:

| Mekanik / Mechanic | REANIMAL karşılığı / REANIMAL equivalent | Durum / Status |
|---|---|---|
| İnceleme ekranı / Inspection screen | (kendi) / (ours) | ✔ `WBP_Incele_*` |
| Anahtar–kilitli kapı / Key–locked door | `BP_Pickup_GenericKey_*`, `BP_Lock_Key_Interaction` | ✔ `BP_YatakhaneKapisi` |
| Projektör (görülünce yakalanma) / Searchlight | `BP_PuzzleLampPost`, lights | ✔ `BP_Projektor` |
| **Dolapta saklanma / Hide in locker** | `BP_HidingSpot_Cupboard*`, `_Oven`, `_Refrigerator` | ✔ `BP_Saklanma` (Kat 1) |
| **Devriye + görüş konisi / Patrol + vision cone** | düşman AI / enemy AI | ✔ `BP_Bekci` (Kat 1) |
| **Sigorta → asansör gücü / Fuse → elevator power** | `BP_Coop_Interaction_PullCordGenerator`, `BP_Elevator` | ✔ `BP_Asansor` (bodrum → 1 → 2 → 3; `KilitMetin`) |
| **Teneke atma / Throwable** | `BP_Pickup_ThrowableBase_TinCan`, `_Brick` | ✔ `BP_Atilabilir` (Kat 2) |
| **Sesi duyup araştırma / Noise investigation** | düşman AI / enemy AI | ✔ `BP_Bekci` `Duyma`/`Bekle` (Kat 2 aşçı) |
| Şifre makinesi / Code machine | `BP_CodeMachine_4x3`, `BP_CodeDecalManager` | planlandı / planned |
| Krank çarkı / Crank wheel | `BP_CrankWheelLarge_SIG`, `BP_DraggableLargeCrank_*` | planlandı / planned |
| İtilebilir kutu / Draggable box | `BP_Draggable_Box`, `BP_DraggableShoppingCart` | planlandı / planned |
| Merdiven indirme / Fall-down ladder | `BP_FallDownLadderGate_*` | planlandı / planned |
| Kol/düğme / Lever/button | `BP_Interaction_VerticalSteppedLever`, `BP_PushButton_SIG` | planlandı / planned |
| Kart kilidi / Keycard | `BP_Interaction_KeycardLock` | planlandı / planned |

## Seslendirme / Voice-over

**TR** — Satır kimlikleri `metinler.py` içinde (`giris`, `tavsan1` …). Kayıtlar `Unreal/SourceArt/Ses/VO/en/<kimlik>.wav` ve `.../tr/<kimlik>.wav` olarak gelecek. Altyazı süresi şimdilik okuma hızından hesaplanıyor (~12 karakter/sn + 2,8 sn). Ses gelince süre ses uzunluğundan alınacak.

**EN** — Line IDs live in `metinler.py` (`giris`, `tavsan1` …). Recordings go to `Unreal/SourceArt/Ses/VO/en/<id>.wav` and `.../tr/<id>.wav`. Subtitle time is currently computed from reading speed (~12 chars/s + 2.8 s). Once audio arrives, the audio length will drive it.
