# Änderungsprotokoll

Kurznotizen zu Änderungen an den Workflows: was, warum, wie getestet. Neueste oben.

## 20.10.2026 · Merge-Workflow: Mengen-Prüfer geschärft

**Workflow:** Verordnungs-Check – Merge (Formular + Vier Prüfer), Export `n8n/merge-formular-vier-pruefer.json`. Vier Prüfer v4 (Fallback) ist unverändert.

**Anlass**
- TF03 als Freitext (Ausführung 898): Der Mengen-Prüfer meldete „Einheiten je Verordnung: fehlerhaft“, obwohl er selbst schrieb, dass 6 Einheiten zulässig sind. Begründung war die falsche Diagnosegruppe – das ist Mandat des Diagnose-Prüfers. Ergebnis: kritischer Fehlalarm.
- Beim Aufbau der Testbatterie zeigte sich: Die Frequenzempfehlung ist nur Orientierung, der Arzt darf ohne Dokumentation abweichen (HeilM-RL § 12 Abs. 1 Satz 4). Ein Hinweis bei Abweichung wäre ein Fehlalarm.

**Änderung (Systemprompt Mengen-Prüfer)**
1. Einheiten je Verordnung: maßgeblich ist `summe_einheiten` aus den berechneten Fakten. Innerhalb der Höchstmenge → „ok“.
2. Neuer Absatz „NICHT dein Mandat“: ICD-Code, Diagnose, Passung der Diagnosegruppe, Leitsymptomatik, Fristen, Pflichtangaben. Diese Punkte bleiben bei Status und Korrekturhinweis außen vor.
3. Therapiefrequenz: angegeben → „ok“, auch außerhalb der Empfehlung.
4. Kombination präzisiert: höchstens ein ergänzendes Heilmittel, Einheiten nicht über der Summe der vorrangigen.

Keine ICD-Codes aus Testfällen im Prompt.

**Nebenbei:** Formular-Pfad `verordnungs-check-merge` wiederhergestellt. Er war bei einer automatischen Speicherung in der n8n-Oberfläche verloren gegangen.

**Test** (Testfälle bewusst nicht aus dem Evaluationsset)

| Ausführung | Eingabe | Erwartet | Ergebnis |
|---|---|---|---|
| 901 | TF03 als Freitext (wie 898) | rot, nur Diagnose-Prüfer | 🔴 rot, nur Diagnosegruppe fehlerhaft, Mengen-Prüfer 3× ok ✅ |
| 902 | TF01 mit Frequenz 4×/Woche (ad hoc) | grün | 🟢 grün, keine Befunde ✅ |
| 903 | TF04: 10 Einheiten bei WS (Gegenprobe) | rot, Mengen-Prüfer | 🔴 rot, Einheiten je Verordnung fehlerhaft ✅ |

Laufzeit 27–34 s (drei Läufe parallel gestartet).

**Offen, beim Test aufgefallen**
- Der Diagnose-Prüfer schrieb in 901, M75.1 stehe nicht auf der KBV-Diagnoseliste. Das ist falsch, M75.1 steht dort für EX. Ohne Einfluss auf die Ampel, weil die Diagnosegruppe ohnehin falsch war. Im Feld „fundstelle“ steht außerdem eine Begründung statt einer Quelle, das gefährdet das Kriterium „Fundstelle 100 %“.
- Die Absetzungsrechnung im Knoten „Ergebnis zusammenführen“ nutzt noch 28 € je Einheit (Ist-Interview: 32 €).
- Robuster als jeder Prompt wäre ein berechneter Fakt `hoechstmenge_eingehalten` für WS und EX im Code-Knoten „Fristen berechnen“ (Leitsatz: Regeln rechnet der Code).
