# Sisli mekanikleri (Blueprint, DSL ile): BP_Kapi, BP_EvKapisi, BP_Anahtar, BP_Projektor, BP_Olum, BP_Son, BP_Fener
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
from mekanik_lib import *
at = unreal.AssetToolsHelpers.get_asset_tools()
SES = "/Game/Sisli/Ses"
def ses(fn):
    ap = f"{SES}/{fn}"
    if not eal.does_asset_exist(ap):
        t = unreal.AssetImportTask(); t.filename = f"C:/Users/Onur/Sisli/Ses/{fn}.wav"; t.destination_path = SES
        t.automated = True; t.save = True; t.replace_existing = True; at.import_asset_tasks([t])
    return eal.load_asset(ap)
for s in ("Anahtar", "Gicirti", "Yakalandi", "FenerTik"): ses(s)
def mesh(n): return eal.load_asset(f"/Game/Sisli/Ortam/SM_Dyn_{n}/SM_Dyn_{n}")
V = unreal.Vector; R = lambda p=0, y=0, r=0: unreal.Rotator(roll=r, pitch=p, yaw=y)
OYUNCU = "(Game|GetPlayerCharacter 0)"
def isinla(hedef_expr):   # karartma → ışınla → aydınlatma (yakalanma/boğulma ortak)
    return f'''
      (bind kam (Game|GetPlayerCameraManager 0))
      (CameraFades|StartCameraFade kam 0.0 1.0 0.5 (Math|Color|MakeColor 0.0 0.0 0.0 1.0) false true)
      (Utilities|FlowControl|Delay 0.7)
      (Transformation|SetActorLocation {OYUNCU} {hedef_expr} false true)
      (CameraFades|StartCameraFade kam 1.0 0.0 1.2 (Math|Color|MakeColor 0.0 0.0 0.0 1.0) false false)'''

def kur(ad, fn):
    try: fn(); log("OK", ad)
    except Exception: log("HATA", ad, traceback.format_exc()[-1200:])

# ---------- BP_Kapi: kilitli çit kapısı — Anahtar aktörü yok olunca (alınınca) açılır ----------
def kapi():
    bp = yeni_bp("BP_Kapi")
    bilesen(bp, unreal.StaticMeshComponent, "Kanat", static_mesh=mesh("CitKapisi"))
    degisken(bp, "Anahtar", unreal.Actor); degisken(bp, "Acik", "bool", False, False); degisken(bp, "Uyarildi", "bool", False, False)
    dsl(bp, f'''
(event EventTick (DeltaSeconds)
  (if (not (Uye|Get|Acik))
    (Utilities|IsValid (Uye|Get|Anahtar)
      (:"Is Valid"
        (bind d (Math|Vector|Distance(Vector) (Transformation|GetActorLocation) (Transformation|GetActorLocation {OYUNCU})))
        (if (and (< d 280.0) (not (Uye|Get|Uyarildi)))
          (Uye|Set|Uyarildi true)
          (Development|PrintString "Kapı kilitli. Odada bir anahtar vardı..." :bPrintToLog false :Duration 4 :TextColor (Math|Color|MakeColor 0.86 0.8 0.66 1.0)))
        (if (> d 600.0)
          (Uye|Set|Uyarildi false)))
      (:"Is Not Valid"
        (Uye|Set|Acik true)
        (Development|PrintString "SISLI CIT_KAPI_ACILDI" :bPrintToScreen false)
        (Audio|PlaySoundatLocation :Sound "{SES}/Gicirti.Gicirti" :Location (Transformation|GetActorLocation))
        (Components|MoveComponentTo :Component (Uye|Get|Kanat) :TargetRelativeLocation (Math|Vector|MakeVector 0.0 0.0 0.0)
          :TargetRelativeRotation (Math|Rotator|MakeRotator 0.0 0.0 -95.0) :bEaseOut true :bEaseIn true :OverTime 2.8)))))
''')
    derle_kaydet(bp)

# ---------- BP_EvKapisi: yaklaşınca içeri açılan kapı ----------
def evkapisi():
    bp = yeni_bp("BP_EvKapisi")
    bilesen(bp, unreal.StaticMeshComponent, "Kanat", static_mesh=mesh("EvKapisi"))
    bilesen(bp, unreal.BoxComponent, "Tetik", box_extent=V(230, 110, 110), relative_location=V(0, -59, 110))
    degisken(bp, "Acik", "bool", False, False)
    dsl(bp, f'''
(event Collision|EventActorBeginOverlap (OtherActor)
  (Utilities|Casting|CastToCharacter :Object OtherActor
  (:then
  (if (not (Uye|Get|Acik))
    (Uye|Set|Acik true)
    (Audio|PlaySoundatLocation :Sound "{SES}/Gicirti.Gicirti" :Location (Transformation|GetActorLocation) :PitchMultiplier 1.25)
    (Components|MoveComponentTo :Component (Uye|Get|Kanat) :TargetRelativeLocation (Math|Vector|MakeVector 0.0 0.0 0.0)
      :TargetRelativeRotation (Math|Rotator|MakeRotator 0.0 0.0 95.0) :bEaseOut true :bEaseIn true :OverTime 1.6)))))
''')
    derle_kaydet(bp)

# ---------- BP_Anahtar: dönerek parlayan anahtar; alınınca ses + yok olur ----------
def anahtar():
    bp = yeni_bp("BP_Anahtar")
    bilesen(bp, unreal.StaticMeshComponent, "Govde", static_mesh=mesh("Anahtar"))
    bilesen(bp, unreal.PointLightComponent, "Isik", intensity_units=unreal.LightUnits.CANDELAS, intensity=1.6, attenuation_radius=160.0,
            light_color=unreal.Color(r=255, g=196, b=120, a=255), cast_shadows=False, relative_location=V(0, 0, 15))
    bilesen(bp, unreal.SphereComponent, "Tetik", sphere_radius=75.0)
    bilesen(bp, unreal.RotatingMovementComponent, "Donme", rotation_rate=R(0, 45, 0))
    dsl(bp, f'''
(event Collision|EventActorBeginOverlap (OtherActor)
  (Utilities|Casting|CastToCharacter :Object OtherActor
  (:then
    (Development|PrintString "SISLI ANAHTAR_ALINDI" :bPrintToScreen false)
    (Development|PrintString "Anahtarı aldın." :bPrintToLog false :Duration 3 :TextColor (Math|Color|MakeColor 0.86 0.8 0.66 1.0))
    (Audio|PlaySound2D :Sound "{SES}/Anahtar.Anahtar")
    (Actor|DestroyActor))))
''')
    derle_kaydet(bp)

