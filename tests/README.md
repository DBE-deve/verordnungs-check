# Tests: Gebrauchsanweisung

Dieser Ordner enthält zwei Arten von Tests:

| Datei | Was | Wofür |
|---|---|---|
| `fakten.test.mjs` | Automatische Tests für den Code-Knoten „Fristen berechnen“ | Fristen, Formate, ICD-Zuordnung ohne Sprachmodell prüfen (`node tests/fakten.test.mjs`) |
| `testbatterie.md` | 13 angewandte Tests + 100 neue Fälle zum Lesen und Abhaken | Prüfen der Soll-Werte, manuelle Testläufe |
| `testbatterie.json` | Dieselben 100 Fälle maschinenlesbar | Automatischer Testlauf, Auswertung |
| `testbatterie_erzeugen.py` | Generator für MD und JSON | Soll-Werte ändern, ohne dass MD und JSON auseinanderlaufen |

## 1. Vor dem ersten Einsatz: Soll-Werte prüfen

Die Soll-Werte sind aus den Regelwerken abgeleitet (HeilM-RL, Heilmittelkatalog, KBV-Diagnoseliste). Bevor sie als Referenzstandard gelten:

1. Eine zweite Person geht `testbatterie.md` Fall für Fall durch und setzt das Häkchen ☐ → ☑, wenn Soll-Ampel und Befunde zur Fundstelle passen.
2. **Grenzfälle zuerst** (Abschnitt ⚖️). Dort steht jeweils die Auslegung, die das Team bestätigen muss.
3. Abweichungen nicht in MD oder JSON von Hand ändern, sondern im Generator (Abschnitt 5).

## 2. Welche Fälle wofür?

| Set | Regel |
|---|---|
| **E** (Evaluation, 65 Fälle) | Nur für die formale Messung in Sprint 3. **Nie zum Nachbessern verwenden.** Wer einen E-Fall ansieht, um einen Prompt zu ändern, macht ihn wertlos. |
| **D** (Entwicklung, 35 Fälle) | Darf zum Testen und Nachbessern benutzt werden. |
| Spalte **v5** | Braucht die Verordnungsfall-Prüfung mit Historie. Bis v5 steht, nicht mitzählen. |

Für schnelle Kontrollen nach einer Änderung: D-Fälle oder die Seed-Fälle TF01–TF10 (`supabase/seed/testfaelle.sql`).

## 3. Einen Fall manuell prüfen

1. In n8n den Workflow **Verordnungs-Check – Merge** öffnen, Chat „Rezeption: Verordnung eingeben“ starten.
2. In `testbatterie.md`, Teil C, den Fall aufklappen und den Inhalt kopieren:
   - **JSON-Fälle** komplett einfügen. Der Workflow erkennt sie als strukturiert und überspringt den Extraktor.
   - **Freitext-Fälle** testen zusätzlich die Erfassung und die PII-Entfernung.
3. Ampel und Befunde mit Teil B vergleichen.

Das Prüfdatum ist in allen neuen Fällen fest auf den **26.10.2026** gesetzt (Feld `pruefdatum`), damit Fristen bei jedem Lauf gleich ausfallen. Über das Formular gilt dagegen immer das Tagesdatum.

## 4. Formale Evaluation (Sprint 3)

1. **Jeden E-Fall dreimal** laufen lassen (65 × 3 = 195 Prüfungen, grob 1,5 h und 6–8 €; *Annahme* nach den bisherigen Werten von ca. 30 s und 3–4 Cent je Prüfung).
2. Ergebnisse stehen in Supabase: Tabelle `pruefungen` (Gesamtampel, Dauer) und `befunde` (je Prüfer und Feld). Zuordnung über `verordnung_ref` (`VO-0013` … `VO-0112`).
3. Auswerten gegen `soll` in `testbatterie.json`:

| Kennzahl | Wie gezählt | Ziel (`docs/erfolgskriterien.md`) |
|---|---|---|
| Ampel korrekt | Gesamtampel = Soll | ≥ 98 % |
| Übersehene Rote | Soll rot, Ergebnis grün oder gelb | 0 |
| Kritischer Fehlalarm | Befund „fehlt“/„fehlerhaft“, der nicht im Soll steht | ≤ 1 |
| Unnötiger Hinweis | Hinweis, der nicht im Soll steht | so wenig wie möglich |
| Stabilität | alle 3 Läufe gleiche Ampel | ≥ 95 % |
| Laufzeit, Kosten | Dauer aus `pruefungen`, Kosten aus dem OpenAI-Dashboard | ≤ 30 s, ≤ 5 Cent |

Die Befund-Felder im Soll sind Klartext („Einheiten je Verordnung“, „Behandlungsbeginn“ …). Beim Vergleich zählt, dass der richtige Prüfer das richtige Thema meldet, nicht der exakte Wortlaut.

## 5. Soll-Werte oder Fälle ändern

```bash
# Fall in tests/testbatterie_erzeugen.py anpassen, dann:
python3 tests/testbatterie_erzeugen.py tests
```

Der Generator prüft beim Erzeugen, dass jeder Fall in seiner Kategorie landet und das E-Set die Mindestvorgaben erfüllt (≥ 12 grün, ≥ 8 gelb, ≥ 25 rot mit je ≥ 5 pro Prüfer, ≥ 5 Grenzfälle). Schlägt eine Prüfung fehl, bricht er mit einer Meldung ab.

## Regeln

- Nur synthetische Daten, keine echten Patientendaten.
- Keine ICD-Codes aus den Testfällen in Prompts übernehmen (kein Lernen auf den Test).
- Referenzstandard sind ausschließlich die Regelwerke.
