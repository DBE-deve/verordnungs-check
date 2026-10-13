# n8n-Workflows

| Datei | Workflow | Zweck |
|---|---|---|
| `wissensbasis-laden.json` | Verordnungs-Check – Wissensbasis laden | Lädt die Regelwerke als PDF, teilt sie in Abschnitte, erzeugt Embeddings und speichert sie in Supabase |
| `vier-pruefer.json` | Verordnungs-Check – Vier Prüfer | Chat, Erfassung, vier Prüf-Agenten, Ampel, Protokoll |

Import: n8n → Workflows → Import from File. Danach die Credentials setzen:
- **OpenAI** (Chat-Modell und Embeddings)
- **Supabase** (Host-URL des Projekts und service_role-Schlüssel – nie ins Repository!)

Danach einmal **Wissensbasis laden** ausführen (füllt die Tabelle `documents`, rund 380 Abschnitte), dann den Chat im Workflow **Vier Prüfer** öffnen und eine Testverordnung aus `supabase/seed/testfaelle.sql` als JSON einfügen.

Stand der Exporte: Version v4 nach der Evaluation vom 13.10.2026 (siehe `docs/evaluation.md`).
