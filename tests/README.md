# Tests: Gebrauchsanweisung

Dieser Ordner enthält drei Arten von Tests:

| Datei | Was | Wofür |
|---|---|---|
| `fakten.test.mjs`, `diagnosen.test.mjs` | Automatische Tests der Code-Knoten „Fristen berechnen“ und „Diagnosen auswählen“ | Rechnen und Regeln ohne Sprachmodell prüfen |
| `pii.test.mjs` | Redaktion: Marker, Pflichtangaben, Dienst-Fallback, Verdrahtung | Prüfen, dass kein Identifikator an ein Modell geht |
| `formular.test.mjs` | Erfassungsmaske gegen Workflow-Schema, Vorlagen-Seite gegen den Seed, Abdeckung der 18 Kriterien | Prüfen, dass Maske, Seed und Workflow zusammenpassen |
| `workflow.test.mjs` | Struktur des Exports: eindeutige IDs, gültige Verbindungen, Erreichbarkeit, keine Credential-IDs, Code syntaktisch | Prüfen, dass der Export importierbar bleibt |
| `testbatterie.md` | 13 angewandte Tests + 100 neue Fälle zum Lesen und Abhaken | Prüfen der Soll-Werte, manuelle Testläufe |
| `testbatterie.json` | Dieselben 100 Fälle maschinenlesbar | Automatischer Testlauf, Auswertung |
| `testbatterie_erzeugen.py` | Generator für MD und JSON | Soll-Werte ändern, ohne dass MD und JSON auseinanderlaufen |

```bash
npm test                    # alle automatischen Tests (Fakten, Diagnoseauswahl, PII, Formular)
npm run test:redaktion      # Regeln des Redaktionsdienstes (Python, ohne Modell)
npm run vorlagen:pruefen    # 23 Seed-Fälle gegen den laufenden Workflow, mit Abdeckungstabelle
```

Die automatischen Tests lesen den Workflow-Export `n8n/merge-formular-vier-pruefer.json`. Ändert sich ein Code-Knoten, schlagen sie fehl, bevor die Änderung in die Instanz wandert.

## 0. Seed-Fälle: ein Fall pro Prüfkriterium

`supabase/seed/testfaelle.sql` enthält 23 Fälle. Jeder Fall ändert gegenüber dem grünen Basisfall (TF01) genau eine Sache, damit der Befund eindeutig zuzuordnen ist; TF01–TF10 sind die ursprünglichen Fälle und Kontrollfälle, TF11–TF23 schließen die Lücken zu den 18 Prüfkriterien (Zuordnung in [`../docs/pruefkriterien.md`](../docs/pruefkriterien.md)).

`npm run vorlagen:pruefen` schickt alle Fälle an den Webhook und prüft **Ampel und erwartete Befunde**. Am Ende steht, welches Kriterium von welchem Fall abgedeckt ist. Dieselben Fälle lassen sich auf der Vorlagen-Seite (`npm run formular` → `/vorlagen`) einzeln anklicken.

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

Für schnelle Kontrollen nach einer Änderung: D-Fälle oder die Seed-Fälle TF01–TF23 (`supabase/seed/testfaelle.sql`).

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
