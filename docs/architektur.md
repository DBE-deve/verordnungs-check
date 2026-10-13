# Architektur

## Ablauf

1. **Chat (n8n Chat Trigger):** Die Rezeption fügt die Angaben einer Verordnung als Text oder JSON ein.
2. **Verordnung erfassen:** Ein LLM-Agent überführt den Text in ein festes JSON-Schema. Fehlende Angaben werden `null`, nichts wird geraten.
3. **Fakten berechnen (Code-Node „Fristen berechnen“):** Alles, was sich als Regel aufschreiben lässt, rechnet der Code, nicht das LLM:
   - Tage zwischen Ausstellung, geplantem Beginn und letzter Behandlung. Grenzwerte: Behandlungsbeginn 28 Tage (14 Tage bei dringlichem Behandlungsbedarf), Unterbrechung 14 Tage
   - Format von LANR und BSNR (9 Ziffern)
   - Körperregion des ICD-Codes → passende Diagnosegruppe (WS oder EX) für die häufigsten Muskel-Skelett-Bereiche
   - Summe der Einheiten, Anzahl vorrangiger Heilmittel

   Die Prüf-Agenten erhalten diese Werte als „berechnete Fakten“, die für sie verbindlich sind. Abgesichert durch `tests/fakten.test.mjs`.
4. **Vier Prüf-Agenten:** Jeder Agent bekommt die Verordnung und die berechneten Fakten, durchsucht seinen Ausschnitt der Wissensbasis und liefert Befunde im gemeinsamen JSON-Schema.
5. **Ergebnis zusammenführen (Code-Node):** Ampel (rot / gelb / grün), Absetzungsrisiko, Antworttext.
6. **Protokoll:** Prüfung und Befunde werden in Supabase gespeichert.

**Ab Sprint 2 (R1, Verordnungsfall):** Zwischen Schritt 3 und 4 kommen zwei Komponenten dazu:

- **Historie abfragen** (Supabase-Node): liest frühere Verordnungen mit demselben Patienten-Pseudonym, derselben ICD-Stelle (3-stellig), Diagnosegruppe und LANR.
- **Verordnungsfall berechnen** (Code-Node): summiert die Einheiten und prüft die 6-Monats-Regel (§ 7 HeilM-RL).

Das Ergebnis geht als berechneter Fakt an den Mengen-Prüfer. Jede geprüfte Verordnung wird in die Historie geschrieben. Details: [`dateneingang.md`](dateneingang.md).
7. **Antwort:** Die Rezeption erhält Ampel, Korrekturhinweise und Fundstellen.

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
| Datenbank | Supabase, Region eu-central-1 (Frankfurt) |
| Zugang für die Rezeption | n8n-Chat. Veröffentlicht wird er erst mit aktiver Anmeldung (Basic Auth oder n8n-Login), sonst kann jeder mit dem Link Kosten erzeugen |
| Nachweis einer erfolgreichen Ausführung | Ausführungsprotokoll in n8n und Zeilen in `pruefungen` und `befunde`. Für die Präsentation: Screenshots je Ampelfarbe |
| Veröffentlichung | Workflow-Export (ohne Credential-IDs und Webhook-ID), Migrationen, Testdaten und Tests auf GitHub |

Komponenten im Detail und Begründung des Wegs: [`implementierung.md`](implementierung.md).

## Bewusste Design-Entscheidungen (Trade-offs)

| Entscheidung | Alternative | Begründung |
|---|---|---|
| Vier spezialisierte Prüfer | Ein Allround-Agent | Jedes Mandat einzeln erklärbar und testbar; Fehler lassen sich einem Prüfer zuordnen |
| Fristen im Code | LLM rechnet Tage | Datumsarithmetik ist keine Sprachaufgabe; reproduzierbar |
| ICD-Bereich → Diagnosegruppe im Code | LLM ordnet zu | In der Evaluation ordnete das LLM einen Knie-Code der Wirbelsäule zu, trotz Prompt-Regeln (siehe `evaluation.md`) |
| Ampel im Code | LLM entscheidet Gesamtstatus | Nachvollziehbar und prüfbar |
| Ein gemeinsames Sprachmodell | Ein Modell je Agent | Geringere Kosten, einfachere Wartung |
| Freigabe durch die Rezeption | Automatische Abweisung | Mensch behält die Verantwortung (menschliche Aufsicht) |
| Synthetische Daten | Echte Verordnungen | Gesundheitsdaten (Art. 9 DSGVO) gehören nicht in einen Prototyp |
