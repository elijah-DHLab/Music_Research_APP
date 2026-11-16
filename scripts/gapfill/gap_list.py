"""Compute exact missing/suspect periods from index.html (embedded WM_DATA) or from the raw Drive exports.

Usage:
  python gap_list.py --html ../../index.html            # from the app snapshot
  python gap_list.py --raw <dir with the Drive xlsx/csv>  # from raw exports (preferred once downloaded)
Writes missing_spotify_days.csv, missing_youtube_weeks.csv, rank_holes.csv next to this script.
"""
import argparse, csv, json, os, re, datetime as dt
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
START = dt.date(2023, 1, 1)

def from_html(p):
    s = open(p, encoding='utf-8').read()
    i = s.index('window.WM_DATA=') + len('window.WM_DATA=')
    obj, _ = json.JSONDecoder().raw_decode(s[i:])
    dates = obj['dates']; rows = defaultdict(lambda: defaultdict(set)); sig = defaultdict(lambda: defaultdict(list))
    for d, r, src, t, v in zip(obj['d'], obj['r'], obj['s'], obj['t'], obj['v']):
        day = dates[d]; rows[src][day].add(r); sig[src][day].append((r, t, v))
    return rows, sig

def from_raw(dirp):
    import pandas as pd, glob
    def rd(pat):
        f = [x for x in glob.glob(os.path.join(dirp, pat + '*')) if x.endswith(('.xlsx', '.csv'))][0]
        return pd.read_csv(f) if f.endswith('.csv') else pd.read_excel(f)
    rows = defaultdict(lambda: defaultdict(set)); sig = defaultdict(lambda: defaultdict(list))
    for src, pat, dc, idc in ((0, 'Spotify-all_israel_charts', 'chart_date', 'uri'), (1, '*TRACKS', 'end_date', 'youtube_url'), (2, '*VIDEOS', 'end_date', 'video_id')):
        df = rd(pat)
        for day, r, i, v in zip(pd.to_datetime(df[dc]).dt.strftime('%Y-%m-%d'), df['rank'], df[idc], df['streams' if src == 0 else 'views']):
            rows[src][day].add(int(r)); sig[src][day].append((int(r), i, v))
    return rows, sig

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--html'); ap.add_argument('--raw'); ap.add_argument('--until', default=str(dt.date.today() - dt.timedelta(days=2)))
    a = ap.parse_args(); rows, sig = from_html(a.html) if a.html else from_raw(a.raw)
    until = dt.date.fromisoformat(a.until)
    # Spotify daily
    have = rows[0]; miss = []
    d = START
    while d <= until:
        k = str(d)
        if k not in have: miss.append((k, 'missing'))
        elif have[k] != set(range(1, 201)): miss.append((k, f'incomplete:{len(have[k])}'))
        d += dt.timedelta(days=1)
    with open(os.path.join(HERE, 'missing_spotify_days.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['date', 'status']); w.writerows(miss)
    # YouTube weekly (Thursday end dates)
    first = dt.date(2023, 1, 5); out = []; holes = []
    for src, name in ((1, 'tracks'), (2, 'videos')):
        seen = {}; d = first
        while d <= until:
            k = str(d)
            if k not in rows[src]: out.append((name, k, 'missing'))
            else:
                key = tuple(sorted(sig[src][k], key=lambda x: x[0]))
                if key in seen: out.append((name, k, f'duplicate_of:{seen[key]}'))
                else: seen[key] = k
                lack = sorted(set(range(1, 101)) - rows[src][k])
                if lack: holes.append((name, k, ' '.join(map(str, lack))))
            d += dt.timedelta(days=7)
    # also mark the FIRST occurrence of a duplicated snapshot as suspect
    dup_targets = {(n, s.split(':')[1]) for n, _, s in out if s.startswith('duplicate_of')}
    out += [(n, k, 'duplicate_original') for n, k in sorted(dup_targets)]
    out.sort()
    with open(os.path.join(HERE, 'missing_youtube_weeks.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['chart', 'end_date', 'status']); w.writerows(out)
    with open(os.path.join(HERE, 'rank_holes.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['chart', 'end_date', 'missing_ranks']); w.writerows(holes)
    print(f'spotify: {len(miss)} days to fetch (until {until}); youtube: {len(out)} week-charts to fetch; rank holes: {len(holes)} weeks')

if __name__ == '__main__':
    main()
