# Non-dilutive funding map for "Übrig Bern" (food-rescue Verein, Stadt Bern) — research notes, 25 Sep 2026

## READ THIS FIRST — evidence status of these notes

**What happened in this research session (facts, with evidence):**
- The session's WebSearch budget was already exhausted (200 of 200 calls) before this task's first query; all 24 planned searches returned "Web search was not performed". No web search was possible.
- WebFetch of 26 primary domains was attempted (bern.ch, be.ch, gsi.be.ch, bgbern.ch, engagement-migros.ch, bafu.admin.ch, coop.ch, stjohnson.ch, venturekick.ch, socialimpactaward.net, bern.impacthub.ch, wemakeit.com, lokalhelden.ch, abs.ch, madamefrigo.ch, innosuisse.admin.ch, stiftung-mercator.ch, ernst-goehner-stiftung.ch, movetia.ch, google.com/nonprofits, seif.org, mobiliar.ch, foodwaste.ch, bekb.ch). **Every one returned `EGRESS_BLOCKED` / HTTP 403 from the organisation's egress proxy** (`curl "$HTTPS_PROXY/__agentproxy/status"` shows "gateway answered 403 to CONNECT (policy denial)"). Fallback routes (web.archive.org, r.jina.ai, de.wikipedia.org, html.duckduckgo.com, bing.com, stiftungschweiz.ch, swissfoundations.ch, zewo.ch, fedlex.admin.ch, be-advanced.ch, crowdify.net, opendata.swiss, admin.ch) were probed with curl: **all 403**. Only `api.github.com` answered 200. The proxy README (`/root/.ccr/README.md`) instructs not to retry policy denials.
- Therefore the ONLY citable evidence in this environment is prior, dated research already stored in the Sautero repository, whose author read the primary pages directly on 9 Aug 2026: `visual data/legal-financing.html` (source list at lines 1716–1738) and `scripts/reports/rdata.py` (FUNDING table, lines 599–635). Those are cited below as repository files, with the primary URL the author recorded.

**How to read the sections below:**
- **Cited Findings** = only facts with a source I could actually read in this environment (repository files quoting primary pages, with the date they were read). These concern Venture Kick, Kickfund, Innosuisse, be-advanced, Fördergutscheine BE, BG Mitte, SICTIC, wemakeit.
- **Unverified leads (model knowledge)** = my own recollection (knowledge cutoff June 2026), **not verified against any live page**. Every item there is a lead to verify, not a fact. Amounts given there are recollections and are marked "(recollection)". Where I do not recall a number I write "not found".
- **Gaps** = what the report writer must treat as unknown.
- Fit ratings are my inference from Übrig Bern's profile (Verein or gGmbH, Stadt Bern, volunteer-run, zero cost, founder non-developer, <1 year old) against the criteria as recalled — they are provisional until the criteria are verified.

**Dilution / loan flags used below:** `[GRANT]` non-dilutive money; `[LOAN]` must be repaid; `[EQUITY/CONVERTIBLE]` dilutive or potentially dilutive; `[IN-KIND]` services/credits, no cash; `[UNKNOWN]` instrument type not verified.

---

## Key question 1 — Stadt Bern (Fachstelle Nachhaltige Entwicklung, Klimafonds, BSS Projektbeiträge, Quartierkommissionen, Ernährungsstrategie, Burgergemeinde, Stadtgrün)

### Takeaway
Nothing about Stadt Bern's funding instruments could be verified in this session: bern.ch and bgbern.ch are egress-blocked and no search was possible. The Stadt Bern items below are unverified leads only. The one Bern-based instrument with repository evidence is the cantonal agency be-advanced (free coaching, no company required) — see Key question 2.

