"""Patch the embedded window.WM_DATA in index.html with the gap-filled V2 observations.

Why not build_data.py: the embedded dataset carries V2.1 identity columns (performance_id, work_id, review status)
that build_data.py does not produce. This script keeps every existing track row and observation, and:
  * maps platform ids (Spotify uri / YouTube video id) to existing track indexes by joining the ORIGINAL raw Drive
    rows with the existing observations on (source, date, rank, value);
  * deletes observations of periods that were replaced (YouTube suspect 2023 weeks, tie-corrected weeks);
  * appends observations of added/corrected periods; ids never seen before become new track rows flagged
    identity_status='gapfill_new_unmatched', review_status='unreviewed';
  * rebuilds the date index and qa block.
Usage: python update_app_data.py [--v2 v2] [--raw raw] [--html ../../index.html]
"""
import argparse, collections, hashlib, json, os, re, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = [(0, 'Spotify-all_israel_charts', 'chart_date', 'streams', 'uri', 'track_name', 'peak_rank', 'days_on_chart'),
       (1, 'all_israel_youtube_charts_2023_to_today-TRACKS', 'end_date', 'views', 'youtube_url', 'track_name', None, 'weeks_on_chart'),
       (2, 'all_israel_youtube_videos_2023_to_today-VIDEOS', 'end_date', 'views', 'video_id', 'video_title', None, 'weeks_on_chart')]
vid = lambda u: (re.search(r'v=([\w-]{6,})', u) or [None, None])[1] if isinstance(u, str) else None

def langof(s):
    h = len(re.findall('[֐-׿]', s)); a = len(re.findall('[؀-ۿ]', s)); l = len(re.findall('[A-Za-z]', s))
    return 'עברית' if h and h >= a else 'ערבית' if a > h and a >= l else 'לועזית' if l else 'אחר'

def pid(src, row, idc):
    v = row[idc]
    return vid(v) if src == 1 else (v if isinstance(v, str) and v else None)

def load(path):
    df = pd.read_excel(path, dtype=str, keep_default_na=False)
    return df

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--v2', default=os.path.join(HERE, 'v2')); ap.add_argument('--raw', default=os.path.join(HERE, 'raw'))
    ap.add_argument('--html', default=os.path.join(HERE, '..', '..', 'index.html')); a = ap.parse_args()
    html = open(a.html, encoding='utf-8').read(); i0 = html.index('window.WM_DATA=') + len('window.WM_DATA=')
    o, n = json.JSONDecoder().raw_decode(html[i0:]); i1 = i0 + n
    D = o['dates']; F = ['d', 'r', 't', 'v', 'pk', 'pr', 'dc', 's', 'status']
    obs = [dict(zip(F, x)) for x in zip(*(o[f] for f in F))]
    for x in obs: x['d'] = D[x['d']]
    T = o['tracks']; C = o['cols']; ci = {c: k for k, c in enumerate(C)}
    idx = collections.defaultdict(list)
    for k, x in enumerate(obs): idx[(x['s'], x['d'], x['r'], x['v'])].append(k)
    id2t = {}; stats = collections.Counter(); new_tracks = {}
    for src, name, dc, vc, idc, tc, pkc, dcc in SRC:
        raw = load([os.path.join(a.raw, f) for f in os.listdir(a.raw) if f.startswith(name.split('_2023')[0] if src == 0 else name) and f.endswith('.xlsx')][0])
        raw[dc] = raw[dc].str[:10]
        for _, r in raw.iterrows():
            if not r[tc]: continue
            ks = idx.get((src, r[dc], int(r['rank']), int(float(r[vc]))))
            p = pid(src, r, idc)
            if ks and p and len({obs[k]['t'] for k in ks}) == 1: id2t.setdefault((src > 0, p), obs[ks[0]]['t'])
        v2 = load(os.path.join(a.v2, [f for f in os.listdir(a.v2) if f.startswith(name) and f.endswith('_V2.xlsx')][0]))
        repl = set(v2.loc[v2.fill_source.isin(['added', 'corrected']), dc])
        before = len(obs); obs = [x for x in obs if not (x['s'] == src and x['d'] in repl)]; stats[f'{src}_removed'] += before - len(obs)
        for _, r in v2[v2[dc].isin(repl)].iterrows():
            if not r[tc]: stats[f'{src}_skipped_untitled'] += 1; continue
            p = pid(src, r, idc); key = (src > 0, p)
            t = id2t.get(key)
            if t is None:
                if key not in new_tracks:
                    row = [''] * len(C); title, artist = r[tc], r['artist_names']
                    row[ci['name']] = title; row[ci['artist']] = artist; row[ci['lang']] = langof(title); row[ci['ver']] = 'original'
                    row[ci['collab']] = 'שיתוף פעולה' if ',' in artist else 'סולו'
                    row[ci['uri' if src == 0 else 'yt']] = p or ''; row[ci['raw']] = f'{title} / {artist}'
                    if src == 0: row[ci['label']] = r.get('source', '')
                    row[ci['how']] = 'single_source_item'
                    row[ci['performance_id']] = 'PERF_GF_' + hashlib.sha1(f'{src > 0}|{p}'.encode()).hexdigest()[:14]
                    row[ci['identity_status']] = 'gapfill_new_unmatched'; row[ci['review_status']] = 'unreviewed'
                    T.append(row); new_tracks[key] = len(T) - 1; stats['new_tracks'] += 1
                t = new_tracks[key]
            else: stats[f'{src}_matched'] += 1
            num = lambda c, dflt=0: int(float(r[c])) if c and r.get(c, '') not in ('', None) else dflt
            obs.append(dict(d=r[dc], r=int(r['rank']), t=t, v=int(r[vc]), pk=num(pkc), pr=num('previous_rank'), dc=num(dcc), s=src, status=0))
            stats[f'{src}_added'] += 1
    obs.sort(key=lambda x: (x['s'], x['d'], x['r']))
    dates = sorted({x['d'] for x in obs}); di = {d: k for k, d in enumerate(dates)}
    for f in F: o[f] = [di[x['d']] if f == 'd' else x[f] for x in obs]
    o['dates'] = dates; o['tracks'] = T
    o['qa'] = {'bad': [], 'suspect_rows': sum(x['status'] for x in obs),
               'policy': 'V2 gap-fill 2026-11-16: missing Spotify days and YouTube 2023 weeks refetched from source; suspect repeated snapshots replaced'}
    out = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    open(a.html, 'w', encoding='utf-8', newline='').write(html[:i0] + out + html[i1:])
    print(dict(stats), 'rows', len(obs), 'tracks', len(T), 'dates', len(dates), 'id map', len(id2t))

if __name__ == '__main__':
    main()