# ---------- BP_Projektor: kuleden tarayan ışık; içinde görünürsen yakalanırsın ----------
def projektor():
    bp = yeni_bp("BP_Projektor")
    bilesen(bp, unreal.SpotLightComponent, "Isik", intensity_units=unreal.LightUnits.CANDELAS, intensity=900.0, attenuation_radius=6000.0,
            outer_cone_angle=13.0, inner_cone_angle=6.0, light_color=unreal.Color(r=230, g=240, b=255, a=255), volumetric_scattering_intensity=6.0,
            source_radius=12.0)
    degisken(bp, "Merkez", "Vector"); degisken(bp, "Donus", unreal.Actor)
    degisken(bp, "Genlik", "float", 35.0); degisken(bp, "Hiz", "float", 0.4); degisken(bp, "AlgiSure", "float", 0.8)
    degisken(bp, "Algi", "float", 0.0, False); degisken(bp, "Zaman", "float", 0.0, False); degisken(bp, "Yakalandi", "bool", False, False)
    dsl(bp, f'''
(event EventTick (DeltaSeconds)
  (Uye|Set|Zaman (+ (Uye|Get|Zaman) DeltaSeconds))
  (bind isik (Uye|Get|Isik))
  (bind konum (Transformation|GetWorldLocation isik))
  (bind bak (Math|Rotator|FindLookatRotation konum (Uye|Get|Merkez)))
  (bind ofs (* (Uye|Get|Genlik) (Math|Trig|Sin(Radians) (* (Uye|Get|Zaman) (Uye|Get|Hiz)))))
  (Transformation|SetWorldRotation isik (Math|Rotator|MakeRotator 0.0 (.pitch bak) (+ (.yaw bak) ofs)) false false)
  (if (not (Uye|Get|Yakalandi))
    (bind hedef (+ (Transformation|GetActorLocation {OYUNCU}) (Math|Vector|MakeVector 0.0 0.0 15.0)))
    (bind yon (Math|Vector|Normalize (- hedef konum)))
    (bind ileri (Transformation|GetForwardVector isik))
    (bind (isabet vurdu) (Collision|LineTraceByChannel :Start (+ konum (* ileri 80.0)) :End (- hedef (* yon 45.0)) :TraceChannel "Visibility" :bIgnoreSelf true))
    (if (and (> (Math|Vector|DotProduct yon ileri) 0.975) (not vurdu))
      (Uye|Set|Algi (+ (Uye|Get|Algi) DeltaSeconds))
      (else
        (Uye|Set|Algi (Math|Float|Max(Float) 0.0 (- (Uye|Get|Algi) (* DeltaSeconds 0.5))))))
    (Rendering|Components|Light|SetLightColor isik (Math|Color|Lerp(LinearColor) (Math|Color|MakeColor 0.9 0.94 1.0 1.0) (Math|Color|MakeColor 1.0 0.12 0.08 1.0)
      (Math|Float|Clamp(Float) (/ (Uye|Get|Algi) (Uye|Get|AlgiSure)) 0.0 1.0)) true)
    (if (> (Uye|Get|Algi) (Uye|Get|AlgiSure))
      (Uye|Set|Yakalandi true)
      (Development|PrintString "SISLI YAKALANDI" :bPrintToScreen false)
      (Development|PrintString "Projektör seni gördü. Siperlerin arkasından geç." :bPrintToLog false :Duration 4.5 :TextColor (Math|Color|MakeColor 0.86 0.8 0.66 1.0))
      (Audio|PlaySound2D :Sound "{SES}/Yakalandi.Yakalandi")
      {isinla("(Transformation|GetActorLocation (Uye|Get|Donus))")}
      (Uye|Set|Algi 0.0)
      (Utilities|FlowControl|Delay 1.5)
      (Uye|Set|Yakalandi false))))
''')
    derle_kaydet(bp)

# ---------- BP_Olum: suya düşünce iskele başına dön ----------
def olum():
    bp = yeni_bp("BP_Olum")
    bilesen(bp, unreal.BoxComponent, "Kutu", box_extent=V(100, 100, 100))
    degisken(bp, "Donus", unreal.Actor); degisken(bp, "Mesgul", "bool", False, False); degisken(bp, "Boyut", "Vector")
    dsl(bp, f'''
(event EventBeginPlay
  (Components|Box|SetBoxExtent :self (Uye|Get|Kutu) :InBoxExtent (Uye|Get|Boyut) :bUpdateOverlaps true))

(event Collision|EventActorBeginOverlap (OtherActor)
  (Utilities|Casting|CastToCharacter :Object OtherActor
  (:then
  (if (not (Uye|Get|Mesgul))
    (Uye|Set|Mesgul true)
    (Development|PrintString "SISLI BOGULDU" :bPrintToScreen false)
    (Development|PrintString "Su çok soğuk..." :bPrintToLog false :Duration 3 :TextColor (Math|Color|MakeColor 0.86 0.8 0.66 1.0))
    (Audio|PlaySound2D :Sound "{SES}/Yakalandi.Yakalandi" :VolumeMultiplier 0.6)
    {isinla("(Transformation|GetActorLocation (Uye|Get|Donus))")}
    (Uye|Set|Mesgul false)))))
''')
    derle_kaydet(bp)

