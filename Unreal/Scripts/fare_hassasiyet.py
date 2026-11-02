# Fare bakış hassasiyeti: IMC_MouseLook'taki Mouse2D eşlemesine Scalar değiştiricisi (FARE_CARPAN, varsayılan 0.35).
# Var olan Scalar değiştirici varsa değeri güncellenir (tekrar çalıştırmak çarpanı katlamaz).
import unreal, os, traceback
OUT = []; eal = unreal.EditorAssetLibrary
K = float(os.environ.get("FARE_CARPAN", "0.35"))
try:
    imc = eal.load_asset("/Game/Input/IMC_MouseLook")
    dkm = imc.get_editor_property("default_key_mappings"); ms = list(dkm.get_editor_property("mappings"))
    for i, m in enumerate(ms):
        key = str(m.get_editor_property("key").get_editor_property("key_name"))
        mods = list(m.get_editor_property("modifiers"))
        OUT.append(f"önce {key}: " + ", ".join(md.get_class().get_name() + (f"({md.get_editor_property('scalar')})" if isinstance(md, unreal.InputModifierScalar) else "") for md in mods))
        if key != "Mouse2D": continue
        sc = next((md for md in mods if isinstance(md, unreal.InputModifierScalar)), None)
        if sc is None:
            sc = unreal.new_object(unreal.InputModifierScalar, outer=imc); mods.append(sc)
        sc.set_editor_property("scalar", unreal.Vector(K, K, 1.0))
        m.set_editor_property("modifiers", mods); ms[i] = m
        OUT.append(f"sonra {key}: scalar={sc.get_editor_property('scalar')}")
    dkm.set_editor_property("mappings", ms); imc.set_editor_property("default_key_mappings", dkm)
    OUT.append("kaydet " + str(eal.save_loaded_asset(imc, only_if_is_dirty=False)))
except Exception:
    OUT.append("HATA " + traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/fare_hassasiyet_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
