"""Resolve new performers (performers sheet, gapfill_status == 'new') on Wikidata and fill the metadata columns
in the same conventions as the existing sheet (Hebrew labels, fallback English).

Acceptance rule (conservative): the performer name must equal (normalized) a label/alias of the candidate in
he/en/ar, AND the candidate is a human with a music occupation, or a musical group/ensemble.
If the resolved Wikidata id already exists in the sheet, the existing performer's metadata is copied verbatim.
Output: wikidata_enrich.json (cache + results). Usage: python wikidata_enrich.py
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from link_new_tracks import nk
HERE = os.path.dirname(os.path.abspath(__file__)); API = 'https://www.wikidata.org/w/api.php'
UA = {'User-Agent': 'MusicChartsResearchGapfill/1.0 (academic research script; python-urllib)'}
CACHE = os.path.join(HERE, 'wikidata_enrich.json')
MUSIC_OCC = {'Q177220', 'Q639669', 'Q488205', 'Q2252262', 'Q36834', 'Q130857', 'Q183945', 'Q855091', 'Q486748', 'Q753110', 'Q158852',
             'Q1259917', 'Q2865819', 'Q1198887', 'Q386854', 'Q584301', 'Q806349', 'Q1075651', 'Q9648008', 'Q12800682', 'Q3089940', 'Q15981151', 'Q1028181'}
GROUPS = {'Q215380', 'Q5741069', 'Q9212979', 'Q216337', 'Q641066', 'Q42998', 'Q131186', 'Q2088357', 'Q281643', 'Q1781010', 'Q2981998', 'Q56816954',
          'Q11225966', 'Q188451', 'Q18127', 'Q1542343', 'Q19464263', 'Q1323584'}

def get(params):
    params = dict(params, format='json'); url = API + '?' + urllib.parse.urlencode(params)
    for k in range(8):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40)); time.sleep(1.0); return r
        except urllib.error.HTTPError as e:
            wait = int(e.headers.get('Retry-After') or 0) or 30 * (k + 1); print(f'  HTTP {e.code}, waiting {wait}s'); time.sleep(wait)
        except Exception:
            time.sleep(10 * (k + 1))
    raise RuntimeError('wikidata unreachable')

def entities(ids, props='labels|descriptions|aliases|claims|sitelinks'):
    out = {}
    ids = [i for i in dict.fromkeys(ids) if i]
    for k in range(0, len(ids), 50):
        out.update(get({'action': 'wbgetentities', 'ids': '|'.join(ids[k:k + 50]), 'props': props, 'languages': 'he|en|ar|mul', 'sitefilter': 'hewiki'}).get('entities', {}))
    return out

claim = lambda e, p: [c['mainsnak'].get('datavalue', {}).get('value') for c in e.get('claims', {}).get(p, []) if c['mainsnak'].get('datavalue')]
qids = lambda e, p: [v['id'] for v in claim(e, p) if isinstance(v, dict) and 'id' in v]
def current(e, p):  # preferred-rank claim, else one without an end time (P582), else the last one
    cs = [c for c in e.get('claims', {}).get(p, []) if c['mainsnak'].get('datavalue')]
    pick = [c for c in cs if c.get('rank') == 'preferred'] or [c for c in cs if 'P582' not in c.get('qualifiers', {})] or cs[-1:]
    return [c['mainsnak']['datavalue']['value']['id'] for c in pick[:1]]
# manual review 2026-11-16: wrong or doubtful automatic matches
REJECT = {'Claude', 'La Mosca', 'Hiroshima', 'Seven Music', 'DNDM'}
def year(e, p):
    for v in claim(e, p):
        m = re.match(r'[+-](\d{4})', v.get('time', '')) if isinstance(v, dict) else None
        if m: return m.group(1)
    return ''
lab = lambda e, lang=('he', 'en', 'mul'): next((e.get('labels', {})[l]['value'] for l in lang if l in e.get('labels', {})), '')
desc = lambda e: next((e.get('descriptions', {})[l]['value'] for l in ('he', 'en') if l in e.get('descriptions', {})), '')

def names_of(e):
    s = {v['value'] for v in e.get('labels', {}).values()}
    for al in e.get('aliases', {}).values(): s |= {a['value'] for a in al}
    return {nk(x) for x in s}

def candidates(name):
    parts = [name] + [p.strip() for p in re.split(r'\s*\|\s*|\s+-\s+', name) if p.strip() and p.strip() != name]
    parts = [re.sub(r'\s*(הערוץ הרשמי|official)\s*$', '', p, flags=re.I) for p in parts]
    found = []
    for p in dict.fromkeys(parts):
        lang = 'he' if re.search('[֐-׿]', p) else 'ar' if re.search('[؀-ۿ]', p) else 'en'
        r = get({'action': 'wbsearchentities', 'search': p, 'language': lang, 'uselang': lang, 'limit': 7, 'type': 'item'})
        found += [x['id'] for x in r.get('search', [])]
    return list(dict.fromkeys(found)), {nk(p) for p in parts}

def main():
    P = pd.read_excel(os.path.join(HERE, 'v2', 'all_works_and_performers_master_list_with_ids_V2.xlsx'), sheet_name='performers', dtype=str).fillna('')
    new = P[P.gapfill_status == 'new'].performer_name.tolist(); known_wd = set(P.wikidata_id) - {''}
    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    for n, name in enumerate(new, 1):  # phase 1: searches (cached)
        if name in cache and 'cands' in cache[name]: continue
        cands, keys = candidates(name); cache[name] = {'cands': cands, 'keys': sorted(keys)}
        if n % 10 == 0: print(f'searched {n}/{len(new)}'); json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    E = entities(sorted({q for v in cache.values() for q in v['cands']}), 'labels|aliases|claims')  # phase 2: one batched fetch
    for name, v in cache.items():
        v['qid'] = None
        for q in v['cands']:
            e = E.get(q, {})
            if not (names_of(e) & set(v['keys'])): continue
            p31 = set(qids(e, 'P31')); occ = set(qids(e, 'P106'))
            if name in REJECT: break
            if ('Q5' in p31 and occ & MUSIC_OCC) or (p31 & GROUPS) or (q in known_wd): v['qid'] = q; break
    # resolve metadata for picked ids
    picked = {v['qid'] for v in cache.values() if v.get('qid')}
    E = entities(sorted(picked))
    places = {q for e in E.values() for p in ('P19', 'P740') for q in qids(e, p)}
    PL = entities(sorted(places), 'labels|claims')
    refs = {q for e in E.values() for p in ('P21', 'P27', 'P495', 'P136') for q in qids(e, p)} | {q for e in PL.values() for q in current(e, 'P17')}
    L = entities(sorted(refs), 'labels')
    L.update(PL)
    for name, v in cache.items():
        q = v.get('qid')
        if not q or q not in E: continue
        e = E[q]; human = 'Q5' in qids(e, 'P31')
        place = (qids(e, 'P19') if human else qids(e, 'P740'))[:1]
        country = ((current(PL.get(place[0], {}), 'P17') if place else []) or current(e, 'P27')) if human else (current(e, 'P495') or (current(PL.get(place[0], {}), 'P17') if place else []))
        v['meta'] = {'wikidata_id': q, 'wikidata_url': 'https://www.wikidata.org/wiki/' + q, 'entity_type': 'אדם' if human else 'להקה / הרכב',
                     'wikidata_description': desc(e), 'gender': {'Q6581097': 'זכר', 'Q6581072': 'נקבה'}.get((qids(e, 'P21') or [''])[0], ''),
                     'birth_or_inception_year': year(e, 'P569' if human else 'P571'), 'death_year': year(e, 'P570') if human else year(e, 'P576'),
                     'birth_or_origin_country': lab(L.get(country[0], {})) if country else '', 'birth_or_formation_city': lab(L.get(place[0], {})) if place else '',
                     'citizenship': lab(L.get((current(e, 'P27') or [''])[0], {})) if human else '',
                     'genres': ' | '.join(x for x in (lab(L.get(g, {})) for g in qids(e, 'P136')[:4]) if x),
                     'hewiki_title': e.get('sitelinks', {}).get('hewiki', {}).get('title', ''), 'label_he': lab(e, ('he',)), 'label_en': lab(e, ('en', 'mul'))}
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('resolved', sum(1 for v in cache.values() if v.get('qid')), 'of', len(cache))

if __name__ == '__main__':
    main()
