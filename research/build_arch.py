# -*- coding: utf-8 -*-
"""Builds uebrig/research/architektura.html: Slovak executive summary + phased plan,
followed by the full technical research notes (English) converted from Markdown."""
import re, html, markdown

S = '/tmp/claude-0/-home-user-Sautero-app/911fc836-514c-54a6-a831-59d4cb035434/scratchpad/'
OUT = '/home/user/uebrig/research/architektura.html'
TODAY = '25. 9. 2026'
notes = open(S + 'research_notes/architektura.md', encoding='utf-8').read()
# reuse the CSS of the other research docs
CSS = re.search(r'CSS = """(.*?)"""', open(S + 'osm/build_docs.py', encoding='utf-8').read(), re.S).group(1)
CSS += """
pre{background:#1e2026;color:#f2f1ec;padding:12px 14px;border-radius:8px;overflow:auto;font-size:.82rem;line-height:1.45}
code{font-size:.9em;background:rgba(0,0,0,.05);padding:1px 4px;border-radius:3px}pre code{background:none;padding:0}
.annex h2{font-size:1.25rem;margin-top:44px}.annex h3{font-size:1.02rem}
.annex{border-top:2px solid var(--line);margin-top:56px;padding-top:12px}
.hier{width:100%;height:auto;display:block;margin:8px 0 6px}.hier rect{fill:var(--card);stroke:var(--line);stroke-width:1.5;rx:8}.hier text{font-size:13px;fill:var(--ink)}.hier .t{font-weight:700}.hier .s{font-size:11px;fill:var(--ink2)}.hier line,.hier path{stroke:var(--accent2);stroke-width:2;fill:none}
.phase{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:14px 0}.phase .card{position:relative}.phase .card .n{position:absolute;top:-12px;left:14px;background:var(--accent);color:#fff;border-radius:999px;padding:2px 10px;font-size:.8rem;font-weight:700}
"""

body_md = notes.split('\n', 3)[3]  # drop title line + intro paragraph handled separately
annex = markdown.markdown(body_md, extensions=['tables', 'fenced_code'])
annex = annex.replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')
annex = re.sub(r'<a href="(http[^"]+)"', r'<a href="\1" rel="noopener" target="_blank"', annex)
annex = annex.replace('<strong>[experience, verify]</strong>', '<span class="m no">experience, verify</span>')
annex = re.sub(r'\*\*\[(verify[^\]]*)\]\*\*|\[(verify[^\]]*)\]', lambda m: f'<span class="m no">{m.group(1) or m.group(2)}</span>', annex)
annex = re.sub(r'\*\*\[experience\]\*\*', '<span class="m sn">experience</span>', annex)

n_sources = len(set(re.findall(r'https://supabase\.com/docs[^\s)"]+', notes)))

