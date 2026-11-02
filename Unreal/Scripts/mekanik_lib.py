# Sisli mekanik yardımcıları: BP oluştur/yeniden kur, bileşen, değişken, DSL yaz, derle
import unreal, traceback
from editor_toolset.toolsets.blueprint import BlueprintTools as BT
from editor_toolset.toolsets.actor import ActorTools as AT
from toolset_registry.tool_call_impl import tool_raising_exceptions
_ctx = tool_raising_exceptions(); _ctx.__enter__()
eal = unreal.EditorAssetLibrary
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
DIR = "/Game/Sisli/Mekanik"

def yeni_bp(name, parent=unreal.Actor):
    path = f"{DIR}/{name}"
    if eal.does_asset_exist(path):
        if not eal.delete_asset(path):
            raise RuntimeError("silinemedi " + path)
    return BT.create(DIR, name, parent.static_class())

def bilesen(bp, cls, name, parent=None, **props):
    c = AT.add_component(parent if parent is not None else bp, cls.static_class(), name)
    for k, v in props.items():
        c.set_editor_property(k, v)
    return c

def degisken(bp, name, tip, varsayilan=None, duzenlenebilir=True):
    if isinstance(tip, str): BT.add_variable(bp, name, tip)
    else: BT.add_object_variable(bp, name, tip.static_class())
    if duzenlenebilir: BT.set_variable_instance_editable(bp, name, True)
    if varsayilan is not None:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        cdo = unreal.get_default_object(bp.generated_class())
        cdo.set_editor_property(name, varsayilan)

from editor_toolset.toolsets import blueprint_dsl
def _create(g, type_id, pos, declaring_class=None):
    # Uye|Get|Ad  /  Uye|Set|Ad  →  üye değişken (bileşenler dahil) düğümü (başsız modda eylem veritabanında yoklar)
    if type_id.startswith("Uye|"):
        parts = type_id.split("|"); kind, name = parts[1], parts[2]
        ed = unreal.BlueprintGraphEditor.get_graph_editor(g)
        node = ed.add_get_member_variable_node(unreal.Name(name)) if kind == "Get" else ed.add_set_member_variable_node(unreal.Name(name))
        assert node, "değişken düğümü oluşmadı: " + type_id
        node.set_node_pos(pos); return node
    return BT.create_node(g, type_id, pos, declaring_class) if declaring_class else BT.create_node(g, type_id, pos)
def dsl(bp, code, graph="EventGraph"):
    g = BT.get_graph(bp, graph)
    blueprint_dsl.Transpiler(g, _create, BT.connect_pins, BT._get_node_info, BT.set_pin_value, lambda gg: BT.find_nodes(gg),
                             delete_node_fn=BT.delete_node, find_node_types_fn=lambda f: BT.find_node_types(g, f)).transpile(code)
    BT.compile_blueprint(bp)
    return g

def derle_kaydet(bp):
    BT.compile_blueprint(bp)
    eal.save_loaded_asset(bp)
    log("TAMAM", bp.get_name())

def yaz(path):
    open(path, "w", encoding="utf-8").write("\n".join(OUT))