# ---------- BP_Son: iskele ucu — yavaş karar, sonra baştan ----------
def son():
    bp = yeni_bp("BP_Son")
    bilesen(bp, unreal.BoxComponent, "Kutu", box_extent=V(160, 120, 150))
    degisken(bp, "Bitti", "bool", False, False)
    dsl(bp, f'''
(event Collision|EventActorBeginOverlap (OtherActor)
  (Utilities|Casting|CastToCharacter :Object OtherActor
  (:then
  (if (not (Uye|Get|Bitti))
    (Uye|Set|Bitti true)
    (Development|PrintString "SISLI SON" :bPrintToScreen false)
    (CameraFades|StartCameraFade (Game|GetPlayerCameraManager 0) 0.0 1.0 4.0 (Math|Color|MakeColor 0.0 0.0 0.0 1.0) true true)
    (Utilities|FlowControl|Delay 6.0)
    (Game|OpenLevel(byName) "L_Oda1")))))
''')
    derle_kaydet(bp)

# ---------- BP_Fener: çocuğa bağlanan el feneri, F ile aç/kapa ----------
def fener():
    bp = yeni_bp("BP_Fener")
    bilesen(bp, unreal.SpotLightComponent, "Isik", intensity_units=unreal.LightUnits.CANDELAS, intensity=55.0, attenuation_radius=1800.0,
            outer_cone_angle=24.0, inner_cone_angle=10.0, light_color=unreal.Color(r=255, g=236, b=205, a=255), volumetric_scattering_intensity=2.5,
            source_radius=3.0, visible=False)
    degisken(bp, "Comeldi", "bool", False, False); degisken(bp, "CAnim", "float", 0.0, False); degisken(bp, "TestComel", "bool", False)
    degisken(bp, "BSKurulu", "bool", False, False); degisken(bp, "ComelA", "float", 0.0, False); degisken(bp, "HizY", "float", 0.0, False)   # CAnim: 0 ABP, 1 çömelik bekleme, 2 çömelik yürüme
    g = BT.get_graph(bp, "EventGraph")
    # F tuşu olayı (InputKey düğümü, Pressed çıkışı)
    dsl(bp, f'''
(event EventBeginPlay
  (Development|PrintString "SISLI FENER_BASLADI" :bPrintToScreen false)
  (bind oyuncu {OYUNCU})
  (bind don (Transformation|GetActorRotation oyuncu))
  (Pawn|SetControlRotation :self (Game|GetPlayerController 0) :NewRotation (Math|Rotator|MakeRotator 0.0 -5.0 (.yaw don)))
  (bind ileri (Math|Vector|GetForwardVector don))
  (Transformation|SetActorLocationAndRotation :NewLocation (+ (Transformation|GetActorLocation oyuncu) (+ (* ileri 22.0) (Math|Vector|MakeVector 0.0 0.0 28.0)))
    :NewRotation (Math|Rotator|MakeRotator 0.0 -14.0 (.yaw don)) :bSweep false :bTeleport true)
  (Transformation|AttachActorToActor :ParentActor oyuncu :LocationRule "KeepWorld" :RotationRule "KeepWorld" :ScaleRule "KeepWorld" :bWeldSimulatedBodies false)
  (Input|EnableInput :PlayerController (Game|GetPlayerController 0)))

(event EventTick (DeltaSeconds)
  (bind pc (Game|GetPlayerController 0))
  (if (Game|Player|WasInputKeyJustPressed :self pc :Key "F")
    (Rendering|ToggleVisibility (Uye|Get|Isik))
    (Audio|PlaySound2D :Sound "{SES}/FenerTik.FenerTik"))
  (bind oy {OYUNCU})
  (bind ctrl (or (or (Game|Player|IsInputKeyDown :self pc :Key "LeftControl") (Game|Player|IsInputKeyDown :self pc :Key "RightControl")) (Uye|Get|TestComel)))
  (bind mb (Actor|GetComponentbyClass oy "/Script/Engine.SkeletalMeshComponent"))
  (bind m (Utilities|Casting|CastToSkeletalMeshComponent :Object mb)
    (:then
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Mouth_Smile_L" :Value 0.00 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Mouth_Smile_R" :Value 0.00 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Mouth_Smile_Sharp_L" :Value 0.00 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Mouth_Smile_Sharp_R" :Value 0.00 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Cheek_Raise_L" :Value 0.00 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Cheek_Raise_R" :Value 0.00 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Mouth_Frown_L" :Value 0.32 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Mouth_Frown_R" :Value 0.32 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Brow_Raise_Inner_L" :Value 0.50 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Brow_Raise_Inner_R" :Value 0.50 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Brow_Compress_L" :Value 0.22 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Brow_Compress_R" :Value 0.22 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Mouth_Press_L" :Value 0.18 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Mouth_Press_R" :Value 0.18 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Eye_Squint_L" :Value 0.12 :bRemoveZeroWeight false)
      (Components|SkeletalMesh|SetMorphTarget :self m :MorphTargetName "Eye_Squint_R" :Value 0.12 :bRemoveZeroWeight false)
      (if (not (Uye|Get|BSKurulu))
        (Uye|Set|BSKurulu true)
        (Components|Animation|PlayAnimation :self m :NewAnimToPlay "/Game/Sisli/Cocuk2/Anim/BS_Cocuk2_Hareket2.BS_Cocuk2_Hareket2" :bLooping true))
      (if (!= ctrl (Uye|Get|Comeldi))
        (Uye|Set|Comeldi ctrl)
        (if ctrl
          (Character|Crouch :self oy)
          (Development|PrintString "SISLI COMELDI" :bPrintToScreen false)
          (else
            (Character|UnCrouch :self oy))))
      (Uye|Set|ComelA (Math|Interpolation|FInterpTo (Uye|Get|ComelA) (select (Uye|Get|Comeldi) 1.0 0.0) DeltaSeconds 5.0))
      (bind v (Transformation|GetVelocity oy))
      (bind hiz (Math|Vector|VectorLength (Math|Vector|MakeVector (.x v) (.y v) 0.0)))
      (Uye|Set|HizY (Math|Interpolation|FInterpTo (Uye|Get|HizY) hiz DeltaSeconds 8.0))
      (bind tek (Utilities|Casting|CastToAnimSingleNodeInstance :Object (Components|SkeletalMesh|GetAnimInstance :self m))
        (:then
          (Animation|SetBlendSpacePosition :self tek :InPosition (Math|Vector|MakeVector (+ 45.0 (* 45.0 (Uye|Get|ComelA))) (* (Uye|Get|HizY) (+ 2.0 (* 1.16 (Uye|Get|ComelA)))) 0.0)))
        (:CastFailed)))
    (:CastFailed)))
''')
    derle_kaydet(bp)

