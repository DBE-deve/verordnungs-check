# Governance

*Verantwortlich: Valentin*

## Datenschutz (DSGVO)

- Verordnungen enthalten Gesundheitsdaten im Sinne von Art. 9 DSGVO.
- Der Prototyp arbeitet ausschließlich mit synthetischen Daten.
- Das Praxisbeispiel ist anonymisiert (Unterschied Anonymisierung / Pseudonymisierung: Art. 4 Nr. 5 DSGVO, Erwägungsgrund 26).
- Für einen Echtbetrieb: Auftragsverarbeitungsvertrag mit allen Dienstleistern, EU-Hosting, Löschkonzept für Protokolle.

## EU AI Act

- Einordnung des Systems: *noch auszuarbeiten*
- Menschliche Aufsicht: Die Rezeption entscheidet über jede Verordnung; das System weist nichts automatisch ab.
- Transparenz: Jeder Befund nennt seine Fundstelle im Regelwerk.

## Cybersecurity

- Row Level Security auf allen Tabellen, keine öffentlichen Policies
- Zugriff nur über den service_role-Schlüssel in n8n; Schlüssel nie im Repository
- Chat-Oberfläche: Hinweis, keine echten Patientendaten einzugeben
- Der Chat ist im Prototyp als öffentlicher n8n-Chat angelegt, aber nicht veröffentlicht. Vor dem Veröffentlichen eine Anmeldung aktivieren (Basic Auth oder n8n-Login), sonst kann jeder mit dem Link Kosten erzeugen
- Workflow-Exporte im Repository ohne Credential-IDs und ohne Webhook-ID

## Lizenzen der Wissensquellen

- Heilmittel-Richtlinie und Heilmittelkatalog: G-BA, frei zugänglich
- Heilmittel-Diagnoseliste: KBV, frei zugänglich
- ICD-10-GM: BfArM, kostenlos, Download begründet einen Nutzungsvertrag – nicht vollständig im Repository
