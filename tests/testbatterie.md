# Testbatterie Verordnungs-Check

*Stand 20.10.2026 · 13 angewandte Tests + 100 neue Fälle · alle Daten synthetisch*

## Zweck und Nutzung

- **Diese Datei** ist zum Lesen, Prüfen und Abhaken. **`testbatterie.json`** enthält dieselben Fälle maschinenlesbar für einen automatischen Testlauf (z. B. per n8n-Schleife oder Import in die Tabelle `testfaelle`).
- **Eingabe:** JSON-Fälle als Text in den Chat „Rezeption: Verordnung eingeben“ einfügen. Der Workflow erkennt sie als strukturiert und überspringt den Extraktor. Freitext-Fälle testen zusätzlich Extraktion und PII-Entfernung.
- **Festes Prüfdatum:** 26.10.2026 für alle neuen Fälle (Feld `pruefdatum`). Nur so sind Fristen reproduzierbar. Beim Formular gilt immer das Tagesdatum.
- **Referenzstandard** sind ausschließlich die Regelwerke (HeilM-RL, Heilmittelkatalog, KBV-Diagnoseliste). Die Soll-Werte sind aus den Texten in eurer Wissensbasis abgeleitet. ⚠️ Vor dem Einsatz als Referenz: Vier-Augen-Prüfung durch das Team, vor allem der Grenzfälle.
- **Kein Lernen auf den Test:** Keine ICD-Codes aus diesen Fällen in Prompts übernehmen.
- **Wertung:** Pro Fall zählt die Gesamtampel. Befunde geben an, welcher Prüfer was melden muss. Zusätzliche Hinweise in grünen Fällen zählen als Fehlalarm, zusätzliche rote Befunde als kritischer Fehlalarm.

### Aufteilung

| Set | Zweck | Fälle | 🟢 | 🟡 | 🔴 | Grenzfälle |
|---|---|---|---|---|---|---|
| **E** | Evaluationsset (Holdout): nur für die formale Messung, nie zum Nachbessern | 65 | 20 | 10 | 35 | 8 |
| **D** | Entwicklungsset: darf zum Nachbessern genutzt werden | 35 | 11 | 5 | 19 | 4 |

Das E-Set erfüllt die Vorgaben aus `docs/erfolgskriterien.md`: ≥ 12 grün, ≥ 8 gelb, ≥ 25 rot (je Prüfer ≥ 5: Formal 10, Diagnose 10, Mengen 9, Fristen 10), ≥ 5 Grenzfälle. Bei 3 Läufen je Fall sind das 195 Prüfungen.

**Ab v5:** 10 Fälle brauchen die Verordnungsfall-Prüfung mit Historie (Feld `vorverordnungen`, Spalte „v5“). Bis v5 steht, zählen sie nicht in die Quote. Das Feldformat ist ein **Vorschlag** und mit Derk abzustimmen.

### Angewandte Regeln

| Regel | Wert | Fundstelle |
|---|---|---|
| Behandlungsbeginn | ≤ 28 Kalendertage nach Ausstellung, dringlich ≤ 14 | HeilM-RL § 15 Abs. 1, sonst ungültig nach Abs. 2 |
| Unterbrechung | > 14 Kalendertage ohne angemessene Begründung → ungültig | HeilM-RL § 16 Abs. 4 |
| Pflichtangaben | vollständig ausgefüllter Vordruck | HeilM-RL § 13 Abs. 1 und 2 |
| Höchstmenge je VO (WS, EX) | bis zu 6 Einheiten, aufteilbar auf max. 3 vorrangige Heilmittel | Heilmittelkatalog; HeilM-RL § 12 Abs. 2 |
| Ergänzendes Heilmittel | max. eins; Einheiten richten sich nach den vorrangigen | HeilM-RL § 12 Abs. 3, § 7 Abs. 5 |
| Ergänzende Heilmittel je Gruppe | WS: Wärme, Kälte, Traktion, Elektro, hydroelektrische Bäder · EX: ohne Traktion | Heilmittelkatalog |
| Leitsymptomatik WS/EX | a, b oder x (patientenindividuell) | Heilmittelkatalog |
| Frequenz | Empfehlung 1–3× wöchentlich; Abweichung ohne Dokumentation zulässig | Heilmittelkatalog; HeilM-RL § 12 Abs. 1 Satz 4 |
| Verordnungsfall | gleicher Patient, ICD 3-stellig, Diagnosegruppe, Verordner; neu nach 6 Monaten ohne Verordnung | HeilM-RL § 7 Abs. 1 und 3 |
| Orientierende Menge (WS, EX) | 18 Einheiten je Fall, nur vorrangige zählen → Überschreitung = gelb | Heilmittelkatalog; HeilM-RL § 7 Abs. 2 |
| Entlassmanagement | Verordnungen aus dem Entlassmanagement zählen nicht zum Fall | HeilM-RL § 16a Abs. 5 |
| Besonderer Verordnungsbedarf | Code auf der Liste mit passender Diagnosegruppe, ggf. mit Zweitcode → Hinweis (gelb), nie rot | KBV-Diagnoseliste |

## Teil A: Bereits angewandte Tests

Quelle: `supabase/seed/testfaelle.sql` (Prüfdatum 12.10.2026), Ausführungen des Merge-Workflows vom 20.10.2026.

| ID | Eingang | Fall | Soll | Erwartete Befunde | Letztes Ergebnis |
|---|---|---|---|---|---|
| TF01 | JSON | Vollständig und regelkonform | grün | – | v4: grün ✅ · Merge (Ausführung 897): grün, 18/18 ok ✅ |
| TF02 | JSON | Beginn 41 Tage nach Ausstellung | rot | Fristen: Behandlungsbeginn | v4: rot ✅ |
| TF03 | JSON / Freitext | Schulter-Code M75.1 mit WS | rot | Diagnose: Diagnosegruppe | v4: rot ✅ · Merge als Freitext (898): rot ✅, aber Fehlalarm Mengen-Prüfer ❌ → Regressionstest nach Prompt-Fix |
| TF04 | JSON | 10 Einheiten bei WS | rot | Mengen: Einheiten | v4: rot ✅ |
| TF05 | JSON | Leitsymptomatik und LANR fehlen | rot | Formal: Leitsymptomatik, LANR | v4: rot ✅ |
| TF06 | JSON | 22 Tage Unterbrechung ohne Grund | rot | Fristen: Unterbrechung | v4: rot ✅ |
| TF07 | JSON | Dringlich, Beginn nach 18 Tagen | rot | Fristen: Behandlungsbeginn | v4: rot ✅ |
| TF08 | JSON | Kontrollfall Gonarthrose mit EX | grün | – | v4: grün ✅ |
| TF09 | JSON | Kontrollfall M50.1 mit EX | rot | Diagnose: Diagnosegruppe (+ Hinweis KBV-Liste) | v4: rot ✅ |
| TF10 | JSON | Kontrollfall dringlich, Beginn nach 7 Tagen | grün ⚠️ | – | v4: grün ✅ · ⚠️ Leitsymptomatik „c“ gibt es bei EX laut Katalog nicht → Soll prüfen (siehe Auffälligkeiten) |
| M-899 | Formular | Formular: M17.1, EX, 6× KG, Ausstellung 15.10.2026 | grün | – | Merge (899): grün, 18/18 ok, 6 PII-Felder ersetzt ✅ · Prüfdatum = Tagesdatum, Frist läuft ab 12.11.2026 ab |
| TF11 | JSON + Historie | geplant v5: Menge im Verordnungsfall überschritten | gelb | Mengen: Verordnungsfall | noch nicht gebaut · Muster: TF047 |
| TF12 | JSON + Historie | geplant v5: neuer Fall nach 6 Monaten | grün | – | noch nicht gebaut · Muster: TF035 |

