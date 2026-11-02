import unreal
out = []
for m in ("add_get_member_variable_node", "add_set_member_variable_node", "create_node_from_name", "add_custom_event_node", "add_component_bound_event_node"):
    out.append(m + ": " + str(getattr(unreal.BlueprintGraphEditor, m).__doc__)[:600])
open("C:/Users/Onur/Sisli/Unreal/Scripts/kesif3_out.txt", "w").write("\n".join(out))
