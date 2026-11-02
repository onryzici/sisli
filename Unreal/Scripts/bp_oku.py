import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
from mekanik_lib import *
import os
bp = eal.load_asset("/Game/Sisli/Mekanik/" + os.environ.get("BP_AD", "BP_Incele"))
log(BT.read_graph_dsl(BT.get_graph(bp, "EventGraph")))
yaz("C:/Users/Onur/Sisli/Unreal/Scripts/bp_oku_out.txt")
