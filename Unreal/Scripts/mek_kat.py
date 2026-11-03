# Kule katları için mekanikler (TASARIM.md "Mekanik kütüphanesi"; REANIMAL karşılıkları: BP_HidingSpot_*, düşman devriyesi, BP_Elevator):
#   BP_Saklanma  — dolapta saklanma: E gir/çık; içerideyken kendi Tags'ine "Dolu" ekler (bekçi GetAllActorsWithTag ile okur)
#   BP_Bekci     — devriye (P1..P4), görüş konisi + görüş hattı; çömelik oyuncuyu yakından görür; görürse ~0.45 sn sonra yakalar → karar, Donus'a ışınla
#   BP_Asansor   — Sigorta aktörü hâlâ duruyorsa "güç yok"; alındıysa kararır ve Hedef seviyesine geçer
#   BP_KatGiris  — kat açılışı: siyahtan açılma + iç ses satırları
#   BP_Atilabilir — teneke: al (E), fırlat (sol tık); düştüğü yer 1 sn "Ses" etiketli → BP_Bekci duyarsa araştırır
# Altyazılar WBP_Altyazi'ye (iki dilli "EN~~TR", metinler.py). Çalıştırma: MEK=BP_Bekci,... ue_py.sh mek_kat.py (önce mek.sh gibi .uasset silinir)
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
from mekanik_lib import *
from metinler import iki
import os
V = lambda x, y, z: unreal.Vector(x, y, z)
SES = "/Game/Sisli/Ses"; ALTYAZI_C = "/Game/Uyanis/UI/WBP_Altyazi.WBP_Altyazi_C"; OYUNCU = "(Game|GetPlayerCharacter 0)"
U = "/Game/Characters/UEFN_Mannequin"
_say = [0]
def soyle(ifade):
    _say[0] += 1; n = _say[0]
    return f'''(bind aws{n} (Widget|GetAllWidgetsOfClass :WidgetClass "{ALTYAZI_C}" :TopLevelOnly true))
  (if (> (Utilities|Array|Length aws{n}) 0)
    (Widget|SetToolTipText :self (Utilities|Array|Get(acopy) aws{n} 0) :InToolTipText {ifade})
    (else
      (bind aw{n} (UserInterface|CreateWidget :Class "{ALTYAZI_C}" :OwningPlayer (Game|GetPlayerController 0)))
      (UserInterface|Viewport|AddtoViewport :self aw{n} :ZOrder 5)
      (Widget|SetToolTipText :self aw{n} :InToolTipText {ifade})))'''
def soz(k): return soyle('(Utilities|Text|ToText(String) "' + iki(k).replace('"', "'") + '")')

# ---------- BP_Saklanma ----------
def saklanma():
    bp = yeni_bp("BP_Saklanma")
    bilesen(bp, unreal.BoxComponent, "Kutu", box_extent=V(45, 45, 90))
    degisken(bp, "Yaricap", "float", 125.0); degisken(bp, "TestOto", "bool", False)
    degisken(bp, "Dolu", "bool", False, False); degisken(bp, "Yakin", "bool", False, False)
    dsl(bp, f'''
(event EventTick (DeltaSeconds)
  (bind pc (Game|GetPlayerController 0))
  (bind oy {OYUNCU})
  (bind yakin (< (Math|Vector|Distance(Vector) (Transformation|GetActorLocation) (Transformation|GetActorLocation oy)) (Uye|Get|Yaricap)))
  (if (and yakin (not (Uye|Get|Yakin)))
    (Uye|Set|Yakin true)
    (if (not (Uye|Get|Dolu))
      {soz("saklan_ipucu")}))
  (if (not yakin)
    (Uye|Set|Yakin false))
  (if (or (Game|Player|WasInputKeyJustPressed :self pc :Key "E") (and (Uye|Get|TestOto) yakin))
    (if (Uye|Get|Dolu)
      (Uye|Set|Dolu false)
      (Utilities|Array|RemoveItem (Variables|Actor|GetTags) "Dolu")
      (Rendering|SetActorHiddenInGame :self oy :bNewHidden false)
      (Collision|SetActorEnableCollision :self oy :bNewActorEnableCollision true)
      (Pawn|Components|CharacterMovement|SetMovementMode :self (Class|Character|GetCharacterMovement :self oy) :NewMovementMode "Walking")
      (Input|SetIgnoreMoveInput :self pc :bNewMoveInput false)
      (Audio|PlaySoundatLocation :Sound "{SES}/Gicirti.Gicirti" :Location (Transformation|GetActorLocation) :VolumeMultiplier 0.5 :PitchMultiplier 1.6)
      (Development|PrintString "SISLI SAKLANMA_BITTI" :bPrintToScreen false)
      (else
        (if yakin
          (Uye|Set|Dolu true)
          (Uye|Set|TestOto false)
          (Utilities|Array|AddUnique (Variables|Actor|GetTags) "Dolu")
          (Rendering|SetActorHiddenInGame :self oy :bNewHidden true)
          (Collision|SetActorEnableCollision :self oy :bNewActorEnableCollision false)
          (Pawn|Components|CharacterMovement|DisableMovement :self (Class|Character|GetCharacterMovement :self oy))
          (Input|SetIgnoreMoveInput :self pc :bNewMoveInput true)
          (Audio|PlaySoundatLocation :Sound "{SES}/Gicirti.Gicirti" :Location (Transformation|GetActorLocation) :VolumeMultiplier 0.5 :PitchMultiplier 1.4)
          (Development|PrintString "SISLI SAKLANDI" :bPrintToScreen false))))))
''')
    derle_kaydet(bp)

