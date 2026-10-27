# Testbatterie gegen die n8n Cloud

Stand 27.10.2026. Prüft den Workflow „Verordnungs-Check – Cloud“ (`n8n/cloud-verordnungs-check.json`) mit allen Testfällen aus Supabase.

| Datei | Zweck |
|---|---|
| `batterie.py` | holt die Testfälle aus Supabase (Tabelle `testfaelle`, über die Datenbrücke `n8n/sdk/testbatterie-datenbruecke.mjs`), schickt jeden Fall an den Chat-Webhook, vergleicht Ampel und erwartete Befunde und schreibt jedes Ergebnis in die Tabelle `testlaeufe`. E-Set dreimal, alle anderen einmal. |
| `auswertung.py` | wertet einen Lauf nach `docs/erfolgskriterien.md` aus (Mehrheitsampel aus drei Läufen, harte Bedingungen, Stabilität, Befund-Genauigkeit, Fundstelle, Laufzeit) |
| `ergebnisse/` | Rohdaten der Läufe (JSONL), Auswertungen und der Stand der Testfälle zum Zeitpunkt der Läufe |

```bash
VC_TOKEN=... python tests/cloud/batterie.py 2026-10-27-cloud          # alle 123 Fälle, ca. 45 min
VC_TOKEN=... FILTER='TF(108|22) ' python tests/cloud/batterie.py nachtest
python tests/cloud/auswertung.py 2026-10-27-cloud
```

## Ergebnisse vom 27.10.2026 (E-Set, 59 Fälle × 3, ohne die 10 Verordnungsfall-Fälle)

| Kennzahl | Ziel | Lauf 1 `2026-10-27-cloud` | Lauf 2 `2026-10-27-cloud-regeln` | nach Nachtest |
|---|---|---|---|---|
| Ampel korrekt | ≥ 98 % | 83,1 % | 94,9 % | 96,6 % |
| Übersehene rote | 0 | 5 | 0 | 0 |
| Kritische Fehlalarme | ≤ 1 | 2 | 2 | 1 |
| Befund-Genauigkeit | ≥ 95 % | 79,7 % | 84,8 % | – |
| Fundstelle | 100 % | 97,3 % | 98,8 % | – |
| Stabilität | ≥ 95 % | 94,9 % | 96,6 % | – |
| Laufzeit (Median) | ≤ 30 s | 34,5 s | 34,4 s | – |

Lauf 1 ist der Blindtest des Stands nach der Zusammenführung. Vor Lauf 2 kamen fünf Regeln in den Code (siehe `docs/aenderungsprotokoll.md`), vor dem Nachtest die Begrenzung des Formal-Prüfers auf das Vorhandensein von Frequenz und Leitsymptomatik. Lauf 2 ist damit kein Blindtest mehr.

**Soll-Korrekturen**, in `auswertung.py` dokumentiert und für alle Läufe gleich angewandt: TF108 (Frequenz 4×/Woche) gelb statt grün – Teamentscheidung, Frequenz außerhalb der Empfehlung ist ein Hinweis; TF10 (Leitsymptomatik „c“ bei EX) rot statt grün – der Heilmittelkatalog nennt für EX nur a, b und x. Seit 27.10.2026 (nach Bestätigung durch Valentin) stehen beide Soll-Werte auch in Supabase, im Seed und in `tests/testbatterie.json`; die Korrektur in `auswertung.py` bleibt für die älteren Läufe nötig.