## Teil B: 100 neue Fälle

### 🟢 Grüne Fälle (23)

| ✓ | ID | Set | Prüfer | Fall | Kurz | Eingang | v5 | Soll | Erwartete Befunde | Fundstelle |
|---|---|---|---|---|---|---|---|---|---|---|
| ☐ | TF013 | E | alle | LWS-Lumboischialgie, Standardfall | M54.4 · WS · KG 6 | JSON |  | 🟢 grün | – | HeilM-RL § 13 Abs. 2; Heilmittelkatalog WS |
| ☐ | TF014 | E | alle | Zervikalneuralgie, MT, Spanne 1-2x | M54.2 · WS · MT 6 | JSON |  | 🟢 grün | – | Heilmittelkatalog WS |
| ☐ | TF015 | E | menge | Zwei vorrangige Heilmittel, Summe 6 | M53.1 · WS · KG 4 + MT 2 | JSON |  | 🟢 grün | – | HeilM-RL § 12 Abs. 2; Heilmittelkatalog WS |
| ☐ | TF016 | D | alle | Bandscheibenverlagerung, KG-Gerät | M51.2 · WS · KG-Gerät 6 | JSON |  | 🟢 grün | – | Heilmittelkatalog WS |
| ☐ | TF017 | E | menge | Ergänzendes Heilmittel gleich viele Einheiten wie vorrangig | M47.86 · WS · KG 6 (+ Wärmetherapie 6) | JSON |  | 🟢 grün | – | HeilM-RL § 7 Abs. 5; Heilmittelkatalog WS |
| ☐ | TF018 | E | frist | HWS-Distorsion, dringlich, Beginn nach 10 Tagen | S13.4 · WS · KG 6 | JSON |  | 🟢 grün | – | HeilM-RL § 15 Abs. 1 |
| ☐ | TF019 | E | formal | Leitsymptomatik x mit patientenindividueller Angabe | M43.16 · WS · KG 6 | JSON |  | 🟢 grün | – | Heilmittelkatalog WS |
| ☐ | TF020 | E | alle | Gonarthrose, Spanne 1-2x | M17.1 · EX · KG 6 | JSON |  | 🟢 grün | – | Heilmittelkatalog EX |
| ☐ | TF021 | D | alle | Koxarthrose, KG-Gerät | M16.1 · EX · KG-Gerät 6 | JSON |  | 🟢 grün | – | Heilmittelkatalog EX |
| ☐ | TF022 | E | alle | Impingement Schulter, MT | M75.4 · EX · MT 6 | JSON |  | 🟢 grün | – | Heilmittelkatalog EX |
| ☐ | TF023 | D | menge | Epicondylitis, KG 3 + MT 3 | M77.1 · EX · KG 3 + MT 3 | JSON |  | 🟢 grün | – | HeilM-RL § 12 Abs. 2; Heilmittelkatalog EX |
| ☐ | TF024 | E | menge | Achillessehne, ergänzend Kältetherapie, 3x/Woche | M76.6 · EX · KG 6 (+ Kältetherapie 6) | JSON |  | 🟢 grün | – | Heilmittelkatalog EX |
| ☐ | TF025 | E | frist | Außenknöchelfraktur, dringlich, Beginn nach 5 Tagen | S82.6 · EX · KG 6 | JSON |  | 🟢 grün | – | HeilM-RL § 15 Abs. 1 |
| ☐ | TF026 | D | frist | Behandlung läuft, letzte Sitzung vor 6 Tagen | S93.40 · EX · KG 6 | JSON |  | 🟢 grün | – | HeilM-RL § 16 Abs. 4 |
| ☐ | TF027 | E | alle | Chondropathie Patella, 1x/Woche | M22.4 · EX · KG 6 | JSON |  | 🟢 grün | – | Heilmittelkatalog EX |
| ☐ | TF028 | E | frist | Unterbrechung 20 Tage mit Begründung | M54.4 · WS · KG 6 | JSON |  | 🟢 grün | – | HeilM-RL § 16 Abs. 4 |
| ☐ | TF029 | D | menge | Drei vorrangige Heilmittel, Summe 6 | M17.1 · EX · KG 2 + MT 2 + KG-Gerät 2 | JSON |  | 🟢 grün | – | HeilM-RL § 12 Abs. 2; Heilmittelkatalog EX |
| ☐ | TF030 | D | frist | Beginn nach 27 Tagen | M54.2 · WS · KG 6 | JSON |  | 🟢 grün | – | HeilM-RL § 15 Abs. 1 |
| ☐ | TF031 | D | alle | Freitext: Gonarthrose vollständig | M17.1 · EX · KG 6 | Freitext |  | 🟢 grün | – | Heilmittelkatalog EX |
| ☐ | TF032 | E | alle | Freitext: LWS, zwei Heilmittel | M54.4 · WS · KG 4 + MT 2 | Freitext |  | 🟢 grün | – | Heilmittelkatalog WS |
| ☐ | TF033 | E | menge | v5: Folgeverordnung, 6 + 6 = 12 im Fall | M54.4 · WS · KG 6 | JSON | ja | 🟢 grün | – | HeilM-RL § 7 Abs. 1; Heilmittelkatalog WS |
| ☐ | TF034 | E | menge | v5: 12 Einheiten bei anderem Arzt, neuer Fall | M54.4 · WS · KG 6 | JSON | ja | 🟢 grün | – | HeilM-RL § 7 Abs. 3 |
| ☐ | TF035 | D | menge | v5: letzte Vorverordnung vor 7 Monaten, neuer Fall (TF12-Muster) | M54.4 · WS · KG 6 | JSON | ja | 🟢 grün | – | HeilM-RL § 7 Abs. 1 Satz 5 |

### 🟡 Gelbe Fälle (15)

