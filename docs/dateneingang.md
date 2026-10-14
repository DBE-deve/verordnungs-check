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
| Demo | **Foto der Verordnung** (Muster 13) im Chat hochladen. Das Sprachmodell liest das Bild aus, danach läuft der bestehende Ablauf. Nur mit selbst ausgefüllten Muster-Formularen und erfundenen Daten. | nur bei Puffer (Entscheidung 13.10.2026: Verordnungsfall-Prüfung hat Vorrang) |
| Echtbetrieb | Übergabe direkt aus der Praxissoftware (Export oder Schnittstelle), abhängig von der eingesetzten Software | Ausblick |

## 3. Historie für den Verordnungsfall: geplant (Sprint 2)

**Fachlicher Hintergrund (§ 7 HeilM-RL):** Ein Verordnungsfall umfasst alle Verordnungen für denselben Patienten mit derselben ICD-Stelle (erste 3 Zeichen) und derselben Diagnosegruppe beim selben Arzt. Ein neuer Fall beginnt nach 6 Monaten ohne neue Verordnung.

- Die **orientierende Behandlungsmenge** (WS/EX: bis zu 18 Einheiten) darf überschritten werden. Der Arzt dokumentiert dann die Gründe in seiner Patientenakte.
- **Harte Grenze (§ 12 Abs. 6):** Massagetherapie und standardisierte Heilmittelkombination höchstens 12 Einheiten je Verordnungsfall.
  - *Zu prüfen:* Ein AOK-Merkblatt (Stand 2023) führt die 12 Einheiten bei Massage als **orientierende** Behandlungsmenge, nicht als harte Grenze. Bis zur Klärung am Richtlinientext bleibt die Ampel gelb (siehe unten).

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

## 4. Rückmeldung der Praxis (13.10.2026)

| Frage | Antwort der Praxis |
|---|---|
| Alltagsproblem | Nicht die Menge **einer** Verordnung ist das Problem, sondern **Folgeverordnungen**. Ärzte wissen oft selbst nicht, wie viel sie auf denselben Schlüssel schon verordnet haben. Prüft die Praxis das nicht, zahlt die Kasse nach ihrer Erfahrung nichts. |
| Massage über 12 Einheiten | Nicht gesondert beantwortet; das Problem betrifft Folgeverordnungen allgemein. |
| Patientennummer als Pseudonym | Ja, die Praxissoftware vergibt Patientennummern. |
| Zusätzlich genannt | Parallele Verordnungen (z. B. Lymphdrainage obere und untere Extremität): Die **Behandlungszeit** beider Verordnungen zusammen kann den übernommenen Zeitbedarf überschreiten. Selten, aber teuer. |
| Zusätzlich genannt | Bei zwei parallelen Verordnungen darf nicht dieselbe Behandlung doppelt abgerechnet werden. Es muss nach Diagnosegruppe **und** Art der Behandlung unterschieden werden. |

### Abgeleitete Prüfregeln

| Prüfregel | Inhalt | Umfang |
|---|---|---|
| Verordnungsfall-Prüfung | Einheiten aller Verordnungen im selben Fall (Patient + ICD 3-stellig + Diagnosegruppe + Arzt) summieren und gegen die orientierende Behandlungsmenge stellen | Sprint 2, im Code, 2 neue Testfälle |
| Zeitprüfung Lymphdrainage | Bei parallelen Lymphdrainage-Verordnungen die gesamte Behandlungszeit je Sitzung gegen den zulässigen Zeitbedarf (Stadium + Anzahl Körperteile) prüfen | Ausbaustufe nach MSIT. *Annahme:* Die genaue Grenze bei parallelen Verordnungen ist noch nicht am Richtlinientext belegt. |
| Doppelabrechnungs-Prüfung | Parallele Verordnungen müssen sich in Diagnosegruppe und Heilmittel unterscheiden | Ausbaustufe nach MSIT. *Annahme:* Regelquelle (HeilM-RL bzw. Rahmenvertrag) noch zu belegen. |

Alle drei Regeln nutzen dieselbe Historie aus Abschnitt 3. Die Architektur (n8n, vier Prüfer, Supabase) bleibt unverändert, es kommen nur die Historie-Tabelle und ein Lookup-Knoten dazu.

### Widerspruch, der vor der Präsentation geklärt sein muss

Laut § 32 Abs. 1b SGB V brauchen Verordnungen über die orientierende Behandlungsmenge hinaus **keine Genehmigung** der Kasse; der Arzt dokumentiert die Gründe. Die Erfahrung der Praxis („Kasse zahlt keinen Cent“) passt dazu nicht. Mögliche Erklärungen:

- Die Kürzung betraf die **Höchstmenge je Verordnung** (z. B. mehr als 6 Einheiten WS/EX), nicht die orientierende Menge.
- Kassen setzen in der Praxis trotzdem ab. Das wäre dann ein Fall für den Widerspruch, nicht für eine rote Ampel.

Bis zur Klärung bleibt die Bewertung aus Abschnitt 3: Überschreiten der orientierenden Menge = **gelb**.

## Offene Fragen an die Praxis

1. Gibt es ein geschwärztes Absetzungsschreiben der Kasse, aus dem die Begründung hervorgeht?
2. Wie oft kommt es zu solchen Absetzungen, und um welchen Betrag geht es grob pro Jahr? (Grundlage für den Business Case)
3. Lymphdrainage: Welche Kombination aus Stadium, Körperteilen und Zeit wurde konkret abgesetzt?
