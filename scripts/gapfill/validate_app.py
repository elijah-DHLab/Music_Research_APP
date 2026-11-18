"""Standing checks on the data embedded in index.html. Exit 1 if a blocking check fails.
Usage: python validate_app.py            (run after every rebuild of index.html / data/v2/runtime)

Blocking:
  1. no entity labelled VIAF and no performance linked to a rejected Wikidata item (REJECT_QID in wikidata_enrich.py)
  2. no two performances with the same title that both credit Ness (the split fixed on 2026-11-18)
  3. no entity whose label is two other credited artists joined by " - " (compound credit)
  4. no (source, date, track) with more than one row
  5. every Spotify day has 200 chart rows and every YouTube week 100, counting rows merged by check 4 and
     rows listed in data/unresolved_rows.csv
Report only (known backlog, see CHANGELOG.md):
  6. Spotify URIs / YouTube ids shared by more than one performance_id
"""
import collections, csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
FULL = {0: 200, 1: 100, 2: 100}; SRC = {'spotify_daily': 0, 'youtube_tracks_weekly': 1, 'youtube_videos_weekly': 2}


def reject_qids():
    src = open(os.path.join(HERE, 'wikidata_enrich.py'), encoding='utf-8').read()
    m = re.search(r'REJECT_QID\s*=\s*\{([^}]*)\}', src)
    return set(re.findall(r"'(Q\d+)'", m.group(1))) if m else set()


def main():
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    o, _ = json.JSONDecoder().raw_decode(html[html.index('window.WM_DATA=') + 15:])
    V, _ = json.JSONDecoder().raw_decode(html[html.index('window.WM_V21=') + 14:])
    E, P, T, D = V['entities'], V['performances'], o['tracks'], o['dates']; C = {c: k for k, c in enumerate(o['cols'])}
    fails, notes = [], []
    ok = lambda name, bad, show=5: (fails.append(f'{name}: {len(bad)} -> {list(bad)[:show]}') if bad else print(f'OK   {name}'))

    rej = {'wd:' + q for q in reject_qids()}
    ok('1 VIAF / rejected Wikidata items', [k for k, e in E.items() if 'VIAF' in (e.get('he'), e.get('display'))] +
       [pid for pid, p in P.items() if set(p['artists']) & rej])

    ness = {k for k, e in E.items() if e.get('wikidata') == 'Q118289471'}
    by_title = collections.Counter(p['title'] for p in P.values() if set(p['artists']) & ness)
    ok('2 split Ness & Stilla performances', [t for t, n in by_title.items() if n > 1])

    alias = collections.defaultdict(set)
    for k, e in E.items():
        for a in [e.get('he'), e.get('en')] + list(e.get('aliases') or []):
            if a: alias[a.strip().lower()].add(k)
    credited = {a for p in P.values() for a in p['artists']}
    compound = []
    for k, e in E.items():
        if k not in credited: continue
        parts = [x.strip().lower() for x in re.split(r'\s+-\s+', e.get('display') or '') if x.strip()]
        if len(parts) == 2 and all(alias.get(x, set()) - {k} for x in parts) and alias[parts[0]] - {k} != alias[parts[1]] - {k}:
            compound.append(f"{k} {e['display']}")
    ok('3 compound credit entities', compound)

    c = collections.Counter(zip(o['s'], o['d'], o['t']))
    ok('4 duplicate (source, date, track) rows', [(s, D[d], T[t][0]) for (s, d, t), n in c.items() if n > 1])

    rows = collections.Counter(zip(o['s'], (D[d] for d in o['d'])))
    for s_, day, _pid, ranks, _v in o['qa'].get('merged_duplicate_rows', []): rows[(s_, day)] += len(ranks) - 1
    up = os.path.join(ROOT, 'data', 'unresolved_rows.csv')
    if os.path.exists(up):
        for r in csv.DictReader(open(up, encoding='utf-8-sig')):
            if r['in_app'] == 'no': rows[(SRC[r['source']], r['date'])] += 1
    ok('5 full charts (200 Spotify / 100 YouTube rows)', [(s, d, n) for (s, d), n in sorted(rows.items()) if n != FULL[s]])

    ids = collections.defaultdict(set)
    for t in T:
        for x in (t[C['uri']] + ' ' + t[C['yt']]).split(): ids[x].add(t[C['performance_id']])
    shared = {k: v for k, v in ids.items() if len(v) > 1}
    print(f'INFO 6 platform ids shared by more than one performance_id: {len(shared)} (backlog; not blocking)')
    print(f'INFO observations {len(o["t"])}, tracks {len(T)}, Spotify days {len({d for s, d in rows if s == 0})}, '
          f'YouTube weeks {len({d for s, d in rows if s == 1})}/{len({d for s, d in rows if s == 2})}')
    for f in fails: print('FAIL', f)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
