"""Vergleicht redaktion/regeln.py (Original, ohne Modell) mit dem JavaScript-Port
redaktion/cloud/regeln.js, der in n8n Cloud im Knoten "Text redigieren (Regeln)" läuft.
Aufruf: python redaktion/cloud/vergleich.py   (braucht node)
"""
import json, pathlib, subprocess, sys
HIER = pathlib.Path(__file__).parent
sys.path.insert(0, str(HIER.parent))
from regeln import redigiere
texte = json.loads((HIER / "vergleich-texte.json").read_text())
js = (HIER / "regeln.js").read_text()
skript = js + ";console.log(JSON.stringify(JSON.parse(require('fs').readFileSync(process.argv[1])).map(t=>{const r=redigiere(t);return [r.text,r.entfernt]})))"
aus = json.loads(subprocess.run(["node", "-e", skript, str(HIER / "vergleich-texte.json")], capture_output=True, text=True, check=True).stdout)
fehler = 0
for t, (jt, je) in zip(texte, aus):
    pt, pe = redigiere(t, [])
    if (pt, pe) != (jt, je):
        fehler += 1
        print("ABWEICHUNG\n PY:", pt, pe, "\n JS:", jt, je)
print(f"{len(texte)} Texte, {fehler} Abweichungen")
sys.exit(1 if fehler else 0)
