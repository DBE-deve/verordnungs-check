# Architektur

## Ablauf

Ein Workflow, zwei Trigger: das **n8n-Formular** (Muster 13, Standardweg) und der **Chat** (Text oder JSON). Beide Wege laufen ab dem Knoten `Eingabe prüfen` identisch weiter; die Weiche `Kam vom Formular?` entscheidet am Ende, ob die Antwort auf der Abschlussseite des Formulars oder im Chat erscheint.

1. **Eingang:** Das Formular liefert bereits eine strukturierte Verordnung (`Verordnung bauen` → `Verordnung übernehmen`). Im Chat erkennt `Eingabe prüfen`, ob schon JSON vorliegt (`Verordnung strukturiert?`); strukturierte Eingaben überspringen den Extraktor.
2. **Redaktion im Freitext-Weg:** `Text redigieren` ruft den Redaktionsdienst (`redaktion/`, HuggingFace-NER plus Regeln) auf. Ist er nicht erreichbar, greift `Text redigieren (Muster)` mit denselben Regeln im Workflow; `Redaktion übernehmen` stellt für beide Wege dieselbe Form her. Details: [`pii-redaktion.md`](pii-redaktion.md).
3. **Verordnung erfassen (nur Freitext):** Ein LLM-Agent (`gpt-4.1-mini`) überführt den Text in ein festes JSON-Schema. Fehlende Angaben werden `null`, nichts wird geraten; Marker wie `[LANR]` übernimmt er als Wert.
4. **Diagnosen auswählen (nur Freitext):** Auf den Vordruck passen zwei ICD-Zeilen; die Regel steht in [`vordruck-muster13.md`](vordruck-muster13.md), Abschnitt 5.
5. **Fakten berechnen (Code-Node „Fristen berechnen“):** Alles, was sich als Regel aufschreiben lässt, rechnet der Code, nicht das LLM:
   - Tage zwischen Ausstellung, geplantem Beginn und letzter Behandlung. Grenzwerte: Behandlungsbeginn 28 Tage (14 Tage bei dringlichem Behandlungsbedarf), Unterbrechung 14 Tage
   - Format von LANR und BSNR (9 Ziffern)
   - Körperregion des ICD-Codes → passende Diagnosegruppe (WS oder EX) für die häufigsten Muskel-Skelett-Bereiche
   - Summe der Einheiten (`summe_einheiten` für die Absetzungsrechnung, `summe_einheiten_vorrangig` für die Höchstmenge – ergänzende Heilmittel zählen dort nicht, § 7 Abs. 5)
   - Anzahl vorrangiger Heilmittel und Anwesenheit der Pflichtangaben (`pflichtangaben`), ermittelt aus dem Original, damit die späteren Redaktions-Marker nicht als „fehlt“ gelesen werden

   Die Prüf-Agenten erhalten diese Werte als „berechnete Fakten“, die für sie verbindlich sind. Abgesichert durch `tests/fakten.test.mjs` und `tests/pii.test.mjs`.
6. **PII entfernen (Code-Node):** Vor den Prüf-Agenten werden direkte Identifikatoren durch Marker wie `[Name]` ersetzt und Freitexte entfernt; das Original bleibt für Protokoll und Antwort erhalten.
7. **Vier Prüf-Agenten:** Jeder Agent bekommt die redigierte Verordnung und die berechneten Fakten und liefert Befunde im gemeinsamen JSON-Schema. Formal-, Diagnose- und Mengen-Prüfer durchsuchen dafür ihren Ausschnitt der Wissensbasis (Vektorsuche); der **Fristen-Prüfer arbeitet ohne Werkzeug**, weil sein Mandat vollständig durch die berechneten Fakten bestimmt ist (§ 15 HeilM-RL). Alle Agenten sind auf Wiederholung gesetzt (`retryOnFail`, 3 Versuche).
8. **Ergebnis zusammenführen (Code-Node):** Ampel (rot / gelb / grün), Absetzungsrisiko, Antworttext – und die Diagnoseauswahl für Protokoll und Erfassungsmaske.
9. **Protokoll:** `Prüfung protokollieren` und `Befunde protokollieren` speichern Lauf und Befunde in Supabase.
10. **Antwort:** `Kam vom Formular?` leitet auf die Abschlussseite (`Ergebnis anzeigen`) oder in den Chat (`Antwort an Rezeption`).

Die 18 Prüfpunkte samt Entscheidungsgrundlage stehen in [`pruefkriterien.md`](pruefkriterien.md).

**Ab Sprint 2 (Verordnungsfall-Prüfung):** Zwischen Schritt 5 und 6 kommen zwei Komponenten dazu:

