"""Erzeugt die Testbatterie (Markdown + JSON) für den Verordnungs-Check.

Soll-Werte werden aus den Regelwerken abgeleitet (eigene Regel-Engine unten,
unabhängig vom Workflow-Code). Alle Daten sind synthetisch.
"""
import copy
import json
import re
import sys
from datetime import date, timedelta

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "."
P = date(2026, 10, 26)  # festes Prüfdatum aller neuen Fälle


def d(days_before=None, days_after=None):
    if days_before is not None:
        return (P - timedelta(days=days_before)).isoformat()
    return (P + timedelta(days=days_after)).isoformat()


def add_months(dt, m):
    y, mo = dt.year + (dt.month - 1 + m) // 12, (dt.month - 1 + m) % 12 + 1
    import calendar
    day = min(dt.day, calendar.monthrange(y, mo)[1])
    return date(y, mo, day)


LANR = ["123456701", "234567802", "345678903", "456789004", "567890105"]
BSNR = ["987654300", "876543200", "765432100"]

BASE = {
    "verordnung_ref": None,
    "ausstellungsdatum": d(days_before=7),
    "pruefdatum": P.isoformat(),
    "geplanter_beginn": d(days_after=1),
    "dringlich": False,
    "icd10": "M54.4",
    "weitere_diagnosen": [],
    "diagnosegruppe": "WS",
    "leitsymptomatik": "a",
    "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}],
    "ergaenzendes_heilmittel": {"name": None, "einheiten": None},
    "frequenz": "2x/Woche",
    "lanr": LANR[0],
    "bsnr": BSNR[0],
    "unterschrift": True,
    "letzte_behandlung": None,
    "unterbrechungsgrund": None,
    "kostentraeger": "GKV",
}

# ---------------------------------------------------------------- Regelwissen
# Quelle: Heilmittelkatalog Physiotherapie, Diagnosegruppen WS und EX (Wissensbasis Supabase)
KATALOG = {
    "WS": {"leitsymptomatik": {"a", "b", "x"},
           "ergaenzend": {"Wärmetherapie", "Kältetherapie", "Traktion", "Elektrotherapie", "Hydroelektrische Bäder"}},
    "EX": {"leitsymptomatik": {"a", "b", "x"},
           "ergaenzend": {"Wärmetherapie", "Kältetherapie", "Elektrotherapie", "Hydroelektrische Bäder"}},
}
HOECHSTMENGE_VO = 6
ORIENTIERENDE_MENGE = 18

# Quelle: KBV-Diagnoseliste (besonderer Verordnungsbedarf / langfristiger Heilmittelbedarf), Auszug
# Schlüssel: (Code-Präfix, nötiger Zweitcode oder None) -> erlaubte Diagnosegruppen
BVB = [
    ("M50.1", "G55.1", {"WS"}),
    ("M51.1", "G55.1", {"WS"}),
    ("M48.0", "G55.3", {"WS"}),
    ("M47.2", "G55.2", {"WS"}),
    ("M45.0", None, {"WS", "EX"}),
    ("M06.0", None, {"WS", "EX"}),
    ("Q79.6", None, {"WS", "EX"}),
    ("M75.1", None, {"EX"}),
    ("Z96.65", "Z98.88", {"EX"}),
    ("Z96.64", "Z98.88", {"EX"}),
]


def region(code):
    """ICD-10-GM-Kapitelstruktur Muskel-Skelett -> WS/EX (None = nicht zuordenbar)."""
    if not code:
        return None
    m = re.match(r"^([A-Z])(\d{2})", code.upper())
    if not m:
        return None
    k, n = m.group(1), int(m.group(2))
    if k == "M" and 40 <= n <= 54:
        return "WS"
    if k == "S" and n in (12, 13, 22, 23, 32, 33):
        return "WS"
    if k == "M" and (15 <= n <= 25 or n in (75, 76, 77)):
        return "EX"
    if k == "S" and 40 <= n <= 99:
        return "EX"
    return None


def bvb_treffer(vo):
    code = (vo.get("icd10") or "").upper()
    zweit = {(x.get("code") or "").upper() for x in vo.get("weitere_diagnosen") or []}
    for praefix, noetig, gruppen in BVB:
        if code.startswith(praefix) and vo.get("diagnosegruppe") in gruppen:
            if noetig is None or noetig in zweit:
                return praefix
    return None


def max_pro_woche(freq):
    if not freq:
        return None
    f = freq.lower()
    if "täglich" in f:
        return 7
    nums = [int(x) for x in re.findall(r"\d+", f)]
    return max(nums) if nums else None


def verordnungsfall(vo):
    """Summe vorrangiger Einheiten im Verordnungsfall (§ 7 HeilM-RL), None ohne Historie."""
    hist = vo.get("vorverordnungen")
    if hist is None:
        return None
    icd3 = (vo["icd10"] or "")[:3].upper()
    kandidaten = sorted(
        [h for h in hist
         if (h["icd10"] or "")[:3].upper() == icd3
         and h["diagnosegruppe"] == vo["diagnosegruppe"]
         and h["lanr"] == vo["lanr"]
         and not h.get("entlassmanagement", False)],
        key=lambda h: h["ausstellungsdatum"], reverse=True)
    summe = sum(h["einheiten"] for h in vo["heilmittel"] if h.get("art") == "vorrangig")
    juengere = date.fromisoformat(vo["ausstellungsdatum"])
    for h in kandidaten:
        dt = date.fromisoformat(h["ausstellungsdatum"])
        if add_months(dt, 6) <= juengere:  # 6 Monate ohne weitere Verordnung -> neuer Fall
            break
        summe += h["einheiten_vorrangig"]
        juengere = dt
    return summe


