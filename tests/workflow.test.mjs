// Struktur-Prüfung des Workflow-Exports.
// Aufruf: node tests/workflow.test.mjs
//
// Fängt genau die Fehler ab, die beim Bearbeiten von Hand oder per Skript entstehen:
// doppelte IDs, Verbindungen auf nicht existierende Knoten, Knoten ohne Verbindung,
// fehlende Trigger-IDs. Inhaltliche Prüfungen stehen in den anderen Testdateien.
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const DATEI = 'n8n/merge-formular-vier-pruefer.json';
const wf = JSON.parse(readFileSync(new URL(`../${DATEI}`, import.meta.url)));

assert.ok(Array.isArray(wf.nodes) && wf.nodes.length > 0, 'keine Knoten im Export');
assert.ok(wf.connections && typeof wf.connections === 'object', 'keine Verbindungen im Export');

// 1. Namen und IDs sind eindeutig
const namen = wf.nodes.map((n) => n.name);
const doppelt = namen.filter((n, i) => namen.indexOf(n) !== i);
assert.deepEqual(doppelt, [], `doppelte Knotennamen: ${doppelt.join(', ')}`);
const ids = wf.nodes.map((n) => n.id).filter(Boolean);
assert.equal(new Set(ids).size, ids.length, 'doppelte Knoten-IDs');
console.log(`✓ ${wf.nodes.length} Knoten, Namen und IDs eindeutig`);

// 2. Jeder Knoten hat Typ und Position
for (const n of wf.nodes) {
  assert.ok(n.type, `Knoten ohne Typ: ${n.name}`);
  assert.ok(Array.isArray(n.position) && n.position.length === 2, `Knoten ohne Position: ${n.name}`);
  assert.ok(n.parameters, `Knoten ohne parameters: ${n.name}`);
}
console.log('✓ Typ, Position und Parameter überall gesetzt');

// 3. Alle Verbindungen zeigen auf existierende Knoten
const bekannt = new Set(namen);
for (const [von, verbindungen] of Object.entries(wf.connections)) {
  assert.ok(bekannt.has(von), `Verbindung von unbekanntem Knoten: ${von}`);
  for (const [art, zweige] of Object.entries(verbindungen)) {
    for (const zweig of zweige ?? []) {
      for (const ziel of zweig ?? []) {
        assert.ok(bekannt.has(ziel.node), `${von} --${art}--> unbekannter Knoten: ${ziel.node}`);
      }
    }
  }
}
console.log('✓ Alle Verbindungen zeigen auf existierende Knoten');

// 4. Jeder Knoten außer Notizen ist von einem Trigger aus erreichbar.
// Sub-Knoten (Modell, Embeddings, Vektorstore, Parser) hängen über ai_*-Verbindungen
// am Agenten – diese Kanten zeigen zum Agenten hin, deshalb wird der Graph für die
// Erreichbarkeit ungerichtet durchlaufen.
const nachbarn = new Map();
const verbinde = (a, b) => {
  if (!nachbarn.has(a)) nachbarn.set(a, new Set());
  nachbarn.get(a).add(b);
};
for (const [von, verbindungen] of Object.entries(wf.connections)) {
  for (const zweige of Object.values(verbindungen)) {
    for (const ziel of (zweige ?? []).flat().filter(Boolean)) {
      verbinde(von, ziel.node);
      verbinde(ziel.node, von);
    }
  }
}
const triggers = wf.nodes.filter((n) => /trigger/i.test(n.type)).map((n) => n.name);
assert.ok(triggers.length >= 2, 'es müssen Chat- und Formular-Trigger vorhanden sein');
const erreicht = new Set(triggers);
const warteschlange = [...triggers];
while (warteschlange.length) {
  for (const ziel of nachbarn.get(warteschlange.shift()) ?? []) {
    if (!erreicht.has(ziel)) {
      erreicht.add(ziel);
      warteschlange.push(ziel);
    }
  }
}
const verwaist = wf.nodes
  .filter((n) => !erreicht.has(n.name) && n.type !== 'n8n-nodes-base.stickyNote')
  .map((n) => n.name);
assert.deepEqual(verwaist, [], `nicht erreichbare Knoten: ${verwaist.join(', ')}`);
console.log(`✓ Alle Knoten von ${triggers.length} Triggern aus erreichbar (${triggers.join(', ')})`);

// 5. Formular-Pfad vorhanden; der Export enthält keine Credential-IDs.
// webhookIds setzt `npm run n8n:vorbereiten` beim Import – im Export dürfen sie
// fehlen, dann vergibt n8n sie beim ersten Import.
const formTrigger = wf.nodes.find((n) => n.type === 'n8n-nodes-base.formTrigger');
assert.ok(formTrigger.parameters.path, 'Form-Trigger ohne Pfad');
for (const n of wf.nodes) {
  for (const [typ, ref] of Object.entries(n.credentials ?? {})) {
    assert.equal(ref.id, undefined, `${n.name}: Credential-ID im Export (${typ}) – gehört nicht ins Repository`);
    assert.ok(ref.name, `${n.name}: Credential ohne Namen (${typ})`);
  }
}
console.log(`✓ Formular unter /form/${formTrigger.parameters.path}, Export ohne Credential-IDs`);

// 6. Inline-Code der Knoten ist syntaktisch gültig
let geprueft = 0;
for (const n of wf.nodes.filter((x) => x.parameters?.jsCode)) {
  try {
    new Function('$input', '$', '$json', n.parameters.jsCode);
    geprueft++;
  } catch (problem) {
    assert.fail(`${n.name}: JavaScript-Fehler – ${problem.message}`);
  }
}
console.log(`✓ ${geprueft} Code-Knoten syntaktisch gültig`);
