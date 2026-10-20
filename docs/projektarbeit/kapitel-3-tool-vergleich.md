# Kapitel 3: Tool-Vergleich

*Verantwortlich: Valentin Klamka · Status: Entwurf für die Eingabekanäle vorhanden*

**Was die IHK erwartet:** Schrittweise und methodisch: Anforderungen definieren, Vorauswahl treffen, Kriterienkatalog aufstellen (Funktionalität, Datenschutz, Benutzerfreundlichkeit, Integrationsfähigkeit, Kosten), Tools praktisch testen, begründetes Fazit.

## Gliederung

### 3.1 Anforderungen
- Aus Kapitel 1 ableiten: Gesundheitsdaten (DSGVO Art. 9), Rezeption ohne IT-Kenntnisse, Antwort in Sekunden, Belege aus den Regelwerken, geringe laufende Kosten

### 3.2 Kriterienkatalog
- Die fünf IHK-Kriterien mit Gewichtung, z. B. als Punkte von 1 bis 5

### 3.3 Vergleich je Baustein
Ehrlich bleiben: Die Plattform **n8n** ist durch das MSIT-Capstone vorgegeben. Ein echter Vergleich lohnt sich dort, wo wir wirklich entschieden haben:

| Baustein | Kandidaten | Gewählt |
|---|---|---|
| Orchestrierung | n8n, Make, Copilot Studio, eigener Code | n8n (Vorgabe, trotzdem kurz bewerten) |
| Sprachmodell | gpt-4.1-mini, größere Modelle, Modelle mit EU-Hosting | gpt-4.1-mini |
| Wissensbasis (RAG) | Supabase pgvector, eigenständige Vektordatenbank | Supabase pgvector (EU-Region) |
| Eingabekanal | Chat-Text, Webformular, Foto + Vision-KI, Scan + OCR, Spezialmodell, E-Mail-Eingang, Messenger, Praxissoftware, E-Verordnung | Chat-Text heute, Foto + Vision-KI als Brücke |

### 3.4 Test und Ergebnis
- Praxistest: Prototyp v1–v4 (siehe [Evaluation](../evaluation.md)), Kosten ca. 3–4 Cent und ca. 24 s je Prüfung

### 3.5 Fazit
- Eingabezeit der Rezeption dominiert die Gesamtkosten, nicht die KI (TCO-Vergleich)

## Vorhandene Bausteine

- Entwurf „Eingabekanäle und TCO“ (2 Folien, 19.10.2026): KI-Kosten 70–142 € pro Jahr, Gesamtkosten je Kanal 823–2.054 € pro Jahr
- [Architektur](../architektur.md), [Implementierungsweg](../implementierung.md)

## Lücken

- [ ] Kriterienkatalog mit Gewichtung
- [ ] Vergleich Sprachmodell und Wissensbasis
- [ ] TCO-Folien als Text übernehmen, Annahmen kennzeichnen
- [ ] Quellen für Preise mit Abrufdatum
