import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
from mekanik_lib import *
bp = eal.load_asset(DIR + "/BP_Titrek"); g = BT.get_graph(bp, "EventGraph")
for t in ["Components|MoveComponentTo", "CameraFades|StartCameraFade", "Collision|LineTraceByChannel", "Transformation|SetActorLocation", "Game|OpenLevel(byName)",
          "Audio|PlaySound2D", "Audio|PlaySoundatLocation", "Math|Rotator|FindLookatRotation", "Math|Color|Lerp(LinearColor)", "Rendering|Components|Light|SetLightColor",
          "Utilities|FlowControl|Delay", "Rendering|ToggleVisibility", "Input|KeyboardEvents|F", "Math|Rotator|MakeRotator", "Math|Trig|Sin(Radians)", "Utilities|IsValid",
          "Transformation|SetWorldRotation", "Math|Vector|DotProduct", "Actor|DestroyActor", "Game|GetPlayerCameraManager", "Utilities|FlowControl|DoOnce", "Math|Rotator|BreakRotator",
          "Transformation|GetWorldLocation", "Game|GetPlayerCharacter"]:
    try:
        ni = BT.get_node_type_pins(g, t)
        log(t, "| IN:", [p.name for p in ni.input_pins] if hasattr(ni, "input_pins") else ni)
        if hasattr(ni, "output_pins"): log("    OUT:", [p.name for p in ni.output_pins])
    except Exception as e:
        log(t, "HATA", str(e)[-200:])
yaz("C:/Users/Onur/Sisli/Unreal/Scripts/pinler_out.txt")
