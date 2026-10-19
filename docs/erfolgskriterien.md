# Erfolgskriterien

*Sprint 1 · Stand 19.10.2026 · Verantwortlich: Derk · gilt für die formale Evaluation in Sprint 3*

> **Änderung 19.10.2026:** Zielwert nach Rückmeldung der Instruktorin von 90 % auf **98 %** angehoben, Testset deshalb von 12 auf **50 Fälle** vergrößert (Begründung unten).

## Referenzstandard

Maßstab sind **ausschließlich die Regelwerke**: Heilmittel-Richtlinie (in Kraft seit 05.08.2025), Heilmittelkatalog und KBV-Diagnoseliste (Stand 01.01.2026). Für jeden Testfall legt das Team **vor dem Testlauf** fest:

- die Soll-Ampel (grün / gelb / rot),
- jeden erwarteten Befund (Prüfer + Feld),
- die Fundstelle im Regelwerk, aus der sich das ergibt.

Ein Testfall ohne belegte Fundstelle wird nicht gewertet. Erfahrungen aus der Praxis fließen nur in die Auswahl der Testfälle ein, nicht in die Bewertung.

## Ampel-Definition

| Ampel | Bedeutung |
|---|---|
| **rot** | Mindestens ein Befund „fehlt“ oder „fehlerhaft“: So behandelt, droht die Absetzung. |
| **gelb** | Kein roter Befund, aber mindestens ein Hinweis, z. B. orientierende Behandlungsmenge im Verordnungsfall überschritten. |
| **grün** | Keine Befunde außer „ok“. |

## Primäre Kennzahl

**Ampel-Trefferquote ≥ 98 %** auf einem neuen Testset von **mindestens 50 Fällen**, die nie zum Nachbessern der Prompts verwendet wurden. Bei 50 Fällen heißt das: höchstens **eine** falsche Ampel.

- **Korrekt** heißt: Die ausgegebene Ampel stimmt mit der Soll-Ampel überein.
- **Grenzfall:** Ampel richtig, aber der Befund kommt vom falschen Prüfer oder nennt das falsche Feld. Das zählt für die Primärkennzahl als bestanden und wird in der Sekundärkennzahl „Befund-Genauigkeit“ als Fehler gezählt.
- **Stabilität:** Jeder Fall läuft dreimal. Gewertet wird die Ampel, die mindestens zweimal kam.

## Harte Bedingungen (unabhängig von der Quote)

| Bedingung | Schwelle | Warum |
|---|---|---|
| Übersehene rote Verordnung (Soll rot, Ist grün) | **0** | Das ist der teure Fehler: Die Kasse setzt ab. |
| Kritische Fehlalarme („fehlt“/„fehlerhaft“ ohne Grundlage) | **≤ 1** über alle Fälle | Zu viel Rot und die Rezeption ignoriert das Werkzeug. |
| Verordnungsfall-Prüfung: berechnete Einheiten im Verordnungsfall | **100 % exakt** | Reine Rechnung im Code, da gibt es keine Toleranz. |

## Sekundäre Kennzahlen

| Kennzahl | Ziel |
|---|---|
| Befund-Genauigkeit (richtiger Prüfer und richtiges Feld je erwartetem Fehler) | ≥ 95 % |
| Fundstelle bei jedem Befund „fehlt“, „fehlerhaft“ oder „hinweis“ vorhanden | 100 % |
| Stabilität (gleiche Ampel in allen 3 Läufen) | ≥ 95 % der Fälle |
| Laufzeit je Prüfung | ≤ 30 s |
| Kosten je Prüfung | ≤ 5 Cent |

Zur Einordnung, der Stand von v4 (13.10.2026, 10 Fälle, je 1 Lauf): 10/10 Ampeln korrekt, 0 kritische Fehlalarme, 24,0 s, ca. 3–4 Cent. **Diese Zahlen zählen nicht als formale Evaluation:** TF01–TF07 wurden zum Nachbessern verwendet, und die Kriterien entstanden erst danach.

## Wann das System noch nicht bereit ist

Das System gilt als **nicht bereit**, wenn eines davon eintritt:

- Ampel-Trefferquote **unter 95 %** (mehr als 2 falsche Ampeln bei 50 Fällen),
- **mindestens eine** übersehene rote Verordnung,
- **mehr als 2** kritische Fehlalarme,
- Die Verordnungsfall-Prüfung rechnet in einem Fall falsch.

Zwischen 95 % und 98 % gilt das System als „bedingt bereit“: Die Ursachen werden einzeln benannt, die Schwelle wird nicht nachträglich gesenkt.

## Zusammensetzung des Testsets (Sprint 3)

Mindestens 50 neue Fälle:

| Art | Anzahl | Inhalt |
|---|---|---|
| grün | ≥ 12 | regelkonform, darunter Folgeverordnungen innerhalb der Menge |
| gelb | ≥ 8 | Verordnungsfall-Prüfung: orientierende Menge überschritten |
| rot | ≥ 25 | je Prüfer mindestens 5 |
| Grenzfall | ≥ 5 | genau an einer Frist oder Mengengrenze |

Schwerpunkt Folgeverordnungen: Laut Ist-Interview entstehen ca. 90 % der Fehler bei Doppel- und Folgeverordnungen ([`ist-interview.md`](ist-interview.md)). Keine ICD-Codes aus diesen Fällen in den Prompts.

## Warum 50 Fälle

Mit 12 Fällen lässt sich 98 % nicht messen: Schon eine falsche Ampel ergibt 92 %. Erst ab 50 Fällen erlaubt das Ziel genau einen Fehler. Mit 3 Läufen je Fall sind das 150 Prüfungen, nach heutigem Stand ca. 1 Stunde Laufzeit und ca. 5–6 € Modellkosten.

*Einordnung:* 50 Fälle sind ein Funktionsnachweis, kein statistischer Beweis für 98 % im Betrieb. Dafür dient der Parallelbetrieb im Pilot: Die Rezeption prüft einige Wochen wie bisher, das System läuft mit (Zusage der Praxis, F11).

*Vergleich:* Menschliche Doppelkontrollen sind laut Praxis bzw. Literatur höchstens etwa 85 % wirksam.