# ---------- BP_IcMekan: çocuk evin içindeyken çatı/tavan/güney duvarı üstü (EvKesit) gizlenir ----------
def icmekan():
    bp = yeni_bp("BP_IcMekan")
    bilesen(bp, unreal.BoxComponent, "Kutu", box_extent=V(100, 100, 100))
    degisken(bp, "Boyut", "Vector")          # örnek değişkeni: kutu yarı boyutu (BeginPlay de uygulanır)
    degisken(bp, "Icerde", "bool", False, False)
    degisken(bp, "Egim", "float", -48.0, False)
    dsl(bp, f'''
(event EventBeginPlay
  (Components|Box|SetBoxExtent :self (Uye|Get|Kutu) :InBoxExtent (Uye|Get|Boyut) :bUpdateOverlaps false))

(event EventTick (DeltaSeconds)
  (bind kutu (Uye|Get|Kutu))
  (bind d (- (Transformation|GetActorLocation {OYUNCU}) (Transformation|GetWorldLocation kutu)))
  (bind e (Components|Box|GetScaledBoxExtent kutu))
  (bind ic (and (and (< (Math|Float|Absolute(Float) (.x d)) (.x e)) (< (Math|Float|Absolute(Float) (.y d)) (.y e))) (< (Math|Float|Absolute(Float) (.z d)) (.z e))))
  (if (!= ic (Uye|Get|Icerde))
    (Uye|Set|Icerde ic)
    (Development|PrintString (select ic "SISLI IC_MEKAN_GIRIS" "SISLI IC_MEKAN_CIKIS") :bPrintToScreen false)
    (bind liste (Actor|GetAllActorswithTag "EvKesit"))
    (for a liste
      (Rendering|SetActorHiddenInGame a ic)))
  (bind kolb (Actor|GetComponentbyClass {OYUNCU} "/Script/Engine.SpringArmComponent"))
  (bind kol (Utilities|Casting|CastToSpringArmComponent :Object kolb)
    (:then
      (Class|SpringArmComponent|SetTargetArmLength :self kol :TargetArmLength (Math|Interpolation|FInterpTo (Class|SpringArmComponent|GetTargetArmLength :self kol) (select ic 1100.0 2000.0) DeltaSeconds 2.5))
      (Class|SpringArmComponent|SetDoCollisionTest :self kol :bDoCollisionTest (not ic))
      (Uye|Set|Egim (Math|Interpolation|FInterpTo (Uye|Get|Egim) (select ic -65.0 -48.0) DeltaSeconds 2.5))
      (Transformation|SetRelativeRotation kol (Math|Rotator|MakeRotator 0.0 (Uye|Get|Egim) 0.0) false false))
    (:CastFailed)))
''')
    derle_kaydet(bp)

# ---------- BP_KameraAlani: iki kip — SERBEST (varsayılan: karakterin fare kamerası) / SİNEMA (bu alanın sabit kamerası) ----------
# Kip = görüş hedefi: hedef oyuncuysa serbest. C tuşu, oyuncunun içinde durduğu alanda kipi değiştirir.
# Sinema kipinde kontrol yönü her karede o kameranın yaw'ına kilitlenir (fare WASD yönünü kaydırmasın).
def kameraalani():
    bp = yeni_bp("BP_KameraAlani")
    bilesen(bp, unreal.BoxComponent, "Kutu", box_extent=V(100, 100, 100))
    degisken(bp, "Kamera", unreal.Actor); degisken(bp, "Boyut", "Vector"); degisken(bp, "Gecis", "float", 1.2); degisken(bp, "Basta", "bool", False)
    kam_yaw = "(Math|Rotator|MakeRotator 0.0 0.0 (.yaw (Transformation|GetActorRotation (Uye|Get|Kamera))))"
    dsl(bp, f'''
(event EventBeginPlay
  (Components|Box|SetBoxExtent :self (Uye|Get|Kutu) :InBoxExtent (Uye|Get|Boyut) :bUpdateOverlaps true)
  (if (Uye|Get|Basta)
    (Utilities|FlowControl|Delay 0.05)
    (bind pc (Game|GetPlayerController 0))
    (Game|Player|SetViewTargetwithBlend :self pc :NewViewTarget (Uye|Get|Kamera) :BlendTime 0.0)
    (Pawn|SetControlRotation :self pc :NewRotation {kam_yaw})))

(event Collision|EventActorBeginOverlap (OtherActor)
  (Utilities|Casting|CastToCharacter :Object OtherActor
    (:then
      (bind pc (Game|GetPlayerController 0))
      (if (!= (Pawn|GetViewTarget :self pc) {OYUNCU})
        (Game|Player|SetViewTargetwithBlend :self pc :NewViewTarget (Uye|Get|Kamera) :BlendTime (Uye|Get|Gecis))))))

(event EventTick (DeltaSeconds)
  (bind pc (Game|GetPlayerController 0))
  (bind oy {OYUNCU})
  (bind kutu (Uye|Get|Kutu))
  (bind d (- (Transformation|GetActorLocation oy) (Transformation|GetWorldLocation kutu)))
  (bind e (+ (Components|Box|GetScaledBoxExtent kutu) (Math|Vector|MakeVector 15.0 15.0 15.0)))
  (bind ic (and (and (< (Math|Float|Absolute(Float) (.x d)) (.x e)) (< (Math|Float|Absolute(Float) (.y d)) (.y e))) (< (Math|Float|Absolute(Float) (.z d)) (.z e))))
  (if ic
    (bind serbest (== (Pawn|GetViewTarget :self pc) oy))
    (if (Game|Player|WasInputKeyJustPressed :self pc :Key "C")
      (if serbest
        (Game|Player|SetViewTargetwithBlend :self pc :NewViewTarget (Uye|Get|Kamera) :BlendTime 0.7)
        (Development|PrintString "SISLI KIP_SINEMA" :bPrintToScreen false)
        (else
          (Game|Player|SetViewTargetwithBlend :self pc :NewViewTarget oy :BlendTime 0.7)
          (Development|PrintString "SISLI KIP_SERBEST" :bPrintToScreen false)))
      (else
        (if (not serbest)
          (Pawn|SetControlRotation :self pc :NewRotation {kam_yaw}))))))
''')
    derle_kaydet(bp)

