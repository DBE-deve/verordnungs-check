# Kapitel 4: Begründete Tool-Auswahl und Einsatzplanung

*Verantwortlich: Valentin Klamka (Auswahl, Architektur, Governance), Derk Ermler (Einsatzplanung, Pilot) · Status: Bausteine vorhanden, Text fehlt*

**Was die IHK erwartet:** Die Auswahl nachvollziehbar aus Anforderungen, Stärken und Schwächen ableiten. Dann ein realistischer Einsatzplan: technische Voraussetzungen, Zeitplan, Personal, Schulung, Integration, datenschutzkonforme Konfiguration, Pilot oder Parallelbetrieb. Der Prototyp dient als Anwendungsbeispiel.

## Gliederung

### 4.1 Begründete Auswahl (Valentin Klamka)
- Rückbezug auf den Kriterienkatalog aus Kapitel 3

### 4.2 Lösung und Architektur (Valentin Klamka)
- Vier Prüfer: Formal, Diagnose, Menge, Fristen; Ampel mit Fundstellen
- Leitsatz: **Was sich als Regel aufschreiben lässt, rechnet der Code, nicht das Sprachmodell**
- Ausbau: Verordnungsfall-Prüfung mit Historie (Sprint 2)

### 4.3 Governance (Valentin Klamka)
- DSGVO (Gesundheitsdaten, Pseudonym statt Name, EU-Region), EU AI Act (Einordnung noch zu prüfen), Mensch entscheidet

### 4.4 Einsatzplanung und Pilot (Derk Ermler)
- Phasen: Vorbereitung, Parallelbetrieb (Praxis hat zugestimmt), Auswertung, Entscheidung
- Rollen: Inhaberin verantwortlich, Rezeption prüft parallel
- Schulung der Rezeption, Rückfallebene ohne System

## Vorhandene Bausteine

- [Architektur](../architektur.md), [Build-Plan](../build-plan.md), [Dateneingang](../dateneingang.md), [Governance](../governance.md)
- Workflow-Export: [vier-pruefer.json](../../n8n/vier-pruefer.json)
- Folien „Einsatzplanung“ und „Risiken“ (Entwurf) in der [IHK-Präsentation](../praesentation/Verordnungs-Check_IHK_Arbeitsstand_2026-10-19.pdf)

## Lücken

- [ ] Auswahlbegründung als Text
- [ ] EU-AI-Act-Einordnung prüfen und belegen
- [ ] Dauer der Pilotphasen festlegen und mit der Praxis abstimmen
- [ ] Schulungskonzept (kurz)
