// Testet den deterministischen Code-Knoten "Fristen berechnen" direkt aus dem Workflow-Export.
// Aufruf: node tests/fakten.test.mjs
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const wf = JSON.parse(readFileSync(new URL('../n8n/vier-pruefer.json', import.meta.url)));
const code = wf.nodes.find((n) => n.name === 'Fristen berechnen').parameters.jsCode;
const fakten = (vo) => {
  const $input = { first: () => ({ json: { output: vo } }) };
  return new Function('$input', code)($input)[0].json.fakten;
};
const basis = {
  ausstellungsdatum: '2026-10-05', pruefdatum: '2026-10-12', geplanter_beginn: '2026-10-13', dringlich: false,
  icd10: 'M54.4', diagnosegruppe: 'WS', heilmittel: [{ name: 'KG', einheiten: 6, art: 'vorrangig' }],
  lanr: '123456701', bsnr: '987654300', letzte_behandlung: null, unterbrechungsgrund: null
};
const faelle = [
  ['Beginn nach 8 Tagen ist fristgerecht', {}, { tage_ausstellung_bis_beginn: 8, beginn_fristgerecht: true }],
  ['Beginn nach 28 Tagen ist noch fristgerecht', { ausstellungsdatum: '2026-09-15' }, { tage_ausstellung_bis_beginn: 28, beginn_fristgerecht: true }],
  ['Beginn nach 29 Tagen ist zu spät', { ausstellungsdatum: '2026-09-14' }, { beginn_fristgerecht: false }],
  ['Dringlich: 15 Tage sind zu spät', { dringlich: true, ausstellungsdatum: '2026-09-28' }, { frist_grenze_tage: 14, beginn_fristgerecht: false }],
  ['Unterbrechung 22 Tage ohne Grund', { letzte_behandlung: '2026-09-21' }, { tage_unterbrechung: 22, unterbrechung_zulaessig: false, beginn_fristgerecht: null }],
  ['Unterbrechung 22 Tage mit Grund', { letzte_behandlung: '2026-09-21', unterbrechungsgrund: 'Urlaub Patient' }, { unterbrechung_zulaessig: true }],
  ['LANR fehlt', { lanr: null }, { lanr_format_ok: null }],
  ['LANR 8-stellig', { lanr: '12345670' }, { lanr_format_ok: false }],
  ['WS-Code mit WS passt', {}, { icd_passende_diagnosegruppe: 'WS', diagnosegruppe_passt_zu_icd: true }],
  ['Schulter-Code mit WS passt nicht', { icd10: 'M75.1' }, { icd_passende_diagnosegruppe: 'EX', diagnosegruppe_passt_zu_icd: false }],
  ['Knie-Verletzung mit EX passt', { icd10: 's83.5', diagnosegruppe: 'ex' }, { diagnosegruppe_passt_zu_icd: true }],
  ['Unbekannter Bereich bleibt offen', { icd10: 'G35', diagnosegruppe: 'ZN' }, { icd_passende_diagnosegruppe: null, diagnosegruppe_passt_zu_icd: null }],
  ['Summe der Einheiten', { heilmittel: [{ name: 'KG', einheiten: 6, art: 'vorrangig' }, { name: 'WT', einheiten: 6, art: 'ergaenzend' }] }, { summe_einheiten: 12, anzahl_vorrangige_heilmittel: 1 }]
];
let ok = 0;
for (const [name, aenderung, erwartet] of faelle) {
  const f = fakten({ ...basis, ...aenderung });
  for (const [k, v] of Object.entries(erwartet)) assert.equal(f[k], v, `${name}: ${k}`);
  ok++; console.log('✓', name);
}
console.log(`\n${ok}/${faelle.length} Tests bestanden`);