### Cited Findings
- No Stadt Bern or Burgergemeinde source could be read in this environment. — WebFetch results for `https://www.bern.ch/...` (three URLs) and `https://www.bgbern.ch/`: `{"error_type":"EGRESS_BLOCKED"}`, 25 Sep 2026 (this session's tool output).

### Inferences
- **Unverified leads (model knowledge, cutoff June 2026 — verify before use):**
  - *Fachstelle Nachhaltige Entwicklung, Stadt Bern* — the city has historically run project contributions for sustainability initiatives by local organisations (Vereine, Quartierorganisationen). Amounts, deadlines, current programme name: **not found**. Fit if it exists: HIGH (food waste is a core municipal sustainability topic). Where to look: bern.ch → Themen → Umwelt, Natur und Energie → Nachhaltige Entwicklung; contact the Fachstelle directly by e-mail and ask for the current "Gesuchsformular Projektbeiträge".
  - *Klimafonds / Klima-Aktionsplan Stadt Bern* — Stadt Bern adopted a climate strategy ("Klimastrategie 2025"/Energie- und Klimastrategie) and has climate funding lines; whether a fund open to Vereine for non-energy projects (food) exists in 2026: **not found**. Fit: MEDIUM (food waste = avoided emissions; argument must be quantified). `[GRANT]` if it exists.
  - *Direktion für Bildung, Soziales und Sport (BSS) / Sozialamt* — Leistungsverträge are normally multi-year contracts with established providers; small one-off "Projektbeiträge" for social projects exist in many Swiss cities but the Bern instrument, amount and process: **not found**. Fit: LOW in year 1 (no track record), MEDIUM from year 2 if the receiving social organisations vouch for Übrig.
  - *Quartierkommissionen / Quartiermitwirkung* — Stadt Bern works with six recognised Quartierorganisationen (recollection: QM3 Stadtteil 3, DIALOG Nordquartier, QUAV4, QBB Bümpliz-Bethlehem, Quartiermitwirkung Stadtteil VI/Länggasse-Felsenau, Vereinigung Bümpliz…). Some hold small quartier project budgets (recollection: low four-figure CHF per project). Amounts and process: **not found**. Fit: MEDIUM for a pilot in one Stadtteil (e.g. a pick-up round in Länggasse or Breitenrain). `[GRANT]`.
  - *"Bern isst Bern" / Ernährungsstrategie Stadt Bern* — Bern is a signatory of the Milan Urban Food Policy Pact (recollection) and has worked on a municipal food strategy; whether a funding line is attached: **not found**. Fit: HIGH as a policy hook for any city application (quote the strategy's food-waste target if one exists).
  - *Burgergemeinde Bern* — a large, independent Bern corporation that gives contributions to cultural and social projects in Bern (recollection: via Kulturkommission and Sozialkommission/Beiträge; rolling or quarterly gesuche; from low four figures to six figures). Exact criteria, deadlines: **not found**. Fit: HIGH (Bern-only funder, social purpose, no ZEWO requirement recalled). `[GRANT]`. Verify at bgbern.ch → "Gesuche"/"Beiträge".
  - *Gemeinwerk, Stadtgrün Bern, Kulturförderung* — no funding line relevant to Übrig recalled; **not found**.

### Gaps
- No Stadt Bern instrument (name, budget, max CHF, deadline, decision time, reporting) could be confirmed; bern.ch blocked, search unavailable.
- Burgergemeinde Bern criteria/amounts unconfirmed; bgbern.ch blocked.
- Whether Stadt Bern's Ernährungsstrategie exists in adopted form in 2026 and carries a fund: unknown.

---

## Key question 2 — Kanton Bern (Lotteriefonds/Swisslos, AUE, GSI/KIP, be-advanced/Wirtschaftsförderung, Fördergutscheine, prizes)

### Takeaway
Repository evidence (primary pages read 9 Aug 2026) shows two cantonal instruments clearly: **be-advanced** gives free coaching with no company or university requirement (fit HIGH as a first step, but CHF 0 cash), and the 2025 **Fördergutscheine BE** were a crisis instrument for exporting industrial firms (≥10 staff, ≥CHF 2 M turnover, window closed 30 Nov 2025 — fit NONE). The Lotteriefonds — probably the single most relevant cantonal cash source for a gemeinnütziger Verein — could not be verified (be.ch blocked).

### Cited Findings
- be-advanced (Canton Bern): "CHF 0 cash — coaching", timeline "weeks", requirement "a Bern base; nothing academic", rated YES for eligibility. — [Sautero repo, `visual data/legal-financing.html` lines 480–485, primary source `be-advanced.ch/startup` read 9 Aug 2026 (author notes the site sits behind a cookie wall, so not a verbatim download)](file:///home/user/Sautero-app/visual%20data/legal-financing.html)
- be-advanced: "The canton's innovation agency. Free advice and access to coaches, no equity and no conditions. … 1) Fill in the contact form at be-advanced.ch. 2) First meeting within two weeks. … No company required." — [Sautero repo, `scripts/reports/rdata.py` lines 600–604](file:///home/user/Sautero-app/scripts/reports/rdata.py)
- Fördergutscheine BE: "CHF 4 000 – 30 000", "window closed 30 Nov 2025", conditions "≥ 10 employees, turnover ≥ CHF 2M, export value chain, ≥ 5% decline"; "Canton Bern's own press release of 26 June 2025 requires the applicant to have a production site in the canton and employ at least 10 people, achieve an annual turnover of at least CHF 2 million, supply into an export-oriented value chain, and demonstrate a decline in business activity of at least 5%. And the vouchers were available from 26 June to 30 November 2025." — [Sautero repo, `visual data/legal-financing.html` lines 487–491 and 571–587; primary source: Canton Bern press release of 26 Jun 2025 on be.ch, read 9 Aug 2026](file:///home/user/Sautero-app/visual%20data/legal-financing.html)
- The same document records an open question: "Whether the Bern Fördergutscheine have a 2026 successor … I did not go through the canton's entire offering." — [Sautero repo, `visual data/legal-financing.html` line 1704](file:///home/user/Sautero-app/visual%20data/legal-financing.html)
- Guaranteed loan via BG Mitte `[LOAN + guarantee]`: "Covers Canton Bern (plus Jura, Solothurn, both Basels, Lucerne, Ob-/Nidwalden), guarantees up to CHF 1 million, loan term max 10 years. Costs: a one-off examination fee of 0.5–1% plus a risk premium of 1.25% p.a. on the guaranteed amount, plus the bank's interest. … positive creditworthiness is required 'von der Unternehmung und deren Exponenten' … and the company must have own equity." — [Sautero repo, `visual data/legal-financing.html` lines 605–616 (author flags BG Mitte as from "secondary overviews", not a verbatim download)](file:///home/user/Sautero-app/visual%20data/legal-financing.html)

### Inferences
- be-advanced is the one cantonal door that a volunteer-run project with no legal entity can open this week; it yields advice and introductions (e.g. to Impact Hub Bern, to foundations), not money. Fit: HIGH as a first step.
- Fördergutscheine BE: fit NONE (four numeric criteria all fail for a zero-cost Verein).
- BG Mitte guarantee: fit NONE for a Verein with no revenue; it is a loan instrument for creditworthy companies.
- **Unverified leads (model knowledge — verify):**
  - *Lotteriefonds Kanton Bern (Swisslos)* `[GRANT]` — funded from Swisslos profits; supports gemeinnützige, non-commercial projects (culture, social, environment, heritage) by non-profit organisations; typically no Betriebsbeiträge (running costs), project costs only; own contribution and other funders expected (recollection: the fund usually covers a share, commonly cited as "up to 50 %", but the exact Bern rule is **not found**); decisions by Finanzdirektion/Regierungsrat depending on amount; applications rolling via be.ch/lotteriefonds. Eligibility of a Verein <1 year old: statutes, board, accounts/budget needed; recollection only. Fit: HIGH for a one-off project (app development, cool boxes, launch campaign), LOW for salaries. Known grantees in Bern social/food space: **not found** in this session.
  - *GSI — Kantonales Integrationsprogramm (KIP 3, 2024–2027)* `[GRANT]` — project funding for integration of migrants via the cantonal Fachstelle; Übrig would need an explicit integration component (e.g. pick-up volunteers from asylum/refugee programmes). Amounts/deadlines: **not found**. Fit: LOW–MEDIUM.
  - *GSI Sozialamt Projektbeiträge* — **not found**.
  - *Amt für Umwelt und Energie (AUE)* — recollection: mostly building/energy subsidies; no project line for Vereine recalled. Fit: LOW.
  - *Prix Nature, Berner Umweltpreis* — **not found**.

### Gaps
- Lotteriefonds Kanton Bern: legal basis, min/max CHF, co-funding %, deadlines, decision time, reporting — all unverified (be.ch blocked; no search).
- Whether a 2026 successor to the Fördergutscheine exists — open since 9 Aug 2026, still open.
- KIP and GSI project lines — unverified (gsi.be.ch blocked).

---

## Key question 3 — Bund (BAFU UTF, Aktionsplan Lebensmittelverschwendung, BLV, SECO, Innosuisse, Swiss Innovation Challenge)

### Takeaway
Innosuisse is documented in the repository from its own FAQ (read 9 Aug 2026): the CHF 15 000 innovation cheque is paid to a mandatory research partner and filed by that partner, a UID is required, and larger projects require the implementation partner to bear 40–60 % of costs with ≥5 % cash — so Innosuisse is not a source of operating money for a volunteer Verein. BAFU's Umwelttechnologieförderung and any food-waste-specific federal line could not be verified.

### Cited Findings
- Innosuisse innovation cheque: "The innovation cheque is CHF 15,000, but not for you — from their FAQ: 'Das Gesuch muss vom Umsetzungspartner eingereicht werden', a research partner is mandatory, and the money funds a preliminary study at the university partner. A UID number is also required. In larger projects with an implementation partner the company bears 40–60% of direct costs, of which at least 5% in cash." — [Sautero repo, `visual data/legal-financing.html` lines 591–601; primary source innosuisse.admin.ch FAQ read 9 Aug 2026](file:///home/user/Sautero-app/visual%20data/legal-financing.html)
- Innosuisse start-up coaching: "up to CHF 10,000 … A voucher for a paid coach. Core Coaching up to CHF 50,000 over 36 months follows it. 1) You need the GmbH — it cannot be filed without a company. … 3) The voucher is drawn against hours, not paid in cash." — [Sautero repo, `scripts/reports/rdata.py` lines 605–609](file:///home/user/Sautero-app/scripts/reports/rdata.py) *(note: this line is the repo author's summary, not a quoted FAQ sentence; whether a Verein counts as a "company" for coaching is not stated)*
- BAFU pages unreadable this session. — WebFetch `https://www.bafu.admin.ch/...umwelttechnologiefoerderung.html`: `EGRESS_BLOCKED`, 25 Sep 2026.

### Inferences
- Innosuisse fit for Übrig Bern: NONE today. It would only become relevant if a university partner (e.g. BFH-HAFL Zollikofen, named in the repo as the nearest hospitality/food research partner — `rdata.py` line 613) wanted to research surplus-food logistics, and even then the money goes to the partner. `[GRANT to partner]`.
- **Unverified leads (model knowledge — verify):**
  - *BAFU Umwelttechnologieförderung (UTF)* `[GRANT]` — supports pilot/demonstration projects of environmental technologies with a clear environmental benefit; applicants may be companies, research bodies or associations; co-funding required; rolling applications; recollection of typical grants in the CHF 100k–500k range for multi-year technical pilots. A software-only matching platform for surplus meals is a borderline "Umwelttechnologie". Fit: LOW–MEDIUM, only with a measurable tonnage-avoided model. Known grantee in food waste: **not found** in this session.
  - *BAFU Aktionsplan gegen Lebensmittelverschwendung (Federal Council 2022) / branchenübergreifende Vereinbarung* — recollection: a policy framework with industry signatories and BAFU-funded support for foodwaste.ch and the "Save Food, Fight Waste" campaign (Pusch); **no open grant call for small NGOs recalled**. Fit as funding: LOW; as policy hook: HIGH (halving food waste by 2030).
  - *BLV, SECO* — no project grant line for a local NGO recalled; **not found**.
  - *Swiss Innovation Challenge* — a competition programme (recollection: FHNW/Basel region); prize amounts and legal-form rules **not found**.
  - *"Nachhaltigkeitsförderung Bund" / ARE Förderprogramm Nachhaltige Entwicklung* `[GRANT]` — recollection: the Bundesamt für Raumentwicklung (ARE) has run an annual small-grants programme for local Agenda-2030 projects, historically with amounts in the low tens of thousands CHF and an annual deadline, open to cantons/municipalities and organisations working with them. Fit: MEDIUM if Stadt Bern co-applies. **Verify existence in 2026.**

### Gaps
- BAFU UTF eligibility of a Verein, max CHF, co-funding %, deadline: unverified.
- Any federal food-waste grant line open to small NGOs in 2026: unknown.
- ARE Förderprogramm status in 2026: unknown.

---

## Key question 4 — Swiss foundations (Engagement Migros, Coop Fonds, Mercator, Gebert Rüf, Göhner, Stanley Thomas Johnson, Bürgi-Willert, Beisheim, Corymbo, Vinetum, etc.)

### Takeaway
No foundation website could be read (all blocked) and no directory (stiftungschweiz.ch, swissfoundations.ch) was reachable, so this section is entirely unverified leads. The strongest leads for a Bern food-rescue Verein, by fit, are Stanley Thomas Johnson Stiftung and Bürgi-Willert-Stiftung (Bern-based social funders), Ernst Göhner Stiftung (national, social projects, online application), Stiftung Corymbo (small organisations), and Engagement Migros (pioneering projects — but typically for scaling, not for a pre-launch volunteer project).

### Cited Findings
- None readable this session. — WebFetch of engagement-migros.ch (`EAI_AGAIN`), stjohnson.ch (`ENOTFOUND` — domain may be wrong), coop.ch, stiftung-mercator.ch, ernst-goehner-stiftung.ch, mobiliar.ch, bekb.ch (`EGRESS_BLOCKED`), 25 Sep 2026.

### Inferences
- **Unverified leads (model knowledge — verify each on its own site):**
  - *Engagement Migros (Migros-Pionierfonds)* `[GRANT]` — funds "pioneering" projects with a systemic approach, usually for several years and typically in the six-figure CHF range cumulatively (recollection); accepts unsolicited online applications; expects an existing legal entity and a team; prefers projects past the idea stage. Fit: MEDIUM long-term, LOW pre-launch. Food-waste grantees: **not found** in this session (do not assert Madame Frigo or foodwaste.ch as grantees without checking).
  - *Migros-Kulturprozent* — culture/society; a food-rescue platform is not its core. Fit: LOW.
  - *Coop Fonds für Nachhaltigkeit* `[GRANT]` — recollection: annual budget in the mid-teens of CHF millions, spent mostly on Coop's own sustainability projects and long-standing partners (WWF, Bio Suisse, ProSpecieRara); external gesuche possible but rarely granted. Fit: LOW.
  - *Stiftung Mercator Schweiz* `[GRANT]` — thematic areas were restructured in the early 2020s; recollection of a "Mensch und Umwelt"/Ernährung strand and an online application route. Fit: MEDIUM if a current call matches; **verify current Förderbereiche**.
  - *Gebert Rüf Stiftung* — science- and FH-graduate-based (First Ventures, InnoBooster); Fit: NONE for a non-developer founder without a Hochschule tie.
  - *Ernst Göhner Stiftung* `[GRANT]` — national; supports social, cultural, environmental projects of gemeinnützige organisations via an online portal; recollection: requires tax-exempt (steuerbefreit) status; grants often in the CHF 5 000–50 000 range; rolling. Fit: MEDIUM–HIGH once Steuerbefreiung is obtained.
  - *Stanley Thomas Johnson Stiftung (Bern)* `[GRANT]` — Bern-based; funds art, medical research and social/humanitarian projects; recollection of fixed application rounds (twice a year) and an online form; Bern/Switzerland (and UK) focus. Fit: HIGH (local social funder). Correct domain: **not found** (stjohnson.ch did not resolve).
  - *Bürgi-Willert-Stiftung (Bern)* `[GRANT]` — supports social, educational and cultural projects in the Bern region with smaller grants. Fit: HIGH for a small first grant.
  - *Stiftung Vinetum (Biel)* — culture/social in Biel/Bern region; Fit: MEDIUM; details **not found**.
  - *Beisheim Stiftung* — Bildung, Gesundheit, Kultur, Soziales; open to social-entrepreneurial projects; Fit: MEDIUM; details **not found**.
  - *Stiftung Corymbo* `[GRANT]` — deliberately funds small organisations across Switzerland in culture/social/environment with small grants. Fit: HIGH for a young Verein.
  - *Paul Schiller Stiftung, Age-Stiftung* — elderly/care focus; Fit: LOW unless the receiving organisations serve elderly people in poverty.
  - *Christoph Merian Stiftung* — Basel-Stadt only. Fit: NONE.
  - *Fondation Botnar (Basel)* — children/youth, digital health, cities; Fit: NONE.
  - *Klimastiftung Schweiz* — energy efficiency in SMEs; Fit: NONE.
  - *Stiftung Drittes Millennium, Hirschmann, Sandoz, Baur, Bachschuster, Dietschweiler, Symphasis, Cassiopeia, Philanthropia, Lombard Odier* — no specific food-waste line recalled; **not found**.
  - *Bern-based corporates with CSR budgets* — Mobiliar (Genossenschaft; society engagement mainly via own programmes/Mobiliar Forum), BEKB (regional sponsoring and a "Förderfonds"/Engagement recollection), Post, Swisscom, Fenaco, Galenica, Emmi: sponsorship is possible but programme names, amounts and processes: **not found**. Fit: MEDIUM for BEKB and Mobiliar (Bern identity), via local branch sponsoring rather than a grant programme.
  - *WWF Innovationsfonds, Greenpeace, Pusch* — no open grant lines recalled; Pusch runs the food-waste campaign itself. **not found**.

### Gaps
- Every foundation's eligibility (legal form, ZEWO, Steuerbefreiung), typical/max CHF, deadlines, decision time and reporting: unverified.
- Which of these have funded food-waste or Bern social projects (grantee lists): unknown — no annual reports readable.
- Correct URL for Stanley Thomas Johnson Stiftung: unknown.

---

## Key question 5 & 6 — Corporate programmes, prizes, competitions, accelerators (Venture Kick, Kickfund, Prix SVC, Social Impact Award, seif, Ashoka, Impact Hub Bern, Swiss Economic Award, Umweltpreis, etc.)

### Takeaway
Venture Kick is documented in the repository (via indexed FAQ content, 9 Aug 2026): three stages CHF 10 000 / 40 000 / 100 000 (max CHF 150 000), but it requires a current or very recent (≤6 months) Swiss academic affiliation and a science-based idea, and the company must not yet be founded — fit for Übrig Bern is NONE. The repository is internally inconsistent on whether stages 2–3 are grants or convertible loans; treat Venture Kick as potentially dilutive until verified. All other prizes/accelerators are unverified leads.

### Cited Findings
- Venture Kick: "Three stages of CHF 10,000 / 40,000 / 100,000, up to CHF 150,000 in total. But it requires the founder to be currently or very recently (max 6 months) affiliated with a Swiss academic institution and the idea to be based on a scientific discipline and specific research results." — [Sautero repo, `visual data/legal-financing.html` lines 551–559; source: indexed content of venturekick.ch FAQ, 9 Aug 2026 — author flags "not a verbatim quote verified from a downloaded file" because of a cookie wall](file:///home/user/Sautero-app/visual%20data/legal-financing.html)
- Venture Kick eligibility column: "university affiliation + a science base + company not yet founded". — [Sautero repo, `visual data/legal-financing.html` line 511](file:///home/user/Sautero-app/visual%20data/legal-financing.html)
- Venture Kick instrument type `[GRANT stage 1 / CONVERTIBLE stages 2–3 — CONTRADICTED]`: "A three-stage competition. The first CHF 10,000 is a grant with no equity; the rest is a convertible loan. Kickfund up to CHF 850,000 sits above it." — [Sautero repo, `scripts/reports/rdata.py` lines 620–622](file:///home/user/Sautero-app/scripts/reports/rdata.py); the companion document lists "10k + 40k + 100k = up to 150k" with no loan qualifier — [`visual data/legal-financing.html` line 509](file:///home/user/Sautero-app/visual%20data/legal-financing.html). **Conflict not resolved in this session (venturekick.ch blocked).**
- Kickfund: "up to CHF 850,000 … The tier above Venture Kick. Without passing all three Venture Kick stages it cannot be reached." — [Sautero repo, `scripts/reports/rdata.py` lines 625–629](file:///home/user/Sautero-app/scripts/reports/rdata.py) `[EQUITY/CONVERTIBLE — investment fund]`
- SICTIC (angel network) `[EQUITY]`: "the startup must be an AG registered in CH or Liechtenstein; 'The core startup team (CEO, CTO, etc.) is based in Switzerland and works on the startup project as their main activity'; solo ventures are not funded — 'At least one other full-time, active team member with a key role and equity participation is required'; and the investment must be equity in a Swiss-registered company." — [Sautero repo, `visual data/legal-financing.html` lines 535–547; primary source sictic.ch/startups/ read directly 9 Aug 2026](file:///home/user/Sautero-app/visual%20data/legal-financing.html)
- Prize/accelerator sites unreadable this session. — WebFetch socialimpactaward.net, bern.impacthub.ch, seif.org, venturekick.ch: `EGRESS_BLOCKED`, 25 Sep 2026.

### Inferences
- Venture Kick, Kickfund and SICTIC: fit NONE for Übrig Bern (no academic tie, non-science idea, non-profit legal form, single founder). SICTIC and Kickfund are dilutive in any case — outside the "non-dilutive" brief.
- **Unverified leads (model knowledge — verify):**
  - *Impact Hub Bern* `[IN-KIND + possible small GRANT]` — hosts the Swiss *Circular Economy Incubator* (multi-city, ~4 months, early-stage circular projects; recollection of small kick-off grants for finalists, amount **not found**) and other programmes; Bern location at Spitalgasse/Marktgasse area (recollection). Fit: HIGH — the natural Bern accelerator for a food-rescue platform; also the place be-advanced would refer to.
  - *Social Impact Award Switzerland* `[GRANT prize]` — for young social entrepreneurs (recollection: students/under-30s), incubation + small prize money (recollection: low four-figure to CHF 5 000–10 000 per winner); annual cycle with spring deadline. Fit: MEDIUM if founder meets the age/stage criteria — **not found**.
  - *seif Awards* `[GRANT prize]` — social-entrepreneurship awards with category prizes (recollection: ~CHF 10 000 per category, corporate sponsors); whether still running in 2026: **not found**. Fit: MEDIUM.
  - *Ashoka Switzerland* — fellowships for proven system-changing entrepreneurs; Fit: NONE at this stage.
  - *Prix SVC, Swiss Economic Award, Swiss Startup Award* — for commercial SMEs/startups; Fit: NONE.
  - *Umweltpreis Schweiz / Prix Eco.ch / "Prix Klima" Stadt Bern / "Bärner Krone" / "Prix Suisse pour l'Engagement" / Zukunftspreis BEKB / Bern Cycle Award / Fondation Zoein / UBS Kickstart / Startfeld / Digitale Woche Bern* — existence, prize money and eligibility **not found** in this session; do not cite.
  - *Kickstart Innovation* — corporate-partnered accelerator for scale-ups, not pre-launch Vereine; Fit: LOW.

### Gaps
- Venture Kick instrument type for stages 2–3 (grant vs convertible) — contradiction unresolved.
- All prize/accelerator amounts, 2026 deadlines and legal-form rules — unverified.
- Impact Hub Bern 2026 programme calendar and grant sizes — unknown.

---

## Key question 7 — Crowdfunding & community (wemakeit, lokalhelden.ch, Crowdify, Projektstarter, Migros/Coop voting, Twint, Genossenschaft Anteilscheine)

### Takeaway
wemakeit is the only platform with repository evidence: 6 % platform fee + 4 % transaction fee, charged only on success, all-or-nothing, no category restrictions, private purposes allowed; whether a project can be run without a legal entity is recorded as an open question. lokalhelden.ch (Raiffeisen, recollection: fee-free for gemeinnützige projects) could not be verified.

### Cited Findings
- wemakeit `[GRANT-like donations/rewards]`: "A Swiss platform, with no category restrictions, and it supports private purposes too, so legal form is no obstacle here. Fee 6% of the amount raised + 4% transaction, payable only on success — the money moves only if a pre-set goal is reached, otherwise you get nothing." — [Sautero repo, `visual data/legal-financing.html` lines 754–760; author marks wemakeit as a "secondary source" (line 1733)](file:///home/user/Sautero-app/visual%20data/legal-financing.html)
- Open question recorded: "Whether wemakeit accepts a project from a private individual with no company. The platform supports private purposes and has no category restrictions, but I found no explicit statement about legal form." — [Sautero repo, `visual data/legal-financing.html` line 1708](file:///home/user/Sautero-app/visual%20data/legal-financing.html)
- lokalhelden.ch, wemakeit.com, crowdify.net unreadable this session. — WebFetch/curl: `EGRESS_BLOCKED`/403, 25 Sep 2026.

### Inferences
- For Übrig Bern, crowdfunding fits much better than it did for Sautero (a B2B SaaS): a food-rescue project sells a public story, and the "donors, not users" objection in the repo (lines 761–768) does not apply — the public IS the intended supporter base. Fit: HIGH for a launch campaign (recollection of typical successful Swiss civic campaigns: CHF 5 000–30 000).
- **Unverified leads (model knowledge — verify):**
  - *lokalhelden.ch (Raiffeisen)* — recollection: no platform fee for gemeinnützige/community projects, Raiffeisen absorbs costs; local Raiffeisen banks sometimes top up; Vereine explicitly welcome. Fit: HIGH (fee advantage over wemakeit). Fee structure, all-or-nothing rule: **not found**.
  - *Crowdify, Projektstarter, "Herzstück"* — Swiss/regional platforms; fees **not found**.
  - *Migros "Unterstützen"/Kulturprozent voting, Coop "Gemeinsam für die Region"* — existence of a 2026 voting/donation scheme **not found**; do not cite.
  - *Twint donation QR* — Twint offers donation QR codes/buttons for Vereine (recollection; transaction fee applies; requires a Verein bank account). Fit: HIGH as a zero-setup channel on posters in partner restaurants. `[IN-KIND channel]`
  - *Genossenschaft with Anteilscheine* — member shares are capital, not a grant; they are non-dilutive in the sense of one-member-one-vote governance but are repayable on exit under the statutes. Flag: `[QUASI-EQUITY / REPAYABLE]`. Fit: LOW at this stage (governance overhead).
  - *wemakeit HQ* — the brief says "Bern-based!"; my recollection is that wemakeit is headquartered in Zürich with offices in other cities; **not verified** — do not assert Bern base.

### Gaps
- lokalhelden.ch fee model and eligibility — unverified.
- Success rates for social projects on wemakeit/lokalhelden — not found.
- wemakeit legal-form rule — open since 9 Aug 2026.

---

## Key question 8 — Church, civil society, public service contracts and work-integration programmes (Leistungsverträge, Sozialfirmen, RAV/IV Einsatzprogramme, church funds)

### Takeaway
Nothing in this area could be verified. The structural inference stands: a Verein under one year old will not obtain a Leistungsvertrag from Stadt Bern's Sozialamt; the realistic route is to be hosted by, or subcontract to, an existing contracted provider (Sozialfirma / Einsatzprogramm) that already runs RAV/IV work-integration participants, who could staff a pick-up round.

### Cited Findings
- None readable this session (bern.ch and gsi.be.ch blocked; no search).

### Inferences
- **Unverified leads (model knowledge — verify):**
  - *Stadt Bern Sozialamt Leistungsverträge* — multi-year contracts with established institutions under the cantonal social-aid framework; a new Verein is out of scope in year 1. Fit: NONE now; MEDIUM in 2–3 years if the receiving social organisations formally rely on Übrig.
  - *RAV Programme zur vorübergehenden Beschäftigung (PvB) / IV Arbeitsintegration* — run by contracted providers, not by ad-hoc Vereine; partnering with a Bern Sozialfirma (recollection of Bern actors in this space; names **not found/verified here**) could provide labour for pick-ups at no cost to Übrig. `[IN-KIND]`. Fit: HIGH as partnership, NONE as direct funding.
  - *Reformierte Kirchen Bern-Jura-Solothurn / Katholische Kirche Region Bern / Kirchgemeinden* `[GRANT]` — parishes and the cantonal churches have diaconal project budgets and Kollekten; small grants (recollection: hundreds to low thousands CHF) with informal applications to the Kirchgemeinderat/Diakonie. Fit: HIGH for seed money and for volunteer recruitment; specific fund names **not found**.
  - *Caritas Bern, Heilsarmee, Gassenarbeit Bern, Passantenheim, Schweizer Tafel, Tischlein deck dich* — these are potential receiving/partner organisations rather than funders; some (Schweizer Tafel, Tischlein deck dich) already collect surplus food and may see Übrig as complementary or overlapping. Verify before approaching.

### Gaps
- Names, contacts and rules of Bern church funds and Sozialfirmen — not found.
- Public procurement thresholds for Stadt Bern social contracts — not found.

---

## Key question 9 — Non-dilutive debt (ABS, BEKB Förderkredite, Bürgschaft) and EU/international + in-kind tech credits

### Takeaway
The only debt instrument with repository evidence is the BG Mitte loan guarantee (Canton Bern in scope, up to CHF 1 M, 0.5–1 % fee + 1.25 % p.a. premium, needs creditworthy company AND principals plus own equity) — fit NONE for a zero-revenue Verein and in any case a loan. Erasmus+/Movetia, EIT Food, LIFE and all tech-credit programmes could not be verified.

### Cited Findings
- BG Mitte guarantee (see Key question 2 citation) `[LOAN + guarantee]` — [Sautero repo, `visual data/legal-financing.html` lines 605–616](file:///home/user/Sautero-app/visual%20data/legal-financing.html)
- abs.ch, movetia.ch, google.com/nonprofits unreadable this session. — WebFetch: `EGRESS_BLOCKED`, 25 Sep 2026.

### Inferences
- Debt of any kind is a poor fit for a project with zero revenue and no assets; even mission-aligned lenders require repayment capacity. Fit for all `[LOAN]` items: NONE in 2026.
- **Unverified leads (model knowledge — verify):**
  - *Alternative Bank Schweiz (ABS)* `[LOAN]` — lends to gemeinnützige organisations and social enterprises with a positive impact screen; still requires debt-service capacity. Fit: NONE now.
  - *BEKB Förderkredite, "Stiftung Gemeinnützige Darlehen", Fondation Ecopreneur* — existence/terms **not found**.
  - *Erasmus+ / Movetia* `[GRANT]` — recollection: Switzerland is a non-associated third country in the 2021–2027 programme, with association to Erasmus+ under negotiation as part of the EU–Switzerland package and targeted for the next programme period; Movetia funds a Swiss national programme (Jugend in Aktion-type cooperation/small partnerships) from federal money for Swiss organisations; amounts and 2026 deadlines **not found**. Fit: LOW–MEDIUM (needs a European partner and a youth/learning angle).
  - *EIT Food* — recollection: Switzerland's transitional association to Horizon Europe (from 2025) improves EIT eligibility, but EIT Food programmes target startups/companies; Fit: LOW.
  - *EU LIFE* — Switzerland does not participate (recollection). Fit: NONE.
  - *Global Innovation Fund, Bloomberg Mayors Challenge, UN SDG grants* — scale/geography mismatch; Fit: NONE.
  - *Google.org Impact Challenge* — no Swiss-specific edition recalled; **not found**.
  - *Tech in-kind credits* `[IN-KIND]`:
    - *Google for Nonprofits* (Workspace free tier, Ad Grants up to USD 10 000/month in-kind ads — recollection) — available to Swiss non-profits after validation through Google's partner (Percent/TechSoup); requires proof of non-profit/charitable status (Steuerbefreiung letter helps). Fit: HIGH.
    - *Microsoft nonprofit offers / TechSoup* — Swiss partner historically "Stifter-helfen.ch"; requires gemeinnützig + steuerbefreit. Fit: MEDIUM.
    - *GitHub for Nonprofits* (free GitHub Team) — Fit: HIGH if the codebase is on GitHub; eligibility via validation.
    - *AWS* — Activate is for startups; a separate nonprofit credit programme runs via TechSoup (recollection: USD 1 000–5 000 credits). Fit: LOW (Übrig is on Supabase).
    - *Supabase* — no dedicated nonprofit programme recalled; startup credits programme exists. **not found**. Fit: unknown.
    - *OpenAI for Nonprofits* (discounted ChatGPT Team/Enterprise — recollection) and *Anthropic nonprofit pricing* — **not verified**; do not cite amounts.

### Gaps
- Every EU/international and tech-credit eligibility rule for a Swiss Verein — unverified.
- Swiss Erasmus+ association status as of Sep 2026 — unverified (may have changed after June 2026).

---

## Cross-cutting practical questions (Verein <1 year, ZEWO, co-funding, success rates)

### Takeaway
No source could be read; the following is inference from general Swiss practice and must be verified with a Treuhänder or the Steuerverwaltung des Kantons Bern.

### Cited Findings
- None readable this session.

### Inferences
- **Unverified leads (model knowledge):**
  - *Steuerbefreiung wegen Gemeinnützigkeit* (cantonal tax exemption) is the gate most Swiss foundations and the Lotteriefonds care about, far more than ZEWO; it is granted by the cantonal Steuerverwaltung on application with statutes (gemeinnütziger Zweck, Uneigennützigkeit, unbegrenzter Destinatärkreis, Vermögen bei Auflösung an andere steuerbefreite Organisation). A newly founded Verein can apply immediately. Fit: DO FIRST.
  - *ZEWO* certification is expensive and usually required only for large public fundraising; typically not required by foundations or Lotteriefonds; not realistic for a zero-budget Verein in year 1.
  - *Co-funding*: Lotteriefonds and most foundations expect the project not to be 100 % funded by one source; volunteer hours are often accepted as Eigenleistung in kind (recollection). Exact percentages: **not found**.
  - *Age of organisation*: foundations generally accept young Vereine if statutes, a board, a budget and a bank account exist; Engagement Migros and Ashoka favour proven projects; church, Quartier, Corymbo, Bürgi-Willert and crowdfunding are the realistic year-1 sources.
  - *Success rates*: **not found** for any programme.

### Gaps
- Success rates, typical decision times and reporting duties for every programme — not obtainable in this session.
- Whether a gGmbH (rather than Verein) changes eligibility for Lotteriefonds/foundations — not verified (recollection: gemeinnützige GmbH is accepted if steuerbefreit, but Verein is the default expectation).

---

## Recommended verification list for the report writer / next session (highest value first)
1. be.ch/lotteriefonds — criteria, Eigenleistung %, form (blocked here).
2. bern.ch — Fachstelle Nachhaltige Entwicklung project contributions; Klimafonds; Ernährungsstrategie (blocked here).
3. bgbern.ch — Burgergemeinde Gesuche (blocked here).
4. Impact Hub Bern — Circular Economy Incubator 2026 dates (blocked here).
5. lokalhelden.ch vs wemakeit.com fee comparison (blocked here).
6. Stanley Thomas Johnson Stiftung, Bürgi-Willert-Stiftung, Stiftung Corymbo, Ernst Göhner Stiftung — eligibility + deadlines (blocked here; correct STJ domain unknown).
7. venturekick.ch — resolve grant vs convertible for stages 2–3 (repo contradiction).
8. Steuerverwaltung Kanton Bern — Steuerbefreiung procedure for a new Verein.
