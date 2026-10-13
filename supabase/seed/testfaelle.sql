-- Synthetische Testverordnungen (keine echten Patientendaten).
-- LANR/BSNR sind erfundene Platzhalter. Prüfdatum für alle Fälle: 2026-10-12.
insert into public.testfaelle (name, verordnung, erwartete_befunde, beschreibung) values
('TF01 korrekt',
 '{"verordnung_ref":"VO-0001","ausstellungsdatum":"2026-10-05","pruefdatum":"2026-10-12","geplanter_beginn":"2026-10-13","dringlich":false,"icd10":"M54.4","diagnosegruppe":"WS","leitsymptomatik":"a","heilmittel":[{"name":"KG","einheiten":6,"art":"vorrangig"}],"frequenz":"2x/Woche","lanr":"123456701","bsnr":"987654300","unterschrift":true,"letzte_behandlung":null,"kostentraeger":"GKV"}',
 '{"gesamtstatus":"gruen","fehler":[]}', 'Vollständig und regelkonform'),
('TF02 Behandlungsbeginn zu spät',
 '{"verordnung_ref":"VO-0002","ausstellungsdatum":"2026-09-01","pruefdatum":"2026-10-12","geplanter_beginn":"2026-10-12","dringlich":false,"icd10":"M54.4","diagnosegruppe":"WS","leitsymptomatik":"a","heilmittel":[{"name":"KG","einheiten":6,"art":"vorrangig"}],"frequenz":"2x/Woche","lanr":"123456701","bsnr":"987654300","unterschrift":true,"letzte_behandlung":null,"kostentraeger":"GKV"}',
 '{"gesamtstatus":"rot","fehler":[{"agent":"frist","feld":"Behandlungsbeginn"}]}', 'Beginn 41 Tage nach Ausstellung, Grenze 28 Tage'),
('TF03 ICD passt nicht zur Diagnosegruppe',
 '{"verordnung_ref":"VO-0003","ausstellungsdatum":"2026-10-06","pruefdatum":"2026-10-12","geplanter_beginn":"2026-10-14","dringlich":false,"icd10":"M75.1","diagnosegruppe":"WS","leitsymptomatik":"a","heilmittel":[{"name":"KG","einheiten":6,"art":"vorrangig"}],"frequenz":"1-2x/Woche","lanr":"123456701","bsnr":"987654300","unterschrift":true,"letzte_behandlung":null,"kostentraeger":"GKV"}',
 '{"gesamtstatus":"rot","fehler":[{"agent":"diagnose","feld":"Diagnosegruppe"}]}', 'Schulter-Diagnose (Rotatorenmanschette) mit Wirbelsäulen-Diagnosegruppe'),
('TF04 Höchstmenge überschritten',
 '{"verordnung_ref":"VO-0004","ausstellungsdatum":"2026-10-07","pruefdatum":"2026-10-12","geplanter_beginn":"2026-10-13","dringlich":false,"icd10":"M54.4","diagnosegruppe":"WS","leitsymptomatik":"a","heilmittel":[{"name":"KG","einheiten":10,"art":"vorrangig"}],"frequenz":"2x/Woche","lanr":"123456701","bsnr":"987654300","unterschrift":true,"letzte_behandlung":null,"kostentraeger":"GKV"}',
 '{"gesamtstatus":"rot","fehler":[{"agent":"menge","feld":"Einheiten"}]}', '10 Einheiten bei WS, Höchstmenge je Verordnung 6'),
('TF05 Pflichtangaben fehlen',
 '{"verordnung_ref":"VO-0005","ausstellungsdatum":"2026-10-08","pruefdatum":"2026-10-12","geplanter_beginn":"2026-10-15","dringlich":false,"icd10":"M54.4","diagnosegruppe":"WS","leitsymptomatik":null,"heilmittel":[{"name":"KG","einheiten":6,"art":"vorrangig"}],"frequenz":"2x/Woche","lanr":null,"bsnr":"987654300","unterschrift":true,"letzte_behandlung":null,"kostentraeger":"GKV"}',
 '{"gesamtstatus":"rot","fehler":[{"agent":"formal","feld":"Leitsymptomatik"},{"agent":"formal","feld":"LANR"}]}', 'Leitsymptomatik und Arztnummer fehlen'),
('TF06 Unterbrechung zu lang',
 '{"verordnung_ref":"VO-0006","ausstellungsdatum":"2026-09-10","pruefdatum":"2026-10-12","geplanter_beginn":"2026-10-12","dringlich":false,"icd10":"S83.5","diagnosegruppe":"EX","leitsymptomatik":"a","heilmittel":[{"name":"KG","einheiten":6,"art":"vorrangig"}],"frequenz":"2x/Woche","lanr":"123456701","bsnr":"987654300","unterschrift":true,"letzte_behandlung":"2026-09-20","unterbrechungsgrund":null,"kostentraeger":"GKV"}',
 '{"gesamtstatus":"rot","fehler":[{"agent":"frist","feld":"Unterbrechung"}]}', '22 Tage Pause ohne dokumentierten Grund, Grenze 14 Tage'),
('TF07 Dringlich, aber zu spät',
 '{"verordnung_ref":"VO-0007","ausstellungsdatum":"2026-09-24","pruefdatum":"2026-10-12","geplanter_beginn":"2026-10-12","dringlich":true,"icd10":"S83.5","diagnosegruppe":"EX","leitsymptomatik":"a","heilmittel":[{"name":"KG","einheiten":6,"art":"vorrangig"}],"frequenz":"2x/Woche","lanr":"123456701","bsnr":"987654300","unterschrift":true,"letzte_behandlung":null,"kostentraeger":"GKV"}',
 '{"gesamtstatus":"rot","fehler":[{"agent":"frist","feld":"Behandlungsbeginn"}]}', 'Dringlicher Behandlungsbedarf: Grenze 14 Tage, hier 18 Tage');
