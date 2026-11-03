# İnceleme arayüzü (kullanıcı referansı: "HYPER Inspection System"): tam ekran bulanık arka plan + ortada kâğıt + altta ipuçları + F ile okuma paneli.
# WBP_Incele_Sablon (mantık: sürükle=kaydır, tekerlek=yakınlaştır, R=sıfırla, F=oku) → kâğıt başına kopya: doku/boyut/başlık/metin işlenir.
# Widget ağacı UMGToolSet ile (ToolsetRegistry.execute_tool, JSON; nesneler {"refPath"}), özellikler doğrudan Python'dan. Açma/kapama BP_Incele'de (E).
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
FONT = lambda yuz: eal.load_asset(f"{P}/Font/FF_Lato_{'Italic' if yuz == 'Italic' else 'Regular'}_Font")   # kullanıcı Garamond'u beğenmedi → Lato
def fnt(yuz, boy, harf=0):
    f = unreal.SlateFontInfo(); f.set_editor_property("font_object", FONT(yuz)); f.set_editor_property("typeface_font_name", "Default"); f.set_editor_property("size", boy)
    try: f.set_editor_property("letter_spacing", harf)
    except Exception: pass
    return f
def renk(r, g, b, a=1.0): s = unreal.SlateColor(); s.set_editor_property("specified_color", unreal.LinearColor(r, g, b, a)); return s
import sys as _s; _s.path.append("C:/Users/Onur/Sisli/Unreal/Scripts"); from metinler import ikili
# iki dilli (EN~~TR): widget her karede Unreal kültürüne göre seçer (L tuşu: WBP_Altyazi)
KAGITLAR = {
    "Kurallar": {"doku": "/Game/Uyanis/Kagit/T_Kurallar", "boyut": (540, 764),
                 "baslik": ikili("HOUSE RULES", "YATAKHANE KURALLARI"),
                 "ic": ikili("Typed. Stamped. Pinned above our beds.", "Daktiloyla yazılmış. Mühürlü. Yataklarımızın üstüne asılı."),
                 "metin": ikili("DORMITORY 4 — HOUSE RULES\n\n1. Lights go out at 21:00.\n2. All children in bed for night count.\n3. No talking in the dormitory.\n"
                                "4. No child leaves through the door without a caretaker.\n5. Siblings sleep in separate bunks.\n6. A child who breaks the rules will be separated.\n\n— The Directorate",
                                "4. YATAKHANE — KURALLAR\n\n1. Işıklar 21.00'de söner.\n2. Gece sayımında her çocuk yatağındadır.\n3. Yatakhanede konuşmak yasaktır.\n"
                                "4. Hiçbir çocuk bakıcı olmadan kapıdan çıkamaz.\n5. Kardeşler ayrı ranzalarda yatar.\n6. Kuralı çiğneyen çocuk ayrılır.\n\n— Müdürlük")},
    "ElaCizim": {"doku": "/Game/Uyanis/Kagit/T_ElaCizim", "boyut": (980, 693),
                 "baslik": ikili("ELA'S DRAWING", "ELA'NIN ÇİZİMİ"),
                 "ic": ikili("Pastels. She pressed so hard the paper tore.", "Pastel boya. O kadar bastırmış ki kâğıt yırtılmış."),
                 "metin": ikili("“ME AND MY BROTHER”\n\nTwo figures holding hands.\nBeside them, a tall tower with a red light on top.",
                                "“BEN VE ABİM”\n\nEl ele tutuşan iki figür.\nYanlarında, tepesinde kırmızı ışık yanan uzun bir kule.")},
}
IPUCU = ikili("DRAG  ·  pan          SCROLL  ·  zoom          R  ·  reset          F  ·  read          E  ·  back",
              "SÜRÜKLE  ·  kaydır          TEKERLEK  ·  yakınlaştır          R  ·  sıfırla          F  ·  oku          E  ·  geri")
def ekle(wbp, sinif, ad, ebeveyn=None):
    kw = dict(widgetBlueprint=ref(wbp), widgetClass={"refPath": f"/Script/UMG.{sinif}"}, widgetDisplayName=ad)
    if ebeveyn is not None: kw["parentWidget"] = ref(ebeveyn)
    i = arac("AddWidget", **kw); return nesne(i.get("widget")), nesne(i.get("slot"))
def tuval(slot, anchor, hiza, poz, boyut, otomatik=False):
    slot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(*anchor[:2]), maximum=unreal.Vector2D(*anchor[2:])))
    slot.set_alignment(unreal.Vector2D(*hiza)); slot.set_position(unreal.Vector2D(*poz)); slot.set_size(unreal.Vector2D(*boyut)); slot.set_auto_size(otomatik)
