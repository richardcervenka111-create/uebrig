# -*- coding: utf-8 -*-
"""Builds uebrig/research/index.html (prehľad situácie) and financovanie.html (monetizácia + financovanie)
from the synthesized research report (Markdown) plus hand-written decision sections."""
import re, html, markdown

REPORT = '/tmp/claude-0/-home-user-Sautero-app/911fc836-514c-54a6-a831-59d4cb035434/scratchpad/reports/Übrig Bern trh hladní ľudia financovanie.md'
OUTDIR = '/home/user/uebrig/research/'
TODAY = '25. 9. 2026'

md = open(REPORT, encoding='utf-8').read()
# split into H2 sections
parts = re.split(r'^## ', md, flags=re.M)
head = parts[0]
sections = {}
order = []
for p in parts[1:]:
    title, _, body = p.partition('\n')
    sections[title.strip()] = body.strip()
    order.append(title.strip())
print('sections:', order)

def slug(t):
    t = t.lower()
    t = re.sub(r'[^a-z0-9áäčďéíľĺňóôŕšťúýž ]', '', t)
    return re.sub(r'\s+', '-', t.strip())[:40]

MARKS = {'overené': 'ok', 'snippet': 'sn', 'neoverené': 'no', 'výpočet': 'calc', 'odhad': 'est'}
def mark(htmltext):
    def rep(m):
        k = m.group(1).split(' ')[0].split(' —')[0]
        cls = MARKS.get(k, 'sn')
        return f'<span class="m {cls}" title="pôvod údaju">{html.escape(m.group(1))}</span>'
    return re.sub(r'\[(overené|snippet|neoverené[^\]]*|výpočet|odhad)\]', rep, htmltext)

def conv(mdtext):
    h = markdown.markdown(mdtext, extensions=['tables'])
    h = mark(h)
    h = h.replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')
    h = re.sub(r'<a href="(http[^"]+)"', r'<a href="\1" rel="noopener" target="_blank"', h)
    return h

def section_html(title, num=None, anchor=None, extra=''):
    body = sections[title]
    a = anchor or slug(title)
    t = html.escape(title)
    return f'<section id="{a}"><h2>{(str(num) + " · ") if num else ""}{t}</h2>{extra}{conv(body)}</section>'

def verify_rows(keep=None):
    body = sections['Čo treba doveriť']
    lines = [l for l in body.splitlines() if l.startswith('|')]
    hdr, sep, rows = lines[0], lines[1], lines[2:]
    if keep:
        rows = [r for r in rows if int(r.split('|')[1].strip()) in keep]
    return conv('\n'.join([hdr, sep] + rows))

BLUF = head.split('\n\n')[1].strip()  # bold BLUF paragraph after H1