| ✓ | ID | Set | Prüfer | Fall | Kurz | Eingang | v5 | Soll | Erwartete Befunde | Fundstelle |
|---|---|---|---|---|---|---|---|---|---|---|
| ☐ | TF036 | E | diagnose | HWS-Bandscheibe mit Radikulopathie, Zweitcode vorhanden | M50.1 · WS · KG 6 | JSON |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF037 | E | diagnose | LWS-Bandscheibe mit Radikulopathie, Zweitcode vorhanden | M51.1 · WS · KG 6 | JSON |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF038 | D | diagnose | Spinalkanalstenose lumbal mit Radikulopathie | M48.06 · WS · KG 6 | JSON |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF039 | E | diagnose | Spondylose mit Radikulopathie | M47.26 · WS · KG 6 | JSON |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF040 | D | diagnose | Spondylitis ankylosans, WS | M45.09 · WS · KG 6 | JSON |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF041 | E | diagnose | Seronegative chronische Polyarthritis, EX | M06.06 · EX · KG 6 | JSON |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF042 | E | diagnose | Ehlers-Danlos-Syndrom, WS | Q79.6 · WS · KG 6 | JSON |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF043 | D | diagnose | Läsion der Rotatorenmanschette, EX | M75.1 · EX · KG 6 | JSON |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF044 | E | diagnose | Knieprothese mit Zweitcode | Z96.65 · EX · KG 6 | JSON |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF045 | D | diagnose | Hüftprothese mit Zweitcode | Z96.64 · EX · KG 6 | JSON |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF046 | E | diagnose | Freitext: LWS-Bandscheibe mit Radikulopathie | M51.1 · WS · KG 6 | Freitext |  | 🟡 gelb | Diagnose: Besonderer Verordnungsbedarf (Hinweis) | KBV-Diagnoseliste |
| ☐ | TF047 | E | menge | v5: 18 im Fall + 6 = 24 (TF11-Muster) | M54.4 · WS · KG 6 | JSON | ja | 🟡 gelb | Mengen: Verordnungsfall (orientierende Menge) (Hinweis) | HeilM-RL § 7 Abs. 2; Heilmittelkatalog WS |
| ☐ | TF048 | E | menge | v5: 14 im Fall + 6 = 20 | M54.4 · WS · KG 6 | JSON | ja | 🟡 gelb | Mengen: Verordnungsfall (orientierende Menge) (Hinweis) | HeilM-RL § 7 Abs. 2; Heilmittelkatalog WS |
| ☐ | TF049 | D | menge | v5: andere 4. Stelle, gleicher Fall (M54.2 → M54.4) | M54.4 · WS · KG 6 | JSON | ja | 🟡 gelb | Mengen: Verordnungsfall (orientierende Menge) (Hinweis) | HeilM-RL § 7 Abs. 1 Satz 1 |
| ☐ | TF050 | E | menge | v5: EX, 18 im Fall + 6 | M17.1 · EX · KG 6 | JSON | ja | 🟡 gelb | Mengen: Verordnungsfall (orientierende Menge) (Hinweis) | HeilM-RL § 7 Abs. 2; Heilmittelkatalog EX |

### 🔴 Rote Fälle (50)

| ✓ | ID | Set | Prüfer | Fall | Kurz | Eingang | v5 | Soll | Erwartete Befunde | Fundstelle |
|---|---|---|---|---|---|---|---|---|---|---|
| ☐ | TF051 | E | formal | Kostenträger fehlt | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Formal: Kostenträger | HeilM-RL § 13 Abs. 2 |
| ☐ | TF052 | E | formal | LANR fehlt | M17.1 · EX · KG 6 | JSON |  | 🔴 rot | Formal: LANR | HeilM-RL § 13 Abs. 2 |
| ☐ | TF053 | D | formal | BSNR fehlt | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Formal: BSNR | HeilM-RL § 13 Abs. 2 |
| ☐ | TF054 | E | formal | Ausstellungsdatum fehlt | M75.4 · EX · KG 6 | JSON |  | 🔴 rot | Formal: Ausstellungsdatum | HeilM-RL § 13 Abs. 2 |
| ☐ | TF055 | D | formal | Unterschrift fehlt | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Formal: Unterschrift | HeilM-RL § 13 Abs. 1 |
| ☐ | TF056 | E | formal | ICD-10-Code fehlt | – · WS · KG 6 | JSON |  | 🔴 rot | Formal: ICD-10-Code | HeilM-RL § 13 Abs. 2 |
| ☐ | TF057 | E | formal | Diagnosegruppe fehlt | M16.1 · – · KG 6 | JSON |  | 🔴 rot | Formal: Diagnosegruppe | HeilM-RL § 13 Abs. 2 |
| ☐ | TF058 | D | formal | Leitsymptomatik fehlt | M53.1 · WS · KG 6 | JSON |  | 🔴 rot | Formal: Leitsymptomatik | HeilM-RL § 13 Abs. 2 |
| ☐ | TF059 | E | formal | Heilmittel ohne Einheiten | M54.4 · WS · KG – | JSON |  | 🔴 rot | Formal: Heilmittel mit Einheiten | HeilM-RL § 13 Abs. 2 |
| ☐ | TF060 | D | formal | Therapiefrequenz fehlt | M77.1 · EX · KG 6 | JSON |  | 🔴 rot | Formal: Therapiefrequenz | HeilM-RL § 13 Abs. 2 |
| ☐ | TF061 | E | formal | LANR nur 8 Ziffern | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Formal: LANR | HeilM-RL § 13 Abs. 2 |
| ☐ | TF062 | E | formal | BSNR mit Buchstaben | S82.6 · EX · KG 6 | JSON |  | 🔴 rot | Formal: BSNR | HeilM-RL § 13 Abs. 2 |
| ☐ | TF063 | E | diagnose | Gonarthrose mit WS | M17.1 · WS · KG 6 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog, Diagnosegruppen WS/EX |
| ☐ | TF064 | E | diagnose | Koxarthrose mit WS | M16.1 · WS · KG 6 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog, Diagnosegruppen WS/EX |
| ☐ | TF065 | D | diagnose | Lumboischialgie mit EX | M54.4 · EX · KG 6 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog, Diagnosegruppen WS/EX |
| ☐ | TF066 | E | diagnose | Zervikobrachial-Syndrom mit EX | M53.1 · EX · KG 6 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog, Diagnosegruppen WS/EX |
| ☐ | TF067 | D | diagnose | Bandscheibenverlagerung mit EX | M51.2 · EX · KG 6 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog, Diagnosegruppen WS/EX |
| ☐ | TF068 | E | diagnose | HWS-Distorsion mit EX | S13.4 · EX · KG 6 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog, Diagnosegruppen WS/EX |
| ☐ | TF069 | E | diagnose | Außenknöchelfraktur mit WS | S82.6 · WS · KG 6 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog, Diagnosegruppen WS/EX |
| ☐ | TF070 | D | diagnose | Epicondylitis mit WS | M77.1 · WS · KG 6 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog, Diagnosegruppen WS/EX |
| ☐ | TF071 | E | diagnose | Impingement Schulter mit WS | M75.4 · WS · KG 6 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog, Diagnosegruppen WS/EX |
| ☐ | TF072 | D | diagnose | Spondylolisthesis mit EX | M43.16 · EX · KG 6 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog, Diagnosegruppen WS/EX |
| ☐ | TF073 | E | menge | 7 Einheiten bei WS | M54.4 · WS · KG 7 | JSON |  | 🔴 rot | Mengen: Einheiten je Verordnung | Heilmittelkatalog WS |
| ☐ | TF074 | E | menge | 8 Einheiten bei EX | M17.1 · EX · KG 8 | JSON |  | 🔴 rot | Mengen: Einheiten je Verordnung | Heilmittelkatalog EX |
| ☐ | TF075 | D | menge | 12 Einheiten bei WS | M54.2 · WS · KG 12 | JSON |  | 🔴 rot | Mengen: Einheiten je Verordnung | Heilmittelkatalog WS |
| ☐ | TF076 | E | menge | KG 4 + MT 4 = 8 bei EX | M75.4 · EX · KG 4 + MT 4 | JSON |  | 🔴 rot | Mengen: Einheiten je Verordnung | HeilM-RL § 12 Abs. 2; Heilmittelkatalog EX |
| ☐ | TF077 | D | menge | Vier vorrangige Heilmittel | M54.4 · WS · KG 2 + MT 2 + KG-Gerät 1 + KMT 1 | JSON |  | 🔴 rot | Mengen: Heilmittel-Kombination | HeilM-RL § 12 Abs. 2 |
| ☐ | TF078 | E | menge | Ergänzend 8 Einheiten bei 6 vorrangigen | M54.4 · WS · KG 6 (+ Wärmetherapie 8) | JSON |  | 🔴 rot | Mengen: Ergänzendes Heilmittel | HeilM-RL § 7 Abs. 5 Satz 2 |
| ☐ | TF079 | E | menge | KG 6 + MT 6 = 12 bei WS | M53.1 · WS · KG 6 + MT 6 | JSON |  | 🔴 rot | Mengen: Einheiten je Verordnung | HeilM-RL § 12 Abs. 2; Heilmittelkatalog WS |
| ☐ | TF080 | D | menge | KG-Gerät 10 bei EX | M16.1 · EX · KG-Gerät 10 | JSON |  | 🔴 rot | Mengen: Einheiten je Verordnung | Heilmittelkatalog EX |
| ☐ | TF081 | E | menge | Ergänzend Elektro 6 bei KG 3 | M77.1 · EX · KG 3 (+ Elektrotherapie 6) | JSON |  | 🔴 rot | Mengen: Ergänzendes Heilmittel | HeilM-RL § 7 Abs. 5 Satz 2 |
| ☐ | TF082 | D | menge | KMT 9 bei EX | M76.6 · EX · KMT 9 | JSON |  | 🔴 rot | Mengen: Einheiten je Verordnung | Heilmittelkatalog EX |
| ☐ | TF083 | E | frist | Beginn nach 35 Tagen | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Fristen: Behandlungsbeginn | HeilM-RL § 15 Abs. 1 und 2 |
| ☐ | TF084 | E | frist | Beginn nach 60 Tagen | M54.2 · WS · KG 6 | JSON |  | 🔴 rot | Fristen: Behandlungsbeginn | HeilM-RL § 15 Abs. 1 und 2 |
| ☐ | TF085 | D | frist | EX, Beginn nach 45 Tagen | M17.1 · EX · KG 6 | JSON |  | 🔴 rot | Fristen: Behandlungsbeginn | HeilM-RL § 15 Abs. 1 und 2 |
| ☐ | TF086 | E | frist | Dringlich, Beginn nach 15 Tagen | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Fristen: Behandlungsbeginn | HeilM-RL § 15 Abs. 1 und 2 |
| ☐ | TF087 | D | frist | Dringlich, Beginn nach 20 Tagen | S82.6 · EX · KG 6 | JSON |  | 🔴 rot | Fristen: Behandlungsbeginn | HeilM-RL § 15 Abs. 1 und 2 |
| ☐ | TF088 | E | frist | Dringlich, Beginn nach 40 Tagen | S13.4 · WS · KG 6 | JSON |  | 🔴 rot | Fristen: Behandlungsbeginn | HeilM-RL § 15 Abs. 1 und 2 |
| ☐ | TF089 | E | frist | Unterbrechung 21 Tage ohne Grund | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Fristen: Unterbrechung | HeilM-RL § 16 Abs. 4 |
| ☐ | TF090 | D | frist | Unterbrechung 30 Tage ohne Grund | M16.1 · EX · KG 6 | JSON |  | 🔴 rot | Fristen: Unterbrechung | HeilM-RL § 16 Abs. 4 |
| ☐ | TF091 | E | frist | Unterbrechung 18 Tage, Grund leer | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Fristen: Unterbrechung | HeilM-RL § 16 Abs. 4 |
| ☐ | TF092 | D | frist | EX, Unterbrechung 25 Tage ohne Grund | M75.4 · EX · KG 6 | JSON |  | 🔴 rot | Fristen: Unterbrechung | HeilM-RL § 16 Abs. 4 |
| ☐ | TF093 | E | mehrere | LANR fehlt und Beginn zu spät | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Formal: LANR; Fristen: Behandlungsbeginn | HeilM-RL § 13 Abs. 2, § 15 Abs. 1 |
| ☐ | TF094 | E | mehrere | Diagnosegruppe falsch und 10 Einheiten | M17.1 · WS · KG 10 | JSON |  | 🔴 rot | Diagnose: Diagnosegruppe; Mengen: Einheiten je Verordnung | Heilmittelkatalog |
| ☐ | TF095 | D | mehrere | 8 Einheiten und Unterbrechung 16 Tage | M54.4 · WS · KG 8 | JSON |  | 🔴 rot | Mengen: Einheiten je Verordnung; Fristen: Unterbrechung | Heilmittelkatalog; HeilM-RL § 16 Abs. 4 |
| ☐ | TF096 | E | mehrere | Drei Fehler: Unterschrift, Diagnosegruppe, dringlich zu spät | M54.4 · EX · KG 6 | JSON |  | 🔴 rot | Formal: Unterschrift; Diagnose: Diagnosegruppe; Fristen: Behandlungsbeginn | HeilM-RL § 13, § 15; Heilmittelkatalog |
| ☐ | TF097 | D | mehrere | Leitsymptomatik und Frequenz fehlen | M22.4 · EX · KG 6 | JSON |  | 🔴 rot | Formal: Leitsymptomatik; Formal: Therapiefrequenz | HeilM-RL § 13 Abs. 2 |
| ☐ | TF098 | E | diagnose | Freitext: Schulterdiagnose mit WS (wie TF03) | M75.4 · WS · KG 6 | Freitext |  | 🔴 rot | Diagnose: Diagnosegruppe | Heilmittelkatalog |
| ☐ | TF099 | E | menge | Freitext: 10 Einheiten KG bei EX | M16.1 · EX · KG 10 | Freitext |  | 🔴 rot | Mengen: Einheiten je Verordnung | Heilmittelkatalog EX |
| ☐ | TF100 | E | frist | Freitext: Beginn 40 Tage nach Ausstellung | M54.4 · WS · KG 6 | Freitext |  | 🔴 rot | Fristen: Behandlungsbeginn | HeilM-RL § 15 Abs. 1 und 2 |