def soll(vo):
    """Leitet Soll-Ampel und erwartete Befunde aus den Regelwerken ab."""
    rot, gelb = [], []
    vorh = lambda v: v is not None and str(v).strip() != ""
    # Formal-Prüfer: Pflichtangaben (HeilM-RL § 13 Abs. 2)
    for feld, label in [("kostentraeger", "Kostenträger"), ("lanr", "LANR"), ("bsnr", "BSNR"),
                        ("ausstellungsdatum", "Ausstellungsdatum"), ("icd10", "ICD-10-Code"),
                        ("diagnosegruppe", "Diagnosegruppe"), ("leitsymptomatik", "Leitsymptomatik"),
                        ("frequenz", "Therapiefrequenz")]:
        if not vorh(vo.get(feld)):
            rot.append(("formal", label))
    if vo.get("unterschrift") is not True:
        rot.append(("formal", "Unterschrift"))
    if not any((h.get("einheiten") or 0) > 0 for h in vo["heilmittel"]):
        rot.append(("formal", "Heilmittel mit Einheiten"))
    for feld, label in [("lanr", "LANR"), ("bsnr", "BSNR")]:
        if vorh(vo.get(feld)) and not re.fullmatch(r"\d{9}", str(vo[feld])):
            rot.append(("formal", label))
    dg = vo.get("diagnosegruppe")
    ls = vo.get("leitsymptomatik")
    if vorh(ls) and dg in KATALOG and ls not in KATALOG[dg]["leitsymptomatik"]:
        rot.append(("diagnose", "Leitsymptomatik"))
    # Diagnose-Prüfer: ICD passt zur Diagnosegruppe, besonderer Verordnungsbedarf
    r = region(vo.get("icd10"))
    if r and dg in ("WS", "EX") and r != dg:
        rot.append(("diagnose", "Diagnosegruppe"))
    elif bvb_treffer(vo):
        gelb.append(("diagnose", "Besonderer Verordnungsbedarf"))
    # Mengen-Prüfer
    vorrangig = [h for h in vo["heilmittel"] if h.get("art") == "vorrangig"]
    summe = sum(h.get("einheiten") or 0 for h in vorrangig)
    if summe > HOECHSTMENGE_VO:
        rot.append(("menge", "Einheiten je Verordnung"))
    if len(vorrangig) > 3:
        rot.append(("menge", "Heilmittel-Kombination"))
    erg = vo.get("ergaenzendes_heilmittel") or {}
    if erg.get("name"):
        if (erg.get("einheiten") or 0) > summe:
            rot.append(("menge", "Ergänzendes Heilmittel"))
        if dg in KATALOG and erg["name"] not in KATALOG[dg]["ergaenzend"]:
            rot.append(("menge", "Ergänzendes Heilmittel"))
    # Frequenz außerhalb der Empfehlung 1–3x/Woche: Hinweis (Teamentscheidung 27.10.2026)
    fr = re.findall(r"\d+", str(vo.get("frequenz") or ""))
    if fr and (min(map(int, fr)) < 1 or max(map(int, fr)) > 3):
        gelb.append(("menge", "Therapiefrequenz"))
    fall = verordnungsfall(vo)
    if fall is not None and fall > ORIENTIERENDE_MENGE:
        gelb.append(("menge", "Verordnungsfall (orientierende Menge)"))
    # Fristen-Prüfer (HeilM-RL § 15 Abs. 1, § 16 Abs. 4)
    if vorh(vo.get("ausstellungsdatum")):
        aus = date.fromisoformat(vo["ausstellungsdatum"])
        beginn = date.fromisoformat(vo.get("geplanter_beginn") or vo["pruefdatum"])
        if vo.get("letzte_behandlung"):
            pause = (beginn - date.fromisoformat(vo["letzte_behandlung"])).days
            if pause > 14 and not vorh(vo.get("unterbrechungsgrund")):
                rot.append(("frist", "Unterbrechung"))
        else:
            grenze = 14 if vo.get("dringlich") else 28
            if (beginn - aus).days > grenze:
                rot.append(("frist", "Behandlungsbeginn"))
    # doppelte Einträge zusammenfassen
    rot = list(dict.fromkeys(rot))
    gelb = list(dict.fromkeys(gelb))
    ampel = "rot" if rot else ("gelb" if gelb else "gruen")
    befunde = [{"agent": a, "feld": f, "status": "fehlt/fehlerhaft"} for a, f in rot] + \
              [{"agent": a, "feld": f, "status": "hinweis"} for a, f in gelb]
    return ampel, befunde, fall


# ---------------------------------------------------------------- Fallkatalog
FALL = []


def fall(kat, pruefer, titel, fundstelle, over=None, freitext=None, v5=False, hinweis=None, soll_ampel=None):
    vo = copy.deepcopy(BASE)
    for k, v in (over or {}).items():
        vo[k] = v
    FALL.append(dict(kat=kat, pruefer=pruefer, titel=titel, fundstelle=fundstelle, vo=vo,
                     freitext=freitext, v5=v5, hinweis=hinweis, soll_ampel=soll_ampel))


HM = lambda *xs: [{"name": n, "einheiten": e, "art": "vorrangig"} for n, e in xs]
ERG = lambda n, e: {"name": n, "einheiten": e}
KAT_WS = "Heilmittelkatalog WS"
KAT_EX = "Heilmittelkatalog EX"


def vv(tage_vor, einheiten, icd="M54.4", dg="WS", lanr=LANR[0], ergaenzend=0, entlass=False):
    """Vorverordnung (Vorschlag für das Historie-Schema von v5)."""
    return {"ausstellungsdatum": d(days_before=tage_vor), "icd10": icd, "diagnosegruppe": dg, "lanr": lanr,
            "einheiten_vorrangig": einheiten, "einheiten_ergaenzend": ergaenzend, "entlassmanagement": entlass}


# ===== GRÜN (23) =====
G = "gruen"
fall(G, "alle", "LWS-Lumboischialgie, Standardfall", "HeilM-RL § 13 Abs. 2; " + KAT_WS)
fall(G, "alle", "Zervikalneuralgie, MT, Spanne 1-2x", KAT_WS,
     {"icd10": "M54.2", "leitsymptomatik": "b", "heilmittel": HM(("MT", 6)), "frequenz": "1-2x/Woche", "lanr": LANR[1]})
fall(G, "menge", "Zwei vorrangige Heilmittel, Summe 6", "HeilM-RL § 12 Abs. 2; " + KAT_WS,
     {"icd10": "M53.1", "heilmittel": HM(("KG", 4), ("MT", 2))})
fall(G, "alle", "Bandscheibenverlagerung, KG-Gerät", KAT_WS,
     {"icd10": "M51.2", "leitsymptomatik": "b", "heilmittel": HM(("KG-Gerät", 6)), "bsnr": BSNR[1]})
fall(G, "menge", "Ergänzendes Heilmittel gleich viele Einheiten wie vorrangig", "HeilM-RL § 7 Abs. 5; " + KAT_WS,
     {"icd10": "M47.86", "ergaenzendes_heilmittel": ERG("Wärmetherapie", 6)})
fall(G, "frist", "HWS-Distorsion, dringlich, Beginn nach 10 Tagen", "HeilM-RL § 15 Abs. 1",
     {"icd10": "S13.4", "dringlich": True, "ausstellungsdatum": d(days_before=9), "geplanter_beginn": d(days_after=1)})
fall(G, "formal", "Leitsymptomatik x mit patientenindividueller Angabe", KAT_WS,
     {"icd10": "M43.16", "leitsymptomatik": "x", "leitsymptomatik_freitext": "Instabilität im Lumbalbereich mit Belastungsschmerz"})
fall(G, "alle", "Gonarthrose, Spanne 1-2x", KAT_EX,
     {"icd10": "M17.1", "diagnosegruppe": "EX", "frequenz": "1-2x/Woche"})
fall(G, "alle", "Koxarthrose, KG-Gerät", KAT_EX,
     {"icd10": "M16.1", "diagnosegruppe": "EX", "leitsymptomatik": "b", "heilmittel": HM(("KG-Gerät", 6)), "lanr": LANR[2]})
fall(G, "alle", "Impingement Schulter, MT", KAT_EX,
     {"icd10": "M75.4", "diagnosegruppe": "EX", "heilmittel": HM(("MT", 6))})
