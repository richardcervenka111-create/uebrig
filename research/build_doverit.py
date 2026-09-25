# -*- coding: utf-8 -*-
"""Builds uebrig/research/doverit.html: everything the research could not open or verify,
as a checklist Richard can tick off (state kept in localStorage)."""
import json, re, html, collections

S = '/tmp/claude-0/-home-user-Sautero-app/911fc836-514c-54a6-a831-59d4cb035434/scratchpad/'
OUT = '/home/user/uebrig/research/doverit.html'
TODAY = '25. 9. 2026'

report = open(S + 'reports/Übrig Bern trh hladní ľudia financovanie.md', encoding='utf-8').read()
urls = json.load(open(S + 'urls.json', encoding='utf-8'))

# --- 24 verification items from the report ---
sec = report.split('## Čo treba doveriť')[1]
rows = [l for l in sec.splitlines() if l.startswith('|')][2:]
items = []
for r in rows:
    c = [x.strip() for x in r.strip().strip('|').split('|')]
    if len(c) >= 4:
        items.append(dict(n=int(c[0]), what=c[1], why=c[2], where=c[3]))

def linkify(t):
    t = html.escape(t)
    t = re.sub(r'(https?://[^\s;]+)', lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener">{m.group(1)[:70] + ("…" if len(m.group(1)) > 70 else "")}</a>', t)
    return t

# --- architecture items to verify (from the architecture research, fixed list) ---
ARCH = [
    ('Supabase Pricing – Free vs Pro: pauza po 7 dňoch nečinnosti, veľkosť DB, egress, MAU, PITR, custom SMTP', 'https://supabase.com/pricing'),
    ('Supabase Realtime – limity správ a pripojení na plán, Realtime Authorization', 'https://supabase.com/docs/guides/realtime/quotas'),
    ('Supabase Auth – rate limity pre magic link / OTP, custom SMTP (Resend)', 'https://supabase.com/docs/guides/auth/rate-limits'),
    ('Supabase regióny a dátová rezidencia (Paríž eu-west-3 pre CH klientov; revDSG/GDPR)', 'https://supabase.com/docs/guides/platform/regions'),
    ('Supabase DPA (Auftragsverarbeitungsvertrag) – podpísať pre Verein', 'https://supabase.com/legal/dpa'),
    ('Web Push na iOS: PWA pridaná na plochu, iOS 16.4+ – aktuálny stav a obmedzenia', 'https://developer.apple.com/documentation/usernotifications/sending-web-push-notifications-in-web-apps-and-browsers'),
    ('WhatsApp Business Platform – podmienky, cena za šablónové správy v CH, alternatíva Signal (bez API)', 'https://developers.facebook.com/docs/whatsapp/pricing'),
    ('Zefix (Handelsregister) API – overenie UID podniku pri registrácii kuchyne', 'https://www.zefix.admin.ch/ZefixPublicREST/'),
    ('Resend – cena a limity pre transakčné e-maily (auth + notifikácie)', 'https://resend.com/pricing'),
    ('EDÖB – povinnosti podľa revDSG pre Verein (Datenschutzerklärung, Bearbeitungsverzeichnis od 250 zamestnancov)', 'https://www.edoeb.admin.ch/'),
    ('Google Fonts self-hosting (Fraunces, Atkinson Hyperlegible, IBM Plex Mono) – licencie OFL, offline použitie v PWA', 'https://fonts.google.com/'),
]

# --- group all URLs by source note ---
TOPIC = {
    'konkurencia.md': ('Konkurencia', 'Platí ešte číslo/poplatok? Existuje hráč stále? Rok údaju.'),
    'hladni_ludia_bern.md': ('Hladní ľudia a inštitúcie v Berne', 'Adresa, hodiny, kapacita, či prijmú teplé jedlo večer.'),
    'restauracie_bern.md': ('Reštaurácie a kuchyne', 'Küchenschluss v pracovný deň, adresa, kontakt na kuchára.'),
    'pravo_statistika_logistika.md': ('Právo, štatistika, logistika', 'Číslo článku, teplotné prahy, lehoty; nosnosť a ceny.'),
    'monetizacia.md': ('Monetizácia a právna forma', 'Poplatky, rozpočty, podmienky Steuerbefreiung.'),
    'financovanie.md': ('Financovanie', 'Existuje program? Suma, termín, oprávnenosť Vereinu, spoluúčasť.'),
}
by_topic = collections.defaultdict(list)
for u, refs in urls.items():
    for f, label in refs:
        by_topic[f].append((u, label))
        break

def host(u):
    return u.split('/')[2].replace('www.', '')

def topic_block(f):
    title, hint = TOPIC.get(f, (f, ''))
    lst = sorted(set(by_topic[f]), key=lambda x: (host(x[0]), x[0]))
    out = [f'<section class="topic" id="{f.replace(".md", "")}"><h3>{html.escape(title)} <small>({len(lst)} zdrojov)</small></h3><p class="sub">Čo si všímať: {html.escape(hint)}</p><ul class="cl">']
    for u, label in lst:
        lab = html.escape(label) if label and label != host(u) else ''
        out.append(f'<li><label><input type="checkbox" data-k="{html.escape(u, quote=True)}"><span><a href="{html.escape(u, quote=True)}" target="_blank" rel="noopener">{html.escape(host(u))}</a>{(" · " + lab) if lab else ""}<small>{html.escape(u[:90])}{"…" if len(u) > 90 else ""}</small></span></label></li>')
    out.append('</ul></section>')
    return ''.join(out)

CSS = """
:root{--bg:#fbfaf7;--card:#fff;--ink:#1b1b1b;--ink2:#52514e;--line:#e6e3dc;--accent:#0d366b;--ok:#0ca30c;--no:#d03b3b;--warn:#eda100}
@media (prefers-color-scheme: dark){:root:not([data-theme=light]){--bg:#15161a;--card:#1e2026;--ink:#f2f1ec;--ink2:#c3c2b7;--line:#2e3138;--accent:#86b6ef}}
:root[data-theme=dark]{--bg:#15161a;--card:#1e2026;--ink:#f2f1ec;--ink2:#c3c2b7;--line:#2e3138;--accent:#86b6ef}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
[hidden]{display:none!important}
main{max-width:960px;margin:0 auto;padding:24px 16px 64px}
nav.top{display:flex;gap:14px;flex-wrap:wrap;font-size:.92rem;margin-bottom:18px}nav.top a{color:var(--accent)}
h1{font-size:clamp(1.6rem,3.5vw,2.3rem);margin:.2em 0 .3em;line-height:1.15}h2{font-size:1.35rem;margin:40px 0 10px}h3{font-size:1.1rem;margin:26px 0 6px}
.sub{color:var(--ink2)}
.prog{position:sticky;top:0;background:var(--bg);padding:10px 0;border-bottom:1px solid var(--line);z-index:5;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.bar{flex:1;height:10px;background:var(--line);border-radius:5px;overflow:hidden;min-width:120px}.bar i{display:block;height:100%;background:var(--ok);width:0}
.imp{border-left:4px solid var(--no);background:rgba(208,59,59,.08);padding:10px 14px;border-radius:6px;margin:16px 0}
.warn{border-left:4px solid var(--warn);background:rgba(237,161,0,.10);padding:10px 14px;border-radius:6px;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:12px 0}
ol.pri{padding-left:0;list-style:none;counter-reset:p}ol.pri li{display:grid;grid-template-columns:28px 1fr;gap:10px;padding:12px 0;border-bottom:1px solid var(--line)}
ol.pri li b{display:block}ol.pri li small{color:var(--ink2);display:block;margin-top:3px}
ol.pri input{width:20px;height:20px;margin-top:2px}
ul.cl{list-style:none;padding:0;margin:0}ul.cl li{border-bottom:1px solid var(--line)}ul.cl label{display:grid;grid-template-columns:22px 1fr;gap:10px;padding:8px 0;cursor:pointer}ul.cl input{width:18px;height:18px;margin-top:3px}
ul.cl small{display:block;color:var(--ink2);font-size:.78rem;word-break:break-all}
li.done span,tr.done td{opacity:.55}li.done span{text-decoration:line-through}
a{color:var(--accent)}
.tools{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}.tools button{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:5px 12px;cursor:pointer}
table{width:100%;border-collapse:collapse;font-size:.92rem}th,td{padding:7px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
footer{margin-top:48px;color:var(--ink2);font-size:.88rem;border-top:1px solid var(--line);padding-top:14px}
"""

JS = """
(function(){
  var KEY='uebrig-doverit-v1', st={};
  try{st=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){st={}}
  var boxes=[].slice.call(document.querySelectorAll('input[type=checkbox][data-k]'));
  function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
  function paint(){var d=0;boxes.forEach(function(b){var on=!!st[b.dataset.k];b.checked=on;var row=b.closest('li,tr');if(row)row.classList.toggle('done',on);if(on)d++});
    document.getElementById('cnt').textContent=d+' / '+boxes.length;document.getElementById('barfill').style.width=(100*d/boxes.length)+'%';}
  boxes.forEach(function(b){b.addEventListener('change',function(){st[b.dataset.k]=b.checked;save();paint();})});
  document.getElementById('reset').addEventListener('click',function(){if(confirm('Vymazať všetky odškrtnutia?')){st={};save();paint();}});
  document.getElementById('exp').addEventListener('click',function(){var lines=boxes.map(function(b){return (st[b.dataset.k]?'[x] ':'[ ] ')+b.dataset.k});
    var blob=new Blob([lines.join('\\n')],{type:'text/plain'});var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='uebrig-doverit.txt';a.click();});
  paint();
})();
"""

pri = ''.join(f'<li><input type="checkbox" data-k="R{it["n"]}"><div><b>{it["n"]}. {linkify(it["what"])}</b><small><b>Prečo:</b> {linkify(it["why"])}</small><small><b>Kde:</b> {linkify(it["where"])}</small></div></li>' for it in items)
arch = ''.join(f'<li><input type="checkbox" data-k="A{i}"><div><b>{html.escape(t)}</b><small><a href="{u}" target="_blank" rel="noopener">{html.escape(u)}</a></small></div></li>' for i, (t, u) in enumerate(ARCH, 1))
topics = ''.join(topic_block(f) for f in TOPIC if f in by_topic)
total_urls = sum(len(set(v)) for v in by_topic.values())

HTML = f"""<!doctype html>
<html lang="sk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Übrig Bern – čo doveriť</title>
<meta name="description" content="Odškrtávací zoznam všetkého, čo sa vo výskume k Übrig Bern nedalo otvoriť alebo overiť: 24 kľúčových položiek, architektúra, a všetkých {total_urls} zdrojov podľa témy.">
<style>{CSS}</style></head><body><main>
<nav class="top"><a href="./">Prehľad situácie</a><a href="mapa.html">Mapa a trasa</a><a href="financovanie.html">Monetizácia a financovanie</a><a href="architektura.html">Architektúra</a><a href="design.html">Dizajn</a><a href="../">Übrig Bern</a></nav>
<h1>Čo sa mi nepodarilo otvoriť – zoznam na doverenie</h1>
<p class="sub">Výskum z {TODAY} bežal v prostredí, ktorého sieťová politika blokovala priame načítanie takmer všetkých stránok (403 pri bern.ch, be.ch, fedlex, blv, sleeper.ch, nadácie, stránky reštaurácií…) a rozpočet vyhľadávania sa vyčerpal. Fakty sú preto zo snippetov vyhľadávača, nie z prečítaných stránok. Tento zoznam je všetko, čo treba prejsť, aby bol výskum na 100 %. Odškrtnutia sa ukladajú v tomto prehliadači.</p>
<div class="prog"><b>Hotovo</b><span id="cnt">0 / 0</span><div class="bar"><i id="barfill"></i></div><div class="tools"><button id="exp">Export .txt</button><button id="reset">Vynulovať</button></div></div>

<div class="imp"><b>Najrýchlejšia cesta k 100 %:</b> odblokovať mi sieť. Sieťová politika tohto cloud prostredia odmietla hostiteľov ako <code>bern.ch</code>, <code>be.ch</code>, <code>fedlex.admin.ch</code>, <code>blv.admin.ch</code>, <code>sleeper.ch</code>, <code>supabase.com</code> a stránky reštaurácií. Zmeníš to v nastaveniach prostredia (menu cloud prostredia v titulku session → Edit → Network access): buď širšia úroveň prístupu, alebo pridať domény do povolených. Úrovne sú opísané na <a href="https://code.claude.com/docs/en/claude-code-on-the-web" target="_blank" rel="noopener">code.claude.com</a>. Potom mi napíš „sieť je otvorená“ a prejdem tento zoznam sám. Alternatíva: otvor mi svoj prehliadač (Chrome), stačí tiež.</div>

<h2 id="telefonaty">A · Štyri telefonáty, ktoré nenahradí žiadna stránka</h2>
<div class="card"><table><thead><tr><th></th><th>Komu</th><th>Číslo</th><th>Otázky</th></tr></thead><tbody>
<tr><td><input type="checkbox" data-k="T1"></td><td><b>Kantonales Laboratorium Bern</b> (Lebensmittelkontrolle), Muesmattstrasse 19</td><td>+41 31 633 11 11</td><td>Musí sa Verein, ktorý len sprostredkuje odovzdanie (nevozí, neskladuje), registrovať ako Lebensmittelbetrieb? Aké minimum musí obsahovať protokol odovzdania? Platia prahy 60 °C / 10 °C do 2 h zo Spendenleitfadenu, alebo 65 °C / 5 °C z GVG? Existuje Merkblatt Lebensmittelspenden?</td></tr>
<tr><td><input type="checkbox" data-k="T2"></td><td><b>Passantenheim Heilsarmee</b>, Muristrasse 6</td><td>031 351 80 27</td><td>Hodina večere; prijmete teplé jedlo o 22:30–22:45 (posledný vstup 23:00)? V akých nádobách? Kto podpíše protokol? Bez bravčoviny/halal podiel? Kapacita 50 alebo 60 lôžok?</td></tr>
<tr><td><input type="checkbox" data-k="T3"></td><td><b>Sleeper</b> Notschlafstelle &amp; Gassenküche, Neubrückstrasse 19</td><td>031 301 64 04</td><td>Večera končí 20:00 – prijmete schladené jedlo o 22:30 na ďalší deň? Koľko porcií varíte za večer? Čo vám chýba (suroviny vs. hotové jedlá)? Kontrola Lebensmittelkontrolle – čo od vás žiadajú?</td></tr>
<tr><td><input type="checkbox" data-k="T4"></td><td><b>Punkt 6 / PINTO</b>, Nägeligasse 3a</td><td>031 321 76 38</td><td>Zimné hodiny 18:00–22:30 platia aj 2026/27? Smiete podávať teplé jedlo (Lebensmittelbetrieb)? Koľko ľudí za večer? Leták „uf dr Gass 09/25“ – poslať PDF.</td></tr>
</tbody></table></div>

<h2 id="kluc">B · 24 kľúčových položiek zo syntézy (podľa hodnoty pre rozhodnutie)</h2>
<div class="card"><ol class="pri">{pri}</ol></div>

<h2 id="arch">C · Architektúra a platforma – čo overiť s otvorenou sieťou</h2>
<p class="sub">Súvisí s dokumentom <a href="architektura.html">Architektúra pre expanziu</a>. Ceny a limity sa menia, preto v dokumente stoja len ako odhady.</p>
<div class="card"><ol class="pri">{arch}</ol></div>

<h2 id="vsetky">D · Všetkých {total_urls} zdrojov podľa témy</h2>
<p class="sub">Každý odkaz je stránka, ktorú vyhľadávač našiel, ale ja som ju nemohol otvoriť. Pri odkaze je text, pod ktorým sa v poznámkach cituje – teda to, čo treba na stránke potvrdiť. Poradie: podľa domény.</p>
{topics}

<h2 id="postup">E · Ako to spracovať za jeden večer</h2>
<div class="card"><ol>
<li>Najprv A (telefonáty) – rozhodujú o tom, či má trasa 21:30–23:00 vôbec príjemcu.</li>
<li>Potom B 1–7 (právo + príjemcovia + kuchyne) – bez nich sa nesmie tlačiť žiadny leták ani protokol.</li>
<li>B 8–15 (peniaze) – až po založení Vereinu; dovtedy stačí zistiť termíny.</li>
<li>C – pred prvou zmenou schémy (architektúra).</li>
<li>D – priebežne; alebo mi otvor sieť a spravím to sám za jednu session.</li>
</ol><p class="sub">Pri každom potvrdenom údaji stačí odškrtnúť; export .txt mi potom pošli a ja aktualizujem dokumenty a odstránim značky <i>snippet</i> / <i>neoverené</i>.</p></div>
<footer>Übrig Bern · zoznam vygenerovaný skriptom <code>research/build_doverit.py</code> z výskumných poznámok (<a href="notes/">research/notes/</a>) {TODAY}</footer>
</main><script>{JS}</script></body></html>
"""
open(OUT, 'w', encoding='utf-8').write(HTML)
print('written', OUT, len(HTML) // 1024, 'kB; items', len(items), 'urls', total_urls)
