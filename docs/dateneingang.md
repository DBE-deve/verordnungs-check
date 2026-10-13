# Dateneingang: Wie Daten in den Workflow kommen

*Stand 13.10.2026*

Der Verordnungs-Check hat drei Datenquellen.

## 1. Regelwerke (Wissensbasis): umgesetzt

- Der Workflow **„Wissensbasis laden“** lädt Heilmittel-Richtlinie, Heilmittelkatalog und KBV-Diagnoseliste direkt von G-BA und KBV.
- Er zerlegt die Texte in Abschnitte, erzeugt Embeddings und speichert alles in der Supabase-Tabelle `documents`.
- Auslöser ist ein Knopfdruck, nur bei einer neuen Fassung nötig (z. B. KBV-Diagnoseliste jeweils zum 1. Januar). Vorher die Tabelle leeren, sonst entstehen Dubletten.

## 2. Die einzelne Verordnung

| Stufe | Eingang | Status |
|---|---|---|
| Prototyp | Rezeption tippt die Angaben in den Chat oder fügt sie als Text bzw. JSON ein. Der Agent „Verordnung erfassen“ überführt sie in das feste Schema. | umgesetzt |
| Demo | **Foto der Verordnung** (Muster 13) im Chat hochladen. Das Sprachmodell liest das Bild aus, danach läuft der bestehende Ablauf. Nur mit selbst ausgefüllten Muster-Formularen und erfundenen Daten. | geplant (Sprint 2) |
| Echtbetrieb | Übergabe direkt aus der Praxissoftware (Export oder Schnittstelle), abhängig von der eingesetzten Software | Ausblick |

## 3. Historie für den Verordnungsfall: geplant (Sprint 2)

**Fachlicher Hintergrund (§ 7 HeilM-RL):** Ein Verordnungsfall umfasst alle Verordnungen für denselben Patienten mit derselben ICD-Stelle (erste 3 Zeichen) und derselben Diagnosegruppe beim selben Arzt. Ein neuer Fall beginnt nach 6 Monaten ohne neue Verordnung.

- Die **orientierende Behandlungsmenge** (WS/EX: bis zu 18 Einheiten) darf überschritten werden. Der Arzt dokumentiert dann die Gründe in seiner Patientenakte.
- **Harte Grenze (§ 12 Abs. 6):** Massagetherapie und standardisierte Heilmittelkombination höchstens 12 Einheiten je Verordnungsfall.

**Umsetzung:**

- Jede geprüfte Verordnung wird mit einem **Patienten-Pseudonym** (praxisinterne Patientennummer, kein Name) in Supabase gespeichert. So wächst die Historie mit jeder Prüfung von selbst.
- Ein Code-Knoten ermittelt die früheren Verordnungen desselben Falls und berechnet:
  - Einheiten bisher und inklusive der aktuellen Verordnung
  - ob die orientierende Behandlungsmenge überschritten ist
  - verbrauchte Einheiten Massage bzw. standardisierte Heilmittelkombination
- Der **Mengen-Prüfer** bekommt diese Werte als verbindliche Fakten. Die Zahl der Prüfer bleibt bei vier.

**Bewertung in der Ampel:**

| Situation | Status |
|---|---|
| Orientierende Behandlungsmenge überschritten | Hinweis (gelb): Arzt dokumentiert die Gründe in seiner Akte |
| Massage oder Heilmittelkombination über 12 Einheiten im Fall | Hinweis (gelb); „fehlerhaft“ (rot) erst, wenn geklärt ist, dass die Kasse dafür kürzt |

**Grenzen:**

- Das System kennt nur Verordnungen, die es selbst geprüft hat. Am Start ist die Historie leer. Im Echtbetrieb wäre ein einmaliger Import der laufenden Fälle aus der Praxissoftware nötig. Im Prototyp verwenden wir synthetische Vorverordnungen.
- Der Verordnungsfall hängt am Arzt. Therapie in einer anderen Praxis ist für das System unsichtbar. Deshalb ergibt die Fallprüfung immer nur einen Hinweis, nie ein Rot wegen der 18er-Menge.
- Datenschutz: Die Historie speichert Behandlungsverläufe pro Patient (Gesundheitsdaten, Art. 9 DSGVO). Pseudonymisierung, Löschfristen und Zugriffsschutz werden in [`governance.md`](governance.md) ergänzt.

## Offene Fragen an die Praxis

1. Was ist das Alltagsproblem genau: Ärzte verweigern Folgeverordnungen, die Praxis verliert den Überblick über die Einheiten, oder die Kasse hat schon gekürzt?
2. Gab es Kürzungen wegen Massage über 12 Einheiten je Verordnungsfall?
3. Gibt es in der Praxissoftware eine Patientennummer, die als Pseudonym dienen kann?