fall(G, "menge", "Epicondylitis, KG 3 + MT 3", "HeilM-RL § 12 Abs. 2; " + KAT_EX,
     {"icd10": "M77.1", "diagnosegruppe": "EX", "heilmittel": HM(("KG", 3), ("MT", 3))})
fall(G, "menge", "Achillessehne, ergänzend Kältetherapie, 3x/Woche", KAT_EX,
     {"icd10": "M76.6", "diagnosegruppe": "EX", "leitsymptomatik": "b", "frequenz": "3x/Woche", "ergaenzendes_heilmittel": ERG("Kältetherapie", 6)})
fall(G, "frist", "Außenknöchelfraktur, dringlich, Beginn nach 5 Tagen", "HeilM-RL § 15 Abs. 1",
     {"icd10": "S82.6", "diagnosegruppe": "EX", "dringlich": True, "ausstellungsdatum": d(days_before=4), "geplanter_beginn": d(days_after=1)})
fall(G, "frist", "Behandlung läuft, letzte Sitzung vor 6 Tagen", "HeilM-RL § 16 Abs. 4",
     {"icd10": "S93.40", "diagnosegruppe": "EX", "ausstellungsdatum": d(days_before=20), "letzte_behandlung": d(days_before=5)})
fall(G, "alle", "Chondropathie Patella, 1x/Woche", KAT_EX,
     {"icd10": "M22.4", "diagnosegruppe": "EX", "leitsymptomatik": "b", "frequenz": "1x/Woche"})
fall(G, "frist", "Unterbrechung 20 Tage mit Begründung", "HeilM-RL § 16 Abs. 4",
     {"ausstellungsdatum": d(days_before=30), "letzte_behandlung": d(days_before=19), "unterbrechungsgrund": "Krankenhausaufenthalt des Patienten"})
fall(G, "menge", "Drei vorrangige Heilmittel, Summe 6", "HeilM-RL § 12 Abs. 2; " + KAT_EX,
     {"icd10": "M17.1", "diagnosegruppe": "EX", "heilmittel": HM(("KG", 2), ("MT", 2), ("KG-Gerät", 2))})
fall(G, "frist", "Beginn nach 27 Tagen", "HeilM-RL § 15 Abs. 1",
     {"icd10": "M54.2", "ausstellungsdatum": d(days_before=26), "geplanter_beginn": d(days_after=1)})
fall(G, "alle", "Freitext: Gonarthrose vollständig", KAT_EX, freitext=(
    "Neue Verordnung für Frau Erika Beispiel, geb. 14.02.1961, Techniker Krankenkasse, Vers.-Nr. K123456789. "
    "Ausgestellt am 19.10.2026 von Dr. med. Hans Probe, LANR 123456701, BSNR 987654300, unterschrieben. "
    "ICD M17.1 Gonarthrose rechts, Diagnosegruppe EX, Leitsymptomatik a. 6x KG, 2x pro Woche. "
    "Geplanter Behandlungsbeginn 27.10.2026, Prüfdatum 26.10.2026."),
    over={"icd10": "M17.1", "diagnosegruppe": "EX"})
fall(G, "alle", "Freitext: LWS, zwei Heilmittel", KAT_WS, freitext=(
    "Herr Max Muster, AOK, Versichertennr. A987654321, Tel. 0621 1234567. Verordnung vom 19.10.2026, "
    "LANR 234567802, BSNR 876543200, Unterschrift vorhanden. Diagnose M54.4 Lumboischialgie, WS, Leitsymptomatik b. "
    "4x KG und 2x MT, 2x wöchentlich. Start am 27.10.2026, geprüft am 26.10.2026."),
    over={"lanr": LANR[1], "bsnr": BSNR[1], "leitsymptomatik": "b", "heilmittel": HM(("KG", 4), ("MT", 2))})
fall(G, "menge", "v5: Folgeverordnung, 6 + 6 = 12 im Fall", "HeilM-RL § 7 Abs. 1; " + KAT_WS, v5=True,
     over={"patient_pseudonym": "P-1001", "vorverordnungen": [vv(40, 6)]})
fall(G, "menge", "v5: 12 Einheiten bei anderem Arzt, neuer Fall", "HeilM-RL § 7 Abs. 3", v5=True,
     over={"patient_pseudonym": "P-1002", "vorverordnungen": [vv(60, 6, lanr=LANR[3]), vv(30, 6, lanr=LANR[3])]})
fall(G, "menge", "v5: letzte Vorverordnung vor 7 Monaten, neuer Fall (TF12-Muster)", "HeilM-RL § 7 Abs. 1 Satz 5", v5=True,
     over={"patient_pseudonym": "P-1003", "vorverordnungen": [vv(260, 6), vv(220, 6), vv(213, 6)]})

# ===== GELB (15) =====
Y = "gelb"
KBV = "KBV-Diagnoseliste"
fall(Y, "diagnose", "HWS-Bandscheibe mit Radikulopathie, Zweitcode vorhanden", KBV,
     {"icd10": "M50.1", "weitere_diagnosen": [{"code": "G55.1"}]})
fall(Y, "diagnose", "LWS-Bandscheibe mit Radikulopathie, Zweitcode vorhanden", KBV,
     {"icd10": "M51.1", "weitere_diagnosen": [{"code": "G55.1"}], "leitsymptomatik": "b"})
fall(Y, "diagnose", "Spinalkanalstenose lumbal mit Radikulopathie", KBV,
     {"icd10": "M48.06", "weitere_diagnosen": [{"code": "G55.3"}]})
fall(Y, "diagnose", "Spondylose mit Radikulopathie", KBV,
     {"icd10": "M47.26", "weitere_diagnosen": [{"code": "G55.2"}], "lanr": LANR[2]})
fall(Y, "diagnose", "Spondylitis ankylosans, WS", KBV, {"icd10": "M45.09"})
fall(Y, "diagnose", "Seronegative chronische Polyarthritis, EX", KBV,
     {"icd10": "M06.06", "diagnosegruppe": "EX"})
fall(Y, "diagnose", "Ehlers-Danlos-Syndrom, WS", KBV, {"icd10": "Q79.6", "leitsymptomatik": "b"})
fall(Y, "diagnose", "Läsion der Rotatorenmanschette, EX", KBV,
     {"icd10": "M75.1", "diagnosegruppe": "EX"})
fall(Y, "diagnose", "Knieprothese mit Zweitcode", KBV,
     {"icd10": "Z96.65", "weitere_diagnosen": [{"code": "Z98.88"}], "diagnosegruppe": "EX"})
fall(Y, "diagnose", "Hüftprothese mit Zweitcode", KBV,
     {"icd10": "Z96.64", "weitere_diagnosen": [{"code": "Z98.88"}], "diagnosegruppe": "EX", "bsnr": BSNR[1]})
