"""Auswertung der Testbatterie nach den Erfolgskriterien (docs/erfolgskriterien.md, Kap. 5)."""
import json, sys, statistics, collections, pathlib, urllib.request, os
HIER = pathlib.Path(__file__).parent

LAUF = sys.argv[1] if len(sys.argv) > 1 else "2026-10-27-cloud"
rows = [json.loads(l) for l in open(HIER / "ergebnisse" / f"{LAUF}.jsonl")]
# Dokumentierte Soll-Korrekturen (27.10.2026), für beide Läufe gleich angewandt:
# TF108: Teamentscheidung Thomas – Frequenz außerhalb 1–3x/Woche = Hinweis (gelb), analog TF22
# TF10: Heilmittelkatalog EX kennt nur Leitsymptomatik a, b, x – "c" ist fehlerhaft (rot); mit Valentin abzustimmen
KORREKTUR = {"TF108 ": "gelb", "TF10 ": "rot"}
for r in rows:
    for p, soll in KORREKTUR.items():
        if r["fall"].startswith(p):
            r["soll"] = soll; r["ampel_ok"] = r["ist"] == soll
            r["kritischer_fehlalarm"] = soll in ("gruen", "gelb") and r["ist"] == "rot"

def mehrheit(xs):
    c = collections.Counter(xs).most_common()
    return c[0][0] if c and (len(xs) < 3 or c[0][1] >= 2) else "uneinig"

faelle = collections.defaultdict(list)
for r in rows:
    faelle[(r["set"], r["fall"])].append(r)

def auswerten(setname, nur_ohne_v5=True):
    sel = {k: v for k, v in faelle.items() if k[0] == setname and (not nur_ohne_v5 or not v[0]["antwort"].get("ab_v5"))}
    n = len(sel); ok = 0; rot_uebersehen = []; krit = []; instabil = []; falsch = []
    for (s, name), rs in sel.items():
        soll = rs[0]["soll"]; ist = mehrheit([r["ist"] for r in rs])
        if ist == soll: ok += 1
        else: falsch.append((name, soll, ist, [r["ist"] for r in rs]))
        if soll == "rot" and ist != "rot": rot_uebersehen.append(name)
        if soll in ("gruen", "gelb") and ist == "rot": krit.append(name)
        if len({r["ist"] for r in rs}) > 1: instabil.append(name)
    alle = [r for rs in sel.values() for r in rs]
    erw = sum(len(r["fehlende_befunde"]) for r in alle)
    # Befund-Genauigkeit: Anteil der erwarteten Befunde, die gefunden wurden
    soll_bef = 0; gef = 0; fund_ok = 0; fund_n = 0
    for r in alle:
        f = next(x for x in [r]);
    return dict(n=n, ok=ok, quote=ok / n if n else None, rot_uebersehen=rot_uebersehen, krit=krit,
                instabil=instabil, falsch=falsch, laeufe=len(alle),
                median_s=statistics.median(r["dauer_ms"] for r in alle) / 1000 if alle else None,
                fehler=[r["fall"] for r in alle if r["fehler"]])

def befund_genauigkeit(setname):
    faelle_db = {f["name"]: f for f in json.load(open(HIER / "ergebnisse" / "testfaelle_2026-10-27.json"))["faelle"]}
    soll = gef = 0; fund_n = fund_ok = 0
    for r in rows:
        if r["set"] != setname or r["antwort"].get("ab_v5"): continue
        e = faelle_db[r["fall"]]["erwartete_befunde"].get("erwartet", [])
        soll += len(e); gef += len(e) - len(r["fehlende_befunde"])
        for b in r["antwort"]["befunde"]:
            if b["status"] != "ok":
                fund_n += 1
                fs = (b.get("fundstelle") or "").strip()
                if fs and "nicht gefunden" not in fs.lower(): fund_ok += 1
    return dict(erwartet=soll, gefunden=gef, quote=gef / soll if soll else None, fund_n=fund_n, fund_ok=fund_ok,
                fund_quote=fund_ok / fund_n if fund_n else None)

ergebnis = {}
for s in ("E", "D", "S"):
    a = auswerten(s); b = befund_genauigkeit(s); a.update(befund=b); ergebnis[s] = a
    print(f"\n=== Set {s}: {a['n']} Fälle (ohne v5), {a['laeufe']} Läufe")
    if a["n"]:
        print(f"Ampel korrekt: {a['ok']}/{a['n']} = {a['quote']:.1%}")
        print(f"Übersehene rote: {len(a['rot_uebersehen'])} {a['rot_uebersehen']}")
        print(f"Kritische Fehlalarme: {len(a['krit'])} {a['krit']}")
        print(f"Stabil: {a['n']-len(a['instabil'])}/{a['n']}  instabil: {a['instabil']}")
        print(f"Befund-Genauigkeit: {b['gefunden']}/{b['erwartet']} = {b['quote'] if b['quote'] is None else format(b['quote'],'.1%')}")
        print(f"Fundstelle: {b['fund_ok']}/{b['fund_n']}")
        print(f"Median Laufzeit: {a['median_s']:.1f} s; Fehler: {a['fehler']}")
        for x in a["falsch"]: print("  FALSCH", x)
v5 = [k for k, v in faelle.items() if v[0]["antwort"].get("ab_v5")]
print("\nv5-Fälle (nicht gewertet):", len(v5))
json.dump(ergebnis, open(HIER / "ergebnisse" / f"{LAUF}_auswertung.json", "w"), ensure_ascii=False, indent=1)
