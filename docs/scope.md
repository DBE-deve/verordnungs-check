# Scope

*Sprint 1 · Stand 13.10.2026 · Verantwortlich: Thomas*

## Geschäftsproblem

Physiotherapie-Praxen behandeln auf Kassenrezept und rechnen erst danach ab. Ist die Verordnung fehlerhaft (Frist überschritten, Diagnose passt nicht zum Heilmittel, Menge zu hoch, Pflichtangabe fehlt) oder sind im selben Verordnungsfall schon zu viele Einheiten verordnet, kürzt die Krankenkasse oder setzt die Verordnung ganz ab. Die Leistung ist dann erbracht, das Geld fehlt. Die Rezeption hat im Alltag keine Zeit, jede Verordnung gegen die Regelwerke und die bisherigen Verordnungen des Patienten zu prüfen.

## Die drei Scope-Fragen

| Frage | Antwort |
|---|---|
| **Für wen?** | Die Rezeption einer Physiotherapie-Praxis (ca. 10 Mitarbeitende, zwei Standorte), die neue GKV-Verordnungen annimmt, bevor die erste Behandlung terminiert wird. *Annahme:* 1–2 Personen an der Rezeption, Zahl der Verordnungen pro Woche im Ist-Interview klären. |
| **Was genau macht es?** | Es nimmt eine Heilmittelverordnung Physiotherapie (Muster 13) als Text im Chat entgegen und prüft sie gegen Heilmittel-Richtlinie, Heilmittelkatalog und KBV-Diagnoseliste. Zusätzlich summiert es die Einheiten aller früher geprüften Verordnungen im selben Verordnungsfall (R1). Ergebnis: eine Ampel mit Korrekturhinweisen und Fundstellen. |
| **Was macht es ausdrücklich nicht?** | Siehe Ausschlüsse unten. |

## Erste Erfolgskennzahl

Das System gibt bei mindestens **90 % von mindestens 12 neuen, vorher ungesehenen Testverordnungen** die richtige Ampel aus und übersieht **keine** rote Verordnung. Die genaue Fassung steht in [`erfolgskriterien.md`](erfolgskriterien.md).

## Ausdrücklich außerhalb des Scopes

1. **Keine automatische Entscheidung.** Das System weist keine Verordnung ab und sagt keinen Termin ab. Die Rezeption entscheidet.
2. **Keine Anbindung an die Praxissoftware.** Kein Import aus der Praxissoftware, keine Schnittstelle. Eingabe nur über den Chat.
3. **Keine Abrechnung.** Keine Übermittlung an Krankenkassen oder Abrechnungszentren, keine Rechnungsstellung.
4. **Nur Physiotherapie auf GKV-Verordnung.** Keine Ergotherapie, Logopädie, Podologie, keine Privat- oder BG-Verordnungen.
5. **Keine parallelen Verordnungen.** Behandlungszeit bei parallelen Lymphdrainage-Verordnungen (R2) und Doppelabrechnung (R3) sind Ausbaustufe nach dem Capstone.
6. **Kein Foto-Upload** im Pflichtumfang. Nur wenn Puffer übrig bleibt (siehe [`build-plan.md`](build-plan.md)).
7. **Keine medizinische Beurteilung.** Das System prüft Regelkonformität, nicht, ob die Therapie medizinisch sinnvoll ist.
8. **Keine echten Patientendaten.** Nur synthetische Verordnungen und Pseudonyme.

## Abgrenzung gegenüber der Ausgangsidee

Die erste Idee war eine „KI-Rezeption“ (Termine, Rezepte, Patientenkommunikation). Der Scope ist auf **einen** Schritt eingegrenzt: die Prüfung einer Verordnung vor Behandlungsbeginn.