fall(Y, "diagnose", "Freitext: LWS-Bandscheibe mit Radikulopathie", KBV, freitext=(
    "Rezept für Patientin Anna Test, geb. 01.07.1975, BARMER, KVNR B112233445. Dr. Lena Muster, LANR 345678903, "
    "BSNR 765432100, ausgestellt 19.10.2026 mit Unterschrift. Diagnosen: M51.1 lumbaler Bandscheibenschaden mit "
    "Radikulopathie und G55.1. Diagnosegruppe WS, Leitsymptomatik a. 6 x KG, 2x/Woche, Beginn 27.10.2026, Prüfung 26.10.2026."),
    over={"icd10": "M51.1", "weitere_diagnosen": [{"code": "G55.1"}], "lanr": LANR[2], "bsnr": BSNR[2]})
fall(Y, "menge", "v5: 18 im Fall + 6 = 24 (TF11-Muster)", "HeilM-RL § 7 Abs. 2; " + KAT_WS, v5=True,
     over={"patient_pseudonym": "P-2001", "vorverordnungen": [vv(90, 6), vv(60, 6), vv(30, 6)]})
fall(Y, "menge", "v5: 14 im Fall + 6 = 20", "HeilM-RL § 7 Abs. 2; " + KAT_WS, v5=True,
     over={"patient_pseudonym": "P-2002", "vorverordnungen": [vv(70, 6), vv(45, 4), vv(20, 4)]})
fall(Y, "menge", "v5: andere 4. Stelle, gleicher Fall (M54.2 → M54.4)", "HeilM-RL § 7 Abs. 1 Satz 1", v5=True,
     over={"patient_pseudonym": "P-2003", "vorverordnungen": [vv(100, 6, icd="M54.2"), vv(70, 6, icd="M54.2"), vv(35, 6, icd="M54.2")]})
fall(Y, "menge", "v5: EX, 18 im Fall + 6", "HeilM-RL § 7 Abs. 2; " + KAT_EX, v5=True,
     over={"patient_pseudonym": "P-2004", "icd10": "M17.1", "diagnosegruppe": "EX",
           "vorverordnungen": [vv(120, 6, "M17.1", "EX"), vv(80, 6, "M17.1", "EX"), vv(40, 6, "M17.1", "EX")]})

# ===== ROT (50) =====
R = "rot"
F13 = "HeilM-RL § 13 Abs. 2"
# Formal-Prüfer (12)
fall(R, "formal", "Kostenträger fehlt", F13, {"kostentraeger": None})
fall(R, "formal", "LANR fehlt", F13, {"lanr": None, "icd10": "M17.1", "diagnosegruppe": "EX"})
fall(R, "formal", "BSNR fehlt", F13, {"bsnr": None})
fall(R, "formal", "Ausstellungsdatum fehlt", F13, {"ausstellungsdatum": None, "icd10": "M75.4", "diagnosegruppe": "EX"})
fall(R, "formal", "Unterschrift fehlt", "HeilM-RL § 13 Abs. 1", {"unterschrift": False})
fall(R, "formal", "ICD-10-Code fehlt", F13, {"icd10": None})
fall(R, "formal", "Diagnosegruppe fehlt", F13, {"diagnosegruppe": None, "icd10": "M16.1"})
fall(R, "formal", "Leitsymptomatik fehlt", F13, {"leitsymptomatik": None, "icd10": "M53.1"})
fall(R, "formal", "Heilmittel ohne Einheiten", F13, {"heilmittel": [{"name": "KG", "einheiten": None, "art": "vorrangig"}]})
fall(R, "formal", "Therapiefrequenz fehlt", F13, {"frequenz": None, "icd10": "M77.1", "diagnosegruppe": "EX"})
fall(R, "formal", "LANR nur 8 Ziffern", F13, {"lanr": "12345670"})
fall(R, "formal", "BSNR mit Buchstaben", F13, {"bsnr": "98765A300", "icd10": "S82.6", "diagnosegruppe": "EX"})
# Diagnose-Prüfer (10)
for icd, dg, txt in [("M17.1", "WS", "Gonarthrose mit WS"), ("M16.1", "WS", "Koxarthrose mit WS"),
                     ("M54.4", "EX", "Lumboischialgie mit EX"), ("M53.1", "EX", "Zervikobrachial-Syndrom mit EX"),
                     ("M51.2", "EX", "Bandscheibenverlagerung mit EX"), ("S13.4", "EX", "HWS-Distorsion mit EX"),
                     ("S82.6", "WS", "Außenknöchelfraktur mit WS"), ("M77.1", "WS", "Epicondylitis mit WS"),
                     ("M75.4", "WS", "Impingement Schulter mit WS"), ("M43.16", "EX", "Spondylolisthesis mit EX")]:
    fall(R, "diagnose", txt, "Heilmittelkatalog, Diagnosegruppen WS/EX", {"icd10": icd, "diagnosegruppe": dg})
# Mengen-Prüfer (10)
fall(R, "menge", "7 Einheiten bei WS", KAT_WS, {"heilmittel": HM(("KG", 7))})
fall(R, "menge", "8 Einheiten bei EX", KAT_EX, {"icd10": "M17.1", "diagnosegruppe": "EX", "heilmittel": HM(("KG", 8))})
fall(R, "menge", "12 Einheiten bei WS", KAT_WS, {"icd10": "M54.2", "heilmittel": HM(("KG", 12))})
fall(R, "menge", "KG 4 + MT 4 = 8 bei EX", "HeilM-RL § 12 Abs. 2; " + KAT_EX,
     {"icd10": "M75.4", "diagnosegruppe": "EX", "heilmittel": HM(("KG", 4), ("MT", 4))})
fall(R, "menge", "Vier vorrangige Heilmittel", "HeilM-RL § 12 Abs. 2",
     {"heilmittel": HM(("KG", 2), ("MT", 2), ("KG-Gerät", 1), ("KMT", 1))})
fall(R, "menge", "Ergänzend 8 Einheiten bei 6 vorrangigen", "HeilM-RL § 7 Abs. 5 Satz 2",
     {"ergaenzendes_heilmittel": ERG("Wärmetherapie", 8)})
fall(R, "menge", "KG 6 + MT 6 = 12 bei WS", "HeilM-RL § 12 Abs. 2; " + KAT_WS,
     {"icd10": "M53.1", "heilmittel": HM(("KG", 6), ("MT", 6))})
fall(R, "menge", "KG-Gerät 10 bei EX", KAT_EX, {"icd10": "M16.1", "diagnosegruppe": "EX", "heilmittel": HM(("KG-Gerät", 10))})
fall(R, "menge", "Ergänzend Elektro 6 bei KG 3", "HeilM-RL § 7 Abs. 5 Satz 2",
     {"icd10": "M77.1", "diagnosegruppe": "EX", "heilmittel": HM(("KG", 3)), "ergaenzendes_heilmittel": ERG("Elektrotherapie", 6)})
