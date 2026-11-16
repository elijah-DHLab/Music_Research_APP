"""Apply wikidata_enrich.json to (1) the V2 master performers sheet and (2) the app (index.html: WM_V21 entities,
performances, track metadata columns).

Performers sheet: new performers get metadata; column metadata_status = copied_from_existing (same Wikidata id
already in sheet) / wikidata_auto / not_found.
App: resolved performers become V21 entities 'wd:<QID>' (or an alias of an existing entity with that QID);
gap-fill tracks still unmatched are re-linked; gap-fill tracks without metadata get the lead performer's metadata
(from the performers sheet, by Wikidata id or name).
Usage: python apply_performers.py
"""
import collections, json, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from link_new_tracks import nk, artists
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
MASTER = os.path.join(HERE, 'v2', 'all_works_and_performers_master_list_with_ids_V2.xlsx')
META_COLS = ['wikidata_id', 'wikidata_url', 'entity_type', 'wikidata_description', 'gender', 'birth_or_inception_year', 'death_year',
             'birth_or_origin_country', 'birth_or_formation_city', 'citizenship', 'genres', 'hewiki_title']

def app_meta(r):  # same mapping as build_data.enrich()
    b = str(r['birth_or_inception_year']).split('.')[0]
    return {'gender': r['gender'], 'country': r['birth_or_origin_country'], 'genre': r['genres'].split(' | ')[0], 'city': r['birth_or_formation_city'],
            'ent': r['entity_type'], 'dec': (str(int(b) // 10 * 10) + 's') if b.isdigit() else '', 'genres': r['genres'], 'birth': b if b.isdigit() else '',
            'desc': r['wikidata_description']}

def main():
    cache = json.load(open(os.path.join(HERE, 'wikidata_enrich.json'), encoding='utf-8'))
    W = pd.read_excel(MASTER, sheet_name=0, dtype=str).fillna(''); P = pd.read_excel(MASTER, sheet_name='performers', dtype=str).fillna('')
    if 'metadata_status' not in P: P['metadata_status'] = ''
    by_wd = {r.wikidata_id: r for _, r in P[(P.gapfill_status != 'new') & (P.wikidata_id != '')].iterrows()}
    st = collections.Counter()
    # same performer under another spelling: hewiki title of an existing performer, or an alias of an app entity with a QID
    html0 = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read(); j = html0.index('window.WM_V21=') + 14
    V0, _ = json.JSONDecoder().raw_decode(html0[j:]); alias_wd = {}
    for e in V0['entities'].values():
        for s in [e.get('he'), e.get('en'), e.get('display')] + list(e.get('aliases') or []):
            if s and e.get('wikidata'): alias_wd.setdefault(nk(s), e['wikidata'])
    for q, r in by_wd.items():
        if r.hewiki_title: alias_wd.setdefault(nk(r.hewiki_title), q)
        alias_wd.setdefault(nk(r.performer_name), q)
    for k, r in P[P.gapfill_status == 'new'].iterrows():
        v = cache.get(r.performer_name, {}); q = v.get('qid') or alias_wd.get(nk(r.performer_name))
        if q and not v.get('qid'): cache.setdefault(r.performer_name, {})['qid'] = q
        if q and q in by_wd:
            for c in META_COLS: P.at[k, c] = by_wd[q][c]
            P.at[k, 'metadata_status'] = 'copied_from_existing'
        elif q and v.get('meta'):
            for c in META_COLS: P.at[k, c] = v['meta'][c]
            P.at[k, 'metadata_status'] = 'wikidata_auto'
        else: P.at[k, 'metadata_status'] = 'not_found'
        st['sheet_' + P.at[k, 'metadata_status']] += 1
    with pd.ExcelWriter(MASTER) as xw:
        W.to_excel(xw, sheet_name='all_works_and_performers_master', index=False); P.to_excel(xw, sheet_name='performers', index=False)

    # ---------- app ----------
    path = os.path.join(ROOT, 'index.html'); html = open(path, encoding='utf-8').read()
    j0 = html.index('window.WM_V21=') + 14; V, m = json.JSONDecoder().raw_decode(html[j0:])
    i0 = html.index('window.WM_DATA=') + 15; o, n = json.JSONDecoder().raw_decode(html[i0:])
    C = {c: k for k, c in enumerate(o['cols'])}; T = o['tracks']; E = V['entities']
    ent_by_wd = {e['wikidata']: eid for eid, e in E.items() if e.get('wikidata')}
    for name, v in cache.items():
        q = v.get('qid'); mt = v.get('meta') or {}
        if not q: continue
        eid = ent_by_wd.get(q)
        if eid:
            if name not in E[eid]['aliases']: E[eid]['aliases'].append(name); st['app_alias_added'] += 1
        else:
            he, en = mt.get('label_he', ''), mt.get('label_en', '')
            eid = 'wd:' + q; ent_by_wd[q] = eid
            E[eid] = {'he': he, 'en': en or name, 'display': he or en or name, 'aliases': list(dict.fromkeys(x for x in (name, he, en) if x)),
                      'kind': 'person' if mt.get('entity_type') == 'אדם' else 'ensemble', 'wikidata': q, 'status': 'gapfill_wikidata_auto'}
            st['app_entity_added'] += 1
    alias = {}
    for eid, e in E.items():
        for s in [e.get('he'), e.get('en'), e.get('display')] + list(e.get('aliases') or []):
            if s: alias.setdefault(nk(s), eid)
    # entity -> metadata from performers sheet (wikidata id first, then name)
    meta_by_ent = {}
    Pm = P[(P.gender != '') | (P.genres != '') | (P.birth_or_origin_country != '')]
    for _, r in Pm.iterrows():
        eid = ent_by_wd.get(r.wikidata_id) or alias.get(nk(r.performer_name))
        if eid: meta_by_ent.setdefault(eid, app_meta(r))
    def ents(raw):
        out = []
        for p in artists(raw):
            for part in [p] + [x.strip() for x in re.split(r'\s[-–]\s', p)]:
                e = alias.get(nk(part))
                if e and e not in out: out.append(e); break
        return out
    for t in T:
        sid = t[C['identity_status']]
        if not sid.startswith('gapfill'): continue
        pid = t[C['performance_id']]
        if sid == 'gapfill_unmatched':
            es = ents(t[C['artist']])
            if es:
                V['performances'][pid] = {'he': '', 'en': '', 'title': t[C['name']], 'artists': es, 'fallback_artist': t[C['artist']], 'aliases': [t[C['name']]], 'work_id': ''}
                t[C['identity_status']] = 'gapfill_artist_linked'; t[C['collab']] = 'שיתוף פעולה' if len(es) > 1 or ',' in t[C['artist']] else 'סולו'
                st['app_relinked'] += 1
        p = V['performances'].get(pid)
        if p and p.get('artists') and not any(t[C[c]] for c in ('gender', 'country', 'genre')):
            mt = meta_by_ent.get(p['artists'][0])
            if mt:
                for c, val in mt.items(): t[C[c]] = val
                st['app_track_meta_filled'] += 1
    html = html[:j0] + json.dumps(V, ensure_ascii=False, separators=(',', ':')) + html[j0 + m:]
    i0 = html.index('window.WM_DATA=') + 15; _, n = json.JSONDecoder().raw_decode(html[i0:])
    html = html[:i0] + json.dumps(o, ensure_ascii=False, separators=(',', ':')) + html[i0 + n:]
    open(path, 'w', encoding='utf-8', newline='').write(html)
    print(dict(st), 'still unmatched', sum(1 for t in T if t[C['identity_status']] == 'gapfill_unmatched'))

if __name__ == '__main__':
    main()