# ---------- BP_Bekci ----------
def bekci():
    bp = yeni_bp("BP_Bekci")
    mi = eal.load_asset("/Game/Uyanis/Sahne/MI_Bekci_Kumas")
    govde = bilesen(bp, unreal.SkeletalMeshComponent, "Govde", skeletal_mesh_asset=eal.load_asset(f"{U}/Meshes/SKM_UEFN_Mannequin"),
                    relative_location=V(0, 0, 0), relative_rotation=unreal.Rotator(roll=0, pitch=0, yaw=-90), relative_scale3d=V(1.08, 1.08, 1.08))
    if mi:
        try: govde.set_editor_property("override_materials", [mi] * 8)
        except Exception as e: log("malzeme", e)
    # baş lambası (alnın önünde): ışık konisi bakış yönünü gösterir; sis saçılımı düşük (gövde önünde parlayan top olmasın)
    bilesen(bp, unreal.SpotLightComponent, "Fener", intensity_units=unreal.LightUnits.CANDELAS, intensity=320.0, attenuation_radius=1300.0,
            outer_cone_angle=26.0, inner_cone_angle=12.0, light_color=unreal.Color(r=255, g=214, b=160, a=255), volumetric_scattering_intensity=1.2,
            source_radius=2.0, relative_location=V(22, 0, 168), relative_rotation=unreal.Rotator(roll=0, pitch=-20, yaw=0))
    for n in ("P1", "P2", "P3", "P4", "Donus"): degisken(bp, n, "Vector")
    degisken(bp, "Hiz", "float", 115.0); degisken(bp, "AnimHiz", "float", 0.7); degisken(bp, "TestKor", "bool", False)
    degisken(bp, "FenerGuc", "float", 320.0)                       # aşçı: daha loş
    degisken(bp, "Duyma", "float", 1500.0); degisken(bp, "Bekle", "float", 4.0); degisken(bp, "SesPerde", "float", 1.0)   # teneke vb. "Ses" etiketli aktörleri duyma menzili, orada bekleme süresi
    degisken(bp, "Kumas", unreal.MaterialInterface, mi)            # gövde malzemesi (bekçi koyu kumaş, aşçı kirli önlük)
    degisken(bp, "Hedef", "int", 1, False); degisken(bp, "Uyari", "float", 0.0, False); degisken(bp, "Yakaliyor", "bool", False, False)
    degisken(bp, "Duruyor", "bool", False, False)
    degisken(bp, "Arastir", "bool", False, False); degisken(bp, "AraNokta", "Vector", None, False); degisken(bp, "AraSure", "float", 0.0, False)
    YURU = f"{U}/Animations/Walk/M_Neutral_Walk_Loop_F.M_Neutral_Walk_Loop_F"; DUR = f"{U}/Animations/Idle/M_Neutral_Stand_Idle_Loop.M_Neutral_Stand_Idle_Loop"
    dsl(bp, f'''
(event EventBeginPlay
  (Rendering|Material|SetMaterial :self (Uye|Get|Govde) :ElementIndex 0 :Material (Uye|Get|Kumas))
  (Rendering|Components|Light|SetIntensity :self (Uye|Get|Fener) :NewIntensity (Uye|Get|FenerGuc))
  (Components|Animation|PlayAnimation :self (Uye|Get|Govde) :NewAnimToPlay "{YURU}" :bLooping true)
  (Components|Animation|SetPlayRate :self (Uye|Get|Govde) :Rate (Uye|Get|AnimHiz))
  (Uye|Set|P1 (Transformation|GetActorLocation)))

(event EventTick (DeltaSeconds)
  (bind oy {OYUNCU})
  (bind konum (Transformation|GetActorLocation))
  (bind sesler (Actor|GetAllActorswithTag :Tag "Ses"))
  (if (and (> (Utilities|Array|Length sesler) 0) (not (Uye|Get|Yakaliyor)))
    (bind sk (Transformation|GetActorLocation (Utilities|Array|Get(acopy) sesler 0)))
    (if (< (Math|Vector|Distance(Vector) konum sk) (Uye|Get|Duyma))
      (if (not (Uye|Get|Arastir))
        (Development|PrintString "SISLI SES_DUYDU" :bPrintToScreen false)
        (Audio|PlaySoundatLocation :Sound "{SES}/Homurtu.Homurtu" :Location konum :VolumeMultiplier 0.9 :PitchMultiplier (Uye|Get|SesPerde)))
      (Uye|Set|Arastir true)
      (Uye|Set|AraNokta sk)
      (Uye|Set|AraSure (Uye|Get|Bekle))))
  (bind i (Uye|Get|Hedef))
  (bind ar (Uye|Get|Arastir))
  (bind an (Uye|Get|AraNokta))
  (bind hp (select (== i 0) (Uye|Get|P1) (select (== i 1) (Uye|Get|P2) (select (== i 2) (Uye|Get|P3) (Uye|Get|P4)))))
  (bind hd (select ar (Math|Vector|MakeVector (.x an) (.y an) (.z konum)) (Math|Vector|MakeVector (.x hp) (.y hp) (.z konum))))
  (bind op (Transformation|GetActorLocation oy))
  (bind yon (Math|Vector|MakeVector (- (.x op) (.x konum)) (- (.y op) (.y konum)) 0.0))
  (bind d (Math|Vector|VectorLength yon))
  (bind cosa (/ (Math|Vector|DotProduct yon (Transformation|GetActorForwardVector)) (Math|Float|Max(Float) d 1.0)))
  (bind dolular (Actor|GetAllActorswithTag :Tag "Dolu"))
  (bind sakli (> (Utilities|Array|Length dolular) 0))
  (bind comel (Movement|IsCrouching :self (Class|Character|GetCharacterMovement :self oy)))
  (bind menzil (select comel 430.0 950.0))
  (bind goz (+ konum (Math|Vector|MakeVector 0.0 0.0 150.0)))
  (bind uc (- op (* yon (/ 40.0 (Math|Float|Max(Float) d 1.0)))))
  (bind (_vurus engel) (Collision|LineTraceByChannel :Start goz :End (+ uc (Math|Vector|MakeVector 0.0 0.0 25.0)) :TraceChannel "Visibility" :bTraceComplex false))
  (bind gordu (and (and (and (< d menzil) (> cosa 0.68)) (and (not sakli) (not engel))) (not (Uye|Get|TestKor))))
  (if (not (Uye|Get|Yakaliyor))
    (if gordu
      (Uye|Set|Uyari (+ (Uye|Get|Uyari) DeltaSeconds))
      (Rendering|Components|Light|SetLightColor :self (Uye|Get|Fener) :NewLightColor (Math|Color|MakeColor 1.0 0.12 0.06 1.0))
      (bind brot (Math|Rotator|FindLookatRotation konum op))
      (Transformation|SetActorRotation :NewRotation (Math|Interpolation|RInterpTo (Transformation|GetActorRotation) (Math|Rotator|MakeRotator 0.0 0.0 (.yaw brot)) DeltaSeconds 6.0))
      (if (not (Uye|Get|Duruyor))
        (Uye|Set|Duruyor true)
        (Components|Animation|PlayAnimation :self (Uye|Get|Govde) :NewAnimToPlay "{DUR}" :bLooping true))
      (else
        (Uye|Set|Uyari (Math|Float|Max(Float) 0.0 (- (Uye|Get|Uyari) (* 0.5 DeltaSeconds))))
        (Rendering|Components|Light|SetLightColor :self (Uye|Get|Fener) :NewLightColor (Math|Color|MakeColor 1.0 0.84 0.63 1.0))
        (bind bel (+ konum (Math|Vector|MakeVector 0.0 0.0 60.0)))
        (bind hrot (Math|Rotator|FindLookatRotation konum hd))
        (bind hyon (Math|Vector|GetForwardVector (Math|Rotator|MakeRotator 0.0 0.0 (.yaw hrot))))
        (bind (_v2 onu_dolu) (Collision|LineTraceByChannel :Start bel :End (+ bel (* hyon 80.0)) :TraceChannel "Visibility" :bTraceComplex false))
        (bind yonA (Math|Vector|GetForwardVector (Math|Rotator|MakeRotator 0.0 0.0 (+ (.yaw hrot) 60.0))))
        (bind yonB (Math|Vector|GetForwardVector (Math|Rotator|MakeRotator 0.0 0.0 (- (.yaw hrot) 60.0))))
        (bind (_va engA) (Collision|LineTraceByChannel :Start bel :End (+ bel (* yonA 80.0)) :TraceChannel "Visibility" :bTraceComplex false))
        (bind (_vb engB) (Collision|LineTraceByChannel :Start bel :End (+ bel (* yonB 80.0)) :TraceChannel "Visibility" :bTraceComplex false))
        (bind adim (select onu_dolu (+ konum (* (select engA yonB yonA) 100.0)) hd))   ; devriyede de engelin kenarından dolaş
        (if (and ar (or (< (Math|Vector|Distance(Vector) konum hd) 45.0) (and onu_dolu (and engA engB))))
          (Uye|Set|AraSure (- (Uye|Get|AraSure) DeltaSeconds))
          (if (not (Uye|Get|Duruyor))
            (Uye|Set|Duruyor true)
            (bind (_e1 _e2 _e3 _e4 _e5 _e6 _e7 _e8 _e9 eakt) (Collision|BreakHitResult _v2))
            (Development|PrintString "SISLI VARDI" :bPrintToScreen false)
            (Development|PrintString (Utilities|String|ToString(Vector) konum) :bPrintToScreen false)
            (Development|PrintString (Utilities|String|ToString(Vector) hd) :bPrintToScreen false)
            (Development|PrintString (Utilities|GetObjectName eakt) :bPrintToScreen false)
            (Components|Animation|PlayAnimation :self (Uye|Get|Govde) :NewAnimToPlay "{DUR}" :bLooping true))
          (Transformation|SetActorRotation :NewRotation (Math|Interpolation|RInterpTo (Transformation|GetActorRotation) (Math|Rotator|MakeRotator 0.0 0.0 (+ (.yaw hrot) (* 45.0 (Math|Trig|Sin(Radians) (* 1.3 (Uye|Get|AraSure)))))) DeltaSeconds 3.0))
          (if (<= (Uye|Get|AraSure) 0.0)
            (Uye|Set|Arastir false)
            (Development|PrintString "SISLI ARASTIRMA_BITTI" :bPrintToScreen false))
          (else
            (if (Uye|Get|Duruyor)
              (Uye|Set|Duruyor false)
              (Components|Animation|PlayAnimation :self (Uye|Get|Govde) :NewAnimToPlay "{YURU}" :bLooping true)
              (Components|Animation|SetPlayRate :self (Uye|Get|Govde) :Rate (Uye|Get|AnimHiz)))
            (if ar
              (Uye|Set|AraSure (- (Uye|Get|AraSure) (* 0.3 DeltaSeconds))))
            (if (and ar (<= (Uye|Get|AraSure) 0.0))
              (Uye|Set|Arastir false)
              (Development|PrintString "SISLI ARASTIRMA_VAZGECTI" :bPrintToScreen false))
            (Transformation|SetActorLocation :NewLocation (Math|Interpolation|VInterptoConstant konum adim DeltaSeconds (select ar (* (Uye|Get|Hiz) 1.3) (Uye|Get|Hiz))) :bSweep false :bTeleport false)
            (bind arot (Math|Rotator|FindLookatRotation konum adim))
            (Transformation|SetActorRotation :NewRotation (Math|Interpolation|RInterpTo (Transformation|GetActorRotation) (Math|Rotator|MakeRotator 0.0 0.0 (.yaw arot)) DeltaSeconds 2.5))
            (if (and (not ar) (< (Math|Vector|Distance(Vector) konum hd) 20.0))
              (Uye|Set|Hedef (select (>= i 3) 0 (+ i 1))))))))
    (if (> (Uye|Get|Uyari) 0.45)
      (Uye|Set|Yakaliyor true)
      (Development|PrintString "SISLI YAKALANDI" :bPrintToScreen false)
      (Audio|PlaySound2D :Sound "{SES}/Yakalandi.Yakalandi")
      (CameraFades|StartCameraFade (Game|GetPlayerCameraManager 0) 0.0 1.0 0.35 (Math|Color|MakeColor 0.0 0.0 0.0 1.0) false true)
      (Utilities|FlowControl|Delay 1.0)
      (Transformation|SetActorLocation :self oy :NewLocation (Uye|Get|Donus) :bSweep false :bTeleport true)
      (Transformation|SetActorLocation :NewLocation (Uye|Get|P1) :bSweep false :bTeleport true)
      (Uye|Set|Hedef 1)
      (Uye|Set|Uyari 0.0)
      (Uye|Set|Arastir false)
      (CameraFades|StartCameraFade (Game|GetPlayerCameraManager 0) 1.0 0.0 1.4 (Math|Color|MakeColor 0.0 0.0 0.0 1.0) false false)
      (Utilities|FlowControl|Delay 1.0)
      (Uye|Set|Yakaliyor false))))
''')
    derle_kaydet(bp)

