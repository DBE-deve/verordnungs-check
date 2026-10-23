# Kapitel 2: Analyse möglicher KI-Einsatzbereiche

*Verantwortlich: Thomas Kullmann · Status: nur Matrix-Folie vorhanden*

**Was die IHK erwartet:** Nicht nur grob ins Unternehmen schauen, sondern je Bereich die Arbeitsprozesse benennen, die sich für KI eignen, und daraus einen Schwerpunkt ableiten.

## Gliederung

### 2.1 Vorgehen
- Bereiche beider Praxen durchgehen (Rezeption, Therapie, Verwaltung; GKV- und Privatpraxis)
- Bewertung nach zwei Achsen: **Nutzen für die Praxis** und **Machbarkeit** (Daten, Schnittstellen, Risiko)

### 2.2 Einsatzfelder

| Einsatzfeld | Bereich | Nutzen | Machbarkeit | Bemerkung |
|---|---|---|---|---|
| Verordnungs-Check | Rezeption | hoch | hoch | gewählter Pilot |
| Zentrale Terminvergabe und Telefon | Rezeption, beide Standorte | hoch | mittel | Schnittstelle zur Praxissoftware nötig; Weiche GKV/privat |
| Kosten- und Erstattungshinweis | Rezeption Privatpraxis | mittel | mittel bis hoch | keine Schnittstelle nötig; nur Hinweis, keine Erstattungszusage |
| Abrechnungs-Vorbereitung | Verwaltung | mittel | gering | heute beim Dienstleister |
| Erinnerungen an Patienten | Rezeption | mittel | hoch | Standardtools vorhanden |
| Therapieberichte an Ärzte | Therapie | gering bis mittel | mittel | Gesundheitsdaten im Freitext |
| Dienst- und Raumplanung | Verwaltung | gering | mittel | |

*Einschätzung des Teams, keine Messung. Im Pilot nur für den Verordnungs-Check überprüft.*

### 2.3 Ausgangslage und Einsatzfelder über beide Standorte

**Ausgangslage:** Die Praxis setzt heute in keinem Bereich KI ein ([Nachtrag zum Ist-Interview vom 23.10.2026](../field-study/Ist-Interview_Nachtrag_2026-10-23.pdf)). Damit gehört sie zur Mehrheit: Laut Destatis nutzte 2024 jedes fünfte Unternehmen KI, laut IW-Befragung 37 %, bei kleinen Unternehmen 36 % (beide zitiert im IHK-Rahmenplan).

**Organisation:** Zwei Praxen an zwei Standorten. Die Terminvergabe ist zentral, Praxis 1 behandelt GKV-Patienten, Praxis 2 Privatpatienten.

Daraus folgt: Der Verordnungs-Check lässt sich **nicht** einfach auf die Privatpraxis übertragen. Für Privatpatienten gibt es kein einheitliches Verordnungsformular, keine Fristen für den Behandlungsbeginn und keine Höchstmengen; die Preise legt die Praxis weitgehend selbst fest, die Erstattung hängt vom Tarif ab, oft mit der Bundesbeihilfeverordnung als Orientierung ([PKV-Verband, privat-patienten.de](https://www.privat-patienten.de/beim-therapeuten/heilmittelerbringer/)). Das Risiko liegt dort nicht bei Absetzungen für die Praxis, sondern bei Erstattungslücken für den Patienten. Das ist eine **andere Tätigkeit** mit einem anderen KI-Einsatz.

| Einsatzfeld | Standort | Tätigkeit | KI-Ansatz | Status |
|---|---|---|---|---|
| Rezeption GKV | Praxis 1 | Verordnung prüfen | Verordnungs-Check (n8n, RAG, vier Prüfer) | Projekt, umgesetzt |
| Zentrale Terminvergabe | beide | Termine vergeben, GKV/privat weiterleiten | Standard-Tool für Online-Buchung und Telefon/Chat | Kandidat |
| Rezeption privat | Praxis 2 | Kosten- und Erstattungshinweis vor Behandlungsbeginn | Sprachmodell mit Preisliste und allgemeinen Tarifinfos | Ausblick |
| Abrechnung | beide | Rechnungen, Absetzungen nachverfolgen | Auswertung der Befunde des Verordnungs-Checks | Ausblick |

Die zentrale Terminvergabe ist die **Weiche**: Ein GKV-Rezept geht durch den Verordnungs-Check, ein Privatpatient bekommt den Erstattungshinweis.

**Grenze:** Der Erstattungshinweis ist ein Hinweis, keine Erstattungszusage. Über die Erstattung entscheidet die Versicherung (in Kap. 4 aufgreifen).

### 2.4 Begründung des Piloten
- Trifft das größte Problem (90 % der Fehler, Prüfzeit an der Rezeption)
- Regeln sind öffentlich und belegbar (G-BA, KBV)
- Keine Schnittstelle nötig, Eingabe im Chat
- Geringes Risiko: Die Rezeption entscheidet
- Messbar: Zeit, Trefferquote, Nacharbeit

## Vorhandene Bausteine

- Folie „Einsatzfelder: erst die Landkarte, dann der Pilot“ in der [IHK-Präsentation](../praesentation/Verordnungs-Check_IHK_Arbeitsstand_2026-10-19.pdf)
- [Scope](../scope.md), Abschnitt Ausschlüsse

## Lücken

- [ ] Je Einsatzfeld zwei, drei Sätze: Was genau würde die KI tun?
- [ ] Prüfen, ob die Praxis die Einschätzung teilt (kurze Rückfrage)
- [ ] Nachtrag N01/N02 von der Mitinhaberin bestätigen lassen
- [ ] Für Terminvergabe und Erstattungshinweis je ein, zwei konkrete Tools nennen (Tool-Vergleich, Kap. 3)
