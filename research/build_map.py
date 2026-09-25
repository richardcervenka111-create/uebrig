# -*- coding: utf-8 -*-
"""Builds uebrig/research/mapa.html: Bern restaurants by estimated kitchen-closing time,
receiving institutions, a two-leg e-cargo-bike pick-up route and a portions estimate.
Data: OpenStreetMap via Overpass (overpass.kumi.systems), fetched 25.09.2026."""
import json, math, re, html, collections, datetime

S = '/tmp/claude-0/-home-user-Sautero-app/911fc836-514c-54a6-a831-59d4cb035434/scratchpad/osm/'
OUT = '/home/user/uebrig/research/mapa.html'
TODAY = '25. 9. 2026'

gastro = json.load(open(S + 'gastro_parsed.json'))
roads = json.load(open(S + 'r1.json'))['elements']
water = json.load(open(S + 'r3.json'))['elements']

# ---------- projection ----------
LON0, LON1, LAT0, LAT1 = 7.405, 7.482, 46.9355, 46.9715
KX = 76100.0  # m per degree lon at 46.95
KY = 111200.0
W = 1200.0
SCALE = W / ((LON1 - LON0) * KX)  # px per metre
H = round((LAT1 - LAT0) * KY * SCALE)
def P(lat, lon):
    return ((lon - LON0) * KX * SCALE, (LAT1 - lat) * KY * SCALE)
def inb(lat, lon, pad=0.004):
    return LAT0 - pad <= lat <= LAT1 + pad and LON0 - pad <= lon <= LON1 + pad
def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(d))

def path_of(geom, close=False):
    pts = []
    last = None
    for p in geom:
        x, y = P(p['lat'], p['lon'])
        q = (round(x, 1), round(y, 1))
        if q != last:
            pts.append(q); last = q
    if len(pts) < 2:
        return ''
    d = 'M' + ' L'.join(f'{x:g} {y:g}' for x, y in pts)
    return d + ('Z' if close else '')

def layer(elements, pred, close=False):
    out = []
    for e in elements:
        g = e.get('geometry')
        if not g or not pred(e['tags']):
            continue
        if not any(inb(p['lat'], p['lon']) for p in g):
            continue
        d = path_of(g, close)
        if d:
            out.append(d)
    return out

hw = lambda cls: (lambda t: t.get('highway') in cls)

# ---------- explicit kitchen-closing statements (web research 25.9.2026, snippet only) ----------
# name pattern -> (kitchen close "HH:MM" typical Tue-Thu, source host)
EXPLICIT = [
    (r'^lötschberg$', '21:30', 'loetschbergbern.ch'),
    (r'^bärenhöfli$', '21:30', 'baerenhoefli.ch (iný zdroj 22:00)'),
    (r'^ringgenberg$', '21:30', 'restaurant-ringgenberg.ch'),
    (r'^volkshaus 1914$', '21:45', 'volkshausbern.ch'),
    (r'^vue$', '21:30', 'bellevue-palace.ch'),
    (r'^goldener schlüssel$', '21:00', 'goldener-schluessel-bern.ch'),
    (r'^sua$', '20:30', 'suarestaurant.ch (St; Št 21:00)'),
    (r'^harmonie$', '22:00', 'harmoniebern.ch'),
    (r'^della casa$', '22:00', 'della-casa.ch'),
    (r'^domino$', '22:00', 'domino-bern.ch'),
    (r'^fédéral$', '22:00', 'entrecote.ch'),
    (r'^kirchenfeld$', '22:00', 'kirchenfeld.ch'),
    (r'^verdi$', '22:00', 'bindella.ch (Po–Št)'),
    (r'^national$', '22:00', 'nationalbern.ch (Restaurant do 22:00; Küche neuvedená)'),
    (r'^brasserie bärengraben$', '22:15', 'brasseriebaerengraben.ch'),
    (r'^bay$', '22:30', 'restaurantbay.ch'),
    (r'^kairo$', '22:30', 'cafe-kairo.ch'),
    (r'^tibits$', '22:30', 'sbb.ch (bufet do zatvorenia)'),
    (r"^jack's brasserie$", '23:00', 'schweizerhofbern.com'),
    (r'^altes tramdepot$', '23:00', 'altestramdepot.ch'),
    (r'^dampfzentrale$', '23:30', 'restaurant-dampfzentrale.ch'),
    (r'^manora$', '17:00', 'swipein (Po–Pi)'),
    (r'^migros restaurant$', None, None),  # keep OSM hours (differ per branch)
]
def explicit_for(name):
    n = (name or '').strip().lower()
    for pat, k, src in EXPLICIT:
        if re.match(pat, n) and k:
            h, m = map(int, k.split(':'))
            return h * 60 + m, src
    return None, None

RETAIL = re.compile(r"coop|migros|to go|take away|take-away|takeaway|kiosk|avec|selecta|mcdonald|burger king|subway|starbucks|spar|volg|denner|aldi|lidl|manor|manora|tibits", re.I)
HOTEL = re.compile(r"bärenhöfli|volkshaus|vue|jack's|national|goldener schlüssel|bellevue|schweizerhof|savoy|kreuz|allegro|giardino", re.I)
BUFFET = re.compile(r"migros|manora|coop|tibits|mensa|cafeteria", re.I)

def fmt(m):
    m = int(m) % (24 * 60)
    return f'{m // 60:02d}:{m % 60:02d}'