def agac(wbp): return {str(x["widgetName"]): x for x in arac("GetWidgets", widgetBlueprint=ref(wbp))["widgets"]}
try:
    for ad in [f"WBP_Incele_{k}" for k in KAGITLAR] + ["WBP_Incele_Sablon"]:
        if eal.does_asset_exist(f"{P}/{ad}"): log("sil", ad, eal.delete_asset(f"{P}/{ad}"))
    unreal.SystemLibrary.collect_garbage()
    wbp = nesne(arac("CreateWidgetBlueprint", folderPath=P, assetName="WBP_Incele_Sablon", parentClass={"refPath": "/Script/UMG.UserWidget"}))
    log("wbp", wbp)
    kok, _ = ekle(wbp, "CanvasPanel", "Kok")
    bb, s = ekle(wbp, "BackgroundBlur", "Bulanik", kok); tuval(s, (0, 0, 1, 1), (0, 0), (0, 0), (0, 0)); bb.set_blur_strength(9.0)
    kr, s = ekle(wbp, "Image", "Karart", kok); tuval(s, (0, 0, 1, 1), (0, 0), (0, 0), (0, 0)); kr.set_color_and_opacity(unreal.LinearColor(0.01, 0.012, 0.015, 0.55))
    kg, s = ekle(wbp, "Image", "Kagit", kok); tuval(s, (0.5, 0.5, 0.5, 0.5), (0.5, 0.5), (0, 10), (540, 764))
    bs, s = ekle(wbp, "TextBlock", "Baslik", kok); tuval(s, (0, 0, 0, 0), (0, 0), (80, 44), (0, 0), True)
    bs.set_editor_property("font", fnt("Regular", 24, 320)); bs.set_color_and_opacity(renk(0.92, 0.88, 0.80, 0.95)); bs.set_text("TITLE")
    ic, s = ekle(wbp, "TextBlock", "Ic", kok); tuval(s, (0, 0, 0, 0), (0, 0), (82, 88), (0, 0), True)
    ic.set_editor_property("font", fnt("Italic", 19)); ic.set_color_and_opacity(renk(0.85, 0.82, 0.76, 0.75)); ic.set_text("inner voice")
    ip, s = ekle(wbp, "TextBlock", "Ipucu", kok); tuval(s, (0.5, 1, 0.5, 1), (0.5, 1), (0, -42), (0, 0), True)
    ip.set_editor_property("font", fnt("Regular", 15, 160)); ip.set_color_and_opacity(renk(0.9, 0.87, 0.8, 0.7))
    ip.set_text("DRAG  ·  pan          SCROLL  ·  zoom          R  ·  reset          F  ·  read          E  ·  back")
    op, s = ekle(wbp, "Border", "OkuPanel", kok); tuval(s, (0.5, 0.5, 0.5, 0.5), (0.5, 0.5), (0, -20), (900, 640))
    op.set_brush_color(unreal.LinearColor(0.0, 0.0, 0.0, 0.78)); op.set_padding(unreal.Margin(60, 50, 60, 50))
    op.set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_FILL); op.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
    om, _ = ekle(wbp, "TextBlock", "OkuMetin", op)
    om.set_editor_property("font", fnt("Regular", 22, 20)); om.set_color_and_opacity(renk(0.93, 0.9, 0.84, 1.0)); om.set_auto_wrap_text(True); om.set_text("transcript")
    try: om.set_editor_property("justification", unreal.TextJustify.CENTER)
    except Exception as e: log("justify", e)
    for w in (kg, op, bs, ic, om, ip): arac("ToggleWidgetAsVariable", widgetBlueprint=ref(wbp), widget=ref(w), bIsVariable=True)
    log("ağaç", list(agac(wbp).keys()))
    log("derleme1", arac("CompileWidgetBlueprint", widgetBlueprint=ref(wbp)))
    for n, d in (("Zoom", 1.0), ("ZoomG", 1.0), ("PanX", 0.0), ("PanY", 0.0), ("PanGX", 0.0), ("PanGY", 0.0)): degisken(wbp, n, "float", d, False)
    degisken(wbp, "Oku", "bool", False, False)
    for n in ("BaslikHam", "IcHam", "OkuHam"): degisken(wbp, n, "string", "", False)   # "EN~~TR"; kâğıt kopyasında CDO'ya yazılır
    degisken(wbp, "IpucuHam", "string", IPUCU, False)
    eg = BT.get_graph(wbp, "EventGraph")
    def tur(ad):
        c = BT.find_node_types(eg, ad); tam = [x for x in c if x.split("|")[-1].lower() == ad.lower()]; wid = [x for x in tam if x.startswith("Widget|")]
        r = (wid or tam or c or [None])[0]; log("tür", ad, "→", r, c[:6]); return r
    T = {k: tur(k) for k in ("GetOwningPlayer", "IsInputKeyDown", "WasInputKeyJustPressed", "GetInputAnalogKeyState", "SetRenderScale", "SetRenderTranslation",
                             "SetVisibility", "MakeVector2D", "Min(Float)", "Max(Float)", "FInterpTo")}
    log("olay türleri", BT.find_node_types(eg, "AddEvent|")[:40])
    def tus(k): return f'({T["WasInputKeyJustPressed"]} :self pc :Key "{k}")'
    gor = lambda v: f'({T["SetVisibility"]} :self (Uye|Get|OkuPanel) :InVisibility "{v}")'
    def dil(w, ham):
        return (f'(bind ({w}_en {w}_tr {w}_ok) (Utilities|String|Split (Uye|Get|{ham}) "~~"))\n'
                f'  (Widget|SetText(Text) :self (Uye|Get|{w}) :InText (Utilities|Text|ToText(String) (select {w}_ok (select tr {w}_tr {w}_en) (Uye|Get|{ham}))))')
    dsl(wbp, f'''
(event UserInterface|EventConstruct
  {gor("Collapsed")})

(event UserInterface|EventTick (MyGeometry InDeltaTime)
  (bind pc ({T["GetOwningPlayer"]}))
  (if ({T["IsInputKeyDown"]} :self pc :Key "LeftMouseButton")
    (Uye|Set|PanX (+ (Uye|Get|PanX) ({T["GetInputAnalogKeyState"]} :self pc :Key "MouseX")))
    (Uye|Set|PanY (- (Uye|Get|PanY) ({T["GetInputAnalogKeyState"]} :self pc :Key "MouseY"))))
  (if {tus("MouseScrollUp")}
    (Uye|Set|Zoom ({T["Min(Float)"]} 3.0 (* (Uye|Get|Zoom) 1.15))))
  (if {tus("MouseScrollDown")}
    (Uye|Set|Zoom ({T["Max(Float)"]} 0.8 (/ (Uye|Get|Zoom) 1.15))))
  (if {tus("R")}
    (Uye|Set|Zoom 1.0)
    (Uye|Set|PanX 0.0)
    (Uye|Set|PanY 0.0))
  (if {tus("F")}
    (Uye|Set|Oku (not (Uye|Get|Oku)))
    (if (Uye|Get|Oku)
      {gor("Visible")}
      (else
        {gor("Collapsed")})))
  (Uye|Set|ZoomG ({T["FInterpTo"]} (Uye|Get|ZoomG) (Uye|Get|Zoom) InDeltaTime 12.0))
  (Uye|Set|PanGX ({T["FInterpTo"]} (Uye|Get|PanGX) (Uye|Get|PanX) InDeltaTime 14.0))
  (Uye|Set|PanGY ({T["FInterpTo"]} (Uye|Get|PanGY) (Uye|Get|PanY) InDeltaTime 14.0))
  ({T["SetRenderScale"]} :self (Uye|Get|Kagit) :Scale ({T["MakeVector2D"]} (Uye|Get|ZoomG) (Uye|Get|ZoomG)))
  ({T["SetRenderTranslation"]} :self (Uye|Get|Kagit) :Translation ({T["MakeVector2D"]} (Uye|Get|PanGX) (Uye|Get|PanGY)))
  ; dil (L tuşu WBP_Altyazi'de): her karede kültüre göre EN/TR seç
  (bind tr (Utilities|String|StartsWith (Utilities|Internationalization|GetCurrentCulture) "tr"))
  {dil("Baslik", "BaslikHam")}
  {dil("Ic", "IcHam")}
  {dil("OkuMetin", "OkuHam")}
  {dil("Ipucu", "IpucuHam")})
''')
    log("derleme2", arac("CompileWidgetBlueprint", widgetBlueprint=ref(wbp))); eal.save_loaded_asset(wbp, only_if_is_dirty=False)
    for k, v in KAGITLAR.items():
        w2 = eal.duplicate_asset(f"{P}/WBP_Incele_Sablon", f"{P}/WBP_Incele_{k}")
        if w2 is None: log("kopya başarısız", k, eal.does_asset_exist(f"{P}/WBP_Incele_{k}")); continue
        ws = agac(w2)
        tex = eal.load_asset(v["doku"]); br = unreal.SlateBrush(); br.set_editor_property("resource_object", tex)
        nesne(ws["Kagit"]["widget"]).set_editor_property("brush", br); nesne(ws["Kagit"]["slot"]).set_size(unreal.Vector2D(*v["boyut"]))
        nesne(ws["Baslik"]["widget"]).set_text(v["baslik"].split("~~")[0]); nesne(ws["Ic"]["widget"]).set_text(v["ic"].split("~~")[0]); nesne(ws["OkuMetin"]["widget"]).set_text(v["metin"].split("~~")[0])
        log("kopya", k, arac("CompileWidgetBlueprint", widgetBlueprint=ref(w2)))
        cdo = unreal.get_default_object(w2.generated_class())
        for n, kk in (("BaslikHam", "baslik"), ("IcHam", "ic"), ("OkuHam", "metin")): cdo.set_editor_property(n, v[kk])
        eal.save_loaded_asset(w2, only_if_is_dirty=False)
    bi = eal.load_asset("/Game/Sisli/Mekanik/BP_Incele"); g2 = BT.get_graph(bi, "EventGraph")
    for ad in ("CreateWidget", "AddToViewport", "RemoveFromParent", "SetIgnoreMoveInput", "SetIgnoreLookInput", "ResetIgnoreInputFlags", "IsInViewport", "IsValid"):
        log("aktör türü", ad, BT.find_node_types(g2, ad)[:6])
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
yaz("C:/Users/Onur/Sisli/Unreal/Scripts/ui_kur_out.txt")
