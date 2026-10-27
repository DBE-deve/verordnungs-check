// n8n Workflow SDK – "Verordnungs-Check – Testbatterie Datenbrücke" (in der Cloud angelegt am 27.10.2026)
// Liefert die Testfälle aus Supabase an tests/cloud/batterie.py und schreibt die Ergebnisse in testlaeufe.
// Das Token steht nur in der Cloud-Instanz, hier als Platzhalter.
import { workflow, node, trigger } from '@n8n/workflow-sdk';
const TOKEN = 'TOKEN_HIER_EINSETZEN';
const supabase = { supabaseApi: { name: 'Supabase Verordnungs_check' } };
const exportHook = trigger({ type: 'n8n-nodes-base.webhook', version: 2.1, config: { name: 'Export Testfälle', parameters: { httpMethod: 'GET', path: 'vc-testfaelle-export', responseMode: 'responseNode', options: {} } } });
const check1 = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Token prüfen (Export)', parameters: { jsCode: `const t = $input.first().json.headers?.['x-token'];\nif (t !== '${TOKEN}') throw new Error('Kein Zugriff');\nreturn $input.all();` } } });
const lesen = node({ type: 'n8n-nodes-base.supabase', version: 1, config: { name: 'Testfälle lesen', executeOnce: true, parameters: { operation: 'getAll', tableId: 'testfaelle', returnAll: true }, credentials: supabase } });
const sammeln = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Als Liste', parameters: { jsCode: 'return [{ json: { faelle: $input.all().map((i) => i.json) } }];' } } });
const antwort1 = node({ type: 'n8n-nodes-base.respondToWebhook', version: 1.4, config: { name: 'Liste zurückgeben', parameters: { respondWith: 'firstIncomingItem', options: {} } } });
const ergebnisHook = trigger({ type: 'n8n-nodes-base.webhook', version: 2.1, config: { name: 'Ergebnisse empfangen', parameters: { httpMethod: 'POST', path: 'vc-testlauf-ergebnis', responseMode: 'responseNode', options: {} } } });
const check2 = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Token prüfen und zerlegen', parameters: { jsCode: `const j = $input.first().json;\nif (j.headers?.['x-token'] !== '${TOKEN}') throw new Error('Kein Zugriff');\nreturn (j.body.rows || []).map((r) => ({ json: r }));` } } });
const schreiben = node({ type: 'n8n-nodes-base.supabase', version: 1, config: { name: 'Testläufe schreiben', parameters: { tableId: 'testlaeufe', dataToSend: 'autoMapInputData' }, credentials: supabase } });
const zaehlen = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Anzahl', parameters: { jsCode: 'return [{ json: { geschrieben: $input.all().length } }];' } } });
const antwort2 = node({ type: 'n8n-nodes-base.respondToWebhook', version: 1.4, config: { name: 'Bestätigen', parameters: { respondWith: 'firstIncomingItem', options: {} } } });
export default workflow('vc-bruecke', 'Verordnungs-Check – Testbatterie Datenbrücke')
  .add(exportHook).to(check1).to(lesen).to(sammeln).to(antwort1)
  .add(ergebnisHook).to(check2).to(schreiben).to(zaehlen).to(antwort2);
