# Ayak yüksekliği ölçümü: referans pozda ve her animasyonda ayak/parmak kemiklerinin bileşen uzayı Z'si
import unreal, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
eal = unreal.EditorAssetLibrary; APE = unreal.AnimPoseExtensions
try:
    sk = eal.load_asset("/Game/Sisli/Cocuk/SK_Cocuk"); skel = sk.get_editor_property("skeleton")
    b = sk.get_bounds(); log("mesh sınır", b.origin, b.box_extent, "minZ", b.origin.z - b.box_extent.z)
    ref = APE.get_reference_pose(skel)
    names = [str(n) for n in APE.get_bone_names(ref)]
    feet = [n for n in names if "foot" in n.lower() or "toe" in n.lower()]
    log("ayak kemikleri", feet)
    def z(pose, n): return APE.get_bone_pose(pose, n, unreal.AnimPoseSpaces.WORLD).translation.z
    log("ref", {n: round(z(ref, n), 1) for n in feet})
    opt = unreal.AnimPoseEvaluationOptions()
    for p in eal.list_assets("/Game/Sisli/Cocuk/Anim", recursive=True):
        a = eal.load_asset(p)
        if not isinstance(a, unreal.AnimSequence): continue
        nf = unreal.AnimationLibrary.get_num_frames(a)
        mins = {n: 1e9 for n in feet}
        for fr in range(0, nf + 1, max(1, nf // 24)):
            pose = APE.get_anim_pose_at_frame(a, fr, opt)
            for n in feet: mins[n] = min(mins[n], z(pose, n))
        log(a.get_name(), "kare", nf, "min", {n: round(v, 1) for n, v in mins.items()})
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/olc_ayak_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
