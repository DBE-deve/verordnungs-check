# n8n-Workflows

| Datei | Workflow | Zweck |
|---|---|---|
| `wissensbasis-laden.json` | Verordnungs-Check – Wissensbasis laden | Lädt die Regelwerke als PDF, teilt sie in Abschnitte, erzeugt Embeddings und speichert sie in Supabase |
| `vier-pruefer.json` | Verordnungs-Check – Vier Prüfer | Chat, Erfassung, vier Prüf-Agenten, Ampel, Protokoll |

Import: n8n → Workflows → Import from File. Danach die Credentials setzen:
- **OpenAI** (Chat-Modell und Embeddings)
- **Supabase** (Host-URL des Projekts und service_role-Schlüssel – nie ins Repository!)

Die Exporte werden nach den ersten erfolgreichen Testläufen ergänzt.