# ---------- BP_Asansor ----------
def asansor():
    bp = yeni_bp("BP_Asansor")
    bilesen(bp, unreal.BoxComponent, "Kutu", box_extent=V(90, 90, 120))
    degisken(bp, "Hedef", "name", "L_Kat01"); degisken(bp, "Sigorta", unreal.Actor); degisken(bp, "Yaricap", "float", 170.0); degisken(bp, "TestOto", "bool", False)
    degisken(bp, "Yakin", "bool", False, False); degisken(bp, "Gidiyor", "bool", False, False); degisken(bp, "Mesgul", "bool", False, False)
    degisken(bp, "KilitMetin", "text", iki("asansor_guc_yok"))   # Sigorta duruyorken söylenen (Kat 2: zincir/asma kilit)
    dsl(bp, f'''
(event EventTick (DeltaSeconds)
  (bind pc (Game|GetPlayerController 0))
  (bind yakin (< (Math|Vector|Distance(Vector) (Transformation|GetActorLocation) (Transformation|GetActorLocation {OYUNCU})) (Uye|Get|Yaricap)))
  (if (and yakin (not (Uye|Get|Yakin)))
    (Uye|Set|Yakin true)
    (if (not (Uye|Get|Gidiyor))
      {soz("asansor_ipucu")}))
  (if (not yakin)
    (Uye|Set|Yakin false))
  (if (and (and (and yakin (not (Uye|Get|Gidiyor))) (not (Uye|Get|Mesgul))) (or (Game|Player|WasInputKeyJustPressed :self pc :Key "E") (Uye|Get|TestOto)))
    (Utilities|IsValid (Uye|Get|Sigorta)
      (:"Is Valid"
        (Uye|Set|Mesgul true)
        (Development|PrintString "SISLI ASANSOR_GUCSUZ" :bPrintToScreen false)
        {soyle("(Uye|Get|KilitMetin)")}
        (Audio|PlaySoundatLocation :Sound "{SES}/Lamba_Vizilti.Lamba_Vizilti" :Location (Transformation|GetActorLocation) :VolumeMultiplier 0.6 :PitchMultiplier 0.5)
        (Utilities|FlowControl|Delay 3.0)
        (Uye|Set|Mesgul false))
      (:"Is Not Valid"
        (Uye|Set|Gidiyor true)
        (Development|PrintString "SISLI ASANSOR_GIDIYOR" :bPrintToScreen false)
        (Input|SetIgnoreMoveInput :self pc :bNewMoveInput true)
        {soz("asansor")}
        (Audio|PlaySoundatLocation :Sound "{SES}/Gicirti.Gicirti" :Location (Transformation|GetActorLocation) :VolumeMultiplier 0.8 :PitchMultiplier 0.6)
        (CameraFades|StartCameraFade (Game|GetPlayerCameraManager 0) 0.0 1.0 2.4 (Math|Color|MakeColor 0.0 0.0 0.0 1.0) false true)
        (Utilities|FlowControl|Delay 3.0)
        (Game|OpenLevel(byName) :LevelName (Uye|Get|Hedef) :bAbsolute true)))))
''')
    derle_kaydet(bp)

