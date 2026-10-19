# Build-Plan

*Sprint 1 · Stand 13.10.2026 · Verantwortlich: Derk*

*Annahme:* Ein Sprint entspricht einer Kalenderwoche. Die IHK-Prüfung liegt in der ersten Novemberwoche (genauer Termin offen), die MSIT-Ausbildung endet am 09.11.2026.

## Ausgangslage

Der Kern läuft bereits: Workflow v4 mit vier Prüfern, Ampel und Protokoll. Er wurde mit 10 Testfällen geprüft. Offen sind die Verordnungsfall-Prüfung, die formale Evaluation, Governance und die Präsentation.

## Meilensteine

| Woche | Sprint | Meilenstein (überprüfbar) | Verantwortlich |
|---|---|---|---|
| bis Fr 16.10. | 1 | Design-Briefing vollständig im Repo (Scope, Erfolgskriterien, Implementierungsweg, Architektur, Build-Plan), an den Peer übergeben | Thomas, alle |
| 19.–23.10. | 2 | **Workflow v5 mit Verordnungsfall-Prüfung:** Tabelle für die Verordnungshistorie angelegt, synthetische Vorverordnungen geladen, die zwei neuen Testfälle TF11 (gelb, Menge im Fall überschritten) und TF12 (grün, neuer Fall nach 6 Monaten) liefern die Soll-Ampel, Tests für den neuen Code-Node grün. Business Case als erste Fassung. Peer-Feedback beantwortet. | Derk (Build), Thomas (Business Case) |
| 26.–30.10. | 3 | **Formale Evaluation** nach `erfolgskriterien.md`: mindestens 50 neue Fälle, je 3 Läufe, Ziel ≥ 98 %, Ergebnis gegen die Schwellen. Governance mit EU-AI-Act-Einordnung fertig. Chat mit Anmeldung veröffentlicht, Workflow-Export v5 im Repo. **IHK-Deck als vollständiger Entwurf.** | Derk (Evaluation, Deployment), Valentin (Governance, Deck) |
| ab 02.11. | 4 | Deck final, Vier-Augen-Korrektur, mindestens eine Probe mit Zeitmessung (4 × 15 min). Präsentation gehalten. | alle |

## Abhängigkeiten

1. **Erfolgskriterien vor Testset:** Die Soll-Ampeln der neuen Fälle hängen an den Kriterien. Deshalb werden sie in Sprint 1 festgelegt.
2. **Verordnungsfall-Prüfung vor Evaluation:** Das Testset in Sprint 3 enthält gelbe Fälle aus dieser Prüfung. Deshalb muss v5 bis Fr 23.10. stehen.
3. **Evaluation vor Deck:** Die Folie zur Erfolgsmessung braucht die Ergebnisse aus Sprint 3. Die übrigen Folien beginnen parallel in Sprint 3.
4. **Ist-Interview vor Business Case:** erledigt am 16.10.2026 (32 € je Einheit, ca. 40 Verordnungen pro Woche, ca. 10 Absetzungen bzw. 500 € pro Jahr), siehe `ist-interview.md`.

## Puffer

- **Freitag 23.10. nachmittags** und **Montag 26.10.** sind frei gehalten für Nacharbeit an der Verordnungsfall-Prüfung.
- **Was zuerst gestrichen wird**, wenn es eng wird:
  1. Foto-Upload, nur bei Puffer überhaupt angefangen,
  2. Stabilitätsläufe von 3 auf 2 reduziert,
  3. Testset von 12 auf das Minimum von 10 Fällen.
- **Nicht gestrichen** werden die harten Bedingungen der Erfolgskriterien und die Governance.

## Größtes Risiko

**Verordnungsfall-Prüfung: richtige Abgrenzung des Verordnungsfalls** (ICD 3-stellig, Diagnosegruppe, Arzt, 6-Monats-Regel) mit einer Historie, die das System nur aus eigenen Prüfungen kennt.

- **Warum zuerst:** Sie ist die einzige neue Komponente mit unklarem Ergebnis. Deshalb steht sie am Anfang von Sprint 2.
- **Frühwarnung:** Liefert der Code-Node bis **Mittwoch 21.10.** nicht für alle Tests die exakte Summe, wird vereinfacht. Dann gilt nur „gleicher Patient + ICD 3-stellig + gleicher Arzt“, ohne die 6-Monats-Regel, und das wird als Grenze dokumentiert.
- **Rückfallposition:** Klappt auch das nicht bis Fr 23.10., kommt die Verordnungsfall-Prüfung als getesteter Code-Baustein und Konzept ins Repo, aber nicht in den Workflow. Die Evaluation läuft dann ohne gelbe Verordnungsfall-Fälle.

## Weitere Risiken

| Risiko | Reaktion |
|---|---|
| Team ab 19.10.2026 nur noch zu dritt (Süle hat das Team verlassen) | Aufgaben neu verteilt (README); was zuerst gestrichen wird, gilt unverändert |
| 50 Testfälle sind viel Handarbeit | Fälle als Varianten aus Vorlagen erzeugen, Soll-Ampel und Fundstelle trotzdem vorher vom Team festgelegt |
| IHK-Termin liegt früh in der Woche des 02.11. | Deck-Entwurf schon in Sprint 3; Termin sofort klären |
| Ist-Interview kommt nicht zustande | Business Case mit klar markierten Annahmen; Schwerpunkt auf Fristen- und Formfehlern, die die Regelwerke belegen |
| LLM-Ergebnisse schwanken zwischen Läufen | Drei Läufe je Fall; Schwankung wird als Ergebnis berichtet, nicht versteckt |