fall(R, "menge", "KMT 9 bei EX", KAT_EX, {"icd10": "M76.6", "diagnosegruppe": "EX", "heilmittel": HM(("KMT", 9))})
# Fristen-Prüfer (10)
FR = "HeilM-RL § 15 Abs. 1 und 2"
FU = "HeilM-RL § 16 Abs. 4"
fall(R, "frist", "Beginn nach 35 Tagen", FR, {"ausstellungsdatum": d(days_before=34)})
fall(R, "frist", "Beginn nach 60 Tagen", FR, {"ausstellungsdatum": d(days_before=59), "icd10": "M54.2"})
fall(R, "frist", "EX, Beginn nach 45 Tagen", FR, {"ausstellungsdatum": d(days_before=44), "icd10": "M17.1", "diagnosegruppe": "EX"})
fall(R, "frist", "Dringlich, Beginn nach 15 Tagen", FR, {"dringlich": True, "ausstellungsdatum": d(days_before=14)})
fall(R, "frist", "Dringlich, Beginn nach 20 Tagen", FR,
     {"dringlich": True, "ausstellungsdatum": d(days_before=19), "icd10": "S82.6", "diagnosegruppe": "EX"})
fall(R, "frist", "Dringlich, Beginn nach 40 Tagen", FR, {"dringlich": True, "ausstellungsdatum": d(days_before=39), "icd10": "S13.4"})
fall(R, "frist", "Unterbrechung 21 Tage ohne Grund", FU,
     {"ausstellungsdatum": d(days_before=35), "letzte_behandlung": d(days_before=20)})
fall(R, "frist", "Unterbrechung 30 Tage ohne Grund", FU,
     {"ausstellungsdatum": d(days_before=45), "letzte_behandlung": d(days_before=29), "icd10": "M16.1", "diagnosegruppe": "EX"})
fall(R, "frist", "Unterbrechung 18 Tage, Grund leer", FU,
     {"ausstellungsdatum": d(days_before=30), "letzte_behandlung": d(days_before=17), "unterbrechungsgrund": ""})
fall(R, "frist", "EX, Unterbrechung 25 Tage ohne Grund", FU,
     {"ausstellungsdatum": d(days_before=40), "letzte_behandlung": d(days_before=24), "icd10": "M75.4", "diagnosegruppe": "EX"})
# Mehrfachfehler (5)
fall(R, "mehrere", "LANR fehlt und Beginn zu spät", "HeilM-RL § 13 Abs. 2, § 15 Abs. 1",
     {"lanr": None, "ausstellungsdatum": d(days_before=32)})
fall(R, "mehrere", "Diagnosegruppe falsch und 10 Einheiten", "Heilmittelkatalog",
     {"icd10": "M17.1", "diagnosegruppe": "WS", "heilmittel": HM(("KG", 10))})
fall(R, "mehrere", "8 Einheiten und Unterbrechung 16 Tage", "Heilmittelkatalog; HeilM-RL § 16 Abs. 4",
     {"heilmittel": HM(("KG", 8)), "ausstellungsdatum": d(days_before=30), "letzte_behandlung": d(days_before=15)})
fall(R, "mehrere", "Drei Fehler: Unterschrift, Diagnosegruppe, dringlich zu spät", "HeilM-RL § 13, § 15; Heilmittelkatalog",
     {"unterschrift": False, "icd10": "M54.4", "diagnosegruppe": "EX", "dringlich": True, "ausstellungsdatum": d(days_before=16)})
fall(R, "mehrere", "Leitsymptomatik und Frequenz fehlen", "HeilM-RL § 13 Abs. 2",
     {"leitsymptomatik": None, "frequenz": None, "icd10": "M22.4", "diagnosegruppe": "EX"})
# Freitext rot (3)
fall(R, "diagnose", "Freitext: Schulterdiagnose mit WS (wie TF03)", "Heilmittelkatalog", freitext=(
    "Bitte prüfen: Herr Peter Probe, DAK, Vers.-Nr. D556677889, Musterstraße 12, 68159 Mannheim. Verordnung "
    "vom 19.10.2026, LANR 456789004, BSNR 987654300, unterschrieben. M75.4 Impingement Schulter links, "
    "Diagnosegruppe WS, Leitsymptomatik a. 6x KG, 2x/Woche, Beginn 27.10.2026, Prüfdatum 26.10.2026."),
    over={"icd10": "M75.4", "diagnosegruppe": "WS", "lanr": LANR[3]})
fall(R, "menge", "Freitext: 10 Einheiten KG bei EX", KAT_EX, freitext=(
    "Verordnung für Frau Maria Beispiel, IKK, Vers.-Nr. I998877665, E-Mail maria.beispiel@example.org. "
    "Ausgestellt 19.10.2026, LANR 567890105, BSNR 876543200, Unterschrift ja. M16.1 Koxarthrose, EX, "
    "Leitsymptomatik b, 10x KG, 2x die Woche, Beginn 27.10.2026, Prüfdatum 26.10.2026."),
    over={"icd10": "M16.1", "diagnosegruppe": "EX", "leitsymptomatik": "b", "lanr": LANR[4], "bsnr": BSNR[1],
          "heilmittel": HM(("KG", 10))})
fall(R, "frist", "Freitext: Beginn 40 Tage nach Ausstellung", FR, freitext=(
    "Patient Jonas Test, geb. 22.09.1990, hkk, KVNR H443322110. Rezept vom 16.09.2026 von Dr. Eva Probe, "
    "LANR 123456701, BSNR 987654300, unterschrieben. M54.4 Lumboischialgie, WS, Leitsymptomatik a, 6x KG, "
    "2x/Woche. Erste Behandlung geplant am 27.10.2026, Prüfdatum 26.10.2026."),
    over={"ausstellungsdatum": "2026-09-16"})

# ===== GRENZFÄLLE (12) =====
B = "grenzfall"
fall(B, "frist", "Beginn exakt am 28. Tag", "HeilM-RL § 15 Abs. 1",
     {"ausstellungsdatum": d(days_before=27)}, hinweis="Tag der Ausstellung zählt nicht mit; 28 Tage danach ist noch fristgerecht.")
fall(B, "frist", "Beginn am 29. Tag (Gegenprobe)", "HeilM-RL § 15 Abs. 1 und 2", {"ausstellungsdatum": d(days_before=28)})
fall(B, "frist", "Dringlich, Beginn exakt am 14. Tag", "HeilM-RL § 15 Abs. 1",
     {"dringlich": True, "ausstellungsdatum": d(days_before=13)})
fall(B, "frist", "Unterbrechung exakt 14 Tage ohne Grund", "HeilM-RL § 16 Abs. 4",
     {"ausstellungsdatum": d(days_before=30), "letzte_behandlung": d(days_before=13)},
     hinweis="Auslegung: Differenz 14 Tage zwischen zwei Sitzungen gilt als nicht länger als 14 Kalendertage. Im Team bestätigen.")
fall(B, "frist", "Unterbrechung 15 Tage ohne Grund (Gegenprobe)", "HeilM-RL § 16 Abs. 4",
     {"ausstellungsdatum": d(days_before=30), "letzte_behandlung": d(days_before=14)})
