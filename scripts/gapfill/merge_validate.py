"""Merge newly fetched rows into the raw Drive exports, then validate (Stage 5 gate).

Usage: python merge_validate.py --raw <dir with the 3 Drive exports (.xlsx or .csv)> [--out merged]
Inputs picked up automatically:
  fetched/spotify/<date>.csv                  (from fetch_spotify.py)
  fetched/youtube_tracks/<end_date>.csv       (same columns as the TRACKS sheet)
  fetched/youtube_videos/<end_date>.csv       (same columns as the VIDEOS sheet)
Output: <out>/ three files with the original names + column fill_source; merged_report.json.
Exit code 1 if validation fails (missing dates, rank holes, duplicate weeks, duplicate rank rows).
"""
import argparse, glob, json, os, sys, datetime as dt
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
TAG = 'refetch_' + dt.date.today().isoformat()
SPECS = [  # key, file pattern, date col, fetched subdir, top-N, unique id col
    ('spotify', 'Spotify-all_israel_charts*', 'chart_date', 'spotify', 200, 'uri'),
    ('tracks', '*TRACKS*', 'end_date', 'youtube_tracks', 100, 'youtube_url'),
    ('videos', '*VIDEOS*', 'end_date', 'youtube_videos', 100, 'video_id')]

def load(path):
    return pd.read_csv(path, dtype=str) if path.endswith('.csv') else pd.read_excel(path, dtype=str)

def validate(key, df, dc, topn, step, start, until):
    probs = []
    d = pd.to_datetime(df[dc]).dt.date
    have = set(d); cur = start
    while cur <= until:
        if cur not in have: probs.append(f'{key}: missing {cur}')
        cur += dt.timedelta(days=step)
    for day, g in df.groupby(d):
        rk = pd.to_numeric(g['rank'], errors='coerce')
        if rk.duplicated().any(): probs.append(f'{key}: duplicate ranks on {day}')
        lack = sorted(set(range(1, topn + 1)) - set(rk.dropna().astype(int)))
        if lack: probs.append(f'{key}: {day} missing ranks {lack[:10]}')
    if step == 7:  # identical consecutive/any weeks
        sig = df.groupby(d).apply(lambda g: tuple(g.sort_values('rank')[['rank', 'views']].astype(str).itertuples(index=False, name=None)))
        dup = sig[sig.duplicated(keep=False)]
        if len(dup): probs.append(f'{key}: {len(dup)} weeks with identical content: {sorted(map(str, dup.index))[:5]}...')
    return probs

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--raw', required=True); ap.add_argument('--out', default=os.path.join(HERE, 'merged'))
    ap.add_argument('--until', default=str(dt.date.today() - dt.timedelta(days=2))); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); until = dt.date.fromisoformat(a.until); report = {}; problems = []
    for key, pat, dc, sub, topn, idc in SPECS:
        src = [f for f in glob.glob(os.path.join(a.raw, pat)) if f.endswith(('.xlsx', '.csv'))][0]
        base = load(src); base['fill_source'] = base.get('fill_source', pd.Series('original', index=base.index)).fillna('original')
        new = [load(f) for f in sorted(glob.glob(os.path.join(HERE, 'fetched', sub, '*.csv')))]
        added = replaced = 0
        if new:
            nw = pd.concat(new, ignore_index=True); nw['fill_source'] = TAG
            if 'is_suspect_duplicate' in base: nw['is_suspect_duplicate'] = 'FALSE'
            new_dates = set(nw[dc])
            old = base[dc].isin(new_dates); replaced = int(old.sum())
            base = pd.concat([base[~old], nw[[c for c in base.columns if c in nw.columns]]], ignore_index=True); added = len(nw)
        # drop still-unfixed suspect duplicated snapshots from the analysable copy? -> keep, but flagged
        base = base.sort_values([dc, 'rank'], key=lambda s: pd.to_numeric(s, errors='coerce') if s.name == 'rank' else s).reset_index(drop=True)
        name = os.path.splitext(os.path.basename(src))[0]
        base.to_excel(os.path.join(a.out, name + '.xlsx'), index=False)
        clean = base[base.get('is_suspect_duplicate', pd.Series('FALSE', index=base.index)).astype(str).str.upper() != 'TRUE']
        start = dt.date(2023, 1, 1) if key == 'spotify' else dt.date(2023, 1, 5)
        p = validate(key, clean, dc, topn, 1 if key == 'spotify' else 7, start, until)
        problems += p; report[key] = dict(rows=len(base), added_rows=added, replaced_rows=replaced, problems=len(p))
    report['problems'] = problems
    json.dump(report, open(os.path.join(a.out, 'merged_report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != 'problems'}, indent=1)); print(f'{len(problems)} problems'); [print(' -', x) for x in problems[:25]]
    sys.exit(1 if problems else 0)

if __name__ == '__main__':
    main()
