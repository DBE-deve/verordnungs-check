// Bereitet die Import-Dateien aus dem Repository-Export vor.
//
// Seit dem Merge gibt es **einen** Workflow: Chat und n8n-Formular liegen zusammen
// in `n8n/merge-formular-vier-pruefer.json`. Das Skript ergänzt, was der
// CLI-Import braucht und die Oberfläche selbst erledigt:
//
//  1. `.n8n/tmp/verordnungs-check-lokal.json` – für die lokale npm-Instanz.
//     Chat- und Formular-Trigger bekommen feste webhookIds (stabile Adressen),
//     und – falls der Workflow dort schon existiert – dessen ID, damit der Import
//     aktualisiert statt dupliziert.
//  2. `.n8n/tmp/import-fremdinstanz/` – für eine laufende Instanz (Docker, Cloud).
//     Workflow und Credentials brauchen eine ID in der Datei, und Credentials
//     werden nur über die ID aufgelöst (getestet mit n8n 2.20.8).
//
// Aufruf: npm run n8n:vorbereiten
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { randomBytes } from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';

const QUELLE_WORKFLOW = 'n8n/merge-formular-vier-pruefer.json';
const QUELLE_CREDENTIALS = '.n8n/credentials/vier-pruefer.json';
const ORDNER_TMP = '.n8n/tmp';
const ORDNER_FREMD = `${ORDNER_TMP}/import-fremdinstanz`;
const LOKALE_DATENBANK = '.n8n/.n8n/database.sqlite';
const WEBHOOK_ID_LOKAL = 'verordnungs-check-lokal';
const WEBHOOK_ID_FREMD = 'verordnungs-check';

/** n8n-IDs sind 16-stellige nanoid-Werte. */
const alphabet = 'useandom-26T198340PX75pxJACKVERYMINDBUSHWOLF_GQZbfghjklqvwyzrict';
const neueId = (size = 16) => Array.from(randomBytes(size), (b) => alphabet[b % 64]).join('');

const lies = (pfad) => {
  const roh = JSON.parse(readFileSync(pfad, 'utf8'));
  return Array.isArray(roh) ? roh[0] : roh;
};
const trigger = (workflow, teil) => {
  const n = workflow.nodes.find((x) => x.type.includes(teil));
  if (!n) throw new Error(`Trigger ${teil} fehlt in ${QUELLE_WORKFLOW}`);
  return n;
};

mkdirSync(ORDNER_TMP, { recursive: true });

/* ------------------------------------------------- 1. lokale npm-Instanz --- */
const lokal = lies(QUELLE_WORKFLOW);
trigger(lokal, 'chatTrigger').webhookId = WEBHOOK_ID_LOKAL;
trigger(lokal, 'formTrigger').webhookId = WEBHOOK_ID_LOKAL;

if (existsSync(LOKALE_DATENBANK)) {
  const db = new DatabaseSync(LOKALE_DATENBANK, { readOnly: true });
  const vorhanden = db.prepare('SELECT id FROM workflow_entity WHERE name = ?').all(lokal.name);
  if (vorhanden.length === 1) {
    lokal.id = vorhanden[0].id;
  } else if (vorhanden.length > 1) {
    console.error(`Mehrere Workflows namens "${lokal.name}" in der lokalen Instanz – bitte einen löschen.`);
    process.exit(1);
  }
}

writeFileSync(`${ORDNER_TMP}/verordnungs-check-lokal.json`, JSON.stringify(lokal, null, 2) + '\n');
console.log(
  `${ORDNER_TMP}/verordnungs-check-lokal.json geschrieben ` +
    `(webhookId=${WEBHOOK_ID_LOKAL}, ID=${lokal.id ?? 'neu'}, ${lokal.nodes.length} Knoten)`,
);
console.log(`  Chat:     /webhook/${WEBHOOK_ID_LOKAL}/chat`);
console.log(`  Formular: /form/${trigger(lokal, 'formTrigger').parameters.path}`);

/* ------------------------------------------- 2. fremde Instanz (Docker) --- */
if (!existsSync(QUELLE_CREDENTIALS)) {
  console.log(
    `${QUELLE_CREDENTIALS} fehlt – die Import-Dateien für eine fremde Instanz wurden übersprungen.\n` +
      '  (Zugangsdaten dort anlegen oder als Datei ablegen: {name, type, data} je Credential.)',
  );
  process.exit(0);
}

mkdirSync(ORDNER_FREMD, { recursive: true });

// IDs einmalig erzeugen und merken: Workflow und Credentials müssen bei jedem
// erneuten Import dieselben IDs behalten, sonst entstehen Kopien und die
// Credential-Verweise im Workflow zeigen ins Leere.
const idDatei = `${ORDNER_FREMD}/ids.json`;
const ids = existsSync(idDatei) ? JSON.parse(readFileSync(idDatei, 'utf8')) : { workflow: null, credentials: {} };
ids.credentials ??= {};

const credentials = JSON.parse(readFileSync(QUELLE_CREDENTIALS, 'utf8'));
const idNachTypUndName = new Map();
for (const c of credentials) {
  const schluessel = `${c.type}|${c.name}`;
  ids.credentials[schluessel] ??= neueId();
  c.id = ids.credentials[schluessel];
  idNachTypUndName.set(schluessel, c.id);
}
writeFileSync(`${ORDNER_FREMD}/credentials.json`, JSON.stringify(credentials, null, 2) + '\n');

const fremd = lies(QUELLE_WORKFLOW);
ids.workflow ??= neueId();
fremd.id = ids.workflow;
trigger(fremd, 'chatTrigger').webhookId = WEBHOOK_ID_FREMD;
trigger(fremd, 'formTrigger').webhookId = WEBHOOK_ID_FREMD;
const fehlend = new Set();
for (const n of fremd.nodes) {
  for (const [typ, ref] of Object.entries(n.credentials ?? {})) {
    const id = idNachTypUndName.get(`${typ}|${ref.name}`);
    if (!id) {
      fehlend.add(`${typ} · ${ref.name} (Knoten ${n.name})`);
      continue;
    }
    n.credentials[typ] = { id, name: ref.name };
  }
}
if (fehlend.size) {
  console.error(`${QUELLE_CREDENTIALS} kennt diese Credentials nicht:`);
  for (const eintrag of fehlend) console.error(`  - ${eintrag}`);
  console.error('  Entweder dort ergänzen (Format: {name, type, data}) oder die Zugangsdaten in der Ziel-Instanz anlegen.');
  process.exit(1);
}
writeFileSync(`${ORDNER_FREMD}/verordnungs-check.json`, JSON.stringify(fremd, null, 2) + '\n');
writeFileSync(idDatei, JSON.stringify(ids, null, 2) + '\n');

console.log(`${ORDNER_FREMD}/credentials.json und verordnungs-check.json geschrieben`);
console.log(`  Workflow-ID: ${fremd.id}  (n8n publish:workflow --id=${fremd.id})`);
console.log(`  Chat nach der Aktivierung:     /webhook/${WEBHOOK_ID_FREMD}/chat`);
console.log(`  Formular nach der Aktivierung: /form/${trigger(fremd, 'formTrigger').parameters.path}`);
console.log(`  IDs gemerkt in ${idDatei} – bei erneutem Import bleiben sie gleich.`);
