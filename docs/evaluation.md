# Evaluation

*Verantwortlich: Süle*

## Testfälle

Die synthetischen Testverordnungen liegen in `supabase/seed/testfaelle.sql` und in der Tabelle `testfaelle`.

| Nr. | Fall | Erwarteter Befund | Erwartete Ampel | Ergebnis | Bestanden |
|---|---|---|---|---|---|
| TF01 | Vollständig und regelkonform | keiner | grün | | |
| TF02 | Behandlungsbeginn 41 Tage nach Ausstellung | Fristen-Prüfer: Behandlungsbeginn | rot | | |
| TF03 | Schulter-Diagnose (M75.1) mit Diagnosegruppe WS | Diagnose-Prüfer: Diagnosegruppe | rot | | |
| TF04 | 10 Einheiten bei WS | Mengen-Prüfer: Einheiten | rot | | |
| TF05 | Leitsymptomatik und LANR fehlen | Formal-Prüfer: Leitsymptomatik, LANR | rot | | |
| TF06 | 22 Tage Unterbrechung ohne Grund | Fristen-Prüfer: Unterbrechung | rot | | |
| TF07 | Dringlich, Beginn nach 18 Tagen | Fristen-Prüfer: Behandlungsbeginn | rot | | |

## Kennzahlen

- Trefferquote: erkannte Fehler / erwartete Fehler
- Fehlalarme: gemeldete Fehler ohne Entsprechung
- Laufzeit pro Prüfung (`pruefungen.dauer_ms`)
- Kosten pro Prüfung (LLM-Aufrufe)

## Wichtigster Fehlermodus

*Wird nach den Testläufen ergänzt.*

## Verbesserungsplan

*Wird nach den Testläufen ergänzt.*
