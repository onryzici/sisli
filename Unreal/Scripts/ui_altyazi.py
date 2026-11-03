# Altyazı arayüzü (kullanıcı: "altyazı fontu çok kötü"; seçim: Lato): motorun kaba gölgeli altyazısı yerine UMG.
# WBP_Altyazi: alt ortada yumuşak koyu hale (T_AltyaziHale) + Lato 24 ıtık beyaz metin + hafif gölge; Goster(Metin, Sure): belirir, Sure sonra söner.
# Çağıranlar (BP_Giris/Oyuncak/Incele/YatakhaneKapisi): mek_hepsi.soyle() widget'ı bulur (GetAllWidgetsOfClass) ve ToolTipText alanına yazar ("gelen kutusu";
# BP sınıfının kendi fonksiyonları başsız modda eylem veritabanında çıkmıyor). Widget her karede okur, gösterir, temizler; süre metin uzunluğundan.
import sys; sys.path.append("C:/Users/Onur/Sisli/Unreal/Scripts")
from mekanik_lib import *
import unreal, json, traceback
TR = unreal.ToolsetRegistry; TS = "UMGToolSet.UMGToolSet"; P = "/Game/Uyanis/UI"
def arac(tool, **kw):
    r = TR.execute_tool(TS, tool, json.dumps(kw))
    if r.error: raise RuntimeError(f"{tool}: {r.error}")
    s = r.get_value_as_json_string(); v = json.loads(s) if s else {}
    if isinstance(v, str): v = json.loads(v)
    return v.get("returnValue") if isinstance(v, dict) else v
def ref(o): return {"refPath": o if isinstance(o, str) else o.get_path_name()}
def nesne(r):
    p = r if isinstance(r, str) else (r or {}).get("refPath")
    return unreal.load_object(None, p) if p and p not in ("None", "") else None
def ekle(wbp, sinif, ad, ebeveyn=None):
    kw = dict(widgetBlueprint=ref(wbp), widgetClass={"refPath": f"/Script/UMG.{sinif}"}, widgetDisplayName=ad)
    if ebeveyn is not None: kw["parentWidget"] = ref(ebeveyn)
    i = arac("AddWidget", **kw); return nesne(i.get("widget")), nesne(i.get("slot"))
def tuval(slot, anchor, hiza, poz, boyut, otomatik=False):
    slot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(*anchor[:2]), maximum=unreal.Vector2D(*anchor[2:])))
    slot.set_alignment(unreal.Vector2D(*hiza)); slot.set_position(unreal.Vector2D(*poz)); slot.set_size(unreal.Vector2D(*boyut)); slot.set_auto_size(otomatik)