# ---------- BP_KatGiris ----------
def katgiris():
    bp = yeni_bp("BP_KatGiris")
    for n in ("Metin1", "Metin2"): degisken(bp, n, "text")
    degisken(bp, "Bekle1", "float", 2.5); degisken(bp, "Bekle2", "float", 6.0)
    dsl(bp, f'''
(event EventBeginPlay
  (CameraFades|StartCameraFade (Game|GetPlayerCameraManager 0) 1.0 0.0 3.5 (Math|Color|MakeColor 0.0 0.0 0.0 1.0) false false)
  (bind aw0 (UserInterface|CreateWidget :Class "{ALTYAZI_C}" :OwningPlayer (Game|GetPlayerController 0)))
  (UserInterface|Viewport|AddtoViewport :self aw0 :ZOrder 5)
  (Development|PrintString "SISLI KAT_GIRIS" :bPrintToScreen false)
  (Utilities|FlowControl|Delay (Uye|Get|Bekle1))
  {soyle("(Uye|Get|Metin1)")}
  (Utilities|FlowControl|Delay (Uye|Get|Bekle2))
  {soyle("(Uye|Get|Metin2)")})
''')
    derle_kaydet(bp)

# ---------- BP_Atilabilir: teneke (REANIMAL BP_Pickup_ThrowableBase_TinCan) ----------
# E ile al (gizlenir, oyuncuyla taşınır) → sol tık: kameranın baktığı yöne ~7.5 m kavisli atış (duvara çarparsa önünde düşer, zemine iz düşürülür)
# Düşünce: tıngırtı + 1 sn boyunca kendi Tags'inde "Ses" → BP_Bekci (Duyma menzilindeyse) oraya gider, Bekle sn bakınır, devriyeye döner. Teneke yerden yeniden alınabilir.
def atilabilir():
    bp = yeni_bp("BP_Atilabilir")
    c = bilesen(bp, unreal.StaticMeshComponent, "Govde", static_mesh=eal.load_asset("/Engine/BasicShapes/Cylinder"),
                relative_location=V(0, 0, 6), relative_scale3d=V(0.075, 0.075, 0.12))
    c.set_editor_property("override_materials", [eal.load_asset("/Game/Uyanis/Sahne/MI_Teneke")])
    try: c.set_collision_profile_name("NoCollision")
    except Exception as e: log("teneke carpisma", e)
    degisken(bp, "Yaricap", "float", 110.0); degisken(bp, "Menzil", "float", 750.0)
    degisken(bp, "TestOto", "bool", False); degisken(bp, "TestHedef", "Vector"); degisken(bp, "TestBekle", "float", 1.2)
    for n in ("Yakin", "Tutuyor", "Ucuyor"): degisken(bp, n, "bool", False, False)
    degisken(bp, "T", "float", 0.0, False); degisken(bp, "Tut", "float", 0.0, False)
    degisken(bp, "Bas", "Vector", None, False); degisken(bp, "Son", "Vector", None, False)
    dsl(bp, f'''
(event EventTick (DeltaSeconds)
  (bind pc (Game|GetPlayerController 0))
  (bind oy {OYUNCU})
  (bind op (Transformation|GetActorLocation oy))
  (if (Uye|Get|Ucuyor)
    (Uye|Set|T (+ (Uye|Get|T) (/ DeltaSeconds 0.7)))
    (bind a (Math|Float|Min(Float) (Uye|Get|T) 1.0))
    (bind duz (Math|Vector|Lerp(Vector) (Uye|Get|Bas) (Uye|Get|Son) a))
    (Transformation|SetActorLocation :NewLocation (+ duz (Math|Vector|MakeVector 0.0 0.0 (* 480.0 (* a (- 1.0 a))))) :bSweep false :bTeleport true)
    (Transformation|AddActorLocalRotation :DeltaRotation (Math|Rotator|MakeRotator 0.0 (* DeltaSeconds 900.0) 0.0) :bSweep false :bTeleport true)
    (if (>= (Uye|Get|T) 1.0)
      (Uye|Set|Ucuyor false)
      (Transformation|SetActorRotation :NewRotation (Math|Rotator|MakeRotator 90.0 0.0 (* 40.0 (Uye|Get|Tut))) :bTeleportPhysics true)
      (Audio|PlaySoundatLocation :Sound "{SES}/Teneke.Teneke" :Location (Uye|Get|Son) :VolumeMultiplier 1.0 :PitchMultiplier 1.0)
      (Utilities|Array|AddUnique (Variables|Actor|GetTags) "Ses")
      (Development|PrintString "SISLI TENEKE_DUSTU" :bPrintToScreen false)
      (Utilities|FlowControl|Delay 1.0)
      (Utilities|Array|RemoveItem (Variables|Actor|GetTags) "Ses"))
    (else
      (if (Uye|Get|Tutuyor)
        (Uye|Set|Tut (+ (Uye|Get|Tut) DeltaSeconds))
        (Transformation|SetActorLocation :NewLocation (+ op (Math|Vector|MakeVector 0.0 0.0 30.0)) :bSweep false :bTeleport true)
        (if (or (Game|Player|WasInputKeyJustPressed :self pc :Key "LeftMouseButton") (and (Uye|Get|TestOto) (> (Uye|Get|Tut) (Uye|Get|TestBekle))))
          (bind kam (Game|GetPlayerCameraManager 0))
          (bind yaw (select (Uye|Get|TestOto) (.yaw (Math|Rotator|FindLookatRotation op (Uye|Get|TestHedef))) (.yaw (Camera|GetCameraRotation :self kam))))
          (bind yon (Math|Vector|GetForwardVector (Math|Rotator|MakeRotator 0.0 0.0 yaw)))
          (bind bas (+ op (+ (* yon 45.0) (Math|Vector|MakeVector 0.0 0.0 40.0))))
          (bind (vur engel) (Collision|LineTraceByChannel :Start bas :End (+ bas (* yon (Uye|Get|Menzil))) :TraceChannel "Visibility" :bTraceComplex false))
          (bind (_h1 _h2 vt) (Collision|BreakHitResult vur))
          (bind dus (+ bas (* yon (- (* (select engel vt 1.0) (Uye|Get|Menzil)) 25.0))))
          (bind (vur2 zem) (Collision|LineTraceByChannel :Start dus :End (- dus (Math|Vector|MakeVector 0.0 0.0 600.0)) :TraceChannel "Visibility" :bTraceComplex false))
          (bind (_k1 _k2 vt2) (Collision|BreakHitResult vur2))
          (Uye|Set|Bas bas)
          (Uye|Set|Son (- dus (Math|Vector|MakeVector 0.0 0.0 (* (select zem vt2 1.0) 600.0))))
          (Uye|Set|T 0.0)
          (Uye|Set|Tutuyor false)
          (Uye|Set|Ucuyor true)
          (Uye|Set|TestOto false)
          (Rendering|SetActorHiddenInGame :bNewHidden false)
          (Audio|PlaySoundatLocation :Sound "{SES}/FenerTik.FenerTik" :Location op :VolumeMultiplier 0.4 :PitchMultiplier 0.7)
          (Development|PrintString "SISLI TENEKE_ATILDI" :bPrintToScreen false))
        (else
          (bind yakin (< (Math|Vector|Distance(Vector) (Transformation|GetActorLocation) op) (Uye|Get|Yaricap)))
          (if (and yakin (not (Uye|Get|Yakin)))
            (Uye|Set|Yakin true)
            {soz("teneke_ipucu")})
          (if (not yakin)
            (Uye|Set|Yakin false))
          (if (and yakin (or (Game|Player|WasInputKeyJustPressed :self pc :Key "E") (Uye|Get|TestOto)))
            (Uye|Set|Tutuyor true)
            (Uye|Set|Tut 0.0)
            (Rendering|SetActorHiddenInGame :bNewHidden true)
            (Audio|PlaySoundatLocation :Sound "{SES}/Anahtar.Anahtar" :Location op :VolumeMultiplier 0.3 :PitchMultiplier 0.55)
            (Development|PrintString "SISLI TENEKE_ALINDI" :bPrintToScreen false)
            {soz("teneke_al")}))))))
''')
    derle_kaydet(bp)