# ---------- BP_SinemaKamera: "biraz serbest" sinematik kamera — taban kadrajı korur, oyuncuyu sınırlı takip eder, fareyle ±12° bakılır, bırakınca geri döner ----------
def sinemakamera():
    bp = yeni_bp("BP_SinemaKamera")
    bilesen(bp, unreal.CameraComponent, "Kam", field_of_view=60.0, constrain_aspect_ratio=False)
    degisken(bp, "Odak", "Vector"); degisken(bp, "Takip", "Vector"); degisken(bp, "Bakis", "float", 0.45); degisken(bp, "MaxKayma", "float", 140.0); degisken(bp, "FOV", "float", 60.0)
    degisken(bp, "BazKonum", "Vector", None, False); degisken(bp, "BazDonus", "Rotator", None, False)
    degisken(bp, "FareYaw", "float", 0.0, False); degisken(bp, "FarePitch", "float", 0.0, False)
    dsl(bp, '''
(event EventBeginPlay
  (Uye|Set|BazKonum (Transformation|GetActorLocation))
  (Uye|Set|BazDonus (Transformation|GetActorRotation))
  (Class|CameraComponent|SetFieldOfView :self (Uye|Get|Kam) :FieldOfView (Uye|Get|FOV)))

(event EventTick (DeltaSeconds)
  (bind oy (Transformation|GetActorLocation (Game|GetPlayerCharacter 0)))
  (bind kay (Math|Vector|ClampVectorSize (* (- oy (Uye|Get|Odak)) (Uye|Get|Takip)) 0.0 (Uye|Get|MaxKayma)))
  (bind hk (+ (Uye|Get|BazKonum) kay))
  (bind bak (Math|Rotator|FindLookatRotation hk (+ oy (Math|Vector|MakeVector 0.0 0.0 50.0))))
  (bind fark (Math|Rotator|Delta(Rotator) bak (Uye|Get|BazDonus)))
  (bind (dx dy) (Game|Player|GetInputMouseDelta :self (Game|GetPlayerController 0)))
  (Uye|Set|FareYaw (Math|Float|Clamp(Float) (+ (* (Uye|Get|FareYaw) (- 1.0 (* DeltaSeconds 1.2))) (* dx 0.3)) -12.0 12.0))
  (Uye|Set|FarePitch (Math|Float|Clamp(Float) (+ (* (Uye|Get|FarePitch) (- 1.0 (* DeltaSeconds 1.2))) (* dy 0.3)) -7.0 7.0))
  (bind hd (Math|Rotator|MakeRotator 0.0
     (+ (+ (.pitch (Uye|Get|BazDonus)) (* (Math|Float|Clamp(Float) (.pitch fark) -8.0 8.0) (Uye|Get|Bakis))) (Uye|Get|FarePitch))
     (+ (+ (.yaw (Uye|Get|BazDonus)) (* (Math|Float|Clamp(Float) (.yaw fark) -18.0 18.0) (Uye|Get|Bakis))) (Uye|Get|FareYaw))))
  (Transformation|SetActorLocationAndRotation :NewLocation (Math|Interpolation|VInterpTo (Transformation|GetActorLocation) hk DeltaSeconds 2.0)
    :NewRotation (Math|Interpolation|RInterpTo (Transformation|GetActorRotation) hd DeltaSeconds 3.0) :bSweep false :bTeleport false))
''')
    derle_kaydet(bp)

# ---------- BP_TestYuru: test aracı — oyuncuyu sırayla H1→H2→H3'e yürütür, her varışı log'a yazar (yalnız ODA_TEST_YURU ile yerleştirilir) ----------
def testyuru():
    bp = yeni_bp("BP_TestYuru")
    for n in ("H1", "H2", "H3", "H4", "H5", "H6"): degisken(bp, n, "Vector")
    degisken(bp, "Son", "float", 3.0); degisken(bp, "Adim", "float", 0.0, False)
    dsl(bp, '''
(event EventTick (DeltaSeconds)
  (bind oy (Game|GetPlayerCharacter 0))
  (if (< (Uye|Get|Adim) (- (Uye|Get|Son) 0.5))
    (bind a (Uye|Get|Adim))
    (bind hedef (select (< a 0.5) (Uye|Get|H1) (select (< a 1.5) (Uye|Get|H2) (select (< a 2.5) (Uye|Get|H3) (select (< a 3.5) (Uye|Get|H4) (select (< a 4.5) (Uye|Get|H5) (Uye|Get|H6)))))))
    (bind konum (Transformation|GetActorLocation oy))
    (bind f (Math|Vector|MakeVector (- (.x hedef) (.x konum)) (- (.y hedef) (.y konum)) 0.0))
    (if (> (Math|Vector|VectorLength f) 70.0)
      (Pawn|Input|AddMovementInput :self oy :WorldDirection (Math|Vector|Normalize f) :ScaleValue 1.0)
      (else
        (Uye|Set|Adim (+ (Uye|Get|Adim) 1.0))
        (Development|PrintString "SISLI TEST_HEDEF_VARILDI" :bPrintToScreen false)))))
''')
    derle_kaydet(bp)

# ================= UYANIŞ (açılış) mekanikleri =================
YAZI = "(Math|Color|MakeColor 0.86 0.84 0.8 1.0)"
# ---------- BP_Giris: siyahtan açılış + ilk iç ses ----------
def giris():
    bp = yeni_bp("BP_Giris")
    dsl(bp, f'''
(event EventBeginPlay
  (bind kam (Game|GetPlayerCameraManager 0))
  (CameraFades|StartCameraFade kam 1.0 0.0 5.0 (Math|Color|MakeColor 0.0 0.0 0.0 1.0) false false)
  (Development|PrintString "SISLI GIRIS" :bPrintToScreen false)
  (Utilities|FlowControl|Delay 3.5)
  (Audio|PlaySound2D :Sound "/Game/Uyanis/Yazi/SW_giris.SW_giris")
  (Utilities|FlowControl|Delay 4.0)
  (Audio|PlaySound2D :Sound "/Game/Uyanis/Yazi/SW_kontrol.SW_kontrol"))
''')
    derle_kaydet(bp)