- **Historie abfragen** (Supabase-Node): liest frühere Verordnungen mit demselben Patienten-Pseudonym, derselben ICD-Stelle (3-stellig), Diagnosegruppe und LANR.
- **Verordnungsfall berechnen** (Code-Node): summiert die Einheiten und prüft die 6-Monats-Regel (§ 7 HeilM-RL).

Das Ergebnis geht als berechneter Fakt an den Mengen-Prüfer. Jede geprüfte Verordnung wird in die Historie geschrieben. Details: [`dateneingang.md`](dateneingang.md).

## Befund-Schema

```json
{
  "agent": "formal | diagnose | menge | frist",
  "befunde": [
    { "feld": "LANR", "status": "ok | fehlt | fehlerhaft | hinweis", "fundstelle": "…", "korrekturhinweis": "…" }
  ]
}
```

## Datenmodell (Supabase)

| Tabelle | Zweck |
|---|---|
| `documents` | Wissensbasis für den RAG (Text, Metadaten, Embedding 1536) |
| `pruefungen` | Ein Prüflauf pro Verordnung: Eingabe, Ampel, Risiko, Dauer, Freigabe |
| `befunde` | Ein Befund pro Prüfpunkt und Agent |
| `testfaelle` | Synthetische Verordnungen mit erwarteten Befunden für die Evaluation |
| `verordnungen` *(Sprint 2)* | Historie: eine Zeile je geprüfter Verordnung mit Pseudonym, ICD 3-stellig, Diagnosegruppe, LANR, Datum, Einheiten |

Row Level Security ist auf allen Tabellen aktiv, es gibt keine öffentlichen Policies. Nur n8n greift mit dem service_role-Schlüssel zu.

## Deployment

| Punkt | Umsetzung |
|---|---|
| Laufzeitumgebung | n8n Cloud (vorhandene Instanz des Teams) |
| Sprachmodell | OpenAI `gpt-4.1-mini` (Temperatur 0,1), Embeddings `text-embedding-3-small` |
| Datenbank | Supabase, Region eu-central-1 (Frankfurt) |
| PII-Redaktion (Freitext) | Dienst aus `redaktion/` über `REDAKTION_URL`; ohne erreichbaren Dienst greift der Muster-Fallback im Workflow |
| Zugang für die Rezeption | n8n-Formular (Muster 13) und Chat. Veröffentlicht wird er erst mit aktiver Anmeldung (Basic Auth oder n8n-Login), sonst kann jeder mit dem Link Kosten erzeugen |
| Nachweis einer erfolgreichen Ausführung | Ausführungsprotokoll in n8n und Zeilen in `pruefungen` und `befunde`. Für die Präsentation: Screenshots je Ampelfarbe |
| Veröffentlichung | Workflow-Export (ohne Credential-IDs und Webhook-ID), Migrationen, Testdaten und Tests auf GitHub |

Komponenten im Detail und Begründung des Wegs: [`implementierung.md`](implementierung.md).

## Bewusste Design-Entscheidungen (Trade-offs)

| Entscheidung | Alternative | Begründung |
|---|---|---|
| Vier spezialisierte Prüfer | Ein Allround-Agent | Jedes Mandat einzeln erklärbar und testbar; Fehler lassen sich einem Prüfer zuordnen |
| Ein Workflow für Chat und Formular | Zwei Workflows, Formular ruft den Chat-Webhook | Ein Import, ein Protokollpfad, keine HTTP-Abhängigkeit zwischen Workflows |
| Redaktionsdienst plus Muster-Fallback | Nur Dienst (fail-closed) oder nur Muster | Volle NER-Redaktion, wo der Dienst läuft; ohne ihn bleibt der Freitext-Weg nutzbar, ohne je Rohtext an ein Modell zu geben |
| Fristen im Code | LLM rechnet Tage | Datumsarithmetik ist keine Sprachaufgabe; reproduzierbar |
| ICD-Bereich → Diagnosegruppe im Code | LLM ordnet zu | In der Evaluation ordnete das LLM einen Knie-Code der Wirbelsäule zu, trotz Prompt-Regeln (siehe `evaluation.md`) |
| Ampel im Code | LLM entscheidet Gesamtstatus | Nachvollziehbar und prüfbar |
| Ein gemeinsames Sprachmodell | Ein Modell je Agent | Geringere Kosten, einfachere Wartung |
| Freigabe durch die Rezeption | Automatische Abweisung | Mensch behält die Verantwortung (menschliche Aufsicht) |
| Synthetische Daten | Echte Verordnungen | Gesundheitsdaten (Art. 9 DSGVO) gehören nicht in einen Prototyp |