CSS = """
:root{--bg:#fbfaf7;--card:#fff;--ink:#1b1b1b;--ink2:#52514e;--mute:#8d8b84;--line:#e6e3dc;--accent:#0d366b;--accent2:#2a78d6;--ok:#0ca30c;--warn:#eda100;--no:#d03b3b}
@media (prefers-color-scheme: dark){:root:not([data-theme=light]){--bg:#15161a;--card:#1e2026;--ink:#f2f1ec;--ink2:#c3c2b7;--mute:#8d8b84;--line:#2e3138;--accent:#86b6ef;--accent2:#3987e5}}
:root[data-theme=dark]{--bg:#15161a;--card:#1e2026;--ink:#f2f1ec;--ink2:#c3c2b7;--mute:#8d8b84;--line:#2e3138;--accent:#86b6ef;--accent2:#3987e5}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
[hidden]{display:none!important}
main{max-width:920px;margin:0 auto;padding:24px 16px 64px}
nav.top{display:flex;gap:14px;flex-wrap:wrap;font-size:.92rem;margin-bottom:18px}nav.top a{color:var(--accent)}
header h1{font-size:clamp(1.6rem,3.5vw,2.3rem);margin:.2em 0 .3em;letter-spacing:-.01em;line-height:1.15}
.sub{color:var(--ink2)}
.bluf{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--accent2);border-radius:10px;padding:16px 18px;margin:18px 0;font-size:1.02rem}
.bluf p{margin:0}
.warn{border-left:4px solid var(--warn);background:rgba(237,161,0,.10);padding:10px 14px;border-radius:6px;margin:16px 0}
.toc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 18px;margin:18px 0;columns:2;column-gap:28px;font-size:.95rem}.toc a{color:var(--accent);text-decoration:none}.toc li{margin:3px 0}
@media (max-width:640px){.toc{columns:1}}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:18px 0}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}.tile b{display:block;font-size:1.6rem;line-height:1.1}.tile small{color:var(--ink2)}
section{margin-top:44px}h2{font-size:1.4rem;margin:0 0 12px;line-height:1.25}h3{font-size:1.1rem;margin:26px 0 8px}
p{margin:0 0 14px}li{margin:4px 0}
a{color:var(--accent)}
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:14px 0}
table{width:100%;border-collapse:collapse;font-size:.9rem}th,td{padding:7px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--ink2);font-weight:600}
.m{font-size:.74rem;border-radius:4px;padding:1px 6px;white-space:nowrap;vertical-align:1px;font-weight:600}
.m.ok{background:rgba(12,163,12,.15);color:#0a7a0a}.m.sn{background:rgba(237,161,0,.18);color:#8a5d00}.m.no{background:rgba(208,59,59,.14);color:#a12c2c}.m.calc,.m.est{background:rgba(42,120,214,.14);color:#1c5cab}
@media (prefers-color-scheme: dark){:root:not([data-theme=light]) .m.ok{color:#5dd35d}:root:not([data-theme=light]) .m.sn{color:#f2c159}:root:not([data-theme=light]) .m.no{color:#f08a8a}:root:not([data-theme=light]) .m.calc,:root:not([data-theme=light]) .m.est{color:#86b6ef}}
.legend{display:flex;gap:10px 18px;flex-wrap:wrap;font-size:.9rem;color:var(--ink2);margin:10px 0 0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}.card h3{margin:0 0 8px;font-size:1.05rem}.card p{font-size:.94rem;margin:0 0 8px}.card ul{padding-left:18px;margin:0;font-size:.92rem}
.flow{width:100%;height:auto;display:block;margin:6px 0 10px}
.flow rect{fill:var(--card);stroke:var(--line);stroke-width:1.5;rx:8}.flow text{font-size:13px;fill:var(--ink)}.flow .t{font-weight:700}.flow .s{font-size:11px;fill:var(--ink2)}.flow path{fill:none;stroke:var(--accent2);stroke-width:2.2;marker-end:url(#arr)}.fig{margin:14px 0;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 14px}.fig figcaption{font-weight:700;font-size:.95rem;margin-bottom:4px}.flow .money{stroke:#eb6834}.flow .food{stroke:#1baf7a}
.steps{counter-reset:s;list-style:none;padding:0}.steps li{position:relative;padding-left:44px;margin:10px 0}.steps li::before{counter-increment:s;content:counter(s);position:absolute;left:0;top:0;width:30px;height:30px;border-radius:50%;background:var(--accent);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center}
.imp{border-left:4px solid var(--no);background:rgba(208,59,59,.08);padding:10px 14px;border-radius:6px;margin:16px 0}
footer{margin-top:48px;color:var(--ink2);font-size:.88rem;border-top:1px solid var(--line);padding-top:14px}
blockquote{margin:0 0 14px;padding:6px 14px;border-left:3px solid var(--line);color:var(--ink2)}
code{font-size:.9em}
"""

LEGEND = ('<div class="legend"><span><span class="m ok">overené</span> primárna stránka prečítaná</span>'
          '<span><span class="m sn">snippet</span> len útržok vyhľadávača, URL existuje</span>'
          '<span><span class="m no">neoverené</span> stopa bez živého zdroja – úloha na overenie</span>'
          '<span><span class="m calc">výpočet</span> / <span class="m est">odhad</span> vlastná aritmetika alebo predpoklad</span></div>')

def page(title, desc, body, nav_extra=''):
    return f"""<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<style>{CSS}</style>
</head>
<body>
<main>
<nav class="top"><a href="./">Prehľad situácie</a><a href="mapa.html">Mapa a trasa</a><a href="financovanie.html">Monetizácia a financovanie</a><a href="plan.html">Audit a plán</a><a href="../">Übrig Bern</a>{nav_extra}</nav>
{body}
<footer>Übrig Bern · výskumný podklad zo {TODAY} · nie je právne ani daňové poradenstvo · zdrojové poznámky: <a href="notes/">research/notes/</a>, syntéza: <a href="REPORT.md">REPORT.md</a></footer>
</main>
</body>
</html>
"""

# ------------------------------------------------------------------ index.html
idx_sections = [
    ('Ako čítať značky v tejto správe', None, 'znacky'),
    ('Švajčiarska konkurencia vozí palety kamiónmi, nie rizoto o 21:30', 1, 'konkurencia-ch'),
    ('V zahraničí platí dodávateľ alebo štát, nikdy charita', 2, 'konkurencia-svet'),
    ('Dopyt: 56 ľudí bez strechy, ≈300 na CHF 10 denne, mesto, kde Sozialhilfe rastie', 3, 'dopyt'),
    ('Ponuka: 760 reštaurácií zatvára kuchyne v troch vlnách', 4, 'ponuka'),
    ('Právo: ≥ 60 °C alebo pod 10 °C do dvoch hodín, obe strany sú prevádzkovateľmi, štít neexistuje', 5, 'pravo'),
    ('Logistika: jedno e-cargo, ≈40 kg na jazdu, CHF 11 za večer', 6, 'logistika'),
    ('Záver', 7, 'zaver'),
]
toc = '<ol class="toc">' + ''.join(f'<li><a href="#{a}">{html.escape(t)}</a></li>' for t, n, a in idx_sections if n) + '<li><a href="#doverit">Čo treba doveriť (24 položiek)</a></li></ol>'

