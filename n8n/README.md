# n8n-Workflows

| Datei | Workflow | Zweck |
|---|---|---|
| `wissensbasis-laden.json` | Verordnungs-Check – Wissensbasis laden | Lädt die Regelwerke als PDF, teilt sie in Abschnitte, erzeugt Embeddings und speichert sie in Supabase |
| `vier-pruefer.json` | Verordnungs-Check – Vier Prüfer | Chat, Erfassung, vier Prüf-Agenten, Ampel, Protokoll (Stand v4, **Fallback**) |
| `merge-formular-vier-pruefer.json` | Verordnungs-Check – Merge (Formular + Vier Prüfer) | Zusammenführung mit Valentins Stand (Fork `ValentinKlamka/verordnungs-check`): Chat **und** Muster-13-Formular in einem Workflow, PII-Redaktion, Diagnoseauswahl, deterministische Pflichtangaben; Modell gpt-4.1-mini und OpenAI-Embeddings wie v4 |

Import: n8n → Workflows → Import from File. Danach die Credentials setzen:
- **OpenAI** (Chat-Modell und Embeddings)
- **Supabase** (Host-URL des Projekts und service_role-Schlüssel – nie ins Repository!)

Danach einmal **Wissensbasis laden** ausführen (füllt die Tabelle `documents`, rund 380 Abschnitte), dann den Chat im Workflow **Vier Prüfer** öffnen und eine Testverordnung aus `supabase/seed/testfaelle.sql` als JSON einfügen.

Stand der Exporte: Version v4 nach der Evaluation vom 13.10.2026 (siehe `docs/evaluation.md`).

## Merge-Workflow (20.10.2026)

- **Zwei Eingänge, eine Prüfkette:** Chat (Text oder JSON) und n8n-Formular (Muster 13). Das Formular läuft im selben Workflow statt per HTTP-Aufruf auf den Chat-Webhook; der Knoten „Kam vom Formular?“ entscheidet am Ende, ob das Ergebnis im Chat oder auf der Abschlussseite des Formulars erscheint.
- **Modell und Embeddings:** gpt-4.1-mini und `text-embedding-3-small` (OpenAI) wie in v4. Valentins Fork nutzt OpenRouter mit Gemini-Embeddings; die passen nicht zur Wissensbasis in Supabase, die mit OpenAI-Embeddings geladen ist.
- **Fristen-Prüfer ohne Vektorsuche:** wie in Valentins Stand; die Fundstelle (HeilM-RL § 15/§ 16) steht im Prompt.
- **Datenbank:** setzt Migration `002_diagnose_auswahl.sql` voraus (Spalte `diagnose_auswahl` in `pruefungen`).
- **Fallback:** `vier-pruefer.json` (v4) bleibt unverändert und lauffähig.
