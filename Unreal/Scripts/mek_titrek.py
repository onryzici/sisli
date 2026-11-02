# BP_Titrek: titreyen ışık (sokak lambası / asılı ampul)
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
from mekanik_lib import *
try:
    bp = yeni_bp("BP_Titrek")
    bilesen(bp, unreal.PointLightComponent, "Isik", intensity_units=unreal.LightUnits.CANDELAS, intensity=20.0,
            attenuation_radius=900.0, light_color=unreal.Color(r=255, g=214, b=160, a=255), source_radius=4.0, volumetric_scattering_intensity=3.0)
    degisken(bp, "TemelSiddet", "float", 20.0)
    degisken(bp, "Sans", "float", 0.04)
    degisken(bp, "Karanlik", "float", 0.0, False)
    dsl(bp, '''
(event EventTick (DeltaSeconds)
  (bind k (Uye|Get|Karanlik))
  (bind temel (Uye|Get|TemelSiddet))
  (bind isik (Uye|Get|Isik))
  (if (> k 0.0)
    (Uye|Set|Karanlik (- k DeltaSeconds))
    (Rendering|Components|Light|SetIntensity :self isik :NewIntensity (* temel (Math|Random|RandomFloatinRange 0.02 0.25)))
    (else
      (if (< (Math|Random|RandomFloatinRange 0.0 1.0) (Uye|Get|Sans))
        (Uye|Set|Karanlik (Math|Random|RandomFloatinRange 0.04 0.35))
        (else
          (Rendering|Components|Light|SetIntensity :self isik :NewIntensity (* temel (Math|Random|RandomFloatinRange 0.92 1.0))))))))
''')
    derle_kaydet(bp)
    log(BT.read_graph_dsl(BT.get_graph(bp, "EventGraph")))
except Exception:
    log("HATA", traceback.format_exc()[-1500:])
yaz("C:/Users/Onur/Sisli/Unreal/Scripts/mek_titrek_out.txt")