try:
    yol = f"{P}/WBP_Altyazi"
    if eal.does_asset_exist(yol): log("sil", eal.delete_asset(yol))
    wbp = nesne(arac("CreateWidgetBlueprint", folderPath=P, assetName="WBP_Altyazi", parentClass={"refPath": "/Script/UMG.UserWidget"}))
    kok, _ = ekle(wbp, "CanvasPanel", "Kok")
    ha, s = ekle(wbp, "Image", "Hale", kok); tuval(s, (0.5, 1, 0.5, 1), (0.5, 0.5), (0, -92), (1800, 240))   # metnin arkasında ortalı, kenarsız
    br = unreal.SlateBrush(); br.set_editor_property("resource_object", eal.load_asset(f"{P}/T_AltyaziHale")); ha.set_editor_property("brush", br)
    ha.set_color_and_opacity(unreal.LinearColor(0, 0, 0, 0.42))
    yz, s = ekle(wbp, "TextBlock", "Yazi", kok); tuval(s, (0.5, 1, 0.5, 1), (0.5, 1), (0, -70), (0, 0), True)
    f = unreal.SlateFontInfo(); f.set_editor_property("font_object", eal.load_asset(f"{P}/Font/FF_Lato_Regular_Font")); f.set_editor_property("typeface_font_name", "Default")
    f.set_editor_property("size", 24); f.set_editor_property("letter_spacing", 20); yz.set_editor_property("font", f)
    c = unreal.SlateColor(); c.set_editor_property("specified_color", unreal.LinearColor(0.93, 0.915, 0.88, 0.95)); yz.set_color_and_opacity(c)
    yz.set_shadow_offset(unreal.Vector2D(0, 1.5)); yz.set_shadow_color_and_opacity(unreal.LinearColor(0, 0, 0, 0.55))
    # otomatik sarma + autosize slot = kelime başına satır → sabit 1100 px sarma
    yz.set_auto_wrap_text(False); yz.set_editor_property("wrap_text_at", 1100.0); yz.set_editor_property("justification", unreal.TextJustify.CENTER); yz.set_text("")
    arac("ToggleWidgetAsVariable", widgetBlueprint=ref(wbp), widget=ref(yz), bIsVariable=True)
    log("derleme1", arac("CompileWidgetBlueprint", widgetBlueprint=ref(wbp)))
    for n, d in (("Kalan", 0.0), ("Alfa", 0.0), ("Hedef", 0.0)): degisken(wbp, n, "float", d, False)
    degisken(wbp, "Ham", "string", "", False)   # son gelen "EN~~TR" satır (dil değişince yeniden seçilir)
    eg = BT.get_graph(wbp, "EventGraph")
    def tur(ad, on=None):
        c_ = BT.find_node_types(eg, ad); tam = [x for x in c_ if x.split("|")[-1].lower() == ad.lower()]
        if on: tam = [x for x in tam if x.startswith(on)] or tam
        r = (tam or c_ or [None])[0]; log("tür", ad, "→", r); return r
    T = {"SetText": tur("SetText(Text)", "Widget") or tur("SetText"), "SetRenderOpacity": tur("SetRenderOpacity", "Widget"), "FInterpTo": tur("FInterpTo"), "Min(Float)": tur("Min(Float)")}
    fg = BT.add_function_graph(wbp, "Goster"); BT.add_function_param(fg, "Metin", "text", True); BT.add_function_param(fg, "Sure", "float", True)
    dsl(wbp, f'''
(fn Goster (Metin Sure)
  ({T["SetText"]} :self (Uye|Get|Yazi) :InText Metin)
  (Uye|Set|Kalan Sure)
  (Uye|Set|Hedef 1.0))
''', graph="Goster")
    dsl(wbp, f'''
(event UserInterface|EventConstruct
  ({T["SetRenderOpacity"]} :self self :InOpacity 0.0)
  (Widget|SetVisibility :self self :InVisibility "HitTestInvisible"))

(event UserInterface|EventTick (MyGeometry InDeltaTime)
  ; dil: L tuşu Unreal kültürünü en <-> tr çevirir (ayara kaydedilir, katlar arası korunur)
  (bind kultur (Utilities|Internationalization|GetCurrentCulture))
  (bind tr (Utilities|String|StartsWith kultur "tr"))
  (if (Game|Player|WasInputKeyJustPressed :self (Widget|GetOwningPlayer) :Key "L")
    (Utilities|Internationalization|SetCurrentCulture :Culture (select tr "en" "tr") :SaveToConfig true))
  ; gelen kutusu (ToolTipText): "EN~~TR" ham metin → Ham'a alınır, süre uzunluktan (okuma ~12 karakter/sn + 2.8 sn, 3.2..12 sn)
  (bind gelen (Variables|Behavior|GetToolTipText))
  (bind gs (Utilities|String|ToString(Text) gelen))
  (bind uz (Utilities|String|Len gs))
  (if (> uz 0)
    (Uye|Set|Ham gs)
    (Widget|SetToolTipText :self self :InToolTipText (Utilities|Text|ToText(String) ""))
    (Uye|Set|Kalan (Math|Float|Max(Float) 3.2 ({T["Min(Float)"]} 12.0 (+ 2.8 (* 0.0425 uz)))))
    (Uye|Set|Hedef 1.0))
  (bind (en trm bol) (Utilities|String|Split (Uye|Get|Ham) "~~"))
  ({T["SetText"]} :self (Uye|Get|Yazi) :InText (Utilities|Text|ToText(String) (select bol (select tr trm en) (Uye|Get|Ham))))
  (Uye|Set|Kalan (- (Uye|Get|Kalan) InDeltaTime))
  (if (<= (Uye|Get|Kalan) 0.0)
    (Uye|Set|Hedef 0.0))
  (Uye|Set|Alfa ({T["FInterpTo"]} (Uye|Get|Alfa) (Uye|Get|Hedef) InDeltaTime 4.0))
  ({T["SetRenderOpacity"]} :self self :InOpacity (Uye|Get|Alfa)))
''')
    log("derleme2", arac("CompileWidgetBlueprint", widgetBlueprint=ref(wbp))); eal.save_loaded_asset(wbp, only_if_is_dirty=False)
    # çağıran tarafta düğüm adları (BP_Giris grafiği bağlamında)
    g2 = BT.get_graph(eal.load_asset("/Game/Sisli/Mekanik/BP_Giris"), "EventGraph")
    for ad in ("GetAllWidgetsofClass", "Length", "Get(acopy)", "Get(aref)", "CastToWBP_Altyazi", "Goster", "IsValid"):
        log("çağıran türü", ad, BT.find_node_types(g2, ad)[:8])
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
yaz("C:/Users/Onur/Sisli/Unreal/Scripts/ui_altyazi_out.txt")