### ⚖️ Grenzfälle (12)

| ✓ | ID | Set | Prüfer | Fall | Kurz | Eingang | v5 | Soll | Erwartete Befunde | Fundstelle |
|---|---|---|---|---|---|---|---|---|---|---|
| ☐ | TF101 | E | frist | Beginn exakt am 28. Tag — *Tag der Ausstellung zählt nicht mit; 28 Tage danach ist noch fristgerecht.* | M54.4 · WS · KG 6 | JSON |  | 🟢 grün | – | HeilM-RL § 15 Abs. 1 |
| ☐ | TF102 | E | frist | Beginn am 29. Tag (Gegenprobe) | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Fristen: Behandlungsbeginn | HeilM-RL § 15 Abs. 1 und 2 |
| ☐ | TF103 | D | frist | Dringlich, Beginn exakt am 14. Tag | M54.4 · WS · KG 6 | JSON |  | 🟢 grün | – | HeilM-RL § 15 Abs. 1 |
| ☐ | TF104 | E | frist | Unterbrechung exakt 14 Tage ohne Grund — *Auslegung: Differenz 14 Tage zwischen zwei Sitzungen gilt als nicht länger als 14 Kalendertage. Im Team bestätigen.* | M54.4 · WS · KG 6 | JSON |  | 🟢 grün | – | HeilM-RL § 16 Abs. 4 |
| ☐ | TF105 | D | frist | Unterbrechung 15 Tage ohne Grund (Gegenprobe) | M54.4 · WS · KG 6 | JSON |  | 🔴 rot | Fristen: Unterbrechung | HeilM-RL § 16 Abs. 4 |
| ☐ | TF106 | E | diagnose | Leitsymptomatik c bei EX — *Der Katalog kennt für EX nur a, b und x. Die Prompts akzeptieren derzeit auch c; TF10 ist davon betroffen.* | S43.4 · EX · KG 6 | JSON |  | 🔴 rot | Diagnose: Leitsymptomatik | Heilmittelkatalog EX (nur a, b, x) |
| ☐ | TF107 | E | menge | Traktion als ergänzendes Heilmittel bei EX — *Kein Prüfer hat die Zulässigkeit des ergänzenden Heilmittels ausdrücklich im Mandat. Zeigt eine Lücke.* | M17.1 · EX · KG 6 (+ Traktion 6) | JSON |  | 🔴 rot | Mengen: Ergänzendes Heilmittel | Heilmittelkatalog EX (Traktion nur bei WS) |
| ☐ | TF108 | E | menge | Frequenz 4x/Woche — *Frequenzempfehlung ist Orientierung; Abweichung ohne zusätzliche Dokumentation zulässig. Soll grün, ein Hinweis wäre ein Fehlalarm.* | M54.4 · WS · KG 6 | JSON |  | 🟢 grün | – | HeilM-RL § 12 Abs. 1 Satz 4 |
| ☐ | TF109 | E | diagnose | M50.1 ohne Zweitcode G55.1 — *Ohne Zweitcode kein anerkannter besonderer Verordnungsbedarf. Soll grün; der Prototyp meldet hier vermutlich einen Hinweis.* | M50.1 · WS · KG 6 | JSON |  | 🟢 grün | – | KBV-Diagnoseliste (beide Codes nötig) |
| ☐ | TF110 | D | menge | v5: Summe im Fall exakt 18 | M54.4 · WS · KG 6 | JSON | ja | 🟢 grün | – | HeilM-RL § 7 Abs. 2; Heilmittelkatalog WS |
| ☐ | TF111 | E | menge | v5: Vorverordnung aus dem Entlassmanagement zählt nicht — *Ohne die Regel ergäbe sich 24 (gelb).* | M54.4 · WS · KG 6 | JSON | ja | 🟢 grün | – | HeilM-RL § 16a Abs. 5 |
| ☐ | TF112 | D | menge | v5: ergänzende Einheiten zählen nicht zur orientierenden Menge — *Mit ergänzenden Einheiten wären es 36, nur vorrangige zählen: 18 (grün).* | M54.4 · WS · KG 6 (+ Wärmetherapie 6) | JSON | ja | 🟢 grün | – | HeilM-RL § 7 Abs. 2 Satz 2 |

