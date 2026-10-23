# Änderungsprotokoll

Kurznotizen zu Änderungen an den Workflows: was, warum, wie getestet. Neueste oben.

## 23.10.2026 · Merge-Workflow: Diagnose-Prüfer, zwei neue Code-Fakten

**Workflow:** Verordnungs-Check – Merge, Export `n8n/merge-formular-vier-pruefer.json`. v4 (Fallback) unverändert.

**Anlass**
- Ausführung 901: Der Diagnose-Prüfer behauptete, M75.1 stehe nicht auf der KBV-Diagnoseliste. Die Vektorsuche hatte den richtigen Abschnitt geliefert, das Modell hat ihn falsch gelesen. Im Feld „fundstelle“ standen Begründungen statt Quellen.
- Der Prompt enthielt drei ICD-Codes als Beispiele, die inzwischen in Testfällen vorkommen (Regel: keine Testfall-Codes in Prompts).
- Der Prompt nannte für alle Diagnosegruppen die Leitsymptomatik a, b, c. Laut Heilmittelkatalog gibt es bei WS und EX nur a, b und x (patientenindividuell).
- Eigener Fehler vom 20.10.: Der Mengen-Prüfer vergleicht `summe_einheiten` mit der Höchstmenge. Dieser Wert zählt ergänzende Heilmittel mit, wenn sie im Array `heilmittel` stehen → mögliches falsches Rot.

**Änderungen**

| Knoten | Änderung |
|---|---|
| Fristen berechnen | Neuer Fakt `leitsymptomatik_zulaessig` (WS/EX: a, b, x; sonst null). Neuer Fakt `summe_einheiten_vorrangig` (ohne ergänzende; unbekannte Art zählt vorsichtshalber mit). `summe_einheiten` bleibt für die Absetzungsrechnung. |
| Diagnose-Prüfer | Leitsymptomatik folgt dem Fakt verbindlich. KBV: nur Teil 1 der Liste (S. 3–21; ab S. 22 Blankoverordnung), verordnete Diagnosegruppe muss passen, ggf. Zweitcode nötig; Treffer ausdrücklich „hinweis“ mit festem Text. Fundstelle nur Quelle und Seite. Beispiel-ICD-Codes entfernt. |
| Formal-Prüfer | Passung der Leitsymptomatik ausdrücklich nicht im Mandat (sonst Doppelmeldung). |
| Mengen-Prüfer | Vergleicht `summe_einheiten_vorrangig` statt `summe_einheiten`. |

Unit-Tests: `tests/fakten.test.mjs` prüft jetzt beide Exporte und die neuen Fakten.

**Tests** (nur Seed-Fälle, Entwicklungsset D und Ad-hoc-Varianten, kein Evaluationsset)

| Ausführung | Fall | Erwartet | Ergebnis |
|---|---|---|---|
| 914, 928 | TF01 | grün | 🟢 ✅ |
| 915 → 923 | TF03 (M75.1 mit WS) | rot, nur Diagnosegruppe | 915: zusätzlich „Leitsymptomatik a gibt es bei WS nicht“ ❌ (Modell-Fehler) → nach Code-Fakt 923: nur Diagnosegruppe ✅ |
| 916, 931 | TF09 (M50.1 mit EX) | rot, kein KBV-Hinweis (Liste: WS, Zweitcode fehlt) | 🔴 ✅ · **929: Abbruch**, Modellantwort passte nicht ins Schema |
| 917 → 924 → 930 | TF10 (Leitsymptomatik c bei EX) | rot (neu, siehe unten) | 924: rot, aber doppelt (Formal + Diagnose) → 930: nur Diagnose ✅ |
| 918, 925 | TF043 (M75.1 mit EX) | gelb (KBV) | 🟢 ❌ Treffer in der Fundstelle genannt, Status trotzdem „ok“ |
| 919, 926 | TF038 (M48.0- mit G55.3) | gelb (KBV) | 🟢 ❌ wie TF043 |
| 920, 927 | TF038 ohne Zweitcode | grün | 🟢 ✅ |
| 921, 922 | TF016, TF021 | grün | 🟢 ✅ |
| 932 | TF01 + ergänzendes Heilmittel im Array (6 + 6) | grün | 🟢 ✅ (vorher Risiko: falsches Rot) |
| 933 | TF04: 10 Einheiten (Gegenprobe) | rot, Mengen | 🔴 ✅ |

Laufzeit 20–33 s.

**Offen**
- **KBV-Hinweis ist per Prompt nicht zuverlässig.** Das Modell findet den Eintrag, setzt aber „ok“. Im Evaluationsset hängen 7 der 10 gelben Fälle daran. Lösung nach dem Leitsatz „Regeln rechnet der Code“: KBV-Teil-1-Einträge für WS/EX als Tabelle im Code (Fakt `kbv_besonderer_bedarf`), das Modell formuliert nur noch. Entscheidung im Team.
- **TF10:** Nach Heilmittelkatalog ist das Soll rot, nicht grün. Seed (`supabase/seed/testfaelle.sql`) und Tabelle `testfaelle` erst nach Vier-Augen-Prüfung anpassen.
- **Abbruch 929:** einmal in zwei Läufen. Für die Stabilitätsmessung „Retry on Fail“ an den Prüf-Agenten erwägen.
- Seitenzahlen in den Fundstellen sind nicht gegengeprüft (z. B. „Heilmittelkatalog, S. 2“).

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
