# ABP_Cocuk: karışımlı hareket. AnimGraph: BlendspacePlayer(BS_Cocuk2_Hareket2; X=BsX, Y=BsY) → Slot(DefaultSlot) → Çıktı.
# EventGraph (her kare): hız + çömelme yumuşatılıp BsX/BsY hesaplanır. Zıplama/düşme/iniş BP_Fener'den Slot montajı (giriş/çıkış karışımlı).
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
from mekanik_lib import *
import unreal, traceback
P = "/Game/Sisli/Cocuk2/Anim"; AD = "ABP_Cocuk"
def pin(node, ad, yon="in"):
    ni = BT._get_node_info(node)
    for p in (ni.input_pins if yon == "in" else ni.output_pins):
        if str(p.name) == ad: return p.pin_id
    raise RuntimeError(f"pin yok {ad} / {[str(p.name) for p in ni.input_pins]} → {[str(p.name) for p in ni.output_pins]}")
def pinler(node):
    ni = BT._get_node_info(node); return [str(p.name) for p in ni.input_pins], [str(p.name) for p in ni.output_pins]
try:
    for eski in (f"{P}/ABP_Kesif", f"{P}/{AD}"):
        if eal.does_asset_exist(eski): log("sil", eski, eal.delete_asset(eski))
    f = unreal.AnimBlueprintFactory(); f.set_editor_property("target_skeleton", eal.load_asset("/Game/Characters/Mannequin_UE4/Meshes/SK_Mannequin_Skeleton"))
    f.set_editor_property("parent_class", unreal.AnimInstance)
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(AD, P, unreal.AnimBlueprint, f)
    for n in ("BsX", "BsY", "HizY", "ComelA"): degisken(bp, n, "float", 0.0, False)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    cdo = unreal.get_default_object(bp.generated_class()); cdo.set_editor_property("BsX", 45.0)
    ag = BT.get_graph(bp, "AnimGraph")
    anim_tur = sorted(set(t for t in BT.find_node_types(ag, "Animation|") if "'" not in t))
    log("Animation| türleri", len(anim_tur), [t for t in anim_tur if any(k in t.lower() for k in ("slot", "inertial", "blendposes", "blend poses", "output"))])
    slot_t = [t for t in BT.find_node_types(ag, "slot") if t.startswith("Animation") and "'" in t]
    log("slot adayları", slot_t)
    bs = BT.create_node(ag, "Animation|BlendSpaces|BlendspacePlayer'BS_Cocuk2_Hareket2'", unreal.IntPoint(-500, 0))
    sl = BT.create_node(ag, slot_t[0], unreal.IntPoint(-150, 0))
    kok = [n for n in BT.find_nodes(ag) if "Root" in n.get_class().get_name()][0] if not isinstance(BT.find_nodes(ag)[0], str) else None
    log("pinler bs", pinler(bs)); log("pinler slot", pinler(sl))
    kok = kok or [n for n in unreal.BlueprintGraphEditor.get_graph_editor(ag).get_nodes() if "Root" in n.get_class().get_name()][0]
    log("pinler kök", pinler(kok))
    bs_out = BT._get_node_info(bs).output_pins[0].pin_id; sl_in = [p.pin_id for p in BT._get_node_info(sl).input_pins if "Pose" in str(p.type_id) or str(p.name) == "Source"][0]
    BT.connect_pins(bs_out, sl_in)
    BT.connect_pins(BT._get_node_info(sl).output_pins[0].pin_id, BT._get_node_info(kok).input_pins[0].pin_id)
    ed = unreal.BlueprintGraphEditor.get_graph_editor(ag)
    for i, (v, p) in enumerate((("BsX", "X"), ("BsY", "Y"))):
        g = ed.add_get_member_variable_node(unreal.Name(v)); g.set_node_pos(unreal.IntPoint(-800, 120 + 60 * i))
        BT.connect_pins(BT._get_node_info(g).output_pins[0].pin_id, pin(bs, p))
    log("AnimGraph bağlandı")
    # olay grafiği
    dsl(bp, '''
(event EventBlueprintUpdateAnimation (DeltaTimeX)
  (bind ch (Utilities|Casting|CastToCharacter :Object (Animation|TryGetPawnOwner))
    (:then
      (bind v (Transformation|GetVelocity ch))
      (bind hiz (Math|Vector|VectorLength (Math|Vector|MakeVector (.x v) (.y v) 0.0)))
      (Uye|Set|HizY (Math|Interpolation|FInterpTo (Uye|Get|HizY) hiz DeltaTimeX 8.0))
      (bind cr (Movement|IsCrouching :self (Class|Character|GetCharacterMovement :self ch)))
      (Uye|Set|ComelA (Math|Interpolation|FInterpTo (Uye|Get|ComelA) (select cr 1.0 0.0) DeltaTimeX 5.0))
      (Uye|Set|BsX (+ 45.0 (* 45.0 (Uye|Get|ComelA))))
      (bind ys (select (<= (Uye|Get|HizY) 100.0) (* (Uye|Get|HizY) 3.0) (+ 300.0 (* (- (Uye|Get|HizY) 100.0) 1.807))))
      (Uye|Set|BsY (+ ys (* (- (* (Uye|Get|HizY) 6.0) ys) (Uye|Get|ComelA)))))
    (:CastFailed)))
''')
    derle_kaydet(bp)
    # BP_Fener için düğüm adları
    eg = BT.get_graph(bp, "EventGraph")
    for flt in ("SetAnimInstanceClass", "DynamicMontage", "StopSlotAnimation", "IsCrouching", "Montage_IsPlaying", "IsAnySlot", "IsPlayingSlotAnimation"):
        log("tür", flt, BT.find_node_types(eg, flt)[:8])
except Exception:
    log("HATA", traceback.format_exc())
yaz("C:/Users/Onur/Sisli/Unreal/Scripts/abp_kur_out.txt")