def bucket_of(k):
    if k is None: return None
    if k < 19 * 60: return 'skôr'
    if k > 22 * 60 + 29: return 'neskôr'
    b = (k // 30) * 30
    return fmt(b)

BUCKETS = ['19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00']
# ordinal blue ramp (dataviz reference palette, steps 250..700) for the seven time buckets
BCOL = {'19:00': '#86b6ef', '19:30': '#6da7ec', '20:00': '#3987e5', '20:30': '#2a78d6',
        '21:00': '#1c5cab', '21:30': '#184f95', '22:00': '#0d366b', 'skôr': '#c9c7c0', 'neskôr': '#8d8b84'}

est = []
for g in gastro:
    if g['amenity'] not in ('restaurant', 'fast_food', 'food_court'):
        continue
    if not g['name'] or g['lat'] is None or not inb(g['lat'], g['lon'], 0):
        continue
    vc = g['close']
    if vc is None or vc < 0:
        continue
    ek, src = explicit_for(g['name'])
    if ek is not None:
        k = ek; kind = 'explicit'
    else:
        k = vc - (30 if g['amenity'] == 'restaurant' else 0); kind = 'odhad'
    if RETAIL.search(g['name']) and g['amenity'] != 'restaurant' or re.search(r'coop|migros', g['name'], re.I): cat = 'retail'
    elif BUFFET.search(g['name']): cat = 'buffet'
    elif HOTEL.search(g['name']): cat = 'hotel'
    elif g['amenity'] == 'restaurant': cat = 'restaurant'
    else: cat = 'fast_food'
    est.append(dict(g, kitchen=k, kind=kind, src=src, bucket=bucket_of(k), cat=cat))

cnt = collections.Counter(e['bucket'] for e in est)
print('establishments', len(est), dict(cnt))
in_buckets = [e for e in est if e['bucket'] in BUCKETS]

# ---------- receivers ----------
RECV = [
    dict(id='punkt6', name='Punkt 6 – Aufenthaltsraum PINTO (Stadt Bern)', addr='Nägeligasse 3a, 3011', lat=46.94955, lon=7.4453, pos='ulica (číslo neoverené)',
         hours='zima 1. 11.–31. 3.: 06:00–10:00 a 18:00–22:30', food='dnes len káva a sendviče zdarma → kandidát na teplé jedlo', role='drop 1 (etapa A)'),
    dict(id='passant', name='Passantenheim Heilsarmee', addr='Muristrasse 6, 3006', lat=46.94443, lon=7.4591, pos='OSM bod',
         hours='príchod do 20:00, posledný vstup 23:00; otvorené 19:00–09:00', food='50–60 lôžok, Halbpension (hodina večere neuvedená)', role='drop 2 (etapa B)'),
    dict(id='sleeper', name='Sleeper – Notschlafstelle & Gassenküche', addr='Neubrückstrasse 19, 3012', lat=46.95383, lon=7.43887, pos='adresný bod OSM',
         hours='večera 18:00–20:00 (CHF 5); check-in 22:00–01:00', food='20 lôžok; varí sám z dodávok Schweizer Tafel; pod Lebensmittelkontrolle', role='alternatíva drop 2 (schladené na ďalší deň)'),
    dict(id='pluto', name='Pluto – Jugend-Notschlafstelle', addr='Studerstrasse 44, 3004', lat=46.96664, lon=7.43951, pos='adresný bod OSM',
         hours='18:00–09:00, 365 dní', food='7 lôžok, teplá večera zdarma', role='malý objem, mimo trasy'),
    dict(id='contact', name='CONTACT Anlaufstelle', addr='Hodlerstrasse 22, 3011', lat=46.95181, lon=7.44237, pos='adresný bod OSM',
         hours='Ut–So 12:30–20:00', food='jedlo neuvedené', role='len do 20:00'),
    dict(id='passhilfe', name='Kirchliche Passantenhilfe – Aufenthaltsraum', addr='Mattenhofstrasse 32, 3007 (od 19. 1. 2026)', lat=46.94384, lon=7.42898, pos='adresný bod OSM',
         hours='hodiny na novej adrese neuvedené', food='—', role='overiť'),
    dict(id='laprairie', name='La Prairie – Das Offene Haus', addr='Sulgeneckstrasse 7, 3007', lat=46.94497, lon=7.43858, pos='adresný bod OSM',
         hours='Ut–Pi 10–15, Ne 10–14 (večer zrušený)', food='obed CHF 5', role='denné centrum'),
]
RID = {r['id']: r for r in RECV}

# ---------- route simulation ----------
SPEED_KMH = 13.0; DETOUR = 1.3; STOP_MIN = 8; WINDOW = 40; DROP_MIN = 10
def travel_min(a, b):
    return hav(a, b) * DETOUR / (SPEED_KMH * 1000 / 60)

def plan_leg(cands, t0, pos, t_end, max_stops):
    stops = []; t = t0; used = set()
    while len(stops) < max_stops:
        best = None
        for c in cands:
            if c['id'] in used: continue
            tr = travel_min(pos, (c['lat'], c['lon'])) if pos else 0
            arr = max(t + tr, c['kitchen'])
            if arr > c['kitchen'] + WINDOW or arr + STOP_MIN > t_end: continue
            wait = arr - (t + tr)
            score = arr + 0.5 * wait - (12 if c['kind'] == 'explicit' else 0) - (6 if c['cat'] in ('hotel', 'buffet') else 0)
            if best is None or score < best[0]:
                best = (score, c, arr, tr)
        if not best: break
        _, c, arr, tr = best
        stops.append(dict(c, arrive=arr, leave=arr + STOP_MIN, dist=tr * (SPEED_KMH * 1000 / 60) / DETOUR))
        used.add(c['id']); t = arr + STOP_MIN; pos = (c['lat'], c['lon'])
    return stops, t, pos

ZYT = (46.9480, 7.4474)  # Zytglogge
RADIUS = 1600
routable = [e for e in in_buckets if e['cat'] != 'retail' and hav(ZYT, (e['lat'], e['lon'])) <= RADIUS]
legA_c = [e for e in routable if 19 * 60 <= e['kitchen'] <= 20 * 60 + 30]
legB_c = [e for e in routable if 21 * 60 <= e['kitchen'] <= 22 * 60]
A, tA, posA = plan_leg(legA_c, 19 * 60, None, 20 * 60 + 45, 8)
p6 = (RID['punkt6']['lat'], RID['punkt6']['lon'])
trA = travel_min(posA, p6); arrA = tA + trA
namesA = {s['name'] for s in A}
legB_c = [e for e in legB_c if e['name'] not in namesA]
B, tB, posB = plan_leg(legB_c, max(arrA + DROP_MIN, 21 * 60 - 10), p6, 22 * 60 + 45, 8)
ph = (RID['passant']['lat'], RID['passant']['lon'])
trB = travel_min(posB, ph); arrB = tB + trB
print('leg A', [(s['name'], fmt(s['kitchen']), fmt(s['arrive'])) for s in A], 'drop', fmt(arrA))
print('leg B', [(s['name'], fmt(s['kitchen']), fmt(s['arrive'])) for s in B], 'drop', fmt(arrB))

def leg_km(stops, start=None, end=None):
    pts = ([start] if start else []) + [(s['lat'], s['lon']) for s in stops] + ([end] if end else [])
    return sum(hav(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) * DETOUR / 1000
kmA = leg_km(A, None, p6); kmB = leg_km(B, p6, ph)

# ---------- portions estimate ----------
PORT = {'restaurant': (2, 4, 6), 'fast_food': (2, 3, 4), 'hotel': (4, 6, 10), 'buffet': (6, 10, 15), 'retail': (0, 0, 0)}
def portions(stops):
    return [sum(PORT[s['cat']][i] for s in stops) for i in range(3)]
pA, pB = portions(A), portions(B)
pT = [a + b for a, b in zip(pA, pB)]
KG = 0.4  # kg per portion incl. packaging

# ---------- SVG map (parametric) ----------
def render_map(lon0, lon1, lat0, lat1, width, svg_id, label_all=False, show_ctx=True, min_r=6):
    scale = width / ((lon1 - lon0) * KX)
    hgt = round((lat1 - lat0) * KY * scale)
    def Pp(lat, lon):
        return ((lon - lon0) * KX * scale, (lat1 - lat) * KY * scale)
    def inside(lat, lon, pad=0.003):
        return lat0 - pad <= lat <= lat1 + pad and lon0 - pad <= lon <= lon1 + pad
    def path_of2(geom, close=False):
        pts = []; last = None
        for q in geom:
            x, y = Pp(q['lat'], q['lon']); r = (round(x, 1), round(y, 1))
            if r != last: pts.append(r); last = r
        if len(pts) < 2: return ''
        return 'M' + ' L'.join(f'{x:g} {y:g}' for x, y in pts) + ('Z' if close else '')
    def layer2(elements, pred, close=False):
        out = []
        for e in elements:
            g = e.get('geometry')
            if not g or not pred(e['tags']): continue
            if not any(inside(q['lat'], q['lon']) for q in g): continue
            d = path_of2(g, close)
            if d: out.append(d)
        return out
    def paths2(cls, ds): return ''.join(f'<path class="{cls}" d="{d}"/>' for d in ds)
    def dot2(e):
        x, y = Pp(e['lat'], e['lon']); col = BCOL[e['bucket']]
        r = min_r if e['bucket'] in BUCKETS else max(2, min_r - 3)
        kind = 'explicit' if e['kind'] == 'explicit' else 'odhad'
        tip = f"{e['name']} · {e['amenity']} · Lokal zatvára {fmt(e['close'])} · Küche {'' if kind=='explicit' else '≈'}{fmt(e['kitchen'])} ({kind})"
        return (f'<circle class="pt b-{e["bucket"].replace(":", "")}" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" '
                f'data-tip="{html.escape(tip, quote=True)}"' + (' stroke="#1b1b1b" stroke-width="1.5"' if kind == 'explicit' and e['bucket'] in BUCKETS else ' stroke="#fff" stroke-width="1"') + '/>')
    out = [f'<svg id="{svg_id}" viewBox="0 0 {width:g} {hgt}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mapa Bernu: reštaurácie podľa času zatvorenia kuchyne, prijímajúce inštitúcie a trasa">']
    out.append(f'<rect width="{width:g}" height="{hgt}" class="land"/>')
    out.append(paths2('water', layer2(water, lambda t: t.get('natural') == 'water', close=True)))
    out.append(paths2('river', layer2(water, lambda t: t.get('waterway') == 'river')))
    out.append(paths2('rail', layer2(water, lambda t: t.get('railway') == 'rail')))
    out.append(paths2('rd-ter', layer2(roads, hw({'tertiary'}))))
    out.append(paths2('rd-sec', layer2(roads, hw({'secondary'}))))
    out.append(paths2('rd-maj', layer2(roads, hw({'trunk', 'primary'}))))
    vis = [e for e in est if inside(e['lat'], e['lon'], 0)]
    if show_ctx:
        out.append(f'<g class="pts-ctx">' + ''.join(dot2(e) for e in vis if e['bucket'] not in BUCKETS) + '</g>')
    out.append('<g class="pts">' + ''.join(dot2(e) for e in vis if e['bucket'] in BUCKETS) + '</g>')
    def poly2(pts): return ' '.join(f'{Pp(a, b)[0]:.1f},{Pp(a, b)[1]:.1f}' for a, b in pts)
    out.append(f'<polyline class="route rA" points="{poly2([(s["lat"], s["lon"]) for s in A] + [p6])}"/>')
    out.append(f'<polyline class="route rB" points="{poly2([p6] + [(s["lat"], s["lon"]) for s in B] + [ph])}"/>')
    for i, s in enumerate(A + B, 1):
        if not inside(s['lat'], s['lon'], 0): continue
        x, y = Pp(s['lat'], s['lon'])
        out.append(f'<g class="stop"><circle cx="{x:.1f}" cy="{y:.1f}" r="11" class="{"sA" if i <= len(A) else "sB"}"/><text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle">{i}</text></g>')
    for r in RECV:
        if not inside(r['lat'], r['lon'], 0): continue
        x, y = Pp(r['lat'], r['lon']); tip = f"{r['name']} · {r['addr']} · {r['hours']}"
        out.append(f'<g class="recv" data-tip="{html.escape(tip, quote=True)}"><rect x="{x - 9:.1f}" y="{y - 9:.1f}" width="18" height="18" rx="3"/><text x="{x + 13:.1f}" y="{y + 5:.1f}">{html.escape(r["name"].split(" –")[0].split(" (")[0])}</text></g>')
    placed = [Pp(r['lat'], r['lon']) for r in RECV if inside(r['lat'], r['lon'], 0)]
    for i, s in enumerate(A + B, 1):
        if not inside(s['lat'], s['lon'], 0): continue
        x, y = Pp(s['lat'], s['lon'])
        if not label_all and any(abs(x - px) < 110 and abs(y - py) < 16 for px, py in placed): continue
        placed.append((x, y))
        out.append(f'<text class="lbl" x="{x + 13:.1f}" y="{y - 8:.1f}">{i} {html.escape(s["name"])}</text>')
    sx, sy = 40, hgt - 30; sl = (500 if width > 900 else 200) * scale
    out.append(f'<g class="scale"><line x1="{sx}" y1="{sy}" x2="{sx + sl:.1f}" y2="{sy}"/><text x="{sx}" y="{sy - 6}">{500 if width > 900 else 200} m</text></g>')
    out.append(f'<text class="attr" x="{width - 12}" y="{hgt - 12}">Mapové dáta © prispievatelia OpenStreetMap (ODbL), stiahnuté {TODAY}</text>')
    out.append('</svg>')
    return ''.join(out)

SVG = render_map(LON0, LON1, LAT0, LAT1, W, 'map')
SVG2 = render_map(7.4335, 7.4585, 46.9435, 46.9555, 1200.0, 'map2', label_all=True, min_r=9)

# ---------- histogram ----------
order = ['skôr'] + BUCKETS + ['neskôr']
maxc = max(cnt[b] for b in order)
bars = []
bw = 90; gap = 14; x0 = 60; hmax = 180; base = 220
for i, b in enumerate(order):
    c = cnt[b]; hh = c / maxc * hmax
    x = x0 + i * (bw + gap)
    lab = {'skôr': 'pred 19:00', 'neskôr': 'po 22:30'}.get(b, b)
    bars.append(f'<rect x="{x}" y="{base - hh:.1f}" width="{bw}" height="{hh:.1f}" rx="4" fill="{BCOL[b]}"/>'
                f'<text class="v" x="{x + bw / 2}" y="{base - hh - 6:.1f}" text-anchor="middle">{c}</text>'
                f'<text class="a" x="{x + bw / 2}" y="{base + 20}" text-anchor="middle">{lab}</text>')
HIST = f'<svg viewBox="0 0 {x0 * 2 + len(order) * (bw + gap)} 260" class="hist" role="img" aria-label="Počet podnikov podľa odhadovaného zatvorenia kuchyne"><line x1="{x0 - 10}" y1="{base}" x2="{x0 + len(order) * (bw + gap)}" y2="{base}" class="ax"/>{"".join(bars)}</svg>'

# ---------- tables ----------
def route_rows(stops, offset=0):
    rows = []
    for i, s in enumerate(stops, 1 + offset):
        lo, mid, hi = PORT[s['cat']]
        rows.append(f'<tr><td>{i}</td><td><b>{html.escape(s["name"])}</b><br><small>{html.escape(s.get("addr") or "adresa v OSM chýba")}</small></td>'
                    f'<td>{ {"restaurant":"reštaurácia","fast_food":"take-away","hotel":"hotelová reštaurácia","buffet":"bufet/veľkokuchyňa","retail":"retail take-away"}[s["cat"]] }</td>'
                    f'<td>{fmt(s["kitchen"])} {"" if s["kind"]=="explicit" else "<small>(≈ z otváracích hodín)</small>"}</td>'
                    f'<td>{fmt(s["arrive"])}–{fmt(s["leave"])}</td><td>{lo}–{hi}</td></tr>')
    return ''.join(rows)

ROUTE_A = route_rows(A); ROUTE_B = route_rows(B, len(A))

def list_rows():
    rows = []
    for b in BUCKETS:
        grp = sorted([e for e in in_buckets if e['bucket'] == b], key=lambda e: (e['kitchen'], e['name']))
        for e in grp:
            src = f'<small>{html.escape(e["src"])}</small>' if e['kind'] == 'explicit' else '<small>odhad: zatvorenie − 30 min</small>' if e['amenity'] == 'restaurant' else '<small>odhad: = zatvorenie</small>'
            web = f' <a href="{html.escape(e["web"])}" rel="noopener">web</a>' if e.get('web') and e['web'].startswith('http') else ''
            rows.append(f'<tr data-b="{b}"><td><span class="sw" style="background:{BCOL[b]}"></span>{b}</td><td><b>{html.escape(e["name"])}</b>{web}</td>'
                        f'<td>{"reštaurácia" if e["amenity"]=="restaurant" else "take-away"}{"" if not e.get("cuisine") else " · " + html.escape(e["cuisine"].replace(";", ", "))}</td>'
                        f'<td>{html.escape(e.get("addr") or "—")}{(" · " + e["pc"]) if e.get("pc") else ""}</td>'
                        f'<td><small>{html.escape(e["oh"])}</small></td><td>{fmt(e["close"])}</td><td><b>{"" if e["kind"]=="explicit" else "≈"}{fmt(e["kitchen"])}</b> {src}</td></tr>')
    return ''.join(rows)
LIST = list_rows()

recv_rows = ''.join(f'<tr><td><b>{html.escape(r["name"])}</b></td><td>{html.escape(r["addr"])}<br><small>poloha: {r["pos"]}</small></td><td>{html.escape(r["hours"])}</td><td>{html.escape(r["food"])}</td><td>{html.escape(r["role"])}</td></tr>' for r in RECV)

n_explicit = sum(1 for e in in_buckets if e['kind'] == 'explicit')
bucket_counts = ''.join(f'<span class="chip"><span class="sw" style="background:{BCOL[b]}"></span>{b}: <b>{cnt[b]}</b></span>' for b in BUCKETS)
legend = ''.join(f'<label class="lg"><input type="checkbox" checked data-b="{b.replace(":", "")}"><span class="sw" style="background:{BCOL[b]}"></span>{b} <small>({cnt[b]})</small></label>' for b in BUCKETS)

CSS = """
:root{--bg:#fbfaf7;--card:#fff;--ink:#1b1b1b;--ink2:#52514e;--mute:#8d8b84;--line:#e6e3dc;--land:#f3f1ea;--water:#cfe3f4;--road:#d8d4ca;--roadmaj:#c4bfb2;--rA:#eb6834;--rB:#4a3aa7;--recv:#e34948;--accent:#0d366b}
@media (prefers-color-scheme: dark){:root:not([data-theme=light]){--bg:#15161a;--card:#1e2026;--ink:#f2f1ec;--ink2:#c3c2b7;--mute:#8d8b84;--line:#2e3138;--land:#23262d;--water:#1f3a55;--road:#3a3e47;--roadmaj:#4b505b;--rA:#f0895c;--rB:#9085e9;--recv:#e66767;--accent:#86b6ef}}
:root[data-theme=dark]{--bg:#15161a;--card:#1e2026;--ink:#f2f1ec;--ink2:#c3c2b7;--mute:#8d8b84;--line:#2e3138;--land:#23262d;--water:#1f3a55;--road:#3a3e47;--roadmaj:#4b505b;--rA:#f0895c;--rB:#9085e9;--recv:#e66767;--accent:#86b6ef}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
[hidden]{display:none!important}
main{max-width:1240px;margin:0 auto;padding:24px 16px 64px}
header h1{font-size:clamp(1.6rem,3.5vw,2.4rem);margin:.2em 0 .2em;letter-spacing:-.01em}
.sub{color:var(--ink2);max-width:70ch}
nav.top{display:flex;gap:14px;flex-wrap:wrap;font-size:.92rem;margin-bottom:18px}nav.top a{color:var(--accent)}
.warn{border-left:4px solid #eda100;background:rgba(237,161,0,.10);padding:10px 14px;border-radius:6px;margin:16px 0}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:18px 0}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}.tile b{display:block;font-size:1.7rem;line-height:1.1}.tile small{color:var(--ink2)}
h2{margin:40px 0 10px;font-size:1.35rem}h3{margin:22px 0 8px;font-size:1.08rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
#map,#map2{width:100%;height:auto;display:block;border-radius:8px}
.land{fill:var(--land)}.water{fill:var(--water);stroke:none}.river{stroke:var(--water);stroke-width:5;fill:none;stroke-linecap:round}
.rail{stroke:var(--mute);stroke-width:1.2;stroke-dasharray:6 4;fill:none}
.rd-ter{stroke:var(--road);stroke-width:1.6;fill:none;stroke-linecap:round}.rd-sec{stroke:var(--road);stroke-width:2.4;fill:none;stroke-linecap:round}.rd-maj{stroke:var(--roadmaj);stroke-width:3.4;fill:none;stroke-linecap:round}
.pt{cursor:pointer}.pt.off{display:none}
.route{fill:none;stroke-width:4;stroke-linejoin:round;stroke-linecap:round;opacity:.9}.rA{stroke:var(--rA)}.rB{stroke:var(--rB)}
.stop circle{stroke:#fff;stroke-width:2}.sA{fill:var(--rA)}.sB{fill:var(--rB)}.stop text{font-size:12px;font-weight:700;fill:#fff}
.recv rect{fill:var(--recv);stroke:#fff;stroke-width:2}.recv text{font-size:12px;font-weight:600;fill:var(--ink);paint-order:stroke;stroke:var(--land);stroke-width:3px}
.lbl{font-size:10.5px;fill:var(--ink2);paint-order:stroke;stroke:var(--land);stroke-width:3px}
.scale line{stroke:var(--ink);stroke-width:2}.scale text{font-size:11px;fill:var(--ink2)}.attr{font-size:10px;fill:var(--mute);text-anchor:end}
.legend{display:flex;gap:10px 16px;flex-wrap:wrap;align-items:center;margin:10px 0;font-size:.92rem}.lg{display:inline-flex;gap:6px;align-items:center;cursor:pointer}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-1px;margin-right:4px}
.key{display:flex;gap:16px;flex-wrap:wrap;font-size:.9rem;color:var(--ink2);margin-top:6px}.key i{display:inline-block;width:22px;height:4px;border-radius:2px;vertical-align:middle;margin-right:6px}
#tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--bg);padding:6px 10px;border-radius:6px;font-size:.85rem;max-width:320px;z-index:9}
table{width:100%;border-collapse:collapse;font-size:.92rem}th,td{padding:7px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--ink2);font-weight:600;position:sticky;top:0;background:var(--card)}
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch}
.hist{width:100%;max-width:960px;height:auto;display:block}.hist .v{font-size:14px;font-weight:700;fill:var(--ink)}.hist .a{font-size:13px;fill:var(--ink2)}.hist .ax{stroke:var(--line);stroke-width:1}
.chip{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:2px 10px;margin:3px 4px 3px 0;font-size:.9rem;background:var(--card)}
.scen{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.scen .tile b{font-size:2rem}
.mark{font-size:.8rem;border-radius:4px;padding:1px 6px;background:rgba(237,161,0,.18)}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}.filters button{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:4px 12px;cursor:pointer}.filters button[aria-pressed=true]{background:var(--accent);color:#fff;border-color:var(--accent)}
footer{margin-top:48px;color:var(--ink2);font-size:.88rem}
@media (max-width:640px){.lbl{display:none}}
"""

JS = """
(function(){
  var tip=document.getElementById('tip');
  function show(e,t){tip.textContent=t;tip.hidden=false;var x=e.clientX+12,y=e.clientY+12;if(x+330>innerWidth)x=e.clientX-330;tip.style.left=x+'px';tip.style.top=y+'px';}
  document.querySelectorAll('[data-tip]').forEach(function(el){
    el.addEventListener('mousemove',function(e){show(e,el.getAttribute('data-tip'));});
    el.addEventListener('mouseleave',function(){tip.hidden=true;});
    el.addEventListener('click',function(e){show(e,el.getAttribute('data-tip'));e.stopPropagation();});
  });
  document.addEventListener('click',function(){tip.hidden=true;});
  document.querySelectorAll('.legend input').forEach(function(cb){cb.addEventListener('change',function(){
    document.querySelectorAll('.pt.b-'+cb.dataset.b).forEach(function(p){p.classList.toggle('off',!cb.checked);});
  });});
  var ctx=document.getElementById('ctx');ctx.addEventListener('change',function(){document.querySelectorAll('.pts-ctx').forEach(function(g){g.style.display=ctx.checked?'':'none';});});
  document.querySelectorAll('.filters button').forEach(function(b){b.addEventListener('click',function(){
    var on=b.getAttribute('aria-pressed')==='true';document.querySelectorAll('.filters button').forEach(function(x){x.setAttribute('aria-pressed','false');});
    if(on){document.querySelectorAll('#lst tr[data-b]').forEach(function(r){r.hidden=false;});return;}
    b.setAttribute('aria-pressed','true');document.querySelectorAll('#lst tr[data-b]').forEach(function(r){r.hidden=r.dataset.b!==b.dataset.b;});
  });});
})();
"""

filters = ''.join(f'<button data-b="{b}" aria-pressed="false"><span class="sw" style="background:{BCOL[b]}"></span>{b} ({cnt[b]})</button>' for b in BUCKETS)

HTML = f"""<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Übrig Bern – mapa zvozu</title>
<meta name="description" content="Reštaurácie v Berne podľa času zatvorenia kuchyne (19:00–22:00), prijímajúce inštitúcie, trasa pre e-cargo bike s dvoma ľuďmi a odhad množstva jedla.">
<style>{CSS}</style>
</head>
<body>
<main>
<nav class="top"><a href="./">← Prehľad situácie</a><a href="financovanie.html">Monetizácia a financovanie</a><a href="../">Übrig Bern</a></nav>
<header>
<h1>Kde a kedy zatvárajú kuchyne v Berne – a ako ich obísť jedným e-cargo bikom</h1>
<p class="sub">Vizuálny podklad k projektu Übrig Bern: {len(est)} podnikov s otváracími hodinami z OpenStreetMap, z toho <b>{len(in_buckets)}</b> s odhadovaným zatvorením kuchyne medzi 19:00 a 22:00, sedem miest, kde sa večer jedáva, a jedna trasa v dvoch etapách. Stav {TODAY}.</p>
</header>

<div class="warn"><b>Ako čítať čísla.</b> Časy sú <b>otváracie hodiny podniku z OpenStreetMap</b> (typický pracovný deň, streda). Kuchyňa zatvára skôr než lokál – kde podnik čas kuchyne neuvádza, počítam <b>zatvorenie − 30 min</b> (take-away: rovnaký čas) a označujem to „≈“. Pri {n_explicit} podnikoch je čas kuchyne prevzatý z webového výskumu z {TODAY} („warme Küche bis …“) – ale <b>ani jeden nebol overený priamo na stránke podniku</b>, sieť ich blokovala. Pred prvou jazdou treba každý čas potvrdiť telefonátom. Trasa je plánovaná vzdušnou čiarou × 1,3 (obchádzky), nie po skutočných uliciach.</div>

<div class="tiles">
<div class="tile"><b>{len(est)}</b><small>podnikov (reštaurácie a take-away) s hodinami v OSM v mapovanom výreze</small></div>
<div class="tile"><b>{len(in_buckets)}</b><small>kuchýň zatvára ≈ 19:00–22:00 (vedrá nižšie)</small></div>
<div class="tile"><b>{len(A) + len(B)}</b><small>zastávok na jednej večernej trase (etapa A + B)</small></div>
<div class="tile"><b>{kmA + kmB:.1f} km</b><small>dĺžka trasy vrátane dvoch odovzdaní (odhad)</small></div>
<div class="tile"><b>{pT[0]}–{pT[2]}</b><small>porcií za večer, stredný odhad {pT[1]} (≈ {pT[1] * KG:.0f} kg)</small></div>
</div>

<h2 id="rozdelenie">1 · Kedy zatvárajú kuchyne</h2>
<div class="card">
{HIST}
<p class="sub">Počet podnikov podľa odhadovaného zatvorenia kuchyne. Tri z piatich podnikov zatvárajú po 22:30 (bary, pizzerie, nočné kuchyne) alebo pred 19:00 (obedové kuchyne, mensy, kaviarne). Pre večerný zvoz je zaujímavý stred: {bucket_counts}</p>
</div>

<h2 id="mapa">2 · Mapa: kuchyne, príjemcovia, trasa</h2>
<div class="card">
<div class="legend"><b>Küche zatvára:</b> {legend} <label class="lg"><input type="checkbox" id="ctx" checked><span class="sw" style="background:#c9c7c0"></span>ostatné podniky (kontext)</label></div>
{SVG}
<h3>Detail Altstadt / Bahnhof – klaster etapy B</h3>
{SVG2}
<div class="key"><span><i style="background:var(--rA)"></i>Etapa A (19:00–20:30 kuchyne → Punkt 6)</span><span><i style="background:var(--rB)"></i>Etapa B (21:00–22:00 kuchyne → Passantenheim)</span><span><span class="sw" style="background:var(--recv)"></span>prijímajúca inštitúcia</span><span>● s čiernym okrajom = čas kuchyne z webu podniku; bez okraja = odhad z otváracích hodín</span></div>
<p class="sub">Prejdi myšou alebo klepni na bod – zobrazí sa názov, čas zatvorenia lokálu a kuchyne. Zaškrtávacími políčkami vypneš vedrá. Číslované body sú zastávky trasy v poradí.</p>
</div>

<h2 id="trasa">3 · Trasa: jeden e-cargo bike, dvaja ľudia, dve etapy</h2>
<p>Dvaja ľudia preto, že jeden ostáva pri bicykli a boxoch, druhý ide do kuchyne, podpíše protokol odovzdania (čas výroby, teplota, alergény, „spotrebovať do“) a naloží. Zastávka tak trvá okolo {STOP_MIN} minút namiesto pätnástich. Rýchlosť plánovaná {SPEED_KMH:g} km/h od dverí k dverám, jazda po každom zatvorení kuchyne v okne {WINDOW} minút (potom personál odchádza).</p>

<h3>Etapa A · skoré kuchyne (19:00–20:30) → Punkt 6, Nägeligasse 3a</h3>
<div class="card tw"><table><thead><tr><th>#</th><th>Podnik</th><th>Typ</th><th>Küche zatvára</th><th>Zastávka</th><th>Porcie (odhad)</th></tr></thead><tbody>{ROUTE_A}
<tr><td>→</td><td><b>Odovzdanie 1: Punkt 6 (PINTO)</b><br><small>otvorené v zime 18:00–22:30; dnes káva a sendviče</small></td><td>drop</td><td>—</td><td>{fmt(arrA)}–{fmt(arrA + DROP_MIN)}</td><td><b>{pA[0]}–{pA[2]}</b> (stred {pA[1]})</td></tr></tbody></table></div>
<p class="sub">Dĺžka etapy A ≈ {kmA:.1f} km. Jedlo z 19:00 kuchyne je pri odovzdaní o {fmt(arrA)} v boxe ≈ {int(arrA - 19*60)} minút – pri predhriatom EPP boxe zostáva nad 60 °C, ale toto je práve hodnota, ktorú musí pilot merať.</p>

<h3>Etapa B · neskoré kuchyne (21:00–22:00) → Passantenheim, Muristrasse 6</h3>
<div class="card tw"><table><thead><tr><th>#</th><th>Podnik</th><th>Typ</th><th>Küche zatvára</th><th>Zastávka</th><th>Porcie (odhad)</th></tr></thead><tbody>{ROUTE_B}
<tr><td>→</td><td><b>Odovzdanie 2: Passantenheim Heilsarmee</b><br><small>posledný vstup 23:00; alternatíva Sleeper (check-in 22:00–01:00, jedlo schladené na ďalší deň)</small></td><td>drop</td><td>—</td><td>{fmt(arrB)}–{fmt(arrB + DROP_MIN)}</td><td><b>{pB[0]}–{pB[2]}</b> (stred {pB[1]})</td></tr></tbody></table></div>
<p class="sub">Dĺžka etapy B ≈ {kmB:.1f} km. Klaster okolo Zeughausgasse/Kornhausplatz (Lötschberg, Bärenhöfli, Ringgenberg, Volkshaus) leží v okruhu ~400 m – to je najhustejší štartovací bod, ktorý sa dá obísť aj pešo s vozíkom.</p>

<h2 id="odhad">4 · Koľko jedla sa dá za večer vyzbierať</h2>
<p>Nikto vo Švajčiarsku nezmeral, koľko porcií večer zostane v bežnej reštaurácii. Odhad preto stojí na troch nepriamych kotvách: Too Good To Go Schweiz predá rádovo <b>1–2 balíčky na partnera a deň</b> (≈ 2,5 mil. jedál / 5 700 partnerov, 2022); United Against Waste meria <b>100–250 g odpadu na hosťa</b>, z čoho väčšina sú zvyšky z tanierov, ktoré sa redistribuovať nedajú; berlínsky RESTLOS Rad vozí na jednu cargo-jazdu <b>≈ 40 kg</b>. Porcia = 350 g jedla, ≈ 0,4 kg s obalom.</p>
<div class="scen">
<div class="tile"><small>Konzervatívne (kuchyne dávajú len to, čo by inak vyhodili dnes)</small><b>{pT[0]} porcií</b><small>≈ {pT[0] * KG:.0f} kg · {pT[0] * 5} porcií týždenne pri 5 večeroch</small></div>
<div class="tile"><small>Stredný odhad (kuchyne porciujú prebytok cielene do GN nádob)</small><b>{pT[1]} porcií</b><small>≈ {pT[1] * KG:.0f} kg · {pT[1] * 5} týždenne · ≈ {pT[1] * 250:,} ročne</small></div>
<div class="tile"><small>Optimisticky (hotelové a bufetové kuchyne naplno, každý deň)</small><b>{pT[2]} porcií</b><small>≈ {pT[2] * KG:.0f} kg · presahuje 3–4 termoboxy → druhá jazda alebo príves</small></div>
</div>
<div class="card tw" style="margin-top:12px"><table><thead><tr><th>Typ podniku</th><th>Porcie/večer konzerv.</th><th>stred</th><th>optim.</th><th>Prečo</th></tr></thead><tbody>
<tr><td>reštaurácia à la carte</td><td>2</td><td>4</td><td>6</td><td>prebytok je nadprodukcia z mise-en-place a nepredané denné menu</td></tr>
<tr><td>take-away / fast food</td><td>2</td><td>3</td><td>4</td><td>malé dávky, často už na Too Good To Go</td></tr>
<tr><td>hotelová reštaurácia</td><td>4</td><td>6</td><td>10</td><td>väčšie kuchyne, banketové zvyšky, Halbpension</td></tr>
<tr><td>bufet / veľkokuchyňa</td><td>6</td><td>10</td><td>15</td><td>bufet sa dopĺňa do zatvorenia; Migros/Manora zatvárajú 17:00–19:00</td></tr>
<tr><td>retail take-away (Coop, Migros…)</td><td>—</td><td>—</td><td>—</td><td>v trase vynechané: koncerny sú už napojené na Tischlein deck dich / Too Good To Go</td></tr>
</tbody></table></div>
<p class="sub">Kapacita bicykla nie je obmedzením: Urban Arrow nesie 125 kg nákladu; obmedzením je objem – tri termoboxy GN 1/1 (≈ 20–25 porcií každý) v korbe = 60–75 porcií na jednu etapu. Obmedzením je ponuka, nie logistika. Preto je prvým výstupom pilotu <b>číslo porcií/večer/podnik</b> – to zatiaľ nikto v CH nemá.</p>

<h2 id="prijemcovia">5 · Kam s jedlom večer</h2>
<div class="card tw"><table><thead><tr><th>Inštitúcia</th><th>Adresa</th><th>Večerný režim</th><th>Jedlo dnes</th><th>Rola v trase</th></tr></thead><tbody>{recv_rows}</tbody></table></div>
<p class="sub">Všetky údaje zo snippetov vyhľadávača ({TODAY}), pred plánovaním potvrdiť telefonicky: Sleeper 031 301 64 04, Passantenheim 031 351 80 27, Punkt 6 031 321 76 38. Otvorená otázka pre Punkt 6: má oprávnenie podávať teplé jedlo (Lebensmittelbetrieb)?</p>

<h2 id="zoznam">6 · Zoznam podnikov podľa zatvorenia kuchyne (19:00–22:00)</h2>
<div class="filters">{filters}</div>
<div class="card tw" style="max-height:70vh;overflow:auto"><table id="lst"><thead><tr><th>Vedro</th><th>Podnik</th><th>Typ</th><th>Adresa (OSM)</th><th>Otváracie hodiny (OSM)</th><th>Lokál zatvára (St)</th><th>Küche zatvára</th></tr></thead><tbody>{LIST}</tbody></table></div>
<p class="sub">Podniky bez adresy v OSM majú súradnice, ale nie ulicu – na mape sú správne, v tabuľke chýba text. Chýbajúce podniky (napr. Lokal Bern, Hotel Savoy Bistro) nemajú v OSM otváracie hodiny, preto tu nie sú.</p>

<h2 id="metoda">7 · Metóda a predpoklady</h2>
<ul>
<li><b>Dáta:</b> Overpass API (zrkadlo overpass.kumi.systems), {TODAY}, výrez 46.925–46.985 N / 7.385–7.500 E; 814 gastro objektov, 666 s otváracími hodinami, 644 parsovateľných. Na mape je výrez centra ({len(est)} reštaurácií a take-away).</li>
<li><b>Deň:</b> streda (typický pracovný večer). Piatok a sobota zatvárajú neskôr, nedeľa skôr – rozdelenie sa posúva o 30–60 min.</li>
<li><b>Kuchyňa vs. lokál:</b> −30 min pre reštaurácie, 0 pre take-away. Kde webový výskum našiel „warme Küche bis“, platí ten čas ({n_explicit} podnikov, čierny okraj).</li>
<li><b>Trasa:</b> kandidáti v okruhu {RADIUS/1000:g} km od Zytglogge (bez retailových take-away); hladný algoritmus s časovými oknami (zastávka možná od zatvorenia kuchyne do +{WINDOW} min), rýchlosť {SPEED_KMH:g} km/h, vzdušná vzdialenosť × {DETOUR}, {STOP_MIN} min na zastávku, {DROP_MIN} min na odovzdanie; preferuje podniky s doloženým časom kuchyne a hotelové/bufetové kuchyne.</li>
<li><b>Bezpečnosť potravín:</b> BLV-Spendenleitfaden 2021 – odovzdať ≥ 60 °C alebo schladiť pod 10 °C do 2 h; obe strany sú Lebensmittelbetrieb. Číselné prahy HyV sa v tomto behu nedali overiť na fedlex.</li>
<li><b>Čo nie je zohľadnené:</b> kopce (Altstadt → Kirchenfeld cez most, Länggasse hore), skutočná cestná sieť, zákazy vjazdu v Altstadt, počasie, ochota podnikov.</li>
</ul>
<footer>Übrig Bern · výskumný podklad, nie právne ani prevádzkové poradenstvo · mapové dáta © prispievatelia OpenStreetMap, licencia ODbL · vygenerované skriptom <code>research/build_map.py</code> {TODAY}</footer>
</main>
<div id="tip" hidden></div>
<script>{JS}</script>
</body>
</html>
"""
open(OUT, 'w', encoding='utf-8').write(HTML)
print('written', OUT, len(HTML.encode()) // 1024, 'kB')