fall(B, "diagnose", "Leitsymptomatik c bei EX", KAT_EX + " (nur a, b, x)",
     {"icd10": "S43.4", "diagnosegruppe": "EX", "leitsymptomatik": "c"},
     hinweis="Der Katalog kennt für EX nur a, b und x. Seit 27.10.2026 prüft der Code das (`leitsymptomatik_zulaessig`); TF10 entsprechend rot.")
fall(B, "menge", "Traktion als ergänzendes Heilmittel bei EX", KAT_EX + " (Traktion nur bei WS)",
     {"icd10": "M17.1", "diagnosegruppe": "EX", "ergaenzendes_heilmittel": ERG("Traktion", 6)},
     hinweis="Kein Prüfer hat die Zulässigkeit des ergänzenden Heilmittels ausdrücklich im Mandat. Zeigt eine Lücke.")
fall(B, "menge", "Frequenz 4x/Woche", "HeilM-RL § 12 Abs. 1 Satz 4",
     {"frequenz": "4x/Woche"},
     hinweis="Frequenzempfehlung ist Orientierung. Teamentscheidung 27.10.2026: Abweichung von 1–3x/Woche ist ein Hinweis (gelb), analog TF22.")
fall(B, "diagnose", "M50.1 ohne Zweitcode G55.1", KBV + " (beide Codes nötig)",
     {"icd10": "M50.1"},
     hinweis="Ohne Zweitcode kein anerkannter besonderer Verordnungsbedarf. Soll grün; der Prototyp meldet hier vermutlich einen Hinweis.")
fall(B, "menge", "v5: Summe im Fall exakt 18", "HeilM-RL § 7 Abs. 2; " + KAT_WS, v5=True,
     over={"patient_pseudonym": "P-3001", "vorverordnungen": [vv(60, 6), vv(30, 6)]})
fall(B, "menge", "v5: Vorverordnung aus dem Entlassmanagement zählt nicht", "HeilM-RL § 16a Abs. 5", v5=True,
     over={"patient_pseudonym": "P-3002", "vorverordnungen": [vv(70, 6, entlass=True), vv(45, 6, entlass=True), vv(20, 6)]},
     hinweis="Ohne die Regel ergäbe sich 24 (gelb).")
fall(B, "menge", "v5: ergänzende Einheiten zählen nicht zur orientierenden Menge", "HeilM-RL § 7 Abs. 2 Satz 2", v5=True,
     over={"patient_pseudonym": "P-3003", "ergaenzendes_heilmittel": ERG("Wärmetherapie", 6),
           "vorverordnungen": [vv(60, 6, ergaenzend=6), vv(30, 6, ergaenzend=6)]},
     hinweis="Mit ergänzenden Einheiten wären es 36, nur vorrangige zählen: 18 (grün).")

# ---------------------------------------------------------------- Auswertung
GRENZ_SOLL = {}
ids = []
for i, f in enumerate(FALL):
    f["id"] = "TF%03d" % (13 + i)
    f["vo"]["verordnung_ref"] = "VO-%04d" % (13 + i)
    ampel, befunde, fallsumme = soll(f["vo"])
    f["soll"] = {"gesamtstatus": ampel, "befunde": befunde}
    if fallsumme is not None:
        f["soll"]["verordnungsfall_summe"] = fallsumme
    if f["kat"] != "grenzfall":
        assert ampel == f["kat"], (f["id"], f["titel"], ampel, befunde)

# Set-Zuordnung: je Kategorie 3 von 5 Fällen ins Evaluationsset (Holdout), Rest Entwicklung
by_kat = {}
for f in FALL:
    key = (f["kat"], f["pruefer"])
    by_kat.setdefault(key, []).append(f)
for key, lst in by_kat.items():
    for j, f in enumerate(lst):
        f["set"] = "E" if (j % 5) in (0, 1, 3) or len(lst) == 1 else "D"

assert len(FALL) == 100, len(FALL)
E = [f for f in FALL if f["set"] == "E"]
cnt = lambda lst, **kw: sum(all(f.get(k) == v for k, v in kw.items()) for f in lst)
amp = lambda lst, a: sum(f["soll"]["gesamtstatus"] == a for f in lst)
stats = {
    "gesamt": len(FALL), "E": len(E), "D": len(FALL) - len(E),
    "E_gruen": amp(E, "gruen"), "E_gelb": amp(E, "gelb"), "E_rot": amp(E, "rot"),
    "E_grenz": cnt(E, kat="grenzfall"),
}
for p in ("formal", "diagnose", "menge", "frist"):
    stats["E_rot_" + p] = sum(f["soll"]["gesamtstatus"] == "rot" and any(b["agent"] == p for b in f["soll"]["befunde"]) for f in E)
print(json.dumps(stats, indent=1))
assert stats["E_gruen"] >= 12 and stats["E_gelb"] >= 8 and stats["E_rot"] >= 25 and stats["E_grenz"] >= 5
assert all(stats["E_rot_" + p] >= 5 for p in ("formal", "diagnose", "menge", "frist")), stats

# ---------------------------------------------------------------- Teil A
TEIL_A = [
    ("TF01", "JSON", "Vollständig und regelkonform", "grün", "–", "v4: grün ✅ · Merge (Ausführung 897): grün, 18/18 ok ✅"),
    ("TF02", "JSON", "Beginn 41 Tage nach Ausstellung", "rot", "Fristen: Behandlungsbeginn", "v4: rot ✅"),
    ("TF03", "JSON / Freitext", "Schulter-Code M75.1 mit WS", "rot", "Diagnose: Diagnosegruppe",
     "v4: rot ✅ · Merge Freitext (898): Fehlalarm Mengen ❌ → 901 ✅ · Merge JSON (923, 23.10.): rot, nur Diagnose ✅"),
    ("TF04", "JSON", "10 Einheiten bei WS", "rot", "Mengen: Einheiten", "v4: rot ✅"),
    ("TF05", "JSON", "Leitsymptomatik und LANR fehlen", "rot", "Formal: Leitsymptomatik, LANR", "v4: rot ✅"),
    ("TF06", "JSON", "22 Tage Unterbrechung ohne Grund", "rot", "Fristen: Unterbrechung", "v4: rot ✅"),
    ("TF07", "JSON", "Dringlich, Beginn nach 18 Tagen", "rot", "Fristen: Behandlungsbeginn", "v4: rot ✅"),
    ("TF08", "JSON", "Kontrollfall Gonarthrose mit EX", "grün", "–", "v4: grün ✅"),
    ("TF09", "JSON", "Kontrollfall M50.1 mit EX", "rot", "Diagnose: Diagnosegruppe (+ Hinweis KBV-Liste)", "v4: rot ✅"),
    ("TF10", "JSON", "Kontrollfall dringlich, Beginn nach 7 Tagen", "rot (bis 27.10. grün)", "Diagnose: Leitsymptomatik",
     "v4: grün (altes Soll) · Merge (930, 23.10.): rot, Leitsymptomatik ✅ · Leitsymptomatik „c“ gibt es bei EX laut Katalog nicht; Seed nach Vier-Augen-Prüfung am 27.10.2026 angepasst"),
    ("M-899", "Formular", "Formular: M17.1, EX, 6× KG, Ausstellung 15.10.2026", "grün", "–",
     "Merge (899): grün, 18/18 ok, 6 PII-Felder ersetzt ✅ · Prüfdatum = Tagesdatum, Frist läuft ab 12.11.2026 ab"),
    ("TF11", "JSON + Historie", "geplant v5: Menge im Verordnungsfall überschritten", "gelb", "Mengen: Verordnungsfall",
     "noch nicht gebaut · Muster: TF{}".format(next(f["id"][2:] for f in FALL if "TF11-Muster" in f["titel"]))),
    ("TF12", "JSON + Historie", "geplant v5: neuer Fall nach 6 Monaten", "grün", "–",
     "noch nicht gebaut · Muster: TF{}".format(next(f["id"][2:] for f in FALL if "TF12-Muster" in f["titel"]))),
]

