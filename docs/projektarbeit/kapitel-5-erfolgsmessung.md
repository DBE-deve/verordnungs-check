# Kapitel 5: Erfolgsmessung

*Verantwortlich: Derk Ermler · Status: Kriterien fertig, Evaluation mit 50 Fällen offen (Sprint 3)*

**Was die IHK erwartet:** Systematische Erfolgskontrolle, technisch und inhaltlich: Liefert das Tool korrekte und vollständige Ergebnisse? Wie werden Nutzung und Akzeptanz gemessen? Was folgt daraus für Optimierung und Schulung?

## Gliederung

### 5.1 Erfolgskriterien
- ≥ 98 % korrekte Ampeln auf ≥ 50 neuen Fällen (höchstens 1 Fehler), jeder Fall 3 Läufe
- 0 übersehene rote Fälle, höchstens 1 kritischer Fehlalarm
- „Bedingt bereit“ zwischen 95 und 98 %
- Begründung für 50 Fälle

### 5.2 Bisherige Ergebnisse (Prototyp)
- Baseline v1: 8 von 8 Fehlern erkannt, aber 12 kritische Fehlalarme
- v4: 10 von 10 Ampeln korrekt, 0 kritische Fehlalarme, ca. 24 s und 3–4 Cent je Prüfung
- Wichtigster Fehlermodus: Das Sprachmodell ordnet ICD-Codes plausibel, aber falsch zu (S83.5)

### 5.3 Formale Evaluation mit 50 Fällen
- Ergebnis folgt nach Sprint 3

### 5.4 Messung im Pilot
- Prüfzeit je Verordnung vorher und nachher
- Trefferquote gegen die Prüfung der Rezeption im Parallelbetrieb
- Akzeptanz: Wie oft folgt die Rezeption der Ampel?

### 5.5 Verbesserungsplan
- Siehe [Evaluation](../evaluation.md), Abschnitt Verbesserungsplan

## Vorhandene Bausteine

- [Erfolgskriterien](../erfolgskriterien.md), [Evaluation](../evaluation.md)
- Automatische Tests: [fakten.test.mjs](../../tests/fakten.test.mjs)

## Lücken

- [ ] 50 Testfälle anlegen und auswerten (kritischer Pfad bis zur Prüfung)
- [ ] Text für 5.1, 5.2 und 5.4 jetzt schreiben, die Zahlen für 5.3 nachtragen
- [ ] Kostenmessung über das OpenAI-Dashboard statt Schätzung
