import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
from mekanik_lib import *
bp = yeni_bp("BP_DugumAra"); g = BT.get_graph(bp, "EventGraph")
for f in ("IsFalling", "GetCharacterMovement", "GetMovementComponent", "RandomFloatinRange", "Min(Float)", "Abs(Float)", "GetPlayLength", "SetPlayRate", "GetPosition", "IsPlaying"):
    try: log(f, "→", [str(t) for t in BT.find_node_types(g, f)][:8])
    except Exception as e: log(f, "HATA", str(e)[:100])
eal.delete_asset("/Game/Sisli/Mekanik/BP_DugumAra")
yaz("C:/Users/Onur/Sisli/Unreal/Scripts/dugum_ara_out.txt")
