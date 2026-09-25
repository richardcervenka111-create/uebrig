import json,re,collections
DAYS=['mo','tu','we','th','fr','sa','su']
def norm(s):
    s=s.lower().replace('–','-').replace('—','-').replace('uhr','')
    s=re.sub(r'(\d)h(?=[\s,;:-]|$)',r'\1:00',s)
    s=re.sub(r'(\d{1,2})[.:](\d{2})',lambda m:f"{int(m.group(1)):02d}:{m.group(2)}",s)
    s=re.sub(r'(?<![\d:])(\d{1,2})(?![\d:])',lambda m:f"{int(m.group(1)):02d}:00",s)  # bare hours
    return s
def parse_day_close(oh, day='we'):
    """return latest closing minute-of-day for given weekday, or None; 'off' -> -1 ; unparsable -> None"""
    s=norm(oh)
    # drop seasonal/month prefixes crudely
    s=re.sub(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(\s+\d+)?(\s*-\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(\s+\d+)?)?\s*','',s)
    s=s.replace('ph off','').replace('ph','')
    rules=[r.strip() for r in re.split(r'[;|]',s) if r.strip()]
    result=None; found=False
    for r in rules:
        m=re.match(r'^((?:(?:mo|tu|we|th|fr|sa|su)(?:\s*-\s*(?:mo|tu|we|th|fr|sa|su))?\s*,?\s*)+)\s*(.*)$',r)
        if m:
            dayspec=m.group(1); rest=m.group(2).strip()
            days=set()
            for part in re.findall(r'(mo|tu|we|th|fr|sa|su)(?:\s*-\s*(mo|tu|we|th|fr|sa|su))?',dayspec):
                a=DAYS.index(part[0]); b=DAYS.index(part[1]) if part[1] else a
                if b<a: b+=7
                for i in range(a,b+1): days.add(DAYS[i%7])
        else:
            days=set(DAYS); rest=r.strip()
        if day not in days: continue
        found=True
        if rest.startswith('off') or rest.startswith('closed') or rest=='':
            if rest.startswith('off') or rest.startswith('closed'): result=-1; continue
        if '24/7' in rest: result=24*60; continue
        ends=[]
        for a,b in re.findall(r'(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})',rest):
            h,mn=map(int,b.split(':')); e=h*60+mn
            h0,m0=map(int,a.split(':')); st=h0*60+m0
            if e<=st: e+=24*60
            ends.append(e)
        if ends: result=max(ends)
    return result if found else None
if __name__=='__main__':
    d=json.load(open('bern_gastro.json'))['elements']
    out=[]; unp=0; buckets=collections.Counter()
    for e in d:
        t=e.get('tags',{})
        if 'opening_hours' not in t: continue
        lat=e.get('lat') or e.get('center',{}).get('lat'); lon=e.get('lon') or e.get('center',{}).get('lon')
        c=parse_day_close(t['opening_hours'])
        if c is None: unp+=1; continue
        out.append({'id':e['id'],'name':t.get('name'),'amenity':t.get('amenity'),'cuisine':t.get('cuisine'),'oh':t.get('opening_hours'),'close':c,'lat':lat,'lon':lon,
                    'addr':' '.join(x for x in [t.get('addr:street'),t.get('addr:housenumber')] if x) or None,'pc':t.get('addr:postcode'),'web':t.get('website') or t.get('contact:website'),'wheelchair':t.get('wheelchair')})
        if c==-1: buckets['off']+=1
        elif c<19*60: buckets['<19']+=1
        elif c>=23*60+30: buckets['>=23:30']+=1
        else: buckets[f"{c//60:02d}:{c%60:02d}"]+=1
    print('parsed',len(out),'unparsable',unp); print(sorted(buckets.items()))
    json.dump(out,open('gastro_parsed.json','w'),ensure_ascii=False)
    # show unparsable samples
    n=0
    for e in d:
        t=e.get('tags',{})
        if 'opening_hours' in t and parse_day_close(t['opening_hours']) is None and n<15: print('  UNP:',t.get('name'),'|',t['opening_hours']); n+=1