# ---------- BP_Oyuncak: kardeşin tavşanı — alınınca iç ses + hedef ----------
def oyuncak():
    bp = yeni_bp("BP_Oyuncak")
    bilesen(bp, unreal.StaticMeshComponent, "Govde", static_mesh=eal.load_asset("/Game/Uyanis/Fab/Oyuncak/SM_ToyBunny"))
    bilesen(bp, unreal.SphereComponent, "Tetik", sphere_radius=85.0)
    degisken(bp, "Alindi", "bool", False, False)
    dsl(bp, f'''
(event Collision|EventActorBeginOverlap (OtherActor)
  (Utilities|Casting|CastToCharacter :Object OtherActor
  (:then
  (if (not (Uye|Get|Alindi))
    (Uye|Set|Alindi true)
    (Development|PrintString "SISLI TAVSAN_ALINDI" :bPrintToScreen false)
    (Audio|PlaySound2D :Sound "{SES}/Anahtar.Anahtar" :PitchMultiplier 0.7)
    (Rendering|SetVisibility :self (Uye|Get|Govde) :bNewVisibility false)
    (Audio|PlaySound2D :Sound "/Game/Uyanis/Yazi/SW_tavsan1.SW_tavsan1")
    (Utilities|FlowControl|Delay 5.0)
    (Audio|PlaySound2D :Sound "/Game/Uyanis/Yazi/SW_tavsan2.SW_tavsan2")))))
''')
    derle_kaydet(bp)

# ---------- BP_Bitis: terasın kenarı — yavaş karar, başlık, baştan ----------
def bitis():
    bp = yeni_bp("BP_Bitis")
    bilesen(bp, unreal.BoxComponent, "Kutu", box_extent=V(300, 120, 200))
    degisken(bp, "Bitti", "bool", False, False)
    dsl(bp, f'''
(event Collision|EventActorBeginOverlap (OtherActor)
  (Utilities|Casting|CastToCharacter :Object OtherActor
  (:then
  (if (not (Uye|Get|Bitti))
    (Uye|Set|Bitti true)
    (Development|PrintString "SISLI SON" :bPrintToScreen false)
    (Development|PrintString "Oralarda bir yerdesin. Geliyorum, Ela." :bPrintToLog false :Duration 6 :TextColor {YAZI})
    (Utilities|FlowControl|Delay 3.0)
    (CameraFades|StartCameraFade (Game|GetPlayerCameraManager 0) 0.0 1.0 4.0 (Math|Color|MakeColor 0.0 0.0 0.0 1.0) true true)
    (Utilities|FlowControl|Delay 4.5)
    (Development|PrintString "U Y A N I Ş" :bPrintToLog false :Duration 5 :TextColor {YAZI})
    (Utilities|FlowControl|Delay 6.0)
    (Game|OpenLevel(byName) "L_Uyanis")))))
''')
    derle_kaydet(bp)

