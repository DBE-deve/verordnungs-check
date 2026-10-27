# Änderungsprotokoll

Kurznotizen zu Änderungen an den Workflows: was, warum, wie getestet. Neueste oben.

## 27.10.2026 · Cloud-Fassung, Testbatterie, fünf Regeln im Code

**Workflow:** „Verordnungs-Check – Cloud“, Export `n8n/cloud-verordnungs-check.json`. Der Merge-Workflow bleibt unverändert als Rückfall aktiv.

**Nachtrag Soll-Werte (27.10.2026, nachmittags):** Valentin hat TF10 bestätigt. TF10 erwartet rot (Diagnose: Leitsymptomatik), TF108 gelb (Mengen: Therapiefrequenz, Hinweis). Geändert in der Supabase-Tabelle `testfaelle` (id 10 und 119), in `supabase/seed/testfaelle.sql`, `tests/testbatterie_erzeugen.py` (Frequenzregel in der Soll-Ableitung, nur TF108 ändert sich) und `tests/testbatterie.json`/`.md`. Die Probezeile in `testlaeufe` ist gelöscht.

**Endfassung (27.10.2026, nachmittags):** Valentin (Kapitel 3, 4) und Derk (Kapitel 4, 5) haben Entwurf v2 freigegeben. Kapitel 1–6 und die Präsentation liegen jetzt als Endfassung ohne Freigabe-Markierungen vor; die Entwurfsdateien der Präsentation sind entfernt.

**Anlass**
- Testbatterie und Demo sollen in der Cloud laufen. Der lokale Redaktionsdienst (Python, BERT-Namensmodell) ist dort nicht erreichbar.
- Lauf 1 der Testbatterie (Blindtest, 59 E-Fälle × 3): 83,1 % richtige Ampeln, 5 übersehene rote Verordnungen, 2 kritische Fehlalarme. 7 von 10 Fehlern betrafen Regeln, die das Modell statt des Codes prüfte (Mengen, Leitsymptomatik, ergänzende Heilmittel, Frequenz).

**Änderungen**

| Bereich | Änderung |
|---|---|
| Redaktion | `Text redigieren` (HTTP) und `Text redigieren (Muster)` ersetzt durch `Text redigieren (Regeln)`: JavaScript-Port von `redaktion/regeln.py` mit Unicode-Wortgrenzen. Gegen das Original geprüft: 17 Texte, 0 Abweichungen (`redaktion/cloud/vergleich.py`). Grenze: Namen ohne Rollenwort erkennt nur das Namensmodell. |
| Fakten (`Fristen berechnen`) | neu: `leitsymptomatik_zulaessig` (WS/EX nur a, b, x), `hoechstmenge_eingehalten` (6 je VO), `ergaenzend_einheiten_ok`, `ergaenzendes_heilmittel_zulaessig` (Liste je Gruppe, Traktion nicht bei EX), `frequenz_im_rahmen` (1–3× pro Woche) |
| Code-Urteile (`Ergebnis zusammenführen`) | Ist ein Fakt entschieden, setzt der Code den Befund; widerspricht das Modell, gewinnt der Code. Frequenz außerhalb des Rahmens = Hinweis (Teamentscheidung 27.10.). Formal-Prüfer: Frequenz und Leitsymptomatik nur auf Vorhandensein. |
| Formular | Pfad `verordnungs-check-cloud` (sprechende Adresse funktioniert in der Cloud) |
| Daten | 123 Testfälle in Supabase (`testfaelle`), neue Tabelle `testlaeufe` (`supabase/migrations/003_testlaeufe.sql`) |

Prompts unverändert. Keine ICD-Codes aus Testfällen im Code. Vor Lauf 2 gegen alle 113 strukturierten Fälle geprüft: keine neuen Fehlalarme durch die Fakten.

**Test** (`tests/cloud/`): Lauf 2 94,9 %, keine übersehene rote Verordnung; Nachtest nach der Formal-Korrektur 15/15 korrekt, rechnerisch 96,6 % auf dem E-Set. Lauf 2 ist kein Blindtest mehr.

**Offen:** KBV-Liste als Tabelle im Code (2 gelbe Fälle), Freitext ohne Feldbezeichnung („WS“), Laufzeit 34 s, Verordnungsfall-Prüfung, Tests in `tests/` für den Cloud-Export ergänzen; gpt-4.1-mini wird von OpenAI als veraltet geführt.

## 27.10.2026 · Zusammenführung der beiden Stände: ein Workflow, OpenAI, PII-Fallback

