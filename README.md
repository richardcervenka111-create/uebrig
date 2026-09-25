# Übrig Bern

Was in der Küche übrig bleibt, sicher weitergeben statt wegwerfen – am Handy, in den letzten fünfzehn
Minuten der Schicht. **Prüfen** (sieben Hygienefragen, jede mit Erklärung), **Meldung** (was, wie viel,
wann, wo, wer – mit Pflicht-Bestätigung für Allergene und Frist), **Etikett** (eine Druckseite, gleicher
Text für WhatsApp/Signal), **Protokoll** (im Browser; Einträge öffnen, bearbeiten, löschen).
Dazu «Wer nimmt Essen an» (Startliste Bern), Unterstützen-Blatt, DE/FR/IT/EN. Ohne Konto, ohne Server.

Live: https://richardcervenka111-create.github.io/uebrig/

Gestaltung «Lístok a pečiať» (Papier, Atrament, Pečiať; Fraunces/Atkinson/Plex Mono) nach dem
[Designmanual](https://richardcervenka111-create.github.io/uebrig/research/design.html); live seit 25. 9. 2026.
Protokolle der alten Startseite (`ub_state`) werden beim ersten Öffnen übernommen.
[Datenschutz](https://richardcervenka111-create.github.io/uebrig/datenschutz.html) beschreibt, was der Code heute tut
(Startseite: nur `localStorage`; App: Supabase, Region Paris). Installierbar als PWA (`manifest.webmanifest`, `icons/`).

## Die App (`app/`): Angebote live melden und reservieren

Zweite Stufe, mit Anmeldung (Magic-Link per E-Mail) und einer Supabase-Datenbank:

- **Küche** meldet ein Angebot (Freigabe-Check, Speise, Portionen, Allergene, Abholfenster, Ort).
- **Abnehmer** (Gassenküche, Passantenheim, Fairteiler, …) sehen offene Angebote live und
  reservieren mit einem Tipp; die Reservation läuft über eine Datenbankfunktion mit Zeilensperre,
  damit nie zwei dasselbe bekommen. Danach sehen beide Seiten Kontakt und Übergabeort.
- **Admin** schaltet neue Betriebe und Organisationen frei (`Freigaben`). Ohne Freigabe sieht
  niemand Daten anderer.
- Schema und Zugriffsregeln: `db/001_schema.sql` (2 Tabellen, RLS auf allem, 3 RPCs),
  `db/002_hardening.sql` (Trigger-Guard, gekapselte Policies), `db/002_rls_test.sql` (20 Isolationstests,
  Protokoll in `db/RLS_TEST_2026-09-25.md`), `db/003_bootstrap_admin.sql` (erster Admin).
  Verbindung: `app/config.js` (öffentlicher Publishable Key; alles Weitere regelt RLS).
- Gleiche Gestaltung wie die Startseite seit 25. 9. 2026 (Tokens, Lis-Buttons, Kruh-Checkboxen, Angebote als Lístky).

## Research (`research/`, slowakisch)

Drei Dokumente vom 25. 9. 2026 als Entscheidungsgrundlage: [Überblick](https://richardcervenka111-create.github.io/uebrig/research/)
(Konkurrenz CH/international, Nachfrage in Bern, Angebot, Recht, Logistik),
[Karte und Route](https://richardcervenka111-create.github.io/uebrig/research/mapa.html)
(398 Betriebe aus OpenStreetMap nach Küchenschluss 19:00–22:00, Empfänger, E-Cargo-Route in zwei Etappen, Portionen-Schätzung) und
[Monetarisierung und Finanzierung](https://richardcervenka111-create.github.io/uebrig/research/financovanie.html)
(Verein/GmbH/Hybrid, Geldflüsse, nicht-verwässernde Finanzierung). Quellenlage ist in jedem Dokument markiert
(`overené` / `snippet` / `neoverené`); Rohnotizen in `research/notes/`, Skripte `research/build_*.py`.
Kartendaten © OpenStreetMap-Mitwirkende (ODbL).

Weitere Dokumente (25. 9. 2026): [Zu prüfende Quellen](https://richardcervenka111-create.github.io/uebrig/research/doverit.html) (Checkliste),
[Architektur für die Expansion](https://richardcervenka111-create.github.io/uebrig/research/architektura.html) (Mandanten, Regelwerke, Ereignisprotokoll, PWA, Phasenplan),
[Designmanual „Lístok a pečiať“](https://richardcervenka111-create.github.io/uebrig/research/design.html),
[Audit und Plan](https://richardcervenka111-create.github.io/uebrig/research/plan.html) (Befunde nach Schwere, was erledigt ist,
Fahrplan, offene Entscheidungen). Der Redesign-Prototyp ist seit 25. 9. 2026 die Startseite (`index.html`);
`research/design/prototyp.html` leitet dorthin weiter; `app/` trägt seit demselben Abend dieselbe Gestaltung.

## Was die Checkliste (Startseite) bewusst nicht ist

Keine Plattform, die Kuchen und Abnehmer automatisch verbindet. Das bräuchte einen Server mit
Konten und Moderation. Die Gruppe gründet der Betrieb selbst, mit den Organisationen aus der
Startliste (Gassenküche, Passantenheim, foodsharing-Fairteiler, Schweizer Tafel, Tischlein deck
dich). Kontakte und Bedingungen werden vor der ersten Weitergabe direkt geklärt.

## Hygienegrundsätze im Check

Speise nie im Gästebereich · heiss ≥ 65 °C oder innert 2 h auf ≤ 5 °C · Zubereitungszeit bekannt ·
14 Allergene bekannt · sauberer, geschlossener, beschrifteter Behälter, nichts Rohes ·
Kühlkette beim Transport · Empfänger kennt Konsumfrist und erhitzt durch (≥ 72 °C Kern).
Rechtsgrundlage: Lebensmittelgesetz, Hygieneverordnung. Bis zur Übergabe haftet der Betrieb.
Die Seite ist keine Rechtsberatung; verbindlich ist die kantonale Lebensmittelkontrolle.

## Technik

Eine Datei, DE / FR / IT / EN, keine Netzwerkaufrufe (der Deploy-Workflow prüft das).
Vor jedem Deploy läuft `tests/e2e.mjs` (Playwright, Chromium: Intro, Blätter inkl. iPad-Scroll, 7/7-Fluss,
Validierung, Druck = eine Seite, Protokoll bearbeiten, FR/IT/EN, Übernahme alter Protokolle, Kontrast,
App-Hülle, Datenschutz). Lokal: `PW_PATH=<pfad zu playwright> BASE_URL=http://127.0.0.1:8080 node tests/e2e.mjs`.
Lizenz CC0. Verwandt: Allergen-Poster, Bärn hilft, Notfallblatt.
