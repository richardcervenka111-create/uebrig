# Übrig Bern

Was in der Küche übrig bleibt, sicher weitergeben statt wegwerfen. Drei Schritte am Handy:
**Freigabe-Check** (sieben Hygienefragen), **Meldung** (fertiger Text für die WhatsApp- oder
Signal-Gruppe der Abnehmer), **Übergabe** (Etikett drucken, Protokoll führen).
Ohne Konto, ohne Server; Protokoll und Adressbuch bleiben im Browser.

Live (sobald GitHub Pages aktiviert ist): https://richardcervenka111-create.github.io/uebrig/

## Die App (`app/`): Angebote live melden und reservieren

Zweite Stufe, mit Anmeldung (Magic-Link per E-Mail) und einer Supabase-Datenbank:

- **Küche** meldet ein Angebot (Freigabe-Check, Speise, Portionen, Allergene, Abholfenster, Ort).
- **Abnehmer** (Gassenküche, Passantenheim, Fairteiler, …) sehen offene Angebote live und
  reservieren mit einem Tipp; die Reservation läuft über eine Datenbankfunktion mit Zeilensperre,
  damit nie zwei dasselbe bekommen. Danach sehen beide Seiten Kontakt und Übergabeort.
- **Admin** schaltet neue Betriebe und Organisationen frei (`Freigaben`). Ohne Freigabe sieht
  niemand Daten anderer.
- Schema und Zugriffsregeln: `db/001_schema.sql` (2 Tabellen, RLS auf allem, 3 RPCs).
  Verbindung: `app/config.js` (öffentlicher Publishable Key; alles Weitere regelt RLS).

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
[Designmanual „Lístok a pečiať“](https://richardcervenka111-create.github.io/uebrig/research/design.html) und der
[lokale Redesign-Prototyp](https://richardcervenka111-create.github.io/uebrig/research/design/prototyp.html) (Intro-Animation, Lis, Zatrasenie, Záblesk). Nichts davon ist in `index.html`/`app/` eingebaut – Entscheidungsgrundlage.

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
Lizenz CC0. Verwandt: Allergen-Poster, Bärn hilft, Notfallblatt.