**Workflow:** `n8n/merge-formular-vier-pruefer.json` ist jetzt der **einzige** Prüf-Workflow. `vier-pruefer.json` (v4) und `formular.json` sind entfallen; ihre Historie steht in Git.

**Anlass**

- Zwei Stände mit unterschiedlichen Verbesserungen: hier die Prüfer-Prompts (Summen-Fakt, Mandats-Abgrenzung, KBV-Präzisierung), im Fork die Erfassungsmaske Muster 13, die PII-Redaktion mit Dienst und 23 Seed-Fälle mit erwarteten Befunden.
- Die Cloud-Instanz nutzt OpenAI (`gpt-4.1-mini`, `text-embedding-3-small`). Die Gemini-Embeddings des Forks passen nicht zur dort geladenen Wissensbasis.
- Der Redaktionsdienst des Forks ist ein lokaler Python-Container (Port 5680) und in der Cloud nicht erreichbar; ein Freitext-Weg, der dann abbricht, wäre dort unbrauchbar.

**Änderungen**

| Bereich | Änderung |
|---|---|
| Struktur | Chat **und** Formular in einem Workflow (aus dem Merge-Stand übernommen); die Weiche `Kam vom Formular?` wählt die Antwort. Kein HTTP-Aufruf zwischen Workflows mehr. |
| PII im Freitext | `Text redigieren` ruft den Dienst über `{{ $env.REDAKTION_URL \|\| 'http://host.docker.internal:5680/redigieren' }}`; bei Fehler geht es auf den neuen Knoten `Text redigieren (Muster)` (dieselben Regeln als Code) und danach in `Redaktion übernehmen`. Es geht nie Rohtext an ein Modell. |
| Diagnose-Prüfer | Satz ergänzt: ein allgemeiner Prüfauftrag („bitte prüfen Sie, ob …") ist kein Befund. Das verhinderte in einem Lauf ein falsches Gelb bei TF08. |
| Leitsymptomatik | Der Code-Fakt `leitsymptomatik_zulaessig` (WS/EX nur a, b, x) ist **wieder entfernt**; der Prüfer beurteilt a/b/c bzw. Freitext selbst (siehe Offen). |
| Mengen-Prüfer | `summe_einheiten_vorrangig` und die Mandats-Abgrenzung übernommen. Die Regel „Frequenzabweichung ist kein Befund" ist **nicht** übernommen – eine belegte Abweichung bleibt ein Hinweis. |
| Agenten | `retryOnFail` (3 Versuche) an allen fünf Agenten, wie im Fork. |
| Tests | Alle automatischen Tests lesen den einen Export. `fakten.test.mjs` prüft zusätzlich `summe_einheiten_vorrangig`; neu sind `pii.test.mjs`, `formular.test.mjs`, `diagnosen.test.mjs` und die Seed-Auswertung `npm run vorlagen:pruefen`. |
| Seed | 23 Fälle, je einer pro Prüfkriterium; Erwartung enthält jetzt die erwarteten Befunde, nicht nur die Ampel. |

**Nicht übernommen (offen, Vier-Augen-Prüfung)**

- Leitsymptomatik-Katalog a/b/x: TF10 (Leitsymptomatik c bei EX) bleibt damit grün, wie im Seed hinterlegt. Wird der Katalog bestätigt, müssen Seed, `docs/pruefkriterien.md` (Kriterium 12) und TF10 geändert werden.
- „Frequenzabweichung ist kein Befund" (HeilM-RL § 12 Abs. 1 Satz 4): TF22 bleibt gelb. Bei Bestätigung entfällt Kriterium 16 in seiner jetzigen Form.

**Tests**

| Prüfung | Ergebnis |
|---|---|
| `npm test` (Fakten, Diagnoseauswahl, PII, Formular) | 15 + 14 + 29 Prüfungen, alle bestanden |
| `npm run test:redaktion` | 14 Regeln bestanden |
| Code-Fakten im Export | `leitsymptomatik_zulaessig` entfernt, `summe_einheiten_vorrangig` vorhanden |
| PII-Fallback | `pii.test.mjs` führt den Muster-Knoten aus: Name, Versichertennummer und Geburtsdatum werden ersetzt |

**Offen**

- Ende-zu-Ende-Lauf mit `gpt-4.1-mini` in der Cloud-Instanz steht aus (lokal liegt kein OpenAI-Key). Nach dem Import: `npm run vorlagen:pruefen -- --url https://<instanz>/webhook/verordnungs-check/chat`.
- `summe_einheiten` bleibt für die Absetzungsrechnung bei 28 € je Einheit (Ist-Interview: 32 €).

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