# ---------- ışık mekanikleri için kalıcı MI'ler (seviye betiği bunları silip yeniden yaratmaz) ----------
KUP = eal.load_asset("/Engine/BasicShapes/Cube.Cube")
def bp_mi(ad, vek, skal=None):
    p = f"/Game/Uyanis/Mekanik/{ad}"
    if eal.does_asset_exist(p): return eal.load_asset(p)
    m = at.create_asset(ad, "/Game/Uyanis/Mekanik", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel_ = unreal.MaterialEditingLibrary; mel_.set_material_instance_parent(m, eal.load_asset("/Game/Uyanis/Malzeme/M_MS"))
    for k, v in vek.items(): mel_.set_material_instance_vector_parameter_value(m, k, unreal.LinearColor(*v))
    for k, v in (skal or {}).items(): mel_.set_material_instance_scalar_parameter_value(m, k, v)
    eal.save_loaded_asset(m); return m

# ---------- BP_Floresan: gerçekçi floresan — neredeyse hep sabit, arada kısa tekleme; tüp ışığı ışıkla birlikte söner ----------
def floresan():
    bp = yeni_bp("BP_Floresan")
    govde = bp_mi("MI_Floresan_Govde", {"Ton": (0.035, 0.036, 0.04, 1)}, {"Metal": 0.7, "PuruzCarpan": 0.45})
    tup = bp_mi("MI_Floresan_Tup", {"Ton": (0.8, 0.85, 0.85, 1), "Isima": (5.5, 7.0, 7.4, 1)}, {"PuruzCarpan": 0.3})
    bilesen(bp, unreal.StaticMeshComponent, "Govde", static_mesh=KUP, relative_scale3d=V(1.4, 0.18, 0.12), relative_location=V(0, 0, 6), override_materials=[govde])
    bilesen(bp, unreal.StaticMeshComponent, "Tup", static_mesh=KUP, relative_scale3d=V(1.32, 0.08, 0.04), relative_location=V(0, 0, -2), override_materials=[tup], cast_shadow=False)
    bilesen(bp, unreal.RectLightComponent, "Isik", intensity_units=unreal.LightUnits.CANDELAS, intensity=26.0, attenuation_radius=1000.0, source_width=130.0, source_height=10.0,
            barn_door_angle=80.0, use_temperature=True, temperature=7200.0, volumetric_scattering_intensity=1.0, relative_rotation=R(-90, 0, 0), relative_location=V(0, 0, -6))
    degisken(bp, "TemelSiddet", "float", 26.0); degisken(bp, "Sans", "float", 0.08)   # Sans: saniyede tekleme olasılığı (~12 sn'de bir)
    degisken(bp, "Tekleme", "float", 0.0, False); degisken(bp, "Seviye", "float", 1.0, False)
    dsl(bp, '''
(event EventTick (DeltaSeconds)
  (if (> (Uye|Get|Tekleme) 0.0)
    (Uye|Set|Tekleme (- (Uye|Get|Tekleme) DeltaSeconds))
    (Uye|Set|Seviye (select (< (Math|Random|RandomFloatinRange 0.0 1.0) 0.5) (Math|Random|RandomFloatinRange 0.04 0.3) (Math|Random|RandomFloatinRange 0.75 1.0)))
    (else
      (Uye|Set|Seviye (Math|Interpolation|FInterpTo (Uye|Get|Seviye) 1.0 DeltaSeconds 14.0))
      (if (< (Math|Random|RandomFloatinRange 0.0 1.0) (* (Uye|Get|Sans) DeltaSeconds))
        (Uye|Set|Tekleme (Math|Random|RandomFloatinRange 0.12 0.4)))))
  (bind k (Uye|Get|Seviye))
  (Rendering|Components|Light|SetIntensity :self (Uye|Get|Isik) :NewIntensity (* (Uye|Get|TemelSiddet) k))
  (Rendering|Material|SetVectorParameterValueonMaterials :self (Uye|Get|Tup) :ParameterName "Isima" :ParameterValue (Math|Vector|MakeVector (* 5.5 k) (* 7.0 k) (* 7.4 k))))
''')
    derle_kaydet(bp)

# ---------- BP_KirmiziLamba: acil durum lambası — yavaş nabız (oyuncuya yolu gösteren kırmızı dil) ----------
def kirmizilamba():
    bp = yeni_bp("BP_KirmiziLamba")
    gm = bp_mi("MI_Kirmizi_Lamba", {"Ton": (0.05, 0.0, 0.0, 1), "Isima": (18.0, 0.6, 0.3, 1)}, {"PuruzCarpan": 0.4})
    kafes = bp_mi("MI_Floresan_Govde", {"Ton": (0.035, 0.036, 0.04, 1)}, {"Metal": 0.7, "PuruzCarpan": 0.45})
    bilesen(bp, unreal.StaticMeshComponent, "Kasa", static_mesh=KUP, relative_scale3d=V(0.34, 0.14, 0.16), override_materials=[kafes])
    bilesen(bp, unreal.StaticMeshComponent, "Cam", static_mesh=KUP, relative_scale3d=V(0.28, 0.06, 0.11), relative_location=V(0, -8, 0), override_materials=[gm], cast_shadow=False)
    bilesen(bp, unreal.PointLightComponent, "Isik", intensity_units=unreal.LightUnits.CANDELAS, intensity=6.0, attenuation_radius=750.0, source_radius=2.0,
            light_color=unreal.Color(r=255, g=38, b=22, a=255), volumetric_scattering_intensity=2.2, relative_location=V(0, -22, 0))
    degisken(bp, "TemelSiddet", "float", 6.0); degisken(bp, "Hiz", "float", 1.7); degisken(bp, "Faz", "float", 0.0)
    degisken(bp, "Zaman", "float", 0.0, False)
    dsl(bp, '''
(event EventTick (DeltaSeconds)
  (Uye|Set|Zaman (+ (Uye|Get|Zaman) DeltaSeconds))
  (bind s (Math|Trig|Sin(Radians) (+ (* (Uye|Get|Zaman) (Uye|Get|Hiz)) (Uye|Get|Faz))))
  (bind k (+ 0.35 (* 0.65 (* (+ 0.5 (* 0.5 s)) (+ 0.5 (* 0.5 s))))))
  (Rendering|Components|Light|SetIntensity :self (Uye|Get|Isik) :NewIntensity (* (Uye|Get|TemelSiddet) k))
  (Rendering|Material|SetVectorParameterValueonMaterials :self (Uye|Get|Cam) :ParameterName "Isima" :ParameterValue (Math|Vector|MakeVector (* 18.0 k) (* 0.6 k) (* 0.3 k))))
''')
    derle_kaydet(bp)

# ================= Yatakhane: inceleme + kapı (altyazılar /Game/Uyanis/Yazi/SW_*) =================
YZ = "/Game/Uyanis/Yazi"
def sw(k): return f"{YZ}/SW_{k}.SW_{k}"

# ---------- BP_Incele: yaklaşınca hafif parıltı + bir kez "[E] İncele"; E → 1-3 iç ses satırı; Al=true ise eşya alınır (aktör gizlenir, BP kendini yok eder) ----------
def incele():
    bp = yeni_bp("BP_Incele")
    bilesen(bp, unreal.PointLightComponent, "Parilti", intensity_units=unreal.LightUnits.CANDELAS, intensity=0.15, attenuation_radius=60.0, source_radius=1.0,
            light_color=unreal.Color(r=255, g=232, b=200, a=255), cast_shadows=False, volumetric_scattering_intensity=0.0)
    for n in ("Satir1", "Satir2", "Satir3"): degisken(bp, n, unreal.SoundBase)
    degisken(bp, "Sure1", "float", 4.0); degisken(bp, "Sure2", "float", 4.0); degisken(bp, "Yaricap", "float", 160.0)
    degisken(bp, "Al", "bool", False); degisken(bp, "AlinanAktor", unreal.Actor); degisken(bp, "TestOto", "bool", False)
    degisken(bp, "Yakin", "bool", False, False); degisken(bp, "Incelendi", "bool", False, False); degisken(bp, "Mesgul", "bool", False, False)
    dsl(bp, f'''
(event EventTick (DeltaSeconds)
  (bind pc (Game|GetPlayerController 0))
  (bind yakin (< (Math|Vector|Distance(Vector) (Transformation|GetWorldLocation (Uye|Get|Parilti)) (Transformation|GetActorLocation {OYUNCU})) (Uye|Get|Yaricap)))
  (if (and yakin (not (Uye|Get|Yakin)))
    (Uye|Set|Yakin true)
    (if (not (Uye|Get|Incelendi))
      (Audio|PlaySound2D :Sound "{sw('ipucu')}")))
  (if (not yakin)
    (Uye|Set|Yakin false))
  (if (and (and yakin (not (Uye|Get|Mesgul))) (or (Game|Player|WasInputKeyJustPressed :self pc :Key "E") (and (Uye|Get|TestOto) (not (Uye|Get|Incelendi)))))
    (Uye|Set|Mesgul true)
    (Uye|Set|Incelendi true)
    (Rendering|SetVisibility :self (Uye|Get|Parilti) :bNewVisibility false)
    (Development|PrintString "SISLI INCELE" :bPrintToScreen false)
    (Audio|PlaySound2D :Sound (Uye|Get|Satir1))
    (if (Uye|Get|Al)
      (Actor|DestroyActor :self (Uye|Get|AlinanAktor))
      (Development|PrintString "SISLI ALINDI" :bPrintToScreen false))
    (Utilities|FlowControl|Delay (Uye|Get|Sure1))
    (Audio|PlaySound2D :Sound (Uye|Get|Satir2))
    (Utilities|FlowControl|Delay (Uye|Get|Sure2))
    (Audio|PlaySound2D :Sound (Uye|Get|Satir3))
    (Uye|Set|Mesgul false)))
''')
    derle_kaydet(bp)

# ---------- BP_YatakhaneKapisi: Megascans çift kanatlı boyalı kapı — E: anahtar yoksa "kilitli", varsa kanatlar menteşeden açılır ----------
def yatakhanekapisi():
    bp = yeni_bp("BP_YatakhaneKapisi")
    K = "/Game/Uyanis/Fab/Yat/Kapi/"
    bilesen(bp, unreal.StaticMeshComponent, "Kasa", static_mesh=eal.load_asset(K + "vmqifgedw_LOD0_TIER1_000"))
    bilesen(bp, unreal.StaticMeshComponent, "KanatSol", static_mesh=eal.load_asset(K + "vmqifgedw_LOD0_TIER1_001"), relative_location=V(-73.7, 0, 110.5))
    bilesen(bp, unreal.StaticMeshComponent, "KanatSag", static_mesh=eal.load_asset(K + "vmqifgedw_LOD0_TIER1_002"), relative_location=V(73.4, 0, 110.5))
    degisken(bp, "Anahtar", unreal.Actor); degisken(bp, "Yaricap", "float", 190.0); degisken(bp, "AcilmaYonu", "float", 1.0); degisken(bp, "TestOto", "bool", False)
    degisken(bp, "Acik", "bool", False, False); degisken(bp, "Yakin", "bool", False, False); degisken(bp, "Mesgul", "bool", False, False)
    degisken(bp, "Aci", "float", 0.0, False)
    dsl(bp, f'''
(event EventTick (DeltaSeconds)
  (bind pc (Game|GetPlayerController 0))
  (if (Uye|Get|Acik)
    (Uye|Set|Aci (Math|Interpolation|FInterpTo (Uye|Get|Aci) 100.0 DeltaSeconds 1.1))
    (Transformation|SetRelativeRotation (Uye|Get|KanatSol) (Math|Rotator|MakeRotator 0.0 0.0 (* (* -1.0 (Uye|Get|Aci)) (Uye|Get|AcilmaYonu))) false false)
    (Transformation|SetRelativeRotation (Uye|Get|KanatSag) (Math|Rotator|MakeRotator 0.0 0.0 (* (* 0.92 (Uye|Get|Aci)) (Uye|Get|AcilmaYonu))) false false))
  (bind yakin (< (Math|Vector|Distance(Vector) (+ (Transformation|GetActorLocation) (Math|Vector|MakeVector 0.0 0.0 100.0)) (Transformation|GetActorLocation {OYUNCU})) (Uye|Get|Yaricap)))
  (if (and yakin (not (Uye|Get|Yakin)))
    (Uye|Set|Yakin true)
    (if (not (Uye|Get|Acik))
      (Audio|PlaySound2D :Sound "{sw('ipucu')}")))
  (if (not yakin)
    (Uye|Set|Yakin false))
  (if (and (and (and yakin (not (Uye|Get|Mesgul))) (not (Uye|Get|Acik))) (or (Game|Player|WasInputKeyJustPressed :self pc :Key "E") (Uye|Get|TestOto)))
    (Utilities|IsValid (Uye|Get|Anahtar)
      (:"Is Valid"
        (Uye|Set|Mesgul true)
        (Development|PrintString "SISLI KAPI_KILITLI" :bPrintToScreen false)
        (Audio|PlaySound2D :Sound "{sw('kapi_kilitli')}")
        (Audio|PlaySoundatLocation :Sound "{SES}/Gicirti.Gicirti" :Location (Transformation|GetActorLocation) :VolumeMultiplier 0.35 :PitchMultiplier 2.2)
        (Utilities|FlowControl|Delay 3.0)
        (Uye|Set|Mesgul false))
      (:"Is Not Valid"
        (Uye|Set|Acik true)
        (Development|PrintString "SISLI KAPI_ACILDI" :bPrintToScreen false)
        (Audio|PlaySoundatLocation :Sound "{SES}/Gicirti.Gicirti" :Location (Transformation|GetActorLocation) :PitchMultiplier 0.85)
        (Utilities|FlowControl|Delay 1.2)
        (Audio|PlaySound2D :Sound "{sw('kapi_acik')}")))))
''')
    derle_kaydet(bp)

import os
SECIM = os.environ.get("MEK", "").split(",") if os.environ.get("MEK") else None
for ad, fn in (("BP_Kapi", kapi), ("BP_EvKapisi", evkapisi), ("BP_Anahtar", anahtar), ("BP_Projektor", projektor), ("BP_Olum", olum), ("BP_Son", son), ("BP_Fener", fener), ("BP_IcMekan", icmekan), ("BP_KameraAlani", kameraalani), ("BP_SinemaKamera", sinemakamera), ("BP_TestYuru", testyuru), ("BP_Giris", giris), ("BP_Oyuncak", oyuncak), ("BP_Bitis", bitis), ("BP_Floresan", floresan), ("BP_KirmiziLamba", kirmizilamba), ("BP_Incele", incele), ("BP_YatakhaneKapisi", yatakhanekapisi)):
    if SECIM is None or ad in SECIM: kur(ad, fn)
yaz("C:/Users/Onur/Sisli/Unreal/Scripts/mek_hepsi_out.txt")
