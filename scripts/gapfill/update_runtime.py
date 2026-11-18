"""Regenerate the data/v2/runtime companion files and data/recordings.csv from the gap-filled index.html.
Usage: python update_runtime.py
Rewrites: runtime/coverage.json, runtime/periods.json, runtime/performances.json (appends new), runtime/manifest.json,
          runtime/names_v21.json/.js (= embedded WM_V21), data/recordings.csv (append new performances).
"""
import collections, csv, datetime as dt, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..'); RT = os.path.join(ROOT, 'data', 'v2', 'runtime')
SID = {0: ('spotify_daily', 'streams', 200), 1: ('youtube_tracks_weekly', 'views', 100), 2: ('youtube_videos_weekly', 'views', 100)}
dump = lambda p, o: json.dump(o, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=None, separators=(',', ':'))

html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
i = html.index('window.WM_DATA=') + 15; o, _ = json.JSONDecoder().raw_decode(html[i:])
j = html.index('window.WM_V21=') + 14; V, _ = json.JSONDecoder().raw_decode(html[j:])
D = o['dates']; T = o['tracks']; C = {c: k for k, c in enumerate(o['cols'])}
by = collections.defaultdict(list)
for d, r, t, v, s in zip(o['d'], o['r'], o['t'], o['v'], o['s']): by[(s, D[d])].append((r, t, v))

# coverage.json: one row per source period. Rows merged by fix_identities_2026_11_18 (same track twice in one
# chart) still count as source chart rows; rows the source left untitled are listed in data/unresolved_rows.csv.
merged = collections.Counter()
for s_, day, _pid, ranks, _vals in o['qa'].get('merged_duplicate_rows', []): merged[(s_, day)] += len(ranks) - 1
cov = []
for (s, day), rows in sorted(by.items(), key=lambda x: (x[0][0], x[0][1])):
    n = len(rows) + merged[(s, day)]; full = SID[s][2]
    cov.append({'source_id': SID[s][0], 'period_end_date': day, 'observed_chart_rows': str(n), 'rank_1_rows': str(sum(1 for r in rows if r[0] == 1)),
                'coverage_status': 'observed' if n == full else f'observed_partial_{n}_of_{full}',
                'interpretation': 'zero appearances may be inferred only within a measured chart for rank-based analyses'})
dump(os.path.join(RT, 'coverage.json'), cov)

# periods.json: Thursday-ending weeks; spotify days aggregated into the week (Fri..Thu)
agg = collections.defaultdict(lambda: {'rows': [], 'periods': set()})
for (s, day), rows in by.items():
    d = dt.date.fromisoformat(day); wk = d + dt.timedelta(days=(3 - d.weekday()) % 7)
    a = agg[(str(wk), s)]; a['rows'] += rows; a['periods'].add(day)
per = []
for (wk, s), a in sorted(agg.items()):
    rows = a['rows']; tot = sum(r[2] for r in rows); t20 = sum(r[2] for r in rows if r[0] <= 20)
    per.append({'week_end': wk, 'source_id': SID[s][0], 'observations': len(rows), 'source_periods': len(a['periods']),
                'mean_chart_positions': round(len(rows) / len(a['periods']), 1), 'sum_source_measure': tot, 'top20_source_measure': t20,
                'top20_share_percent': round(100 * t20 / tot, 4) if tot else None, 'unique_performances': len({r[1] for r in rows}), 'unit': SID[s][1]})
dump(os.path.join(RT, 'periods.json'), per)

# performances: append gap-fill performances
pf = [p for p in json.load(open(os.path.join(RT, 'performances.json'), encoding='utf-8')) if not p['id'].startswith('PERF_GF_')]; have = {p['id'] for p in pf}; added = []  # idempotent
for t in T:
    pid = t[C['performance_id']]
    if pid in have or not t[C['identity_status']].startswith('gapfill'): continue
    vp = V['performances'].get(pid, {})
    rec = {'id': pid, 'title': t[C['name']], 'artists': t[C['artist']], 'review': t[C['review_status']], 'language': t[C['lang']] or None,
           'genre': t[C['genre']] or None, 'identity': t[C['identity_status']], 'work_id': vp.get('work_id') or None, 'entities': vp.get('artists', [])}
    pf.append(rec); added.append(rec); have.add(pid)
dump(os.path.join(RT, 'performances.json'), pf)

rec_path = os.path.join(ROOT, 'data', 'recordings.csv')
keep = [r for r in csv.reader(open(rec_path, encoding='utf-8-sig')) if not r[0].startswith('PERF_GF_')]
with open(rec_path, 'w', newline='', encoding='utf-8-sig') as fh:
    w = csv.writer(fh); w.writerows(keep)
    for r in added: w.writerow([r['id'], r['title'], r['artists'], '', 'unspecified', r['identity'], 1, r['review'], '', '', ''])

m = json.load(open(os.path.join(RT, 'manifest.json'), encoding='utf-8'))
m['build_type'] = 'validated_snapshot_with_gapfill_2026_11_16_fix_2026_11_18'
m['summary'].update(observations=len(o['t']), performances=len(pf), periods=len(per))
m['data_policy']['identity_status'] = 'provisional; gap-fill performances flagged gapfill_artist_linked / gapfill_unmatched'
m['notes'] = ['Gap-fill 2026-11-16: 502 missing Spotify days and 41 YouTube weeks refetched from source (charts.spotify.com, charts.youtube.com).',
              'The 40 repeated 2023-01-05..2023-10-05 YouTube weeks were replaced by the true weekly charts; no suspect rows remain.',
              'Coverage: Spotify 2023-01-01..2026-11-14 (1,414 days); YouTube 2023-01-05..2026-11-12 (202 weeks).',
              'Untitled rows (removed videos / unnamed tracks) are omitted, as before; see coverage.json observed_partial_*.',
              'runtime/weeks/*.json week-detail files are not part of this APP package.',
              'Fix 2026-11-18: wrong Wikidata links corrected (V, Static, Ness, Stilla, Black Sabbath, Forever Tel-Aviv), duplicate entities merged, '
              'split Ness & Stilla performances merged, same-track duplicate chart rows merged (qa.merged_duplicate_rows), '
              'Spotify 2026-07-13..18 unnamed row identified; unidentifiable rows in data/unresolved_rows.csv.']
dump(os.path.join(RT, 'manifest.json'), m)
ej = [e for e in json.load(open(os.path.join(RT, 'entities.json'), encoding='utf-8')) if not str(e.get('review', '')).startswith('gapfill')]
have_e = {e['id'] for e in ej}
for eid, e in V['entities'].items():
    if e.get('status') == 'gapfill_wikidata_auto' and eid not in have_e:
        ej.append({'id': eid, 'name': e.get('display') or e.get('en'), 'kind': e.get('kind'), 'review': 'gapfill_wikidata_auto', 'genres_source': ''})
dump(os.path.join(RT, 'entities.json'), ej)
dump(os.path.join(RT, 'names_v21.json'), V)
open(os.path.join(RT, 'names_v21.js'), 'w', encoding='utf-8').write('window.WM_V21=' + json.dumps(V, ensure_ascii=False, separators=(',', ':')) + ';')
print('coverage', len(cov), 'periods', len(per), 'performances', len(pf), f'(+{len(added)})')