HIER = """<svg class="hier" viewBox="0 0 880 250" role="img" aria-label="Hierarchia nájomcov: mesto, organizácia, miesto, členstvo">
<rect x="20" y="20" width="200" height="56"/><text class="t" x="120" y="44" text-anchor="middle">cities (Standort)</text><text class="s" x="120" y="62" text-anchor="middle">Bern → Zürich → Wien · config, pravidlá, téma</text>
<rect x="340" y="20" width="200" height="56"/><text class="t" x="440" y="44" text-anchor="middle">organisations</text><text class="s" x="440" y="62" text-anchor="middle">reštaurácia, skupina, NGO · status schválenia</text>
<rect x="660" y="20" width="200" height="56"/><text class="t" x="760" y="44" text-anchor="middle">sites</text><text class="s" x="760" y="62" text-anchor="middle">kuchyňa / výdajné miesto · PostGIS bod</text>
<rect x="340" y="120" width="200" height="56"/><text class="t" x="440" y="144" text-anchor="middle">memberships</text><text class="s" x="440" y="162" text-anchor="middle">používateľ × org × rola (owner, staff)</text>
<rect x="660" y="120" width="200" height="56"/><text class="t" x="760" y="144" text-anchor="middle">offers · handover_events</text><text class="s" x="760" y="162" text-anchor="middle">každý riadok nesie org_id + city_id</text>
<rect x="20" y="120" width="200" height="56"/><text class="t" x="120" y="144" text-anchor="middle">rulesets · allergen_lists</text><text class="s" x="120" y="162" text-anchor="middle">global → krajina → mesto, verzované</text>
<line x1="220" y1="48" x2="340" y2="48"/><line x1="540" y1="48" x2="660" y2="48"/><line x1="440" y1="76" x2="440" y2="120"/><line x1="760" y1="76" x2="760" y2="120"/><line x1="120" y1="76" x2="120" y2="120"/>
<text class="s" x="280" y="40" text-anchor="middle">1 : n</text><text class="s" x="600" y="40" text-anchor="middle">1 : n</text>
<text class="s" x="440" y="220" text-anchor="middle">RLS: org_id = any(array(select private.my_org_ids())) · moderátori mesta cez city_roles · nikdy schéma alebo projekt na mesto</text>
</svg>"""

INTRO = notes.split('\n', 3)[2]