# ---------------------------------------------------------------- Ausgabe JSON
def eingabe(f):
    if f["freitext"]:
        return f["freitext"]
    vo = {k: v for k, v in f["vo"].items()}
    if vo.get("ergaenzendes_heilmittel") == {"name": None, "einheiten": None}:
        pass
    return vo


export = {
    "titel": "Testbatterie Verordnungs-Check",
    "stand": "2026-10-20",
    "pruefdatum": P.isoformat(),
    "hinweis": "Synthetische Daten. Soll-Werte aus den Regelwerken abgeleitet (HeilM-RL, Heilmittelkatalog, KBV-Diagnoseliste), Vier-Augen-Prüfung vor Einsatz als Referenzstandard nötig.",
    "faelle": [{
        "id": f["id"], "set": f["set"], "kategorie": f["kat"], "pruefer": f["pruefer"],
        "eingang": "freitext" if f["freitext"] else "json", "ab_v5": f["v5"], "titel": f["titel"],
        "fundstelle": f["fundstelle"], "hinweis": f["hinweis"],
        "eingabe": eingabe(f),
        "soll": f["soll"],
        **({"soll_strukturiert": f["vo"]} if f["freitext"] else {}),
    } for f in FALL],
}
with open(f"{OUT_DIR}/testbatterie.json", "w", encoding="utf-8") as fh:
    json.dump(export, fh, ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- Ausgabe Markdown
AMP = {"gruen": "🟢 grün", "gelb": "🟡 gelb", "rot": "🔴 rot"}
AGENT = {"formal": "Formal", "diagnose": "Diagnose", "menge": "Mengen", "frist": "Fristen"}


def bef(f):
    if not f["soll"]["befunde"]:
        return "–"
    return "; ".join(f"{AGENT[b['agent']]}: {b['feld']}" + (" (Hinweis)" if b["status"] == "hinweis" else "")
                     for b in f["soll"]["befunde"])


def kurz(f):
    vo = f["vo"]
    hm = " + ".join(f"{h['name']} {h['einheiten'] if h['einheiten'] is not None else '–'}" for h in vo["heilmittel"])
    erg = vo.get("ergaenzendes_heilmittel") or {}
    if erg.get("name"):
        hm += f" (+ {erg['name']} {erg['einheiten']})"
    return f"{vo.get('icd10') or '–'} · {vo.get('diagnosegruppe') or '–'} · {hm}"


L = []
w = L.append
w("# Testbatterie Verordnungs-Check")
w("")
w("*Stand 20.10.2026 · 13 angewandte Tests + 100 neue Fälle · alle Daten synthetisch*")
w("")
w("## Zweck und Nutzung")
w("")
w("- **Diese Datei** ist zum Lesen, Prüfen und Abhaken. **`testbatterie.json`** enthält dieselben Fälle maschinenlesbar für einen automatischen Testlauf (z. B. per n8n-Schleife oder Import in die Tabelle `testfaelle`).")
w("- **Eingabe:** JSON-Fälle als Text in den Chat „Rezeption: Verordnung eingeben“ einfügen. Der Workflow erkennt sie als strukturiert und überspringt den Extraktor. Freitext-Fälle testen zusätzlich Extraktion und PII-Entfernung.")
w(f"- **Festes Prüfdatum:** {P.strftime('%d.%m.%Y')} für alle neuen Fälle (Feld `pruefdatum`). Nur so sind Fristen reproduzierbar. Beim Formular gilt immer das Tagesdatum.")
w("- **Referenzstandard** sind ausschließlich die Regelwerke (HeilM-RL, Heilmittelkatalog, KBV-Diagnoseliste). Die Soll-Werte sind aus den Texten in eurer Wissensbasis abgeleitet. ⚠️ Vor dem Einsatz als Referenz: Vier-Augen-Prüfung durch das Team, vor allem der Grenzfälle.")
w("- **Kein Lernen auf den Test:** Keine ICD-Codes aus diesen Fällen in Prompts übernehmen.")
w("- **Wertung:** Pro Fall zählt die Gesamtampel. Befunde geben an, welcher Prüfer was melden muss. Zusätzliche Hinweise in grünen Fällen zählen als Fehlalarm, zusätzliche rote Befunde als kritischer Fehlalarm.")
w("")
w("### Aufteilung")
w("")
w("| Set | Zweck | Fälle | 🟢 | 🟡 | 🔴 | Grenzfälle |")
w("|---|---|---|---|---|---|---|")
D = [f for f in FALL if f["set"] == "D"]
for name, lst, zweck in [("E", E, "Evaluationsset (Holdout): nur für die formale Messung, nie zum Nachbessern"),
                         ("D", D, "Entwicklungsset: darf zum Nachbessern genutzt werden")]:
    w(f"| **{name}** | {zweck} | {len(lst)} | {amp(lst, 'gruen')} | {amp(lst, 'gelb')} | {amp(lst, 'rot')} | {cnt(lst, kat='grenzfall')} |")
w("")
w(f"Das E-Set erfüllt die Vorgaben aus `docs/erfolgskriterien.md`: ≥ 12 grün, ≥ 8 gelb, ≥ 25 rot (je Prüfer ≥ 5: Formal {stats['E_rot_formal']}, Diagnose {stats['E_rot_diagnose']}, Mengen {stats['E_rot_menge']}, Fristen {stats['E_rot_frist']}), ≥ 5 Grenzfälle. Bei 3 Läufen je Fall sind das {3 * len(E)} Prüfungen.")
w("")
w(f"**Ab v5:** {sum(f['v5'] for f in FALL)} Fälle brauchen die Verordnungsfall-Prüfung mit Historie (Feld `vorverordnungen`, Spalte „v5“). Bis v5 steht, zählen sie nicht in die Quote. Das Feldformat ist ein **Vorschlag** und mit Derk abzustimmen.")
w("")
w("### Angewandte Regeln")
w("")
w("| Regel | Wert | Fundstelle |")
w("|---|---|---|")
for r in [
    ("Behandlungsbeginn", "≤ 28 Kalendertage nach Ausstellung, dringlich ≤ 14", "HeilM-RL § 15 Abs. 1, sonst ungültig nach Abs. 2"),
    ("Unterbrechung", "> 14 Kalendertage ohne angemessene Begründung → ungültig", "HeilM-RL § 16 Abs. 4"),
    ("Pflichtangaben", "vollständig ausgefüllter Vordruck", "HeilM-RL § 13 Abs. 1 und 2"),
    ("Höchstmenge je VO (WS, EX)", "bis zu 6 Einheiten, aufteilbar auf max. 3 vorrangige Heilmittel", "Heilmittelkatalog; HeilM-RL § 12 Abs. 2"),
    ("Ergänzendes Heilmittel", "max. eins; Einheiten richten sich nach den vorrangigen", "HeilM-RL § 12 Abs. 3, § 7 Abs. 5"),
    ("Ergänzende Heilmittel je Gruppe", "WS: Wärme, Kälte, Traktion, Elektro, hydroelektrische Bäder · EX: ohne Traktion", "Heilmittelkatalog"),
    ("Leitsymptomatik WS/EX", "a, b oder x (patientenindividuell)", "Heilmittelkatalog"),
    ("Frequenz", "Empfehlung 1–3× wöchentlich; Abweichung ohne Dokumentation zulässig", "Heilmittelkatalog; HeilM-RL § 12 Abs. 1 Satz 4"),
    ("Verordnungsfall", "gleicher Patient, ICD 3-stellig, Diagnosegruppe, Verordner; neu nach 6 Monaten ohne Verordnung", "HeilM-RL § 7 Abs. 1 und 3"),
    ("Orientierende Menge (WS, EX)", "18 Einheiten je Fall, nur vorrangige zählen → Überschreitung = gelb", "Heilmittelkatalog; HeilM-RL § 7 Abs. 2"),
    ("Entlassmanagement", "Verordnungen aus dem Entlassmanagement zählen nicht zum Fall", "HeilM-RL § 16a Abs. 5"),
    ("Besonderer Verordnungsbedarf", "Code auf der Liste mit passender Diagnosegruppe, ggf. mit Zweitcode → Hinweis (gelb), nie rot", "KBV-Diagnoseliste"),
]:
    w("| " + " | ".join(r) + " |")
w("")
w("## Teil A: Bereits angewandte Tests")
w("")
w("Quelle: `supabase/seed/testfaelle.sql` (Prüfdatum 12.10.2026), Ausführungen des Merge-Workflows vom 20.10.2026.")
w("")
w("| ID | Eingang | Fall | Soll | Erwartete Befunde | Letztes Ergebnis |")
w("|---|---|---|---|---|---|")
for row in TEIL_A:
    w("| " + " | ".join(row) + " |")
w("")
w("## Teil B: 100 neue Fälle")
w("")
TITEL = [("gruen", "🟢 Grüne Fälle"), ("gelb", "🟡 Gelbe Fälle"), ("rot", "🔴 Rote Fälle"), ("grenzfall", "⚖️ Grenzfälle")]
for kat, ueber in TITEL:
    lst = [f for f in FALL if f["kat"] == kat]
    w(f"### {ueber} ({len(lst)})")
    w("")
    w("| ✓ | ID | Set | Prüfer | Fall | Kurz | Eingang | v5 | Soll | Erwartete Befunde | Fundstelle |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for f in lst:
        titel = f["titel"] + (f" — *{f['hinweis']}*" if f["hinweis"] else "")
        w(f"| ☐ | {f['id']} | {f['set']} | {f['pruefer']} | {titel} | {kurz(f)} | {'Freitext' if f['freitext'] else 'JSON'} | {'ja' if f['v5'] else ''} | {AMP[f['soll']['gesamtstatus']]} | {bef(f)} | {f['fundstelle']} |")
    w("")
w("## Teil C: Eingaben zum Kopieren")
w("")
w("Aufklappen, Inhalt kopieren und in den Chat einfügen.")
w("")
for f in FALL:
    w(f"<details><summary><b>{f['id']}</b> · {AMP[f['soll']['gesamtstatus']]} · {f['titel']}</summary>")
    w("")
    if f["freitext"]:
        w("```text")
        w(f["freitext"])
        w("```")
    else:
        w("```json")
        w(json.dumps(eingabe(f), ensure_ascii=False))
        w("```")
    w("")
    w("</details>")
    w("")
w("## Auffälligkeiten beim Erstellen")
w("")
w("1. **TF10 ist nach Regelwerk falsch bewertet.** Der Heilmittelkatalog kennt für EX (und WS) nur die Leitsymptomatik a, b und x. TF10 nutzt „c“ und erwartete grün. *Im Merge-Workflow seit 23.10.2026 als Code-Fakt umgesetzt (`leitsymptomatik_zulaessig`), siehe `docs/aenderungsprotokoll.md`.* Seed von TF10 am 27.10.2026 nach Vier-Augen-Prüfung angepasst (Grenzfall TF{}).".format(
    next(f["id"][2:] for f in FALL if f["titel"] == "Leitsymptomatik c bei EX")))
w("2. **Frequenz-Hinweise widersprechen dem Regelwerk.** Nach HeilM-RL § 12 Abs. 1 Satz 4 darf der Arzt ohne zusätzliche Dokumentation von der Frequenzempfehlung abweichen. *Teamentscheidung 27.10.2026:* Die Abweichung bleibt ein Hinweis (gelb), kein Fehler; der Code prüft sie seit 27.10. (`frequenz_im_rahmen`). TF108 und TF22 erwarten gelb, siehe `docs/aenderungsprotokoll.md`.")
w("3. **Zweitcode beim besonderen Verordnungsbedarf.** Bei M50.1, M51.1, M47.2-, M48.0- und Z96.6- verlangt die KBV-Liste den Zweitcode. Ohne ihn gibt es keinen Hinweis (Grenzfall TF{}). M75.1 steht ohne Zweitcode auf der Liste: Grüne Fälle mit M75.1 und EX gibt es deshalb nicht.".format(
    next(f["id"][2:] for f in FALL if f["titel"] == "M50.1 ohne Zweitcode G55.1")))
w("4. **Zulässigkeit des ergänzenden Heilmittels hat keinen Prüfer.** Traktion ist nur bei WS vorgesehen. Klären, ob der Mengen-Prüfer das ins Mandat bekommt.")
w("5. **Merge-Workflow rechnet noch mit 28 € je Einheit** (Knoten „Ergebnis zusammenführen“). Laut Ist-Interview sind es 32 €.")
w("6. **Für v5:** Ergänzende Einheiten und Verordnungen aus dem Entlassmanagement dürfen nicht in die Fallsumme (HeilM-RL § 7 Abs. 2 Satz 2, § 16a Abs. 5). Der Verordnungsfall gilt je Verordner (§ 7 Abs. 3).")
w("7. **Massage über 12 Einheiten je Fall** ist bewusst nicht enthalten. Ob das eine harte Grenze oder orientierend ist, ist weiter offen.")
w("")
with open(f"{OUT_DIR}/testbatterie.md", "w", encoding="utf-8") as fh:
    fh.write("\n".join(L))
print("ok", len(FALL))
