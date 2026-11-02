import unreal
OUT = []
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.load_level("/Game/Uyanis/Maps/L_Uyanis")
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    n = a.get_actor_label()
    if n.startswith(("Incele_", "YatakhaneKapisi", "TestYuru", "Bak_Anahtar")):
        comps = [(c.get_name(), str(c.get_world_location()) if hasattr(c, "get_world_location") else "-") for c in a.get_components_by_class(unreal.SceneComponent)]
        r = a.root_component.get_name() if a.root_component else None
        vals = {}
        for k in ("Yaricap", "TestOto", "Al", "Satir1", "AlinanAktor", "Anahtar", "Son", "H4"):
            try: vals[k] = str(a.get_editor_property(k))[:60]
            except Exception: pass
        OUT.append(f"{n} | {vals}")
open("C:/Users/Onur/Sisli/Unreal/Scripts/seviye_oku_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
