# Altyazı satırları: her satır = sessiz SoundWave + Subtitles (motorun altyazı yöneticisi ekranın alt ortasında gösterir).
# /Game/Uyanis/Yazi/SW_<id>. Süre: metin uzunluğuna göre 2..9 sn (sessiz_Ns.wav).
import unreal, math, traceback
OUT = []
def log(*a): OUT.append(" ".join(str(x) for x in a))
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary
D = "/Game/Uyanis/Yazi"; WAV = "C:/Users/Onur/Sisli/Unreal/SourceArt/Ses/sessiz_{}s.wav"
SATIR = {
    "giris": "...Ela?",
    "kontrol": "Fare: bak   ·   WASD: yürü   ·   Ctrl: çömel   ·   E: incele   ·   F: fener",
    "ipucu": "[E]  İncele",
    "tavsan1": "Ela'nın tavşanı. Onu hiç yanından ayırmazdı...",
    "tavsan2": "Ela'yı bulmalıyım.",
    "yatak_ela": "Ela'nın yatağı. Çarşafı buz gibi.",
    "yatak_ben": "Benim yatağım. Ela hep alttakini isterdi; korkunca yanıma kıvrılırdı.",
    "cizim1": "Ela'nın çizimi. İkimiz... el ele.",
    "cizim2": "Arkaya kırmızı bir ışık çizmiş. Neden kırmızı?",
    "kurallar1": "\"Işıklar 21.00'de söner. Gece sayımında herkes yatağında olur.\"",
    "kurallar2": "\"Kural dışı hareket eden çocuk ayrılır.\"  ...Ayrılır mı?",
    "pencere": "Sis. Sisin ardında hiç bitmeyen duvarlar.",
    "dolap_ela": "Ela'nın dolabı. Boşaltılmış... Kıyafetleri bile yok.",
    "dolap_bakici": "Kilitli. İçinden ilaç kokusu geliyor.",
    "defter1": "Bakıcının defteri.  \"Gece sayımı — 4. Yatakhane: 23 çocuk.\"",
    "defter2": "\"02:40 — K. Ela (7). 7. Blok'a nakledildi. Ağabeyine bildirilmeyecek.\"",
    "defter3": "7. Blok... Onu götürmüşler. Anahtarları alıyorum.",
    "kapi_kilitli": "Kilitli. Bakıcının anahtarları olmalı.",
    "anahtar": "Bakıcının anahtarları.",
    "kapi_acik": "Ela... Geliyorum.",
}
try:
    for k, metin in SATIR.items():
        sure = max(2, min(9, int(math.ceil(len(metin) * 0.065 + 1.6))))
        ad = "SW_" + k; p = f"{D}/{ad}"
        if not eal.does_asset_exist(p):   # var olanı SİLME: BP'lerdeki referanslar kopar; yalnız altyazıyı güncelle
            t = unreal.AssetImportTask(); t.filename = WAV.format(sure); t.destination_path = D; t.destination_name = ad
            t.automated = True; t.save = False; t.replace_existing = True; at.import_asset_tasks([t])
        sw = eal.load_asset(p)
        cue = unreal.SubtitleCue(); cue.set_editor_property("text", metin); cue.set_editor_property("time", 0.0)
        sw.set_editor_property("subtitles", [cue])
        try: sw.set_editor_property("manual_word_wrap", False)
        except Exception: pass
        eal.save_loaded_asset(sw); log("YAZI", ad, f"{sure}s", metin)
    log("TAMAM")
except Exception:
    log("HATA", traceback.format_exc())
open("C:/Users/Onur/Sisli/Unreal/Scripts/yazi_kur_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