at_ = unreal.AssetToolsHelpers.get_asset_tools(); mel_ = unreal.MaterialEditingLibrary
def ses_al(fn):
    ap = f"{SES}/{fn}"
    if not eal.does_asset_exist(ap):
        t = unreal.AssetImportTask(); t.filename = f"C:/Users/Onur/Sisli/Ses/{fn}.wav"; t.destination_path = SES
        t.automated = True; t.save = True; t.replace_existing = True; at_.import_asset_tasks([t])
    return eal.load_asset(ap)
def mi_yap(ad, ana, ton, puruz=0.9, metal=None):
    p = f"/Game/Uyanis/Sahne/{ad}"
    m = eal.load_asset(p) if eal.does_asset_exist(p) else at_.create_asset(ad, "/Game/Uyanis/Sahne", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel_.set_material_instance_parent(m, eal.load_asset(ana))
    mel_.set_material_instance_scalar_parameter_value(m, "PuruzCarpan", puruz)
    if metal is not None: mel_.set_material_instance_scalar_parameter_value(m, "Metal", metal)
    mel_.set_material_instance_vector_parameter_value(m, "Ton", unreal.LinearColor(*ton, 1))
    eal.save_loaded_asset(m); return m
try:
    for s_ in ("Teneke", "Homurtu"): ses_al(s_)
    # iskelet örgülerinde M_Sisli (used_with_skeletal_mesh=True; yoksa -game'de varsayılan gri malzeme). Çok koyu: sis+sRGB 0.045'i bile griye çekiyor
    mi_yap("MI_Bekci_Kumas", "/Game/Sisli/Malzeme/M_Sisli", (0.012, 0.0115, 0.013), 0.95)   # bekçi: siyah kumaş, yüzsüz
    mi_yap("MI_Asci_Onluk", "/Game/Sisli/Malzeme/M_Sisli", (0.34, 0.27, 0.17), 0.9)       # aşçı: kirli, sararmış önlük
    mi_yap("MI_Teneke", "/Game/Uyanis/Malzeme/M_MS", (0.55, 0.5, 0.42), 0.4, 0.85)
except Exception:
    log("HATA malzeme/ses", traceback.format_exc())
SECIM = os.environ.get("MEK", "").split(",") if os.environ.get("MEK") else None
for ad, fn in (("BP_Saklanma", saklanma), ("BP_Bekci", bekci), ("BP_Asansor", asansor), ("BP_KatGiris", katgiris), ("BP_Atilabilir", atilabilir)):
    if SECIM is None or ad in SECIM:
        try: fn(); log("OK", ad)
        except Exception: log("HATA", ad, traceback.format_exc()[-1500:])
yaz("C:/Users/Onur/Sisli/Unreal/Scripts/mek_kat_out.txt")
