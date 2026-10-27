// Text redigieren (Regeln) – JavaScript-Port von redaktion/regeln.py (Valentin Klamka).
// Läuft vollständig in n8n Cloud, kein Text verlässt den Workflow.
// Portiert: alle Regeln, Spannen-Logik, Zusammenfassen gleicher Marker.
// Nicht portiert: das NER-Modell (Davlan BERT) – Namen ohne Rollenwort
// ("Mustermann klagt …") werden in der Cloud NICHT erkannt. Für echte Daten
// ist deshalb der Formularweg vorgesehen (deterministische Redaktion je Feld).
const W = '[\\p{L}\\p{N}_]';
const B = `(?<!${W})`;   // Wortgrenze vorn (Unicode, wie Python \b)
const E = `(?!${W})`;    // Wortgrenze hinten
const R = (src, flags = '') => new RegExp(src.replaceAll('\\b<', B).replaceAll('\\b>', E), 'gu' + flags);
const GR = '[A-ZÄÖÜ]', KL = '[a-zäöüß-]';
const ROLLE = '(?:Patient(?:in|en)?|Versicherte(?:r|n)?|Herr(?:n)?|Frau(?:en)?|Kind(?:er)?|Sohn|Tochter|Ehefrau|Ehemann|Lebenspartner(?:in)?|Mutter|Vater|Angehörige(?:r|n)?)';
const NUMERISCH = R('\\b<(?:\\+49|0049|0)[ \\t\\d/.-]{6,}\\d');
const DATUM = /^\d{1,2}\.\d{1,2}\.\d{4}$/;
const REGELN = [
  ['geburtsdatum', R('\\b<(?:geb(?:oren|\\.)?\\s*(?:am)?|Geb\\.?-?Datum|Geburtsdatum)\\s*:?\\s*\\d{1,2}\\.\\d{1,2}\\.\\d{4}', 'i'), '[Geburtsdatum]'],
  ['versichertennummer', R('\\b<[A-Z]{1,2}\\d{8,10}\\b>'), '[Versichertennummer]'],
  ['email', R('[\\p{L}\\p{N}_.+-]+@[\\p{L}\\p{N}_-]+(?:\\.[\\p{L}\\p{N}_-]+)+'), '[E-Mail]'],
  ['telefon', R('\\b<(?:Tel\\.?|Telefon|Mobil|Handy|Fax)\\s*:?\\s*\\+?[\\d \\t/()-]{6,}\\d', 'i'), '[Telefon]'],
  ['iban-de', R('\\b<DE\\d{2}(?: ?\\d{4}){4} ?\\d{2}\\b>'), '[IBAN]'],
  ['iban', R('\\b<[A-Z]{2}\\d{2}(?: ?[A-Z0-9]{4}){2,7} ?[A-Z0-9]{0,2}\\b>'), '[IBAN]'],
  ['lanr', R('\\b<LANR\\s*:?\\s*\\d{6,10}\\b>', 'i'), 'LANR [LANR]'],
  ['bsnr', R('\\b<BSNR\\s*:?\\s*\\d{6,10}\\b>', 'i'), 'BSNR [BSNR]'],
  ['rolle-name', R(`\\b<${ROLLE}\\s+(?:Dr\\.\\s*)?(?:med\\.\\s*)?(?<name>${GR}${KL}+(?:\\s+${GR}${KL}+)*)`), '[Name]', 'name'],
  ['arzt', R(`\\b<Dr\\.\\s*(?:med\\.\\s*)?(?:dent\\.\\s*)?${GR}${KL}+(?:\\s+${GR}${KL}+)*`), '[Arzt]'],
  ['name-zeile', R('\\b<(?:Nach)?[Nn]ame\\s*:\\s*[^\\n;,]+'), '[Name]'],
  ['anschrift', R('\\b<[A-ZÄÖÜ][a-zäöüß]+(?:straße|strasse|str\\.|weg|allee|platz|ring|gasse|damm|ufer)\\s*\\d+[a-z]?\\b>', 'i'), '[Anschrift]'],
  ['plz-ort', R('\\b<\\d{5}\\s+[A-ZÄÖÜ][a-zäöüß]+(?:\\s+[A-ZÄÖÜ][a-zäöüß]+)?'), '[PLZ Ort]'],
  ['praxis', R(`\\b<Praxis\\s+(?:(?:am|an der|im|für)\\s+)?(?:Dr\\.\\s*(?:med\\.\\s*)?)?${GR}${KL}+(?:\\s+${GR}${KL}+){0,2}`), '[Praxis]'],
];
const NAME_FUER_MARKE = { '[Name]': 'Name', '[Anschrift]': 'Anschrift', '[PLZ Ort]': 'PLZ und Ort', '[Telefon]': 'Telefonnummer', '[E-Mail]': 'E-Mail', '[Versichertennummer]': 'Versichertennummer', '[Geburtsdatum]': 'Geburtsdatum', '[Arzt]': 'Arzt', '[Praxis]': 'Praxis', '[IBAN]': 'IBAN', 'LANR [LANR]': 'LANR', 'BSNR [BSNR]': 'BSNR' };

function regelSpannen(text) {
  const sp = [];
  for (const m of text.matchAll(NUMERISCH)) {
    if (DATUM.test(m[0].trim())) continue;
    sp.push({ start: m.index, end: m.index + m[0].length, marke: '[Telefon]' });
  }
  for (const [, muster, marke, gruppe] of REGELN) {
    for (const m of text.matchAll(new RegExp(muster.source, muster.flags + 'd'))) {
      const [s, e] = gruppe ? m.indices.groups[gruppe] : m.indices[0];
      sp.push({ start: s, end: e, marke });
    }
  }
  return sp;
}
function verschmelze(text, sp) {
  const sortiert = [...sp].sort((a, b) => a.start - b.start || (b.end - b.start) - (a.end - a.start));
  const beh = [];
  for (const s of sortiert) if (!beh.some((b) => b.start < s.end && s.start < b.end)) beh.push(s);
  const zus = [];
  for (const s of beh) {
    const l = zus[zus.length - 1];
    if (l && l.marke === s.marke && /^[ \t,]*$/.test(text.slice(l.end, s.start))) zus[zus.length - 1] = { ...l, end: s.end };
    else zus.push(s);
  }
  return zus;
}
function redigiere(text) {
  if (typeof text !== 'string' || !text.trim()) return { text, entfernt: [] };
  const sp = verschmelze(text, regelSpannen(text));
  const entfernt = [];
  let out = text;
  for (const s of [...sp].sort((a, b) => b.start - a.start)) out = out.slice(0, s.start) + s.marke + out.slice(s.end);
  for (const s of sp) { const n = NAME_FUER_MARKE[s.marke] ?? s.marke.replace(/[[\]]/g, ''); if (!entfernt.includes(n)) entfernt.push(n); }
  return { text: out, entfernt };
}
