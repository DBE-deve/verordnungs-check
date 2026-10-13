# Erfolgskriterien

*Sprint 1 · Stand 13.10.2026 · Verantwortlich: Süle · gilt für die formale Evaluation in Sprint 3*

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

**Ampel-Trefferquote ≥ 90 %** auf einem neuen Testset von **mindestens 12 Fällen**, die nie zum Nachbessern der Prompts verwendet wurden.

- **Korrekt** heißt: Die ausgegebene Ampel stimmt mit der Soll-Ampel überein.
- **Grenzfall:** Ampel richtig, aber der Befund kommt vom falschen Prüfer oder nennt das falsche Feld. Das zählt für die Primärkennzahl als bestanden und wird in der Sekundärkennzahl „Befund-Genauigkeit“ als Fehler gezählt.
- **Stabilität:** Jeder Fall läuft dreimal. Gewertet wird die Ampel, die mindestens zweimal kam.

## Harte Bedingungen (unabhängig von der Quote)

| Bedingung | Schwelle | Warum |
|---|---|---|
| Übersehene rote Verordnung (Soll rot, Ist grün) | **0** | Das ist der teure Fehler: Die Kasse setzt ab. |
| Kritische Fehlalarme („fehlt“/„fehlerhaft“ ohne Grundlage) | **≤ 1** über alle Fälle | Zu viel Rot und die Rezeption ignoriert das Werkzeug. |
| R1: berechnete Einheiten im Verordnungsfall | **100 % exakt** | Reine Rechnung im Code, da gibt es keine Toleranz. |

## Sekundäre Kennzahlen

| Kennzahl | Ziel |
|---|---|
| Befund-Genauigkeit (richtiger Prüfer und richtiges Feld je erwartetem Fehler) | ≥ 90 % |
| Fundstelle bei jedem Befund „fehlt“, „fehlerhaft“ oder „hinweis“ vorhanden | 100 % |
| Stabilität (gleiche Ampel in allen 3 Läufen) | ≥ 90 % der Fälle |
| Laufzeit je Prüfung | ≤ 30 s |
| Kosten je Prüfung | ≤ 5 Cent |

Zur Einordnung, der Stand von v4 (13.10.2026, 10 Fälle, je 1 Lauf): 10/10 Ampeln korrekt, 0 kritische Fehlalarme, 24,0 s, ca. 3–4 Cent. **Diese Zahlen zählen nicht als formale Evaluation:** TF01–TF07 wurden zum Nachbessern verwendet, und die Kriterien entstanden erst danach.

## Wann das System noch nicht bereit ist

Das System gilt als **nicht bereit**, wenn eines davon eintritt:

- Ampel-Trefferquote **unter 80 %**,
- **mindestens eine** übersehene rote Verordnung,
- **mehr als 2** kritische Fehlalarme,
- R1 rechnet in einem Fall falsch.

Zwischen 80 % und 90 % gilt das System als „bedingt bereit“: Die Ursachen werden einzeln benannt, die Schwelle wird nicht nachträglich gesenkt.

## Zusammensetzung des Testsets (Sprint 3)

Mindestens 12 neue Fälle, davon mindestens 3 grün, 2 gelb (R1: orientierende Menge überschritten), 6 rot (je mindestens 1 je Prüfer) und 1 Grenzfall genau an einer Frist. Keine ICD-Codes aus diesen Fällen in den Prompts.
