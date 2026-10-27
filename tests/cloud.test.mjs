// Testet den Cloud-Export (n8n/cloud-verordnungs-check.json): Struktur und die Code-Fakten,
// auf denen die Code-Urteile in "Ergebnis zusammenführen" beruhen.
// Aufruf: node tests/cloud.test.mjs
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const roh = readFileSync(new URL('../n8n/cloud-verordnungs-check.json', import.meta.url), 'utf8');
const wf = JSON.parse(roh);
const knoten = (name) => {
  const n = wf.nodes.find((x) => x.name === name);
  assert.ok(n, `Knoten fehlt: ${name}`);
  return n;
};

// Struktur
const namen = wf.nodes.map((n) => n.name);
assert.equal(new Set(namen).size, namen.length, 'Knotennamen nicht eindeutig');
for (const [von, ziele] of Object.entries(wf.connections)) {
  assert.ok(namen.includes(von), `Verbindung von unbekanntem Knoten: ${von}`);
  for (const ausgang of Object.values(ziele)) for (const zweig of ausgang) for (const z of zweig || [])
    assert.ok(namen.includes(z.node), `Verbindung auf unbekannten Knoten: ${z.node}`);
}
for (const n of wf.nodes.filter((x) => x.type.endsWith('.code'))) new Function(n.parameters.jsCode);
assert.equal(knoten('Formular: Verordnung erfassen').parameters.options.path, 'verordnungs-check-cloud');
knoten('Text redigieren (Regeln)');
assert.ok(!/"id":\s*"[A-Za-z0-9]{16}"/.test(JSON.stringify(wf.nodes.map((n) => n.credentials || {}))), 'Credential-IDs im Export');
assert.ok(!/webhookId/.test(roh), 'webhookId im Export');
assert.match(knoten('Ergebnis zusammenführen').parameters.jsCode, /quelle:\s*'code'/, 'Code-Urteile fehlen');
console.log(`✓ ${wf.nodes.length} Knoten, Verbindungen, Code-Syntax, Export ohne IDs`);

// Code-Fakten
const code = knoten('Fristen berechnen').parameters.jsCode;
const fakten = (vo) => new Function('$input', code)({ first: () => ({ json: { output: vo } }) })[0].json.fakten;
const basis = {
  ausstellungsdatum: '2026-10-05', pruefdatum: '2026-10-12', geplanter_beginn: '2026-10-13', dringlich: false,
  icd10: 'M54.4', diagnosegruppe: 'WS', leitsymptomatik: 'a', frequenz: '2x/Woche',
  heilmittel: [{ name: 'KG', einheiten: 6, art: 'vorrangig' }], lanr: '123456701', bsnr: '987654300'
};
const faelle = [
  ['Grüner Grundfall', {}, { leitsymptomatik_zulaessig: true, hoechstmenge_eingehalten: true, frequenz_im_rahmen: true }],
  ['Leitsymptomatik c bei EX unzulässig', { diagnosegruppe: 'EX', icd10: 'M75.1', leitsymptomatik: 'c' }, { leitsymptomatik_zulaessig: false }],
  ['8 Einheiten über Höchstmenge 6', { heilmittel: [{ name: 'KG', einheiten: 8, art: 'vorrangig' }] }, { hoechstmenge_eingehalten: false }],
  ['Wärme als ergänzendes Heilmittel bei WS zulässig',
    { heilmittel: [{ name: 'KG', einheiten: 6, art: 'vorrangig' }, { name: 'Wärmetherapie', einheiten: 6, art: 'ergaenzend' }] },
    { anzahl_ergaenzende_heilmittel: 1, ergaenzendes_heilmittel_zulaessig: true, ergaenzend_einheiten_ok: true }],
  ['Traktion bei EX nicht zulässig',
    { diagnosegruppe: 'EX', icd10: 'M75.1', heilmittel: [{ name: 'KG', einheiten: 6, art: 'vorrangig' }, { name: 'Traktion', einheiten: 6, art: 'ergaenzend' }] },
    { ergaenzendes_heilmittel_zulaessig: false }],
  ['Frequenz 4x/Woche außerhalb 1–3', { frequenz: '4x/Woche' }, { frequenz_im_rahmen: false }]
];
let ok = 0;
for (const [titel, aenderung, erwartet] of faelle) {
  const f = fakten({ ...basis, ...aenderung });
  for (const [k, v] of Object.entries(erwartet)) assert.equal(f[k], v, `${titel}: ${k} = ${f[k]}, erwartet ${v}`);
  ok++;
}
console.log(`✓ ${ok} Fakten-Fälle des Cloud-Workflows bestanden`);
