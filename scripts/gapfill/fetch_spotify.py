"""Fetch missing Israel daily Spotify charts (regional-il-daily) for the dates in missing_spotify_days.csv.

Spotify closed anonymous history: the per-date endpoint needs the Bearer token of YOUR logged-in
charts.spotify.com session. To get it: log in at https://charts.spotify.com, open any Israel daily chart,
DevTools > Network > a request to charts-spotify-com-service.spotify.com > copy the 'authorization' header
value (without 'Bearer '). Tokens last ~1 hour; the script is resumable and stops cleanly on 401.

Usage:  set SPOTIFY_TOKEN=xxxx   (PowerShell: $env:SPOTIFY_TOKEN='xxxx')
        python fetch_spotify.py [--limit N]
Output: fetched/spotify/<date>.csv (only complete 200-row days are written), fetched/spotify_log.csv
"""
import csv, json, os, sys, time, random, argparse, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'fetched', 'spotify'); os.makedirs(OUT, exist_ok=True)
API = 'https://charts-spotify-com-service.spotify.com/auth/v0/charts/regional-il-daily/{}'
COLS = ['chart_date', 'rank', 'uri', 'artist_names', 'track_name', 'source', 'peak_rank', 'previous_rank', 'days_on_chart', 'streams']

def rows_from(js, day):
    out = []
    for e in js.get('entries', []):
        c, m = e.get('chartEntryData', {}), e.get('trackMetadata', {})
        out.append([day, c.get('currentRank'), m.get('trackUri'), ', '.join(a.get('name', '') for a in m.get('artists', [])), m.get('trackName'),
                    ', '.join(l.get('name', '') for l in m.get('labels', [])), c.get('peakRank'), c.get('previousRank', -1),
                    c.get('appearancesOnChart', c.get('consecutiveAppearancesOnChart')), (c.get('rankingMetric') or {}).get('value')])
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--limit', type=int, default=0); ap.add_argument('--all', help='refetch every day from 2023-01-01 to this date (full verification)'); a = ap.parse_args()
    tok = os.environ.get('SPOTIFY_TOKEN', '').replace('Bearer ', '').strip()
    if not tok: sys.exit('SPOTIFY_TOKEN is not set (see header of this file).')
    days = [r['date'] for r in csv.DictReader(open(os.path.join(HERE, 'missing_spotify_days.csv'), encoding='utf-8'))]
    if a.all:
        import datetime as dt
        d0, d1 = dt.date(2023, 1, 1), dt.date.fromisoformat(a.all); days = [str(d0 + dt.timedelta(n)) for n in range((d1 - d0).days + 1)]
    todo = [d for d in days if not os.path.exists(os.path.join(OUT, d + '.csv'))]
    if a.limit: todo = todo[:a.limit]
    log = open(os.path.join(HERE, 'fetched', 'spotify_log.csv'), 'a', newline='', encoding='utf-8'); lw = csv.writer(log)
    print(f'{len(todo)} days to fetch')
    for i, d in enumerate(todo, 1):
        req = urllib.request.Request(API.format(d), headers={'Authorization': 'Bearer ' + tok, 'Accept': 'application/json'})
        js = None
        for attempt in range(6):
            try:
                js = json.load(urllib.request.urlopen(req, timeout=30)); break
            except urllib.error.HTTPError as e:
                lw.writerow([d, e.code, '']); log.flush()
                if e.code == 401: sys.exit(f'401 at {d}: token expired. Paste a fresh token and re-run (progress is kept).')
                if e.code == 429: print(f'429 at {d}, retry in {60 * (attempt + 1)}s'); time.sleep(60 * (attempt + 1)); continue
                print(d, 'HTTP', e.code); break
        if js is None: continue
        rows = rows_from(js, d); ranks = sorted(int(r[1]) for r in rows if r[1] is not None)
        meta_date = (js.get('displayChart') or {}).get('date')
        ok = ranks == list(range(1, 201)) and all(r[2] and r[9] is not None for r in rows) and (meta_date in (None, d))
        lw.writerow([d, 200, f'rows={len(rows)} ok={ok} chart_date={meta_date}']); log.flush()
        if ok:
            with open(os.path.join(OUT, d + '.csv'), 'w', newline='', encoding='utf-8') as fh:
                w = csv.writer(fh); w.writerow(COLS); w.writerows(rows)
        print(f'[{i}/{len(todo)}] {d}: {len(rows)} rows {"OK" if ok else "REJECTED (incomplete or wrong date)"}')
        time.sleep(1.2 + random.random())

if __name__ == '__main__':
    main()
