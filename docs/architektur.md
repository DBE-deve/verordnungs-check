# Architektur

## Ablauf

1. **Chat (n8n Chat Trigger):** Die Rezeption fügt die Angaben einer Verordnung als Text oder JSON ein.
2. **Verordnung erfassen:** Ein LLM-Agent überführt den Text in ein festes JSON-Schema. Fehlende Angaben werden `null`, nichts wird geraten.
3. **Fristen berechnen (Code-Node):** Tage zwischen Ausstellung, geplantem Beginn und letzter Behandlung werden deterministisch berechnet. Grenzwerte: Behandlungsbeginn 28 Tage (14 Tage bei dringlichem Behandlungsbedarf), Unterbrechung 14 Tage.
4. **Vier Prüf-Agenten:** Jeder Agent bekommt die Verordnung und die berechneten Fakten, durchsucht seinen Ausschnitt der Wissensbasis und liefert Befunde im gemeinsamen JSON-Schema.
5. **Ergebnis zusammenführen (Code-Node):** Ampel (rot / gelb / grün), Absetzungsrisiko, Antworttext.
6. **Protokoll:** Prüfung und Befunde werden in Supabase gespeichert.
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

Row Level Security ist auf allen Tabellen aktiv, es gibt keine öffentlichen Policies. Nur n8n greift mit dem service_role-Schlüssel zu.

## Bewusste Design-Entscheidungen (Trade-offs)

| Entscheidung | Alternative | Begründung |
|---|---|---|
| Vier spezialisierte Prüfer | Ein Allround-Agent | Jedes Mandat einzeln erklärbar und testbar; Fehler lassen sich einem Prüfer zuordnen |
| Fristen im Code | LLM rechnet Tage | Datumsarithmetik ist keine Sprachaufgabe; reproduzierbar |
| Ampel im Code | LLM entscheidet Gesamtstatus | Nachvollziehbar und prüfbar |
| Ein gemeinsames Sprachmodell | Ein Modell je Agent | Geringere Kosten, einfachere Wartung |
| Freigabe durch die Rezeption | Automatische Abweisung | Mensch behält die Verantwortung (menschliche Aufsicht) |
| Synthetische Daten | Echte Verordnungen | Gesundheitsdaten (Art. 9 DSGVO) gehören nicht in einen Prototyp |
