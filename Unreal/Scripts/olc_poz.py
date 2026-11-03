# Duruş ölçümü (bileşen uzayı, GERÇEK mesh oranlarıyla): kaynak MCO manken ↔ çocuk mesh; bağlama pozu + idle.
# Yüz +Y (UE4 iskeleti). "ön" = +Y'ye yatma, "yan" = X'e yatma (dikeyden derece).
import unreal, math, traceback
OUT = []; eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions
def log(*a): OUT.append(" ".join(str(x) for x in a))
W = unreal.AnimPoseSpaces.WORLD
def yon(v):
    n = v.normal(); asagi = math.degrees(math.acos(max(-1, min(1, -n.z))))
    return "aşağıdan %5.1f° ön %+5.2f yan %+5.2f" % (asagi, n.y, n.x)
def egim(v):
    n = v.normal(); return "ön %+5.1f° yan %+5.1f°" % (math.degrees(math.atan2(n.y, n.z)), math.degrees(math.atan2(n.x, n.z)))
def rapor(ad, bp):
    log("== " + ad)
    log("  gövde pelvis→neck  ", egim(bp("neck_01") - bp("pelvis")))
    log("  alt gövde pel→sp2  ", egim(bp("spine_02") - bp("pelvis")))
    log("  üst gövde sp2→neck ", egim(bp("neck_01") - bp("spine_02")))
    log("  boyun→kafa         ", egim(bp("head") - bp("neck_01")))
    for s in ("l", "r"):
        log("  kol %s üst          " % s, yon(bp("lowerarm_" + s) - bp("upperarm_" + s)))
        log("  kol %s alt          " % s, yon(bp("hand_" + s) - bp("lowerarm_" + s)))
    ayak = (bp("foot_l") + bp("foot_r")) * 0.5; pel = bp("pelvis"); hl = bp("hand_l"); tl = bp("thigh_l")
    log("  pelvis−ayak (cm) x %+.1f y %+.1f z %.1f | el_l−uyluk_l (cm) x %+.1f y %+.1f z %+.1f" % (pel.x - ayak.x, pel.y - ayak.y, pel.z - ayak.z, hl.x - tl.x, hl.y - tl.y, hl.z - tl.z))
def poz_an(an, t, mesh):
    o = unreal.AnimPoseEvaluationOptions(); o.set_editor_property("optional_skeletal_mesh", mesh)
    pose = APE.get_anim_pose_at_time(an, t, o)
    return lambda b: APE.get_bone_pose(pose, b, W).translation
try:
    M_SRC = eal.load_asset("/Game/MCO_Mocap_Basics/Character/Mesh/SK_Mannequin"); M_DST = eal.load_asset("/Game/child_test_2/mesh/unreal_file")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for ad, ms in (("KAYNAK mesh bağlama", M_SRC), ("ÇOCUK mesh bağlama", M_DST)):
        try:
            a_ = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -5000))
            c_ = a_.get_editor_property("skeletal_mesh_component"); c_.set_skeletal_mesh_asset(ms)
            def bp(b, c_=c_): return c_.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_COMPONENT).translation
            rapor(ad, bp)
            for b_ in ("pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head", "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l"):
                tr = c_.get_socket_transform(b_, unreal.RelativeTransformSpace.RTS_COMPONENT); r_ = tr.rotation.rotator()
                log("   ", b_, "konum", [round(v, 1) for v in (tr.translation.x, tr.translation.y, tr.translation.z)], "dönüş p/y/r", round(r_.pitch, 1), round(r_.yaw, 1), round(r_.roll, 1))
            a_.destroy_actor()
        except Exception:
            log("bağlama HATA", traceback.format_exc())
    MCO = "/Game/MCO_Mocap_Basics/Animation/Mobility_Pro/In_Place/"; C3 = "/Game/Sisli/Cocuk2/Anim/MCO3/"
    n = "MOB1_Stand_Relaxed_Idle_v2_IPC"; a = eal.load_asset(MCO + n); b = eal.load_asset(C3 + n + "_C3")
    for t in (0.0, a.get_play_length() * 0.5):
        rapor("KAYNAK idle t=%.2f (manken mesh)" % t, poz_an(a, t, M_SRC))
        rapor("ÇOCUK idle_C3 t=%.2f (çocuk mesh)" % t, poz_an(b, t, M_DST))
        rapor("DOĞRUDAN kaynak idle çocuk mesh t=%.2f" % t, poz_an(a, t, M_DST))
    # MCO paketindeki diğer bekleme animasyonları
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    idl = sorted(str(x.package_name) for x in ar.get_assets_by_path("/Game/MCO_Mocap_Basics/Animation", recursive=True) if "Idle" in str(x.asset_name) or "Stand" in str(x.asset_name))
    log("MCO idle listesi", idl)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/olc_poz_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