BODY = f"""
<header>
<h1>Architektúra Übrig: začať v Berne, rozšíriť bez prerábania</h1>
<p class="sub">Výskum a plán, {TODAY}. Podložené aktuálnou schémou (<code>db/001_schema.sql</code>), aplikáciou (<code>app/index.html</code>) a {n_sources} stránkami dokumentácie Supabase, ktoré boli v tejto session čitateľné cez nástroj vyhľadávania v dokumentácii. Všetko ostatné je označené <span class="m no">experience, verify</span> a zoradené v <a href="doverit.html#arch">zozname na doverenie</a>.</p>
</header>

<div class="bluf"><p><b>Odporúčanie v jednej vete:</b> jeden Supabase projekt pre Švajčiarsko, jedna zdieľaná schéma, a na každom riadku dva stĺpce – <code>org_id</code> (bezpečnostná hranica) a <code>city_id</code> (prevádzková hranica) – s hierarchiou <b>mesto → organizácia → miesto → členstvo</b>; pravidlá (teploty, alergény, lehoty) v tabuľke <b>rulesets</b> verzovanej podľa krajiny a mesta, nie v kóde; protokol odovzdania ako <b>nemenný záznam udalostí</b> s hash-reťazou; frontend ostáva bez build kroku, ale prejde na ES moduly, PWA a push notifikácie; druhé mesto sa pridá <b>riadkom v tabuľke</b>, druhá krajina <b>riadkom v rulesets</b> a rozhodnutím o regióne – nikdy prepisom.</p></div>

<div class="imp"><b>🟥 Dôležité – tri diery v dnešnej živej schéme, nájdené pri čítaní (nie domnienky):</b> (1) politika <code>offers_update_kitchen</code> pripína len <code>reserved_by</code>, takže kuchyňa môže priamym UPDATE nastaviť <code>status='picked'</code> alebo <code>'expired'</code> a obísť RPC; (2) <code>profiles_select_counterpart</code> volá vnorený <code>EXISTS</code> na tabuľku s vlastným RLS – vzor, ktorý dokumentácia Supabase odporúča nahradiť SECURITY DEFINER helperom; (3) helpery <code>my_role()</code> / <code>i_am_approved()</code> nie sú v politikách obalené <code>(select …)</code>, čo Advisor lint 0003 označí a pri raste dát stojí výkon. Oprava je migrácia <code>002_hardening.sql</code> vo Fáze 0 (aditívna, bez zmeny aplikácie). Nespúšťam ju, kým nepovieš – dnes sa nič nestavia.</div>

<h2 style="margin-top:28px">Obsah</h2>
<ol class="toc"><li><a href="#rozhodnutia">Desať rozhodnutí</a></li><li><a href="#hierarchia">Model nájomcov</a></li><li><a href="#pravidla">Pravidlá podľa jurisdikcie</a></li><li><a href="#protokol">Protokol ako záznam udalostí</a></li><li><a href="#frontend">Frontend, PWA, notifikácie</a></li><li><a href="#platforma">Platforma, región, plán</a></li><li><a href="#naklady">Náklady</a></li><li><a href="#plan">Plán vo fázach</a></li><li><a href="#doplnit">Čo doplniť s odblokovanou sieťou</a></li><li><a href="#priloha">Technická príloha (EN, úplné poznámky)</a></li></ol>

<section id="rozhodnutia"><h2>1 · Desať rozhodnutí</h2>
<div class="tw"><table><thead><tr><th>#</th><th>Rozhodnutie</th><th>Prečo</th><th>Čo zamietame</th></tr></thead><tbody>
<tr><td>1</td><td><b>Jeden projekt, zdieľaná schéma, tenant stĺpce</b></td><td>Jediný vzor, ktorý dokumentácia Supabase podporuje a benchmarkuje; používateľ aktívny v dvoch mestách je jeden účet.</td><td>Schéma na mesto, projekt na mesto (násobí fixné náklady, láme krížové štatistiky).</td></tr>
<tr><td>2</td><td><b>Hierarchia mesto → organizácia → miesto → členstvo</b></td><td>Reštauračná skupina má viac kuchýň, NGO viac výdajní; dnes je používateľ = profil = kuchyňa, čo neškáluje.</td><td>„Osobný“ režim – každý koná za organizáciu (jednotlivec = org druhu <code>individual</code>).</td></tr>
<tr><td>3</td><td><b>Pravidlá v tabuľke <code>rulesets</code></b>, verzované, s platnosťou od–do, riešené mesto → krajina → global</td><td>CH 65 °C vs. UK 63 °C vs. US 60 °C; EU-14 = CH-14, US má 9 alergénov. Snapshot <code>ruleset_id</code> na každej udalosti povie v roku 2027, čo platilo.</td><td>Prahy a zoznam alergénov v kóde (dnes <code>allergens &lt;@ 1..14</code>, <code>lang in (…)</code>).</td></tr>
<tr><td>4</td><td><b>Protokol odovzdania = append-only <code>handover_events</code></b> s hash-reťazou a JSON-schema validáciou</td><td>Obe strany sú Lebensmittelbetrieb; stav ponuky sa odvodzuje z udalostí, záznam sa nedá tichým UPDATE zmeniť.</td><td>Stav ako jediná pravda v <code>offers.status</code>.</td></tr>
<tr><td>5</td><td><b>RLS cez dva helpery v schéme <code>private</code></b> obalené <code>(select …)</code>, index na každom tenant stĺpci</td><td>Dokumentácia meria 2–24 ms na 1 mil. riadkov s indexom oproti timeoutom bez obalenia.</td><td>Vnorené RLS podotázky v politikách (dnes <code>profiles_select_counterpart</code>).</td></tr>
<tr><td>6</td><td><b>Frontend bez build kroku, ES moduly + import map, JSDoc + <code>tsc --noEmit</code></b> na generovaných typoch</td><td>Jeden vývojár, ~10 pohľadov; typová kontrola názvov stĺpcov zadarmo (pravidlo 9: nikdy nepísať názov, ktorý si nečítal).</td><td>React/Tailwind/bundler; framework až pri &gt; 15 previazaných reaktívnych stavoch.</td></tr>
<tr><td>7</td><td><b>Realtime cez Broadcast z DB na privátnych kanáloch <code>city:&lt;id&gt;</code></b>, Web Push cez Edge Function pre zavretú stránku</td><td><code>postgres_changes</code> robí jednu RLS kontrolu na odberateľa a zmenu a je jednovláknový – dokumentácia ho pri škále neodporúča.</td><td>Nefiltrované <code>postgres_changes</code> (dnes).</td></tr>
<tr><td>8</td><td><b>Fronta <code>pgmq</code> + <code>pg_cron</code> + Edge Function <code>dispatch</code></b> pre e-mail, push, SMS, WhatsApp</td><td>Odosielanie oddelené od transakcie, opakovanie a dead-letter zadarmo v Postgrese.</td><td>Vystavenie <code>pgmq_public</code> prehliadaču (tabuľky front nemajú RLS).</td></tr>
<tr><td>9</td><td><b>Pro plán v deň, keď má prvý cudzí používateľ dostať magic link</b>; región rozhodnúť pred prvým skutočným protokolom (Zürich <code>eu-central-2</code> odporúčaný pre live, Paríž ostáva staging)</td><td>Predvolený SMTP doručuje len členom tímu; Free pauzuje po 7 dňoch; región sa nedá zmeniť na mieste.</td><td>PITR, log drains, read replicas pre pilot (až pri &gt; 4 GB alebo požiadavke regulátora).</td></tr>
<tr><td>10</td><td><b>Druhé mesto = riadok v <code>cities</code> (téma, moderátori, manifest), druhá krajina = riadok v <code>rulesets</code> + rozhodnutie o projekte podľa právneho regiónu</b></td><td>Test architektúry: onboarding mesta cez UI s nulou commitov.</td><td>Fork kódu na mesto/krajinu.</td></tr>
</tbody></table></div>
</section>

<section id="hierarchia"><h2>2 · Model nájomcov</h2>
{HIER}
<p><b>Migrácia z dnešného stavu bez výpadku</b> (dual-write): 1) aditívna migrácia vytvorí <code>cities</code> (seed <code>bern</code>), <code>organisations</code>, <code>sites</code>, <code>memberships</code>, <code>city_roles</code> a pridá nullable <code>org_id/site_id/city_id</code> na <code>offers</code>; 2) backfill v tej istej transakcii – jedna org na existujúci profil, jedno členstvo owner, jedno miesto na kuchyňu, admini → <code>city_roles(bern, moderator)</code>; 3) trigger <code>offers_fill_tenant</code> doplní tenant stĺpce, keď starý klient vloží len <code>kitchen_id</code> – stará aplikácia beží ďalej; 4) nové politiky žijú popri starých (permisívne politiky sa spájajú OR), pgTAP dokáže, že oba tvary vidia to isté, potom sa staré zahodia; 5) feature flag <code>cities.features->>'orgs_ui'</code> zapne nové UI; 6) až nakoniec DESTRUKTÍVNE <code>set not null</code> a zahodenie <code>profiles.org/address</code> – s tvojím výslovným áno.</p>
</section>

<section id="pravidla"><h2>3 · Pravidlá podľa jurisdikcie</h2>
<p>Tabuľka <code>rulesets(scope, country, city_id, version, effective_from, effective_to, rules jsonb, source)</code> + <code>allergen_lists(code, version, items)</code>. Resolver <code>private.active_ruleset(city, at)</code> zlúči global ← krajina ← mesto. Klient si pri štarte zavolá <code>app_bootstrap(city_slug)</code> (anon, bez PII) a dostane <code>{{city, ruleset, allergens, locales, theme, features}}</code> – sedem otázok Freigabe-Checku sa renderuje z pravidiel. Príklad pre CH:</p>
<pre>{{ "hot_min_c": 65, "cold_max_c": 5, "cool_down_max_minutes": 120, "reheat_core_min_c": 72,
  "allergen_list": "EU14", "max_hours_after_made": 24, "require_temp_at_handover": true,
  "require_receiver_signature": true, "label_fields": ["dish","made_at","use_by","allergens","kitchen"] }}</pre>
<p class="sub">Pozor: výskum právneho rámca našiel dve sady prahov – BLV-Spendenleitfaden 2021 (≥ 60 °C, &lt; 10 °C do 2 h) a GVG/HyV prax (65 °C / 5 °C). Ktorá platí pre odovzdanie, rozhodne telefonát s Kantonales Laboratorium (zoznam na doverenie, položka A1) – a zapíše sa do <code>rulesets.source</code>, nie do kódu.</p>
</section>

<section id="protokol"><h2>4 · Protokol ako záznam udalostí</h2>
<p><code>handover_events(offer_id, org_id, city_id, event_type, actor_id, actor_org_id, occurred_at, payload jsonb, ruleset_id, prev_hash, hash)</code>; typy <code>published, reserved, released, handed_over, received, temp_checked, cancelled, expired, disputed, note</code>. UPDATE/DELETE odobraté rolám a blokované triggerom; <code>payload</code> validovaný <code>pg_jsonschema</code> podľa <code>(event_type, version)</code>. Podpisy a fotky v privátnom Storage buckete <code>protocols</code> s RLS cez <code>storage.foldername</code>. Odovzdanie je „úplné“, až keď kuchyňa zapíše <code>handed_over</code> a odberateľ <code>received</code> – obe strany si vedia dokázať, čo prešlo. Export CSV/PDF pre inšpektora, mesto a fundraising.</p>
<p>Audit v troch vrstvách: obchodný (<code>handover_events</code>), správcovský (<code>audit_log</code> trigger na org/členstvá/pravidlá) a <code>pgaudit</code> object-mode na dvoch citlivých tabuľkách. Log drains až na žiadosť regulátora.</p>
</section>

<section id="frontend"><h2>5 · Frontend, PWA, notifikácie</h2>
<ul>
<li><b>Moduly bez bundlera:</b> <code>js/main.js</code>, <code>sb.js</code>, <code>i18n.js</code>, <code>views/*</code>; supabase-js pripnutý (SRI) alebo vendorovaný do <code>app/vendor/</code> pre offline.</li>
<li><b>i18n:</b> zdroj de-CH, JSON na jazyk, ~40 riadkov vlastného <code>t()</code> s <code>Intl.PluralRules</code>; časové pásmo vždy z <code>cities.timezone</code>; RTL pripravenosť cez logické CSS vlastnosti; coverage meter v pre-commite.</li>
<li><b>PWA:</b> manifest na mesto (Edge Function), service worker: precache shell + slovník, network-first pre bootstrap, <b>nikdy</b> cache autentifikovaných dát; offline zápis len pre protokol (IndexedDB fronta, idempotentné <code>client_event_id</code>).</li>
<li><b>Live zoznam:</b> trigger na <code>offers</code> → <code>realtime.broadcast_changes('city:'||city_id)</code>, privátny kanál, jedna politika na <code>realtime.messages</code>; replay 3 dni.</li>
<li><b>Zavretá stránka:</b> Web Push (VAPID) z Edge Function spustenej Database Webhookom; na iOS len pre PWA pridanú na plochu – overiť aktuálny stav.</li>
<li><b>Testy:</b> pgTAP na každú politiku (pozitívny + negatívny), Playwright proti lokálnemu stacku, kontraktový test „Freigabe-Check má N otázok z rulesetu“.</li>
</ul>
</section>

<section id="platforma"><h2>6 · Platforma, región, plán</h2>
<div class="tw"><table><thead><tr><th>Otázka</th><th>Odpoveď</th><th>Zdroj / status</th></tr></thead><tbody>
<tr><td>Kedy Pro?</td><td>V deň, keď má prvý ne-tímový používateľ dostať magic link (default SMTP doručuje len tímu; Free pauzuje po 7 dňoch; bez záloh na stiahnutie).</td><td>docs Custom SMTP, Production checklist</td></tr>
<tr><td>Región</td><td>Paríž (EU) je pre CH pilot právne OK (adekvátnosť); Zürich <code>eu-central-2</code> existuje a pre mestá je „Daten in der Schweiz“ predajný argument. Odporúčanie: Pro projekt v Zürichu pri go-live, Paríž ako staging. Edge Functions nemajú Zürich región (beh najbližšie k používateľovi).</td><td>docs GDPR, PrivateLink, Regional invocations · <span class="m no">verify</span> zmena regiónu na mieste</td></tr>
<tr><td>Prihlásenie</td><td>Prejsť z magic linku na <b>e-mail OTP kód</b> (link z mailu otvára iný prehliadač než nainštalovaná PWA); <code>shouldCreateUser:false</code> + pozvánky.</td><td>docs Passwordless</td></tr>
<tr><td>Plánované úlohy</td><td><code>pg_cron</code> každých 5 min expiruje ponuky a emituje udalosť; nočne retencia a štatistiky; Edge Functions cez <code>pg_net</code> + Vault.</td><td>docs Cron, Schedule functions</td></tr>
<tr><td>Správy</td><td><code>pgmq</code> fronta, dispatcher každú minútu; e-mail + push pri štarte, SMS len pre zrušenie tesne pred vyzdvihnutím, WhatsApp len ak ho odberatelia už používajú (Business API – overiť ceny a schvaľovanie šablón).</td><td>docs PGMQ · <span class="m no">verify</span> WhatsApp</td></tr>
<tr><td>Identita</td><td>Roly v tabuľkách (okamžité odobratie), nie v JWT; výnimka: <code>platform_admin</code> claim cez Access Token Hook pre UI. Pozvánky s jednorazovým tokenom. Overenie UID cez Zefix. MFA povinné pre moderátorov mesta. SSO pre mestá až na žiadosť (Pro+).</td><td>docs RBAC, Hooks, MFA, SSO</td></tr>
<tr><td>Bezpečnosť</td><td>13-bodový RLS checklist (v prílohe §10) s pgTAP testom, ktorý prejde <code>pg_policies</code> a padne na neobalenom <code>auth.uid()</code>. Telefón kuchyne viditeľný len protistrane <b>rezervovanej</b> ponuky (dnes každému schválenému odberateľovi).</td><td>docs RLS</td></tr>
<tr><td>Ochrana údajov</td><td>revDSG: Datenschutzerklärung pri prvom prihlásení, jednostranový register spracovaní, DPA so Supabase; retencia: ponuky 30 d → anonymizácia, 24 mes. → zmazanie; udalosti bez PII navždy (hash-reťaz). <b>Nikdy</b> alergie ľudí – len alergény jedla.</td><td>docs GDPR · <span class="m no">verify</span> lehota Selbstkontrolle</td></tr>
</tbody></table></div>
</section>

<section id="naklady"><h2>7 · Náklady (odhad; USD podľa dokumentácie, CHF ≈ 0,85 × USD)</h2>
<div class="tw"><table><thead><tr><th>Etapa</th><th>Plán a doplnky</th><th>USD/mes.</th><th>≈ CHF/mes.</th></tr></thead><tbody>
<tr><td>Bern pilot</td><td>Free, Nano, SMTP len pre tím</td><td>0</td><td>0</td></tr>
<tr><td>Bern live</td><td>Pro 25 + Micro 10 − 10 kredit + vlastná doména 10 + Resend free</td><td>≈ 35</td><td>≈ 30</td></tr>
<tr><td>5 miest (~300 org, ~2 000 MAU)</td><td>Pro + Small 15 + doména + Resend ~20 (+ PITR 7 d 100 voliteľne)</td><td>≈ 60 (160 s PITR)</td><td>≈ 50–135</td></tr>
<tr><td>50 miest, 2 krajiny (~3 000 org, ~20 000 MAU, 2 projekty)</td><td>Pro/Team + Medium 60 + staging + 2 domény + PITR 14 d 200 + log drain 60 + egress + SMS/WhatsApp</td><td>≈ 350–600 + správy</td><td>≈ 300–500 + správy</td></tr>
</tbody></table></div>
<p class="sub">Kvóty z dokumentácie: MAU 50 k Free / 100 k Pro; egress 5 GB / 250 GB; DB 500 MB / 8 GB; Realtime 2 mil. správ a 200 spojení / 5 mil. a 500; Edge 500 k / 2 mil. volaní. Ceny sa menia – <a href="doverit.html#arch">overiť na pricing stránke</a>.</p>
</section>

<section id="plan"><h2>8 · Plán vo fázach</h2>
<p>Konvencie pre každú fázu: číslované migrácie v <code>db/</code> zrkadlené do <code>supabase/migrations/</code>; ku každej pgTAP test; rollback napísaný <b>pred</b> nasadením; „hotové“ = videné na skutočnom telefóne proti živému projektu. Nič z toho sa nestavia dnes – je to plán na tvoje schválenie.</p>
<div class="phase">
<div class="card"><span class="n">Fáza 0</span><h3>Bern pilot – nič, čo rozbije</h3><ul><li><code>002_hardening.sql</code>: obaliť helpery <code>(select …)</code>, pripnúť <code>status</code> v update politike, nahradiť vnorený EXISTS helperom, tabuľka <code>cities</code> s riadkom bern, <code>offers.city_id</code>, <code>profiles</code> von z realtime publikácie</li><li>pgTAP: odberateľ nenastaví picked; anon nič nevidí</li><li>Ops: rozhodnúť Zürich vs. Paríž; Pro + Resend ak sa hlási cudzí používateľ</li><li><b>Exit:</b> Advisor čistý, pgTAP zelený, jedna kuchyňa + jeden odberateľ dokončili rezerváciu na telefónoch</li></ul></div>
<div class="card"><span class="n">Fáza 1</span><h3>Organizácie, mestá, pravidlá</h3><ul><li><code>003_orgs.sql</code> (tabuľky, backfill, trigger, nové politiky popri starých), <code>004_rulesets.sql</code> (seed CH + EU14, resolver, <code>app_bootstrap</code>), <code>005_drop_legacy_policies.sql</code> po dvoch týždňoch</li><li>App: ES moduly (bez zmeny správania), prahy z bootstrapu, org switcher za flagom, i18n do JSON</li><li><b>Exit:</b> každý profil má org + členstvo, nula prahov v kóde (grep guard), i18n 100 % de-CH</li></ul></div>
<div class="card"><span class="n">Fáza 2</span><h3>Protokol, notifikácie, PWA</h3><ul><li><code>006_events.sql</code>, <code>007_storage.sql</code>, <code>008_queue.sql</code> (pgmq, push_subscriptions, cron), <code>009_realtime.sql</code> (broadcast)</li><li>Edge Functions: <code>dispatch</code>, <code>notify-offer</code>, <code>manifest</code></li><li>App: protokol z rulesetu, offline fronta, service worker, push opt-in</li><li><b>Exit:</b> úplné odovzdanie s teplotou a oboma potvrdeniami exportované a ukázané kontaktu z Lebensmittelkontrolle; push doručený na iOS PWA aj Androide</li></ul></div>
<div class="card"><span class="n">Fáza 3</span><h3>Druhé mesto, white-label, štatistiky</h3><ul><li><code>010_city2.sql</code> – <b>len INSERT, žiadna zmena schémy</b> (to je test)</li><li><code>011_stats.sql</code> (<code>api_v1</code> pohľady, k-anonymita ≥ 5 org), <code>012_webhooks.sql</code></li><li>App: rozlíšenie mesta (subdoména → param → default), tokeny témy pri štarte, manifest na mesto</li><li><b>Exit:</b> druhé mesto onboardované moderátorom cez UI s nulou commitov; štatistiky konzumuje externá strana</li></ul></div>
<div class="card"><span class="n">Fáza 4</span><h3>Druhá krajina</h3><ul><li><code>013_country.sql</code> (rulesets AT/DE, de-AT overlay), <code>014_legal_ids.sql</code></li><li>Rozhodnutie: ten istý projekt vs. nový podľa právneho regiónu (prenos dát, zmluva mesta, latencia)</li><li><b>Exit:</b> pilotná ponuka vo Viedni s AT pravidlami a formátmi bez forku kódu; právna kontrola AT Datenschutzerklärung</li></ul></div>
</div>
</section>

<section id="doplnit"><h2>9 · Čo doplniť s odblokovanou sieťou</h2>
<p>Tieto veci sa v session nedali otvoriť; sú aj v <a href="doverit.html#arch">zozname na doverenie, sekcia C</a>. Kým nie sú overené, čísla v tomto dokumente sú odhady.</p>
<ol>
<li>Supabase pricing (Pro/Team, spend cap, egress/GB, compute tabuľka) a stránka regiónov (Zürich <code>eu-central-2</code>, medzery vo funkciách).</li>
<li>Realtime limits (kanály na spojenie, veľkosť správy, joins/s podľa plánu).</li>
<li>Custom SMTP na Free pláne – povolené alebo len Pro.</li>
<li>Web Push na iOS PWA – minimálna verzia, nutnosť inštalácie, akcie/odznaky (stav 2026).</li>
<li>Zefix API (endpoint, registrácia, podmienky, kvóty) a špecifikácia kontrolného čísla UID (eCH-0097).</li>
<li>WhatsApp Business Cloud API (schvaľovanie šablón, cena za konverzáciu v CH/AT), Twilio CH sender ID, Signal (bez oficiálneho API).</li>
<li>revDSG: adekvátnosť EU (EDÖB), ohlasovanie incidentov, prah registra spracovaní; lehota uchovávania Selbstkontrolle (HyV) a AT ekvivalent.</li>
<li>Supabase DPA a zoznam subprocesorov.</li>
<li>PostgREST CSV výstup a limity veľkosti.</li>
<li>Import maps a <code>Intl.RelativeTimeFormat</code> – minimálne verzie Safari pre telefóny pilotu.</li>
<li>Retencia Postgres logov podľa plánu (rozhodnutie o pgaudit).</li>
<li>Či sa dá zmeniť región projektu bez nového projektu.</li>
</ol>
</section>

<section id="priloha" class="annex"><h2>10 · Technická príloha – úplné výskumné poznámky (EN)</h2>
<p class="sub">{INTRO}</p>
{annex}
</section>
"""

page_tpl = open(S + 'osm/build_docs.py', encoding='utf-8').read()
HTML = f"""<!doctype html>
<html lang="sk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Übrig – architektúra pre expanziu</title>
<meta name="description" content="Ako postaviť Übrig tak, aby začal v Berne a rozšíril sa do ďalších miest a krajín bez prerábania: model nájomcov, pravidlá podľa jurisdikcie, protokol ako záznam udalostí, PWA, Supabase platforma, plán vo fázach.">
<style>{CSS}</style></head><body><main>
<nav class="top"><a href="./">Prehľad situácie</a><a href="mapa.html">Mapa a trasa</a><a href="financovanie.html">Financovanie</a><a href="doverit.html">Čo doveriť</a><a href="design.html">Dizajn</a><a href="plan.html">Audit a plán</a><a href="../">Übrig Bern</a></nav>
{BODY}
<footer>Übrig · architektonický výskum {TODAY} · zdroj poznámok: <a href="notes/architektura.md">research/notes/architektura.md</a> · generované <code>research/build_arch.py</code></footer>
</main></body></html>"""
open(OUT, 'w', encoding='utf-8').write(HTML)
print('written', OUT, len(HTML) // 1024, 'kB; supabase doc urls', n_sources)