idx_body = f"""
<header>
<h1>Übrig Bern – prehľad situácie: konkurencia, hladní ľudia, kuchyne, právo</h1>
<p class="sub">Deep research k projektu Übrig Bern (kuchyne vypíšu prebytok, schválené organizácie si ho rezervujú a vyzdvihnú). Zostavené {TODAY} zo šiestich výskumných blokov. Sesterské dokumenty: <a href="mapa.html">mapa a trasa zvozu</a> a <a href="financovanie.html">monetizácia a financovanie</a>.</p>
</header>
<div class="bluf">{conv(BLUF)}</div>
<div class="tiles">
<div class="tile"><b>≈760</b><small>reštaurácií v meste Bern (Der Bund, 2023)</small></div>
<div class="tile"><b>56</b><small>ľudí bez strechy známych mestu (2025; 21 v 2021)</small></div>
<div class="tile"><b>≈300</b><small>ľudí na Nothilfe CHF 10/deň dlhšie ako rok (kantón)</small></div>
<div class="tile"><b>0</b><small>švajčiarskych platforiem, ktoré večer prenášajú uvarené jedlo z reštaurácií do útulkov</small></div>
<div class="tile"><b>≥ 60 °C / &lt; 10 °C</b><small>do 2 h – BLV-Spendenleitfaden 2021 pre odovzdanie pripraveného jedla</small></div>
<div class="tile"><b>3</b><small>miesta v Berne, kde sa po 20:00 podáva jedlo: Passantenheim, Pluto, Punkt 6 (zima)</small></div>
</div>
<div class="warn"><b>Obmedzenie tohto výskumu.</b> Sieťová politika prostredia zablokovala priame načítanie takmer všetkých primárnych stránok (bern.ch, be.ch, fedlex, blv, sleeper.ch, nadácie…) a rozpočet vyhľadávania sa vyčerpal. Väčšina faktov je preto zo <b>snippetov vyhľadávača s URL</b>, nie z prečítaných stránok. Každý údaj nesie značku pôvodu a na konci je zoznam 24 vecí, ktoré treba pred použitím v žiadosti či na letáku doveriť.</div>
{LEGEND}
<h2 style="margin-top:28px">Obsah</h2>{toc}
{''.join(section_html(t, n, a) for t, n, a in idx_sections)}
<section id="doverit"><h2>8 · Čo treba doveriť</h2><p class="sub">Zoradené podľa hodnoty pre rozhodnutie; každá položka je jeden klik alebo jeden telefonát s odblokovanou sieťou.</p>{verify_rows()}</section>
"""
open(OUTDIR + 'index.html', 'w', encoding='utf-8').write(page('Übrig Bern – prehľad situácie', 'Konkurencia, hladní ľudia v Berne, reštaurácie a právny rámec pre presun prebytočného jedla – výskumný prehľad.', idx_body))

# ------------------------------------------------------------------ financovanie.html
def flow(title, boxes, arrows, w=880, h=225):
    """boxes: list of (id, x, y, w, label, sub); arrows: list of (from, to, cls, label)"""
    bx = {b[0]: b for b in boxes}
    out = [f'<svg class="flow" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}"><defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="#8d8b84"/></marker></defs>']
    for _id, x, y, bw, lab, sub in boxes:
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="58"/><text class="t" x="{x + bw / 2}" y="{y + 25}" text-anchor="middle">{html.escape(lab)}</text><text class="s" x="{x + bw / 2}" y="{y + 44}" text-anchor="middle">{html.escape(sub)}</text>')
    for a, b, cls, lab in arrows:
        A, B = bx[a], bx[b]
        ax, ay = A[1] + A[3] / 2, A[2] + 29; bx_, by = B[1] + B[3] / 2, B[2] + 29
        if abs(ay - by) < 5:  # horizontal
            sx = A[1] + A[3] if bx_ > ax else A[1]; ex = B[1] if bx_ > ax else B[1] + B[3]
            mx = (sx + ex) / 2
            out.append(f'<path class="{cls}" d="M{sx} {ay} L{ex} {by}"/><text class="s" x="{mx}" y="{ay - 8}" text-anchor="middle">{html.escape(lab)}</text>')
        else:
            sy = A[2] + 58 if by > ay else A[2]; ey = B[2] if by > ay else B[2] + 58
            out.append(f'<path class="{cls}" d="M{ax} {sy} C{ax} {(sy + ey) / 2} {bx_} {(sy + ey) / 2} {bx_} {ey}"/><text class="s" x="{(ax + bx_) / 2 + 8}" y="{(sy + ey) / 2 + 4}">{html.escape(lab)}</text>')
    out.append('</svg>')
    return ''.join(out)

