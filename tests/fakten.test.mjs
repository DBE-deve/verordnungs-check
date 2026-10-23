// Testet den deterministischen Code-Knoten "Fristen berechnen" direkt aus den Workflow-Exporten
// (v4 und Merge). Aufruf: node tests/fakten.test.mjs
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const laden = (datei) => {
  const wf = JSON.parse(readFileSync(new URL('../n8n/' + datei, import.meta.url)));
  const code = wf.nodes.find((n) => n.name === 'Fristen berechnen').parameters.jsCode;
  return (vo) => new Function('$input', code)({ first: () => ({ json: { output: vo } }) })[0].json.fakten;
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
// Nur im Merge-Workflow (seit 23.10.2026): Leitsymptomatik je Diagnosegruppe, Summe ohne ergänzende Heilmittel
const nurMerge = [
  ['Leitsymptomatik a bei WS zulässig', { leitsymptomatik: 'a' }, { leitsymptomatik_zulaessig: true }],
  ['Leitsymptomatik x bei EX zulässig', { leitsymptomatik: 'x', icd10: 'M17.1', diagnosegruppe: 'EX' }, { leitsymptomatik_zulaessig: true }],
  ['Leitsymptomatik c bei EX nicht im Katalog', { leitsymptomatik: 'C', icd10: 'S43.4', diagnosegruppe: 'EX' }, { leitsymptomatik_zulaessig: false }],
  ['Leitsymptomatik leer bleibt offen', { leitsymptomatik: null }, { leitsymptomatik_zulaessig: null }],
  ['Leitsymptomatik als Freitext bleibt offen', { leitsymptomatik: 'patientenindividuell' }, { leitsymptomatik_zulaessig: null }],
  ['Leitsymptomatik bei anderer Gruppe bleibt offen', { leitsymptomatik: 'c', icd10: 'G35', diagnosegruppe: 'ZN' }, { leitsymptomatik_zulaessig: null }],
  ['Höchstmenge zählt ergänzende nicht', { heilmittel: [{ name: 'KG', einheiten: 6, art: 'vorrangig' }, { name: 'WT', einheiten: 6, art: 'ergaenzend' }] }, { summe_einheiten: 12, summe_einheiten_vorrangig: 6 }],
  ['Unbekannte Art zählt vorsichtshalber mit', { heilmittel: [{ name: 'KG', einheiten: 10, art: 'unbekannt' }] }, { summe_einheiten_vorrangig: 10 }]
];

let ok = 0, gesamt = 0;
for (const [datei, liste] of [['vier-pruefer.json', faelle], ['merge-formular-vier-pruefer.json', [...faelle, ...nurMerge]]]) {
  const fakten = laden(datei);
  console.log(`\n${datei}`);
  for (const [name, aenderung, erwartet] of liste) {
    gesamt++;
    const f = fakten({ ...basis, leitsymptomatik: 'a', ...aenderung });
    for (const [k, v] of Object.entries(erwartet)) assert.equal(f[k], v, `${datei} – ${name}: ${k}`);
    ok++; console.log('✓', name);
  }
}
console.log(`\n${ok}/${gesamt} Tests bestanden`);
