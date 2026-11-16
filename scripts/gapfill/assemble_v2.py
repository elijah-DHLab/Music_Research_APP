"""Build corrected V2 sheets from the fetched charts, label every row's provenance against the app snapshot,
validate, and write xlsx files ready to upload to Drive.

Usage: python assemble_v2.py [--html ../../index.html] [--out v2]
fill_source values:
  unchanged  - period identical (rank+value) to the previous dataset
  corrected  - period existed but differed (e.g. tied ranks previously dropped)
  added      - period was missing, or was a suspect repeated snapshot (YouTube 2023-01-05..2023-10-05)
Spotify: periods not refetched are taken from --spotify-old (Drive export) if given; else only fetched days are written.
"""
import argparse, csv, glob, json, os, sys, collections, datetime as dt
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
SPECS = [('spotify', 0, 'spotify', 'Spotify-all_israel_charts_2023_to_today', 'chart_date', 'streams', 200, 1, '2023-01-01'),
         ('tracks', 1, 'youtube_tracks', 'all_israel_youtube_charts_2023_to_today-TRACKS', 'end_date', 'views', 100, 7, '2023-01-05'),
         ('videos', 2, 'youtube_videos', 'all_israel_youtube_videos_2023_to_today-VIDEOS', 'end_date', 'views', 100, 7, '2023-01-05')]
SUSPECT_END = '2023-10-12'

def old_snapshot(html):
    s = open(html, encoding='utf-8').read(); i = s.index('window.WM_DATA=') + 15
    o, _ = json.JSONDecoder().raw_decode(s[i:]); D = o['dates']; old = collections.defaultdict(list)
    for d, r, src, v in zip(o['d'], o['r'], o['s'], o['v']): old[(src, D[d])].append((int(r), int(v)))
    return {k: sorted(v) for k, v in old.items()}

def check(key, df, dc, vc, topn, step, start, until):
    probs = []; have = set(df[dc]); d = dt.date.fromisoformat(start)
    while d <= until:
        if str(d) not in have: probs.append(f'{key}: missing {d}')
        d += dt.timedelta(days=step)
    sigs = {}
    for day, g in df.groupby(dc):
        rk = sorted(pd.to_numeric(g['rank']).astype(int))
        # competition ranking allowed (ties: 60,60,62); require len==topn, starts at 1, each rank <= its position
        if len(rk) != topn or rk[0] != 1 or any(r > i + 1 for i, r in enumerate(rk)): probs.append(f'{key}: {day} bad ranks (n={len(rk)})')
        sig = tuple(zip(rk, g.sort_values('rank')[vc].astype(str)))
        if sig in sigs: probs.append(f'{key}: {day} identical to {sigs[sig]}')
        sigs[sig] = day
    return probs

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--html', default=os.path.join(HERE, '..', '..', 'index.html'))
    ap.add_argument('--out', default=os.path.join(HERE, 'v2')); ap.add_argument('--spotify-old'); ap.add_argument('--until', default='2026-11-14')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); old = old_snapshot(a.html); rep = {}; allp = []
    for key, src, sub, name, dc, vc, topn, step, start in SPECS:
        files = sorted(glob.glob(os.path.join(HERE, 'fetched', sub, '*.csv')))
        df = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in files], ignore_index=True)
        if key == 'spotify' and a.spotify_old:
            o = pd.read_excel(a.spotify_old, dtype=str) if a.spotify_old.endswith('xlsx') else pd.read_csv(a.spotify_old, dtype=str, keep_default_na=False)
            o[dc] = o[dc].astype(str).str[:10]; o = o[~o[dc].isin(set(df[dc]))]; df = pd.concat([o, df], ignore_index=True)
        tags = {}
        for day, g in df.groupby(dc):
            new = sorted(zip(pd.to_numeric(g['rank']).astype(int), pd.to_numeric(g[vc]).astype(int)))
            prev = old.get((src, day))
            tags[day] = 'added' if prev is None or (src > 0 and day < SUSPECT_END) else 'unchanged' if prev == new else 'corrected'
        df['fill_source'] = df[dc].map(tags)
        if 'is_suspect_duplicate' in df: df['is_suspect_duplicate'] = 'FALSE'
        for c in ('rank', vc, 'previous_rank', 'peak_rank', 'weeks_on_chart', 'days_on_chart'):
            if c in df: df[c] = pd.to_numeric(df[c], errors='coerce').astype('Int64')
        df = df.sort_values([dc, 'rank'], kind='stable').reset_index(drop=True)
        p = check(key, df, dc, vc, topn, step, start, dt.date.fromisoformat(a.until) if step == 1 else dt.date(2026, 11, 12)); allp += p
        df.to_excel(os.path.join(a.out, name + '_V2.xlsx'), index=False)
        rep[key] = dict(rows=len(df), periods=df[dc].nunique(), first=df[dc].min(), last=df[dc].max(), **collections.Counter(tags.values()), problems=len(p))
    rep['problems'] = allp
    json.dump(rep, open(os.path.join(a.out, 'V2_report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1)[:3000]); sys.exit(1 if allp else 0)

if __name__ == '__main__':
    main()