F_VEREIN = flow('Model A: gemeinnütziger Verein', [
    ('k', 20, 20, 190, 'Kuchyne (reštaurácie)', 'darujú prebytok, CHF 0 alebo malý paušál'),
    ('o', 670, 20, 190, 'Schválené organizácie', 'vyzdvihnú a podávajú'),
    ('n', 20, 150, 260, 'Nadácie · Lotteriefonds · mesto · cirkvi', 'granty, dary, crowdfunding – nie kapitál'),
    ('v', 400, 150, 220, 'Verein Übrig Bern', 'Steuerbefreiung, neplatené predstavenstvo'),
], [('k', 'o', 'food', 'jedlo + protokol odovzdania (cez platformu Vereinu)'), ('n', 'v', 'money', 'granty a dary'), ('k', 'v', 'money', 'paušál CHF 0–59/rok')])

F_GMBH = flow('Model B: GmbH', [
    ('k', 20, 20, 170, 'Kuchyne', 'platia licenciu / za presun'),
    ('g', 355, 20, 190, 'Übrig GmbH', 'softvér ako majetok zakladateľa'),
    ('m', 690, 20, 170, 'Iné mestá / Städteverband', 'white-label licencie'),
    ('o', 355, 150, 190, 'Sociálne organizácie', 'používajú zdarma'),
], [('k', 'g', 'money', 'CHF/mesiac'), ('m', 'g', 'money', 'licencie'), ('g', 'o', 'food', 'platforma zdarma')])

F_HYB = flow('Model C: hybrid Verein + GmbH', [
    ('v', 20, 20, 210, 'Verein Übrig Bern', 'prevádzka v Berne, granty, Steuerbefreiung'),
    ('g', 340, 20, 210, 'Übrig Software GmbH', 'vlastní kód; licencia Vereinu za trhovú cenu'),
    ('m', 660, 20, 200, 'Ďalšie mestá', 'platia GmbH za licenciu'),
    ('n', 20, 150, 210, 'Nadácie, mesto, kantón', 'financujú Verein, nie GmbH'),
], [('n', 'v', 'money', 'granty'), ('v', 'g', 'money', 'licenčný poplatok (arm\'s length)'), ('m', 'g', 'money', 'licencie')])

