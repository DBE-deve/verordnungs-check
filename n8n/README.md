# n8n-Workflows

| Datei | Workflow | Zweck |
|---|---|---|
| `merge-formular-vier-pruefer.json` | Verordnungs-Check | **Der** Workflow: Chat **und** Muster-13-Formular in einem, PII-Redaktion, Diagnoseauswahl, vier Prüf-Agenten, Ampel, Protokoll |
| `wissensbasis-laden.json` | Verordnungs-Check – Wissensbasis laden | Lädt die Regelwerke als PDF, teilt sie in Abschnitte, erzeugt Embeddings und speichert sie in Supabase |
| `cloud-verordnungs-check.json` | Verordnungs-Check – Cloud (Valentins Architektur, Regel-Redaktion) | **Stand in der n8n Cloud seit 27.10.2026**: Merge-Workflow 1:1, Freitext-Redaktion als Code-Knoten (`redaktion/cloud/regeln.js`, Port von `redaktion/regeln.py` ohne Namensmodell), fünf Regel-Fakten mit Code-Urteilen. Formular `/form/verordnungs-check-cloud` |
| `verordnungsbackup-scan.json` | verordnungsbackup | Scan-Variante in der Cloud: Upload `/form/verordnungsbackup`, Felder per Vision auslesen, danach Merge-Prüfung. Stand vor den Code-Urteilen vom 27.10., Prototyp für den Foto-/Scan-Kanal |
| `sdk/testbatterie-datenbruecke.mjs` | Verordnungs-Check – Testbatterie Datenbrücke | Webhooks für `tests/cloud/batterie.py`: Testfälle aus Supabase lesen, Ergebnisse nach `testlaeufe` schreiben (Token nur in der Instanz) |
| `sdk/testfaelle-laden.mjs` | Verordnungs-Check – Testfälle laden | Einmalig: Seed und Testbatterie aus dem Repo in die Tabelle `testfaelle` |

Seit dem Merge vom 27.10.2026 gibt es nur noch diesen einen Prüf-Workflow. Die früheren Exporte (`vier-pruefer.json` als v4-Fallback, `formular.json` als eigener Formular-Workflow) sind entfallen – ihre Historie steht in Git und in [`../docs/aenderungsprotokoll.md`](../docs/aenderungsprotokoll.md).

## Import

**Über die Oberfläche** (Cloud und lokal): Workflows → *Import from File* → `merge-formular-vier-pruefer.json`.

**Per CLI** in eine bestehende Instanz: Der CLI-Import braucht IDs in der Datei und löst Credentials nur über die ID auf (getestet mit n8n 2.20.8). `npm run n8n:vorbereiten` erzeugt dafür passende Dateien:

```bash
npm run n8n:vorbereiten
docker cp .n8n/tmp/import-fremdinstanz/verordnungs-check.json <container>:/tmp/
docker exec <container> n8n import:workflow --input=/tmp/verordnungs-check.json
docker exec <container> n8n publish:workflow --id=<workflow-id>   # älter: update:workflow --active=true
docker restart <container>
```

## Credentials

Die Knoten verweisen auf diese Namen – in der Instanz genau so anlegen oder die Verweise anpassen:

| Name | Typ | Inhalt |
|---|---|---|
| `OpenAI account` | OpenAI | API-Key; Chat-Modell `gpt-4.1-mini` (Temperatur 0,1), Embeddings `text-embedding-3-small` |
| `Supabase Verordnungs_check` | Supabase | Host-URL und service_role-Key des Projekts – nie ins Repository |

Die Wissensbasis ist mit `text-embedding-3-small` (1536 Dimensionen) geladen. Ein anderes Embedding-Modell macht die Vektorsuche unbrauchbar: `wissensbasis-laden.json` erneut ausführen.

## Adressen

| Was | Adresse | Wo einstellen |
|---|---|---|
| Chat | `/webhook/verordnungs-check/chat` | `webhookId` des Chat-Triggers |
| Formular | `/form/verordnungs-check-merge` | Feld *Path* im Form-Trigger |
| Abschlussseite | erscheint nach dem Absenden | Knoten `Ergebnis anzeigen` |

Die Weiche `Kam vom Formular?` entscheidet am Ende, ob die Antwort auf der Formular-Abschlussseite oder im Chat erscheint.

## PII-Redaktion im Freitext-Weg

`Text redigieren` ruft den Redaktionsdienst aus [`../redaktion/`](../redaktion/README.md) auf:

- Standard-URL: `http://host.docker.internal:5680/redigieren`
- In der Cloud über die Umgebungsvariable `REDAKTION_URL` setzen:
  `={{ $env.REDAKTION_URL || 'http://host.docker.internal:5680/redigieren' }}` steht bereits im Knoten.
- Ist der Dienst nicht erreichbar, greift automatisch `Text redigieren (Muster)` – dieselben Regeln als Code im Workflow. Es geht **nie** Rohtext an ein Modell, nur weniger gründlich redigiert.

Der Formular-Weg braucht den Dienst nicht: Dort ersetzt `PII entfernen` die Felder deterministisch.

## Eigenheiten beim CLI-Import

- **Knoten-Reihenfolge:** n8n ermittelt Vorgänger/Nachfolger teilweise über die Position in der `nodes`-Liste. Steht ein Knoten dort vor seinen Nachfolgern, kann die Ausführung mit `Cannot read properties of undefined` scheitern.
- **webhookId:** Trigger-Knoten (`chatTrigger`, `formTrigger`) brauchen eine `webhookId`, sonst meldet die Aktivierung `No webhook path could be found` und die Adresse liefert 404.
- **Modellwahl:** `gpt-4.1-mini` ist bewusst klein gewählt (Kosten, Latenz). Beobachtet: einzelne Läufe brechen mit `Model output doesn't fit required format` ab; dagegen sind alle fünf Agenten auf `retryOnFail` (3 Versuche) gesetzt.