## Teil C: Eingaben zum Kopieren

Aufklappen, Inhalt kopieren und in den Chat einfügen.

<details><summary><b>TF013</b> · 🟢 grün · LWS-Lumboischialgie, Standardfall</summary>

```json
{"verordnung_ref": "VO-0013", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF014</b> · 🟢 grün · Zervikalneuralgie, MT, Spanne 1-2x</summary>

```json
{"verordnung_ref": "VO-0014", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.2", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "b", "heilmittel": [{"name": "MT", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "1-2x/Woche", "lanr": "234567802", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF015</b> · 🟢 grün · Zwei vorrangige Heilmittel, Summe 6</summary>

```json
{"verordnung_ref": "VO-0015", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M53.1", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 4, "art": "vorrangig"}, {"name": "MT", "einheiten": 2, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF016</b> · 🟢 grün · Bandscheibenverlagerung, KG-Gerät</summary>

```json
{"verordnung_ref": "VO-0016", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M51.2", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "b", "heilmittel": [{"name": "KG-Gerät", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "876543200", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF017</b> · 🟢 grün · Ergänzendes Heilmittel gleich viele Einheiten wie vorrangig</summary>

```json
{"verordnung_ref": "VO-0017", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M47.86", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": "Wärmetherapie", "einheiten": 6}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF018</b> · 🟢 grün · HWS-Distorsion, dringlich, Beginn nach 10 Tagen</summary>

```json
{"verordnung_ref": "VO-0018", "ausstellungsdatum": "2026-10-17", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": true, "icd10": "S13.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF019</b> · 🟢 grün · Leitsymptomatik x mit patientenindividueller Angabe</summary>

```json
{"verordnung_ref": "VO-0019", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M43.16", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "x", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "leitsymptomatik_freitext": "Instabilität im Lumbalbereich mit Belastungsschmerz"}
```

</details>

<details><summary><b>TF020</b> · 🟢 grün · Gonarthrose, Spanne 1-2x</summary>

```json
{"verordnung_ref": "VO-0020", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M17.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "1-2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF021</b> · 🟢 grün · Koxarthrose, KG-Gerät</summary>

```json
{"verordnung_ref": "VO-0021", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M16.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "b", "heilmittel": [{"name": "KG-Gerät", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "345678903", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF022</b> · 🟢 grün · Impingement Schulter, MT</summary>

```json
{"verordnung_ref": "VO-0022", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M75.4", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "MT", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF023</b> · 🟢 grün · Epicondylitis, KG 3 + MT 3</summary>

```json
{"verordnung_ref": "VO-0023", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M77.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 3, "art": "vorrangig"}, {"name": "MT", "einheiten": 3, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF024</b> · 🟢 grün · Achillessehne, ergänzend Kältetherapie, 3x/Woche</summary>

```json
{"verordnung_ref": "VO-0024", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M76.6", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "b", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": "Kältetherapie", "einheiten": 6}, "frequenz": "3x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF025</b> · 🟢 grün · Außenknöchelfraktur, dringlich, Beginn nach 5 Tagen</summary>

```json
{"verordnung_ref": "VO-0025", "ausstellungsdatum": "2026-10-22", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": true, "icd10": "S82.6", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF026</b> · 🟢 grün · Behandlung läuft, letzte Sitzung vor 6 Tagen</summary>

```json
{"verordnung_ref": "VO-0026", "ausstellungsdatum": "2026-10-06", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "S93.40", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": "2026-10-21", "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF027</b> · 🟢 grün · Chondropathie Patella, 1x/Woche</summary>

```json
{"verordnung_ref": "VO-0027", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M22.4", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "b", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "1x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF028</b> · 🟢 grün · Unterbrechung 20 Tage mit Begründung</summary>

```json
{"verordnung_ref": "VO-0028", "ausstellungsdatum": "2026-09-26", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": "2026-10-07", "unterbrechungsgrund": "Krankenhausaufenthalt des Patienten", "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF029</b> · 🟢 grün · Drei vorrangige Heilmittel, Summe 6</summary>

```json
{"verordnung_ref": "VO-0029", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M17.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 2, "art": "vorrangig"}, {"name": "MT", "einheiten": 2, "art": "vorrangig"}, {"name": "KG-Gerät", "einheiten": 2, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF030</b> · 🟢 grün · Beginn nach 27 Tagen</summary>

```json
{"verordnung_ref": "VO-0030", "ausstellungsdatum": "2026-09-30", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.2", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF031</b> · 🟢 grün · Freitext: Gonarthrose vollständig</summary>

```text
Neue Verordnung für Frau Erika Beispiel, geb. 14.02.1961, Techniker Krankenkasse, Vers.-Nr. K123456789. Ausgestellt am 19.10.2026 von Dr. med. Hans Probe, LANR 123456701, BSNR 987654300, unterschrieben. ICD M17.1 Gonarthrose rechts, Diagnosegruppe EX, Leitsymptomatik a. 6x KG, 2x pro Woche. Geplanter Behandlungsbeginn 27.10.2026, Prüfdatum 26.10.2026.
```

</details>

<details><summary><b>TF032</b> · 🟢 grün · Freitext: LWS, zwei Heilmittel</summary>

```text
Herr Max Muster, AOK, Versichertennr. A987654321, Tel. 0621 1234567. Verordnung vom 19.10.2026, LANR 234567802, BSNR 876543200, Unterschrift vorhanden. Diagnose M54.4 Lumboischialgie, WS, Leitsymptomatik b. 4x KG und 2x MT, 2x wöchentlich. Start am 27.10.2026, geprüft am 26.10.2026.
```

</details>

<details><summary><b>TF033</b> · 🟢 grün · v5: Folgeverordnung, 6 + 6 = 12 im Fall</summary>

```json
{"verordnung_ref": "VO-0033", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "patient_pseudonym": "P-1001", "vorverordnungen": [{"ausstellungsdatum": "2026-09-16", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}]}
```

</details>

<details><summary><b>TF034</b> · 🟢 grün · v5: 12 Einheiten bei anderem Arzt, neuer Fall</summary>

```json
{"verordnung_ref": "VO-0034", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "patient_pseudonym": "P-1002", "vorverordnungen": [{"ausstellungsdatum": "2026-08-27", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "456789004", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-09-26", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "456789004", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}]}
```

</details>

<details><summary><b>TF035</b> · 🟢 grün · v5: letzte Vorverordnung vor 7 Monaten, neuer Fall (TF12-Muster)</summary>

```json
{"verordnung_ref": "VO-0035", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "patient_pseudonym": "P-1003", "vorverordnungen": [{"ausstellungsdatum": "2026-02-08", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-03-20", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-03-27", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}]}
```

</details>

<details><summary><b>TF036</b> · 🟡 gelb · HWS-Bandscheibe mit Radikulopathie, Zweitcode vorhanden</summary>

```json
{"verordnung_ref": "VO-0036", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M50.1", "weitere_diagnosen": [{"code": "G55.1"}], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF037</b> · 🟡 gelb · LWS-Bandscheibe mit Radikulopathie, Zweitcode vorhanden</summary>

```json
{"verordnung_ref": "VO-0037", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M51.1", "weitere_diagnosen": [{"code": "G55.1"}], "diagnosegruppe": "WS", "leitsymptomatik": "b", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF038</b> · 🟡 gelb · Spinalkanalstenose lumbal mit Radikulopathie</summary>

```json
{"verordnung_ref": "VO-0038", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M48.06", "weitere_diagnosen": [{"code": "G55.3"}], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF039</b> · 🟡 gelb · Spondylose mit Radikulopathie</summary>

```json
{"verordnung_ref": "VO-0039", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M47.26", "weitere_diagnosen": [{"code": "G55.2"}], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "345678903", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF040</b> · 🟡 gelb · Spondylitis ankylosans, WS</summary>

```json
{"verordnung_ref": "VO-0040", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M45.09", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF041</b> · 🟡 gelb · Seronegative chronische Polyarthritis, EX</summary>

```json
{"verordnung_ref": "VO-0041", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M06.06", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF042</b> · 🟡 gelb · Ehlers-Danlos-Syndrom, WS</summary>

```json
{"verordnung_ref": "VO-0042", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "Q79.6", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "b", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF043</b> · 🟡 gelb · Läsion der Rotatorenmanschette, EX</summary>

```json
{"verordnung_ref": "VO-0043", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M75.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF044</b> · 🟡 gelb · Knieprothese mit Zweitcode</summary>

```json
{"verordnung_ref": "VO-0044", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "Z96.65", "weitere_diagnosen": [{"code": "Z98.88"}], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF045</b> · 🟡 gelb · Hüftprothese mit Zweitcode</summary>

```json
{"verordnung_ref": "VO-0045", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "Z96.64", "weitere_diagnosen": [{"code": "Z98.88"}], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "876543200", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF046</b> · 🟡 gelb · Freitext: LWS-Bandscheibe mit Radikulopathie</summary>

```text
Rezept für Patientin Anna Test, geb. 01.07.1975, BARMER, KVNR B112233445. Dr. Lena Muster, LANR 345678903, BSNR 765432100, ausgestellt 19.10.2026 mit Unterschrift. Diagnosen: M51.1 lumbaler Bandscheibenschaden mit Radikulopathie und G55.1. Diagnosegruppe WS, Leitsymptomatik a. 6 x KG, 2x/Woche, Beginn 27.10.2026, Prüfung 26.10.2026.
```

</details>

<details><summary><b>TF047</b> · 🟡 gelb · v5: 18 im Fall + 6 = 24 (TF11-Muster)</summary>

```json
{"verordnung_ref": "VO-0047", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "patient_pseudonym": "P-2001", "vorverordnungen": [{"ausstellungsdatum": "2026-07-28", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-08-27", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-09-26", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}]}
```

</details>

<details><summary><b>TF048</b> · 🟡 gelb · v5: 14 im Fall + 6 = 20</summary>

```json
{"verordnung_ref": "VO-0048", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "patient_pseudonym": "P-2002", "vorverordnungen": [{"ausstellungsdatum": "2026-08-17", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-09-11", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 4, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-10-06", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 4, "einheiten_ergaenzend": 0, "entlassmanagement": false}]}
```

</details>

<details><summary><b>TF049</b> · 🟡 gelb · v5: andere 4. Stelle, gleicher Fall (M54.2 → M54.4)</summary>

```json
{"verordnung_ref": "VO-0049", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "patient_pseudonym": "P-2003", "vorverordnungen": [{"ausstellungsdatum": "2026-07-18", "icd10": "M54.2", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-08-17", "icd10": "M54.2", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-09-21", "icd10": "M54.2", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}]}
```

</details>

<details><summary><b>TF050</b> · 🟡 gelb · v5: EX, 18 im Fall + 6</summary>

```json
{"verordnung_ref": "VO-0050", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M17.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "patient_pseudonym": "P-2004", "vorverordnungen": [{"ausstellungsdatum": "2026-06-28", "icd10": "M17.1", "diagnosegruppe": "EX", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-08-07", "icd10": "M17.1", "diagnosegruppe": "EX", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-09-16", "icd10": "M17.1", "diagnosegruppe": "EX", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}]}
```

</details>

<details><summary><b>TF051</b> · 🔴 rot · Kostenträger fehlt</summary>

```json
{"verordnung_ref": "VO-0051", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": null}
```

</details>

<details><summary><b>TF052</b> · 🔴 rot · LANR fehlt</summary>

```json
{"verordnung_ref": "VO-0052", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M17.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": null, "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF053</b> · 🔴 rot · BSNR fehlt</summary>

```json
{"verordnung_ref": "VO-0053", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": null, "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF054</b> · 🔴 rot · Ausstellungsdatum fehlt</summary>

```json
{"verordnung_ref": "VO-0054", "ausstellungsdatum": null, "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M75.4", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF055</b> · 🔴 rot · Unterschrift fehlt</summary>

```json
{"verordnung_ref": "VO-0055", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": false, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF056</b> · 🔴 rot · ICD-10-Code fehlt</summary>

```json
{"verordnung_ref": "VO-0056", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": null, "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF057</b> · 🔴 rot · Diagnosegruppe fehlt</summary>

```json
{"verordnung_ref": "VO-0057", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M16.1", "weitere_diagnosen": [], "diagnosegruppe": null, "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF058</b> · 🔴 rot · Leitsymptomatik fehlt</summary>

```json
{"verordnung_ref": "VO-0058", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M53.1", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": null, "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF059</b> · 🔴 rot · Heilmittel ohne Einheiten</summary>

```json
{"verordnung_ref": "VO-0059", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": null, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF060</b> · 🔴 rot · Therapiefrequenz fehlt</summary>

```json
{"verordnung_ref": "VO-0060", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M77.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": null, "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF061</b> · 🔴 rot · LANR nur 8 Ziffern</summary>

```json
{"verordnung_ref": "VO-0061", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "12345670", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF062</b> · 🔴 rot · BSNR mit Buchstaben</summary>

```json
{"verordnung_ref": "VO-0062", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "S82.6", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "98765A300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF063</b> · 🔴 rot · Gonarthrose mit WS</summary>

```json
{"verordnung_ref": "VO-0063", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M17.1", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF064</b> · 🔴 rot · Koxarthrose mit WS</summary>

```json
{"verordnung_ref": "VO-0064", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M16.1", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF065</b> · 🔴 rot · Lumboischialgie mit EX</summary>

```json
{"verordnung_ref": "VO-0065", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF066</b> · 🔴 rot · Zervikobrachial-Syndrom mit EX</summary>

```json
{"verordnung_ref": "VO-0066", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M53.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF067</b> · 🔴 rot · Bandscheibenverlagerung mit EX</summary>

```json
{"verordnung_ref": "VO-0067", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M51.2", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF068</b> · 🔴 rot · HWS-Distorsion mit EX</summary>

```json
{"verordnung_ref": "VO-0068", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "S13.4", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF069</b> · 🔴 rot · Außenknöchelfraktur mit WS</summary>

```json
{"verordnung_ref": "VO-0069", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "S82.6", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF070</b> · 🔴 rot · Epicondylitis mit WS</summary>

```json
{"verordnung_ref": "VO-0070", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M77.1", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF071</b> · 🔴 rot · Impingement Schulter mit WS</summary>

```json
{"verordnung_ref": "VO-0071", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M75.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF072</b> · 🔴 rot · Spondylolisthesis mit EX</summary>

```json
{"verordnung_ref": "VO-0072", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M43.16", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF073</b> · 🔴 rot · 7 Einheiten bei WS</summary>

```json
{"verordnung_ref": "VO-0073", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 7, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF074</b> · 🔴 rot · 8 Einheiten bei EX</summary>

```json
{"verordnung_ref": "VO-0074", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M17.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 8, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF075</b> · 🔴 rot · 12 Einheiten bei WS</summary>

```json
{"verordnung_ref": "VO-0075", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.2", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 12, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF076</b> · 🔴 rot · KG 4 + MT 4 = 8 bei EX</summary>

```json
{"verordnung_ref": "VO-0076", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M75.4", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 4, "art": "vorrangig"}, {"name": "MT", "einheiten": 4, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF077</b> · 🔴 rot · Vier vorrangige Heilmittel</summary>

```json
{"verordnung_ref": "VO-0077", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 2, "art": "vorrangig"}, {"name": "MT", "einheiten": 2, "art": "vorrangig"}, {"name": "KG-Gerät", "einheiten": 1, "art": "vorrangig"}, {"name": "KMT", "einheiten": 1, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF078</b> · 🔴 rot · Ergänzend 8 Einheiten bei 6 vorrangigen</summary>

```json
{"verordnung_ref": "VO-0078", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": "Wärmetherapie", "einheiten": 8}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF079</b> · 🔴 rot · KG 6 + MT 6 = 12 bei WS</summary>

```json
{"verordnung_ref": "VO-0079", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M53.1", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}, {"name": "MT", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF080</b> · 🔴 rot · KG-Gerät 10 bei EX</summary>

```json
{"verordnung_ref": "VO-0080", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M16.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG-Gerät", "einheiten": 10, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF081</b> · 🔴 rot · Ergänzend Elektro 6 bei KG 3</summary>

```json
{"verordnung_ref": "VO-0081", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M77.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 3, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": "Elektrotherapie", "einheiten": 6}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF082</b> · 🔴 rot · KMT 9 bei EX</summary>

```json
{"verordnung_ref": "VO-0082", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M76.6", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KMT", "einheiten": 9, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF083</b> · 🔴 rot · Beginn nach 35 Tagen</summary>

```json
{"verordnung_ref": "VO-0083", "ausstellungsdatum": "2026-09-22", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF084</b> · 🔴 rot · Beginn nach 60 Tagen</summary>

```json
{"verordnung_ref": "VO-0084", "ausstellungsdatum": "2026-08-28", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.2", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF085</b> · 🔴 rot · EX, Beginn nach 45 Tagen</summary>

```json
{"verordnung_ref": "VO-0085", "ausstellungsdatum": "2026-09-12", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M17.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF086</b> · 🔴 rot · Dringlich, Beginn nach 15 Tagen</summary>

```json
{"verordnung_ref": "VO-0086", "ausstellungsdatum": "2026-10-12", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": true, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF087</b> · 🔴 rot · Dringlich, Beginn nach 20 Tagen</summary>

```json
{"verordnung_ref": "VO-0087", "ausstellungsdatum": "2026-10-07", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": true, "icd10": "S82.6", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF088</b> · 🔴 rot · Dringlich, Beginn nach 40 Tagen</summary>

```json
{"verordnung_ref": "VO-0088", "ausstellungsdatum": "2026-09-17", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": true, "icd10": "S13.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF089</b> · 🔴 rot · Unterbrechung 21 Tage ohne Grund</summary>

```json
{"verordnung_ref": "VO-0089", "ausstellungsdatum": "2026-09-21", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": "2026-10-06", "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF090</b> · 🔴 rot · Unterbrechung 30 Tage ohne Grund</summary>

```json
{"verordnung_ref": "VO-0090", "ausstellungsdatum": "2026-09-11", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M16.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": "2026-09-27", "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF091</b> · 🔴 rot · Unterbrechung 18 Tage, Grund leer</summary>

```json
{"verordnung_ref": "VO-0091", "ausstellungsdatum": "2026-09-26", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": "2026-10-09", "unterbrechungsgrund": "", "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF092</b> · 🔴 rot · EX, Unterbrechung 25 Tage ohne Grund</summary>

```json
{"verordnung_ref": "VO-0092", "ausstellungsdatum": "2026-09-16", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M75.4", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": "2026-10-02", "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF093</b> · 🔴 rot · LANR fehlt und Beginn zu spät</summary>

```json
{"verordnung_ref": "VO-0093", "ausstellungsdatum": "2026-09-24", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": null, "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF094</b> · 🔴 rot · Diagnosegruppe falsch und 10 Einheiten</summary>

```json
{"verordnung_ref": "VO-0094", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M17.1", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 10, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF095</b> · 🔴 rot · 8 Einheiten und Unterbrechung 16 Tage</summary>

```json
{"verordnung_ref": "VO-0095", "ausstellungsdatum": "2026-09-26", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 8, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": "2026-10-11", "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF096</b> · 🔴 rot · Drei Fehler: Unterschrift, Diagnosegruppe, dringlich zu spät</summary>

```json
{"verordnung_ref": "VO-0096", "ausstellungsdatum": "2026-10-10", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": true, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": false, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF097</b> · 🔴 rot · Leitsymptomatik und Frequenz fehlen</summary>

```json
{"verordnung_ref": "VO-0097", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M22.4", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": null, "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": null, "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF098</b> · 🔴 rot · Freitext: Schulterdiagnose mit WS (wie TF03)</summary>

```text
Bitte prüfen: Herr Peter Probe, DAK, Vers.-Nr. D556677889, Musterstraße 12, 68159 Mannheim. Verordnung vom 19.10.2026, LANR 456789004, BSNR 987654300, unterschrieben. M75.4 Impingement Schulter links, Diagnosegruppe WS, Leitsymptomatik a. 6x KG, 2x/Woche, Beginn 27.10.2026, Prüfdatum 26.10.2026.
```

</details>

<details><summary><b>TF099</b> · 🔴 rot · Freitext: 10 Einheiten KG bei EX</summary>

```text
Verordnung für Frau Maria Beispiel, IKK, Vers.-Nr. I998877665, E-Mail maria.beispiel@example.org. Ausgestellt 19.10.2026, LANR 567890105, BSNR 876543200, Unterschrift ja. M16.1 Koxarthrose, EX, Leitsymptomatik b, 10x KG, 2x die Woche, Beginn 27.10.2026, Prüfdatum 26.10.2026.
```

</details>

<details><summary><b>TF100</b> · 🔴 rot · Freitext: Beginn 40 Tage nach Ausstellung</summary>

```text
Patient Jonas Test, geb. 22.09.1990, hkk, KVNR H443322110. Rezept vom 16.09.2026 von Dr. Eva Probe, LANR 123456701, BSNR 987654300, unterschrieben. M54.4 Lumboischialgie, WS, Leitsymptomatik a, 6x KG, 2x/Woche. Erste Behandlung geplant am 27.10.2026, Prüfdatum 26.10.2026.
```

</details>

<details><summary><b>TF101</b> · 🟢 grün · Beginn exakt am 28. Tag</summary>

```json
{"verordnung_ref": "VO-0101", "ausstellungsdatum": "2026-09-29", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF102</b> · 🔴 rot · Beginn am 29. Tag (Gegenprobe)</summary>

```json
{"verordnung_ref": "VO-0102", "ausstellungsdatum": "2026-09-28", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF103</b> · 🟢 grün · Dringlich, Beginn exakt am 14. Tag</summary>

```json
{"verordnung_ref": "VO-0103", "ausstellungsdatum": "2026-10-13", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": true, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF104</b> · 🟢 grün · Unterbrechung exakt 14 Tage ohne Grund</summary>

```json
{"verordnung_ref": "VO-0104", "ausstellungsdatum": "2026-09-26", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": "2026-10-13", "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF105</b> · 🔴 rot · Unterbrechung 15 Tage ohne Grund (Gegenprobe)</summary>

```json
{"verordnung_ref": "VO-0105", "ausstellungsdatum": "2026-09-26", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": "2026-10-12", "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF106</b> · 🔴 rot · Leitsymptomatik c bei EX</summary>

```json
{"verordnung_ref": "VO-0106", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "S43.4", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "c", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF107</b> · 🔴 rot · Traktion als ergänzendes Heilmittel bei EX</summary>

```json
{"verordnung_ref": "VO-0107", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M17.1", "weitere_diagnosen": [], "diagnosegruppe": "EX", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": "Traktion", "einheiten": 6}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF108</b> · 🟢 grün · Frequenz 4x/Woche</summary>

```json
{"verordnung_ref": "VO-0108", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "4x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF109</b> · 🟢 grün · M50.1 ohne Zweitcode G55.1</summary>

```json
{"verordnung_ref": "VO-0109", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M50.1", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV"}
```

</details>

<details><summary><b>TF110</b> · 🟢 grün · v5: Summe im Fall exakt 18</summary>

```json
{"verordnung_ref": "VO-0110", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "patient_pseudonym": "P-3001", "vorverordnungen": [{"ausstellungsdatum": "2026-08-27", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}, {"ausstellungsdatum": "2026-09-26", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}]}
```

</details>

<details><summary><b>TF111</b> · 🟢 grün · v5: Vorverordnung aus dem Entlassmanagement zählt nicht</summary>

```json
{"verordnung_ref": "VO-0111", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": null, "einheiten": null}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "patient_pseudonym": "P-3002", "vorverordnungen": [{"ausstellungsdatum": "2026-08-17", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": true}, {"ausstellungsdatum": "2026-09-11", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": true}, {"ausstellungsdatum": "2026-10-06", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 0, "entlassmanagement": false}]}
```

</details>

<details><summary><b>TF112</b> · 🟢 grün · v5: ergänzende Einheiten zählen nicht zur orientierenden Menge</summary>

```json
{"verordnung_ref": "VO-0112", "ausstellungsdatum": "2026-10-19", "pruefdatum": "2026-10-26", "geplanter_beginn": "2026-10-27", "dringlich": false, "icd10": "M54.4", "weitere_diagnosen": [], "diagnosegruppe": "WS", "leitsymptomatik": "a", "heilmittel": [{"name": "KG", "einheiten": 6, "art": "vorrangig"}], "ergaenzendes_heilmittel": {"name": "Wärmetherapie", "einheiten": 6}, "frequenz": "2x/Woche", "lanr": "123456701", "bsnr": "987654300", "unterschrift": true, "letzte_behandlung": null, "unterbrechungsgrund": null, "kostentraeger": "GKV", "patient_pseudonym": "P-3003", "vorverordnungen": [{"ausstellungsdatum": "2026-08-27", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 6, "entlassmanagement": false}, {"ausstellungsdatum": "2026-09-26", "icd10": "M54.4", "diagnosegruppe": "WS", "lanr": "123456701", "einheiten_vorrangig": 6, "einheiten_ergaenzend": 6, "entlassmanagement": false}]}
```

</details>

## Auffälligkeiten beim Erstellen

1. **TF10 ist nach Regelwerk vermutlich falsch bewertet.** Der Heilmittelkatalog kennt für EX (und WS) nur die Leitsymptomatik a, b und x. TF10 nutzt „c“ und erwartet grün. Formal- und Diagnose-Prüfer akzeptieren „c“ laut Prompt. Prüft die Stelle im Katalog; dann Soll von TF10 auf rot setzen und Prompts anpassen (Grenzfall TF106).
2. **Frequenz-Hinweise widersprechen dem Regelwerk.** Nach HeilM-RL § 12 Abs. 1 Satz 4 darf der Arzt ohne zusätzliche Dokumentation von der Frequenzempfehlung abweichen. Ein Hinweis bei 4×/Woche wäre ein Fehlalarm.
3. **Zweitcode beim besonderen Verordnungsbedarf.** Bei M50.1, M51.1, M47.2-, M48.0- und Z96.6- verlangt die KBV-Liste den Zweitcode. Ohne ihn gibt es keinen Hinweis (Grenzfall TF109). M75.1 steht ohne Zweitcode auf der Liste: Grüne Fälle mit M75.1 und EX gibt es deshalb nicht.
4. **Zulässigkeit des ergänzenden Heilmittels hat keinen Prüfer.** Traktion ist nur bei WS vorgesehen. Klären, ob der Mengen-Prüfer das ins Mandat bekommt.
5. **Merge-Workflow rechnet noch mit 28 € je Einheit** (Knoten „Ergebnis zusammenführen“). Laut Ist-Interview sind es 32 €.
6. **Für v5:** Ergänzende Einheiten und Verordnungen aus dem Entlassmanagement dürfen nicht in die Fallsumme (HeilM-RL § 7 Abs. 2 Satz 2, § 16a Abs. 5). Der Verordnungsfall gilt je Verordner (§ 7 Abs. 3).
7. **Massage über 12 Einheiten je Fall** ist bewusst nicht enthalten. Ob das eine harte Grenze oder orientierend ist, ist weiter offen.
