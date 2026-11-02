# RTG_UE4_Cocuk2 / RTG_Manny_Cocuk2 işlemleri (op) ve zincir ayarları — kamburluğun kaynağı
import unreal, traceback
OUT = []; eal = unreal.EditorAssetLibrary
try:
    for ad in ("RTG_UE4_Cocuk2", "RTG_Manny_Cocuk2"):
        r = eal.load_asset("/Game/Sisli/Cocuk2/" + ad); rc = unreal.IKRetargeterController.get_controller(r)
        OUT.append("== " + ad)
        OUT.append("metotlar: " + " ".join(m for m in dir(rc) if not m.startswith("_") and any(k in m for k in ("op", "Op", "chain", "pose", "setting", "enable"))))
        n = rc.get_num_retarget_ops(); OUT.append("op sayısı %d" % n)
        for i in range(n):
            info = []
            for f in ("get_op_name", "get_retarget_op_name", "get_op_type", "get_op_enabled", "get_retarget_op_enabled", "is_op_enabled"):
                if hasattr(rc, f):
                    try: info.append(f + "=" + str(getattr(rc, f)(i)))
                    except Exception as e: info.append(f + "!" + str(e)[:60])
            try:
                op = rc.get_retarget_op_at_index(i) if hasattr(rc, "get_retarget_op_at_index") else None
                if op: info.append("tip " + type(op).__name__)
            except Exception as e: info.append("at_index!" + str(e)[:60])
            OUT.append("  op %d: %s" % (i, " | ".join(info)))
        for poz_kaynak in (unreal.RetargetSourceOrTarget.SOURCE, unreal.RetargetSourceOrTarget.TARGET):
            try: OUT.append("  poz %s: %s" % (poz_kaynak, rc.get_current_retarget_pose_name(poz_kaynak)))
            except Exception as e: OUT.append("  poz!" + str(e)[:80])
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/rtg_incele_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
