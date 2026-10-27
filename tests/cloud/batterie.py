"""Testbatterie Verordnungs-Check gegen n8n Cloud.

Liest alle Testfälle aus Supabase (über die Datenbrücke, n8n/sdk/testbatterie-datenbruecke.mjs), schickt jeden Fall an den
Chat-Webhook des Cloud-Workflows, vergleicht Ampel und erwartete Befunde mit dem Soll
und schreibt jedes Ergebnis in die Supabase-Tabelle testlaeufe.
E-Set: 3 Wiederholungen (Erfolgskriterien), alle anderen: 1.
Aufruf: VC_TOKEN=... python tests/cloud/batterie.py <lauf-id>   (optional FILTER=<regex>)
"""
import json, os, sys, time, uuid, urllib.request, concurrent.futures as cf, threading, pathlib

BASIS = "https://tobsi1911.app.n8n.cloud"
CHAT = BASIS + "/webhook/7fce36dd-bfee-4fce-b4e0-389bc842f3a7/chat"
BRUECKE = BASIS + "/webhook/vc-testlauf-ergebnis"
TOKEN = os.environ["VC_TOKEN"]  # Token der Datenbrücke, nie ins Repository
LAUF = sys.argv[1] if len(sys.argv) > 1 else "2026-10-27-cloud"
WORKFLOW = "QkVyxJe3slDIo03h@502b5ade"
PARALLEL = 4

HIER = pathlib.Path(__file__).parent
ERG = HIER / "ergebnisse"
# Testfälle kommen aus Supabase (Tabelle testfaelle) über die Datenbrücke
req = urllib.request.Request(BASIS + "/webhook/vc-testfaelle-export", headers={"x-token": TOKEN})
faelle = json.loads(urllib.request.urlopen(req, timeout=120).read().decode())["faelle"]
auftraege = []
import os, re as _re
FILTER = os.environ.get("FILTER")
for f in sorted(faelle, key=lambda x: x["name"]):
    if FILTER and not _re.match(FILTER, f["name"]): continue
    e = f["erwartete_befunde"]
    for w in range(1, (3 if e.get("set") == "E" else 1) + 1):
        auftraege.append((f, w))

def post(url, daten, kopf=None, zeit=240):
    req = urllib.request.Request(url, data=json.dumps(daten).encode(), headers={"Content-Type": "application/json", **(kopf or {})})
    with urllib.request.urlopen(req, timeout=zeit) as r:
        return json.loads(r.read().decode())

def gefunden(befunde, erw):
    st = erw["status"] if isinstance(erw["status"], list) else [erw["status"]]
    return any(b.get("agent") == erw["agent"] and erw["feld"].lower() in str(b.get("feld", "")).lower() and b.get("status") in st for b in befunde)

def pruefe(fall, wdh):
    e = fall["erwartete_befunde"]
    vo = fall["verordnung"]
    eingabe = vo["freitext"] if isinstance(vo, dict) and "freitext" in vo else json.dumps(vo, ensure_ascii=False)
    start = time.time(); fehler = None; antwort = {}
    for versuch in range(2):
        try:
            antwort = post(CHAT, {"action": "sendMessage", "sessionId": f"tb-{uuid.uuid4().hex[:8]}", "chatInput": eingabe})
            fehler = None
            break
        except Exception as ex:
            fehler = f"{type(ex).__name__}: {ex}"
            time.sleep(5)
    dauer = int((time.time() - start) * 1000)
    ist = antwort.get("gesamtstatus")
    befunde = antwort.get("befunde") or []
    fehlend = [x for x in e.get("erwartet", []) if not gefunden(befunde, x)]
    soll = e["gesamtstatus"]
    return {
        "lauf": LAUF, "workflow_id": WORKFLOW, "testfall_id": fall["id"], "fall": fall["name"],
        "quelle": e.get("quelle"), "set": e.get("set"), "wiederholung": wdh,
        "soll": soll, "ist": ist if ist else ("fehler" if fehler else "ohne_ampel"),
        "ampel_ok": ist == soll, "befunde_ok": ist is not None and not fehlend,
        "fehlende_befunde": fehlend, "kritischer_fehlalarm": soll in ("gruen", "gelb") and ist == "rot",
        "dauer_ms": dauer, "fehler": fehler or (None if ist else str(antwort)[:300]),
        "antwort": {"befunde": befunde, "ab_v5": e.get("ab_v5"), "kategorie": e.get("kategorie"), "eingang": e.get("eingang")},
    }

ergebnisse, puffer, sperre = [], [], threading.Lock()
def sende(rows):
    for _ in range(3):
        try:
            post(BRUECKE, {"rows": rows}, {"x-token": TOKEN}, 120); return
        except Exception as ex:
            print("Brücke:", ex, flush=True); time.sleep(5)

print(f"{len(auftraege)} Prüfungen, Lauf {LAUF}", flush=True)
with open(ERG / f"{LAUF}.jsonl", "a") as aus, cf.ThreadPoolExecutor(PARALLEL) as pool:
    for i, r in enumerate(pool.map(lambda a: pruefe(*a), auftraege), 1):
        aus.write(json.dumps(r, ensure_ascii=False) + "\n"); aus.flush()
        ergebnisse.append(r); puffer.append(r)
        print(f"{i:3}/{len(auftraege)} {r['fall'][:45]:45} soll={r['soll']:5} ist={r['ist']:6} {'OK' if r['ampel_ok'] else 'XX'} {r['dauer_ms']/1000:.0f}s", flush=True)
        if len(puffer) >= 20:
            sende(puffer); puffer = []
    if puffer: sende(puffer)
print("fertig", flush=True)