fin_body = f"""
<header>
<h1>Übrig Bern – ako to monetizovať a financovať bez riedenia</h1>
<p class="sub">Tretí z troch dokumentov. Odpovedá na tri otázky: podnikať, alebo ísť cez neziskový sektor? Ako v tomto segmente reálne tečú peniaze? A odkiaľ zohnať financie tak, aby si nikto nekupoval podiel. Stav {TODAY}; pôvod každého údaju je označený.</p>
</header>
<div class="bluf"><p><b>Odporúčanie v jednej vete:</b> založiť <b>gemeinnütziger Verein „Übrig Bern“</b> a hneď požiadať Steuerverwaltung Kanton Bern o Steuerbefreiung – to je brána k nadáciám, Lotteriefondu a cirkevným peniazom, ktoré tento sektor reálne živia; peniaze brať od <b>ponukovej strany a donorov</b> (malý paušál od kuchýň, granty, sponzoring, mesto), <b>nikdy od prijímajúcich organizácií</b>; a ak Richard chce raz softvér predať alebo licencovať iným mestám, držať kód od prvého dňa v <b>samostatnej GmbH</b>, ktorá ho Vereinu licencuje za trhovú cenu (model C). Všetko, čo sa tvári ako „grant“ a pritom je konvertibilná pôžička alebo equity (Venture Kick stupne 2–3, Kickfund, SICTIC), je riedenie – vynechať.</p></div>
{LEGEND}
<div class="warn"><b>Obmedzenie.</b> V tomto výskume sa nedala otvoriť ani jedna stránka mesta, kantónu či nadácie a vyhľadávanie sa vyčerpalo. Overených je len sedem finančných nástrojov (čítané 9. 8. 2026 v inom projekte). Všetko ostatné v mape financovania je <span class="m no">neoverené</span> – stopa, nie fakt. Preto je tu na konci zoznam, čo overiť ako prvé, a pri každej sume, ktorá nie je zo zdroja, stojí <span class="m est">odhad</span>.</div>

<h2 style="margin-top:28px">Obsah</h2>
<ol class="toc"><li><a href="#lekcia">Čo učí segment: pohyb jedla peniaze neprináša</a></li><li><a href="#modely">Tri modely, ako môžu tiecť peniaze</a></li><li><a href="#organizacia">Právna forma vo Švajčiarsku (výskum)</a></li><li><a href="#toky">Príjmové toky a ich realizmus</a></li><li><a href="#zdroje">Financovanie bez riedenia (výskum)</a></li><li><a href="#riedenie">Čo je a čo nie je riedenie</a></li><li><a href="#plan">Plán na 12 mesiacov</a></li><li><a href="#kroky">Kroky na tento týždeň</a></li><li><a href="#doverit">Čo doveriť</a></li></ol>

<section id="lekcia"><h2>1 · Čo učí segment: pohyb jedla peniaze neprináša</h2>
<p>Každý, kto sa pokúsil zarobiť na samotnom presune prebytku, narazil: Karma padla zo 100 na 18 ľudí a ziskovosť dosiahla až v Q3 2025, Sirplus skončil v insolvencii, Olio kryje poplatkami ≈30 % nákladov, Too Good To Go Schweiz sa operatívne sťahuje do Viedne (všetko <span class="m sn">snippet</span>, detail v <a href="./#konkurencia-svet">prehľade</a>). Fungujú tri veci: (a) <b>B2C predaj</b> vo veľkom objeme s tenkou maržou (TGTG: CHF 2.90/balíček + CHF 59/rok, skupinový zisk DKK 9,6 mil. na DKK 725 mil. príjmov, 2024), (b) <b>redistribúcia platená donormi</b> – Tischlein deck dich a Schweizer Tafel žijú z Coop, Migros, Ernst Göhner Stiftung a darcov, Tafel výslovne bez štátnych peňazí, (c) <b>fee-for-service platený darcom</b> (Copia, Goodr, Rescuing Leftover Cuisine v USA), kde motiváciu drží daňový odpočet, ktorý vo Švajčiarsku pre 10 porcií nič neznamená.</p>
<p>Pre Übrig z toho plynie: <b>produktom nie je presun jedla, ale dôkaz o ňom</b> – protokol odovzdania (čas, teplota, alergény, „spotrebovať do“, podpisy), ktorý chráni kuchyňu aj útulok tam, kde švajčiarske právo žiadny „Good Samaritan“ štít nedáva. Za dôkaz sa dá platiť: mesto (Nachhaltige Ernährung, Gastro Charta), nadácie (merateľný výstup), kuchyne (ESG komunikácia, Gastro-Charta kredit) a neskôr iné mestá (licencia).</p>
</section>

<section id="modely"><h2>2 · Tri modely, ako môžu tiecť peniaze</h2>
<div class="cards">
<div class="card"><h3>A · gemeinnütziger Verein</h3><p><b>Kedy:</b> cieľom sú granty a dary a Richardovi stačí rola plateného Geschäftsführera (trhovo primeraná mzda je dovolená).</p><ul><li>+ založenie za deň, CHF 0 kapitálu, dve osoby</li><li>+ jediná forma, ktorú nadácie, Lotteriefonds a cirkvi financujú bez otázok</li><li>+ Steuerbefreiung (DBG Art. 56 lit. g) = žiadna daň zo zisku a odpočítateľné dary</li><li>− majetok je účelovo viazaný: <b>nedá sa predať</b>, pri zrušení ide inej gemeinnützigen organizácii</li><li>− v kantóne Bern sa predpokladá neplatené predstavenstvo</li></ul></div>
<div class="card"><h3>B · GmbH</h3><p><b>Kedy:</b> cieľom je predajný softvérový majetok (SaaS pre mestá) a charitatívne peniaze nie sú potrebné.</p><ul><li>+ vlastníctvo a exit sú možné, licencie iným mestám sú čistý B2B/B2G obchod</li><li>+ „gemeinnützige GmbH“ ako právna forma v CH neexistuje, ale GmbH sa dá koncipovať na charitatívny účel a oslobodiť od daní <span class="m sn">snippet</span> – potom však platí zákaz rozdelenia zisku, čiže exit opäť mizne</li><li>− CHF 20 000 Stammkapital + CHF 2 500–5 000 založenie <span class="m sn">snippet</span></li><li>− nadácie a Lotteriefonds GmbH bez Steuerbefreiung spravidla nefinancujú</li></ul></div>
<div class="card"><h3>C · hybrid Verein + GmbH</h3><p><b>Kedy:</b> Richard chce oboje – bernskú prevádzku financovanú grantmi <i>a</i> softvér, ktorý raz predá alebo licencuje.</p><ul><li>+ granty tečú do Vereinu, hodnota softvéru rastie v GmbH</li><li>+ precedens oddelenia existuje (Schweizer Tafel: Stiftung + Gönnerverein) <span class="m sn">snippet</span></li><li>− licencia Verein → GmbH musí byť za trhovú cenu a transparentná, inak Steuerverwaltung vidí skryté rozdelenie zisku; <b>potrebuje daňového poradcu pred založením</b> <span class="m no">neoverené</span></li><li>− dve účtovníctva, dve valné zhromaždenia</li></ul></div>
</div>
<h3>Ako v každom modeli tečú peniaze (oranžová) a jedlo (zelená)</h3>
<figure class="fig"><figcaption>Model A · Verein</figcaption>{F_VEREIN}</figure>
<figure class="fig"><figcaption>Model B · GmbH</figcaption>{F_GMBH}</figure>
<figure class="fig"><figcaption>Model C · hybrid</figcaption>{F_HYB}</figure>
<p><b>Odporúčanie:</b> model A okamžite (Verein sa dá založiť tento týždeň), s klauzulou v stanovách, že softvér je licencovaný od zakladateľa/GmbH – teda model C pripravený „na papieri“, GmbH založená až vtedy, keď prvé iné mesto reálne chce licenciu. Prestavovať Verein na hybrid dodatočne je drahšie než ho tak navrhnuť od začiatku.</p>
</section>

{section_html('Organizácia: Verein so Steuerbefreiung, peniaze z ponukovej strany, nie od NGO', 3, 'organizacia')}

<section id="toky"><h2>4 · Príjmové toky a ich realizmus pre jedno mesto</h2>
<div class="tw"><table><thead><tr><th>Tok</th><th>Kto platí</th><th>Kotva z výskumu</th><th>Realizmus rok 1</th><th>Rok 3</th></tr></thead><tbody>
<tr><td><b>Granty nadácií a Lotteriefonds</b></td><td>nadácie, kantón</td><td>Tischlein/Tafel žijú z Coop, Göhner, darcov <span class="m sn">snippet</span>; Zug dal CHF 25 000 na 10 chladničiek Madame Frigo <span class="m sn">snippet</span></td><td><b>hlavný tok</b> – po Steuerbefreiung</td><td>hlavný tok</td></tr>
<tr><td><b>Paušál od kuchýň</b></td><td>reštaurácie</td><td>TGTG berie CHF 59/rok + CHF 2.90/balíček a kuchyňa <i>dostáva</i> peniaze <span class="m sn">snippet</span></td><td>CHF 0 (pilot zdarma; odstraňuje len náklad 6–12 Rp/kg bioodpadu)</td><td>CHF 50–100/rok „Mitglied“ – symbolické, skôr záväzok než príjem <span class="m est">odhad</span></td></tr>
<tr><td><b>Mesto Bern – Leistungsvertrag / projektový príspevok</b></td><td>Stadt Bern (BSS, Nachhaltigkeit)</td><td>mesto uvoľnilo ≈CHF 400 000 na ľudí bez strechy (2024/25) <span class="m sn">snippet</span>; stratégia Nachhaltige Ernährung má pole „Food Losses“ <span class="m sn">snippet</span></td><td>projektový príspevok možný, Leistungsvertrag nie (Verein &lt; 1 rok)</td><td>reálny, ak prijímajúce organizácie potvrdia závislosť</td></tr>
<tr><td><b>Korporátny sponzoring</b></td><td>Migros Aare, Coop, BEKB, Mobiliar, Kursaal</td><td>Coop dáva Tischlein CHF 425 000/rok <span class="m sn">snippet</span>; SV Stiftung platí chladničky Madame Frigo <span class="m sn">snippet</span></td><td>in-kind (termoboxy, cargo-bike) skôr než hotovosť</td><td>hotovosť za viditeľnosť na štítku/protokole</td></tr>
<tr><td><b>Crowdfunding</b></td><td>verejnosť</td><td>wemakeit 6 % + 4 % <span class="m ok">overené</span>; Sleeper a Pluto uspeli na lokalhelden/Crowdify <span class="m sn">snippet</span></td><td>launch kampaň CHF 10–20 tis. <span class="m est">odhad</span></td><td>jednorazovo</td></tr>
<tr><td><b>Licencie iným mestám (SaaS)</b></td><td>mestá, Städteverband</td><td>412 Food Rescue / MealConnect v USA <span class="m sn">snippet</span>; v CH bez precedensu</td><td>0</td><td>možný, len cez GmbH (model C)</td></tr>
<tr><td><b>Arbeitsintegration ako pracovná sila</b></td><td>Sozialamt / RAV / IV platia poskytovateľa</td><td>Kompetenzzentrum Arbeit má 350+ partnerov; Drahtesel vedie bicyklovú dielňu <span class="m sn">snippet</span></td><td>jazdci bez nákladu pre Übrig – rokovať s Drahtesel/KA</td><td>štandard</td></tr>
<tr><td><b>Potvrdenia o dare pre kuchyne</b></td><td>—</td><td>Naturalspenden odpočítateľné od 2007, ale treba Verkehrswert <span class="m sn">snippet</span></td><td>ESG-artefakt, nie peniaze</td><td>—</td></tr>
<tr><td><b>Reklama, predaj dát</b></td><td>—</td><td>—</td><td colspan="2">nie – ničí dôveru útulkov aj kuchýň</td></tr>
</tbody></table></div>
<p>Jednotková ekonomika, ktorú treba mať v hlave pri každom rozhovore: Schweizer Tafel presunie za 1 darovaný frank 1,81 kg tovaru <span class="m sn">snippet</span> (≈ CHF 0.55/kg <span class="m calc">výpočet</span>); marginálny náklad Übrig na jeden presun je blízko nule, lebo príjemca si vyzdvihne a softvér beží na free-tier – viažuci náklad je čas koordinátora. Správna jednotka pre grant je preto „<b>náklad na aktívnu kuchyňu a mesiac</b>“ a „<b>počet dokumentovaných odovzdaní</b>“, nie kilogramy.</p>
</section>

{section_html('Financovanie bez riedenia: sedem overených dverí, z toho žiadne s hotovosťou pre Verein', 5, 'zdroje')}

<section id="riedenie"><h2>6 · Čo je a čo nie je riedenie</h2>
<div class="cards">
<div class="card"><h3>Bez riedenia ✔</h3><ul><li><b>Granty a dary</b> (nadácie, Lotteriefonds, mesto, kantón, cirkvi) – peniaze za výstup, žiadny podiel</li><li><b>Ceny a súťaže</b> (Social Impact Award, seif, Prix) – ak sú výslovne „Preisgeld“</li><li><b>Crowdfunding s odmenami</b> (wemakeit, lokalhelden) – podporovatelia nedostávajú podiel</li><li><b>Sponzoring a in-kind</b> (termoboxy, bicykel, cloud kredity)</li><li><b>Leistungsvertrag</b> s mestom – platba za službu</li><li><b>Členské a paušály</b></li><li><b>Genossenschaft-Anteilscheine</b> – kapitál bez kontroly (jeden člen = jeden hlas), ale s právom na vrátenie <span class="m no">neoverené</span></li></ul></div>
<div class="card"><h3>Riedenie alebo dlh ✘ / ⚠</h3><ul><li><b>Venture Kick stupne 2–3</b>: repozitár si protirečí, či grant alebo konvertibilná pôžička <span class="m ok">overené</span> – správať sa k nim ako k riediacim, kým sa neoverí</li><li><b>Kickfund, SICTIC, angel investori</b>: equity <span class="m ok">overené</span></li><li><b>BG Mitte, BEKB Förderkredit, ABS</b>: pôžičky/ručenia – nie riedenie, ale dlh, ktorý Verein bez príjmov nemá z čoho splácať</li><li><b>„Impact investing“ s convertible note</b>: riedenie s oneskorením</li><li><b>Fördergutscheine BE</b>: bol grant, ale okno zavreté 30. 11. 2025 a cieľ boli priemyselné firmy <span class="m ok">overené</span></li></ul><p>Pozor: vo Vereine s Steuerbefreiung sa equity ani vydať nedá – riedenie je otázka len pre GmbH v modeli B/C.</p></div>
</div>
</section>

<section id="plan"><h2>7 · Plán financovania na 12 mesiacov (bez riedenia)</h2>
<p>Sumy sú <span class="m est">odhad</span> podľa rádov z výskumu (Zug CHF 25 000 za 10 chladničiek; Landeskirche CHF 25 000 pre Tischlein; Coop Regionalrat CHF 3 000 pre Sleeper). Cieľ roka 1: pokryť koordinátora na 20–40 %, termoboxy, cargo-bike a prvé merania, spolu rádovo <b>CHF 40 000–70 000</b>.</p>
<div class="tw"><table><thead><tr><th>Mesiac</th><th>Krok</th><th>Zdroj</th><th>Rád (CHF)</th><th>Podmienka</th></tr></thead><tbody>
<tr><td>1</td><td>Založiť Verein, podať Steuerbefreiung, be-advanced prvé stretnutie</td><td>—</td><td>0</td><td>2 osoby, stanovy s Liquidationsklausel; be-advanced <span class="m ok">overené</span></td></tr>
<tr><td>1–2</td><td>Telefonát Kantonales Laboratorium; pilot s 5–10 kuchyňami klastra Zeughausgasse, carvelo2go, vlastné merania</td><td>vlastné + carvelo2go</td><td>≈ 250 (CHF 11/večer × 20)</td><td>protokol odovzdania hotový</td></tr>
<tr><td>2–3</td><td>Seed od cirkví (Kirchgemeinden, Kath. Kirche Region Bern), Quartierkommission, Burgergemeinde</td><td>diakonálne fondy</td><td>3 000–10 000</td><td>Verein existuje; číslo „porcie/večer“ z pilotu</td></tr>
<tr><td>3–4</td><td>Crowdfunding na launch (termoboxy, bicykel, kampaň)</td><td>lokalhelden / wemakeit</td><td>10 000–20 000</td><td>wemakeit all-or-nothing 6 % + 4 % <span class="m ok">overené</span></td></tr>
<tr><td>4–6</td><td>Impact Hub Bern (Circular Economy Incubator), Social Impact Award</td><td>akcelerátor / cena</td><td>in-kind + 0–10 000</td><td>termíny <span class="m no">neoverené</span></td></tr>
<tr><td>5–8</td><td>Lotteriefonds Kanton Bern – jednorazový projekt (softvér, vybavenie, kampaň), nie mzdy</td><td>kantón</td><td>10 000–30 000</td><td>Steuerbefreiung, spoluúčasť <span class="m no">neoverené</span></td></tr>
<tr><td>6–10</td><td>Nadácie: Stanley Thomas Johnson, Bürgi-Willert, Corymbo, Ernst Göhner; Engagement Migros (dlhšie)</td><td>nadácie</td><td>10 000–30 000</td><td>Steuerbefreiung + prvé výsledky pilotu</td></tr>
<tr><td>6–12</td><td>Stadt Bern – projektový príspevok (Nachhaltige Ernährung / BSS); Gastro Charta ako rámec pre kuchyne</td><td>mesto</td><td>5 000–20 000</td><td>listy podpory od Passantenheim/Sleeper/PINTO</td></tr>
<tr><td>9–12</td><td>Jazdci cez Arbeitsintegration (Drahtesel / Kompetenzzentrum Arbeit); Google/GitHub nonprofit kredity</td><td>in-kind</td><td>0</td><td>Verein + Steuerbefreiung</td></tr>
</tbody></table></div>
<p>Poradie nie je náhodné: <b>forma → dozor → meranie → seed → verejný príbeh → inštitucionálne granty</b>. Každý ďalší krok používa výstup predošlého (počet odovzdaní, teplotný log, listy podpory) ako dôkaz. Leistungsvertrag so Sozialamtom je téma roka 2–3.</p>
</section>

<section id="kroky"><h2>8 · Kroky na tento týždeň</h2>
<ol class="steps">
<li><b>Stanovy Vereinu</b> (účel: „Verminderung von Lebensmittelverlusten durch Weitergabe an gemeinnützige Organisationen in Bern“, Liquidationsklausel, neplatené predstavenstvo, možnosť plateného Geschäftsführera) – dve osoby, Gründungsversammlung, zápis.</li>
<li><b>Žiadosť o Steuerbefreiung</b> na Steuerverwaltung Kanton Bern (TaxInfo) – priložiť stanovy, popis činnosti, rozpočet.</li>
<li><b>Telefonát Kantonales Laboratorium Bern</b> (031 633 11 11): musí sa Verein, ktorý len sprostredkuje a nevozí, registrovať ako Lebensmittelbetrieb? Aké sú požiadavky na protokol?</li>
<li><b>Telefonáty príjemcom</b>: Passantenheim (031 351 80 27), Sleeper (031 301 64 04), Punkt 6 (031 321 76 38) – prijmú teplé jedlo po 21:30? v akých nádobách? kto podpíše?</li>
<li><b>be-advanced</b> – bezplatné prvé stretnutie (do 2 týždňov) <span class="m ok">overené</span>; pýtať sa na kontakt do Impact Hub Bern a na Lotteriefonds.</li>
<li><b>Overiť 8 finančných dverí</b> zo zoznamu nižšie s odblokovanou sieťou alebo v prehliadači – predovšetkým Lotteriefonds, Burgergemeinde, Stanley Thomas Johnson Stiftung, Impact Hub Bern.</li>
</ol>
</section>

<section id="doverit"><h2>9 · Čo doveriť pre financovanie</h2>{verify_rows(keep={8, 9, 10, 11, 12, 13, 14, 15, 19, 4, 6})}</section>
"""
open(OUTDIR + 'financovanie.html', 'w', encoding='utf-8').write(page('Übrig Bern – monetizácia a financovanie', 'Podnikať alebo nezisk? Ako tečú peniaze v segmente záchrany jedla a ako financovať Übrig Bern bez riedenia.', fin_body))
print('written index.html + financovanie.html')
