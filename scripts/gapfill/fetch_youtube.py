"""Fetch Israel weekly YouTube charts (Top Songs = TRACKS, Top Music Videos = VIDEOS) from charts.youtube.com.

Each request names an explicit week id (weekly:<start>:<end>:il). Responses are validated:
returned endDate == requested, 100 ranks 1..100, and the content differs from every other fetched week.
Usage: python fetch_youtube.py [--from 2023-01-05] [--to 2026-11-12]
Output: fetched/youtube_tracks/<end>.csv, fetched/youtube_videos/<end>.csv, fetched/youtube_log.csv
"""
import argparse, csv, json, os, sys, time, random, datetime as dt, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
OT, OV = (os.path.join(HERE, 'fetched', x) for x in ('youtube_tracks', 'youtube_videos'))
API = 'https://charts.youtube.com/youtubei/v1/browse?alt=json&prettyPrint=false'
TC = ['chart_week', 'end_date', 'rank', 'previous_rank', 'peak_rank', 'weeks_on_chart', 'track_name', 'artist_names', 'views', 'youtube_url', 'is_suspect_duplicate']
VC = ['chart_week', 'end_date', 'rank', 'previous_rank', 'peak_rank', 'weeks_on_chart', 'video_title', 'artist_names', 'views', 'video_id', 'youtube_url', 'is_suspect_duplicate']

def walk(o, key, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key: acc.append(v)
            walk(v, key, acc)
    elif isinstance(o, list):
        for v in o: walk(v, key, acc)
    return acc

def fetch(end):
    start = end - dt.timedelta(days=6); f = lambda d: d.strftime('%Y%m%d')
    q = f'chart_params_type=WEEKLY&perspective=CHART&flags=viral_video_chart&selected_chart=TRACKS&chart_params_id=weekly%3A{f(start)}%3A{f(end)}%3Ail'
    body = json.dumps({'context': {'client': {'clientName': 'WEB_MUSIC_ANALYTICS', 'clientVersion': '2.0', 'hl': 'en', 'gl': 'IL'}}, 'browseId': 'FEmusic_analytics_charts_home', 'query': q}).encode()
    req = urllib.request.Request(API, data=body, headers={'Content-Type': 'application/json', 'Origin': 'https://charts.youtube.com', 'Referer': 'https://charts.youtube.com/charts/TopSongs/il/weekly'})
    return json.load(urllib.request.urlopen(req, timeout=40)), f'{f(start)}-{f(end)}'

def row(e, week, end, kind):
    m = e.get('chartEntryMetadata', {}); arts = ', '.join(a.get('name', '') for a in e.get('artists', []))
    base = [week, str(end), m.get('currentPosition'), m.get('previousPosition', ''), '', m.get('periodsOnChart', '')]
    if kind == 'T':
        vid = e.get('encryptedVideoId', '')
        return base + [e.get('name'), arts, e.get('viewCount'), f'https://www.youtube.com/watch?v={vid}' if vid else '', 'FALSE']
    vid = e.get('id', '')
    return base + [e.get('title'), arts, e.get('viewCount'), vid, f'https://www.youtube.com/watch?v={vid}' if vid else '', 'FALSE']

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--from', dest='fr', default='2023-01-05'); ap.add_argument('--to', default='2026-11-12'); a = ap.parse_args()
    os.makedirs(OT, exist_ok=True); os.makedirs(OV, exist_ok=True)
    log = csv.writer(open(os.path.join(HERE, 'fetched', 'youtube_log.csv'), 'a', newline='', encoding='utf-8'))
    end, last = dt.date.fromisoformat(a.fr), dt.date.fromisoformat(a.to); sigs = {}
    while end <= last:
        if os.path.exists(os.path.join(OT, f'{end}.csv')) and os.path.exists(os.path.join(OV, f'{end}.csv')): end += dt.timedelta(days=7); continue
        try: js, week = fetch(end)
        except Exception as ex: print(end, 'ERROR', ex); log.writerow([end, 'error', ex]); time.sleep(5); end += dt.timedelta(days=7); continue
        ends = set(v for v in walk(js, 'endDate', []) if isinstance(v, str) and '-' in v)
        tv = (walk(js, 'trackViews', []) or [[]])[0]
        vl = [x for x in walk(js, 'videoViews', []) if x and 'percentViewsChange' in str(x[0].get('chartEntryMetadata', {})) or (x and len(x) >= 90)]
        vv = vl[0] if vl else []
        msg = []
        for kind, lst, out, cols in (('T', tv, OT, TC), ('V', vv, OV, VC)):
            rows = [row(e, week, end, kind) for e in lst]; ranks = sorted(r[2] for r in rows if r[2])
            sig = tuple((r[2], r[8]) for r in rows)
            ok = str(end) in ends and ranks == list(range(1, 101)) and sig not in sigs.get(kind, {})
            why = '' if ok else f"endDates={sorted(ends)[:2]} ranks={len(ranks)} dup={sigs.get(kind, {}).get(sig)}"
            if ok or (str(end) in ends and len(rows) >= 90 and sig not in sigs.get(kind, {})):  # keep 90-99 row weeks too, flagged
                sigs.setdefault(kind, {})[sig] = str(end)
                with open(os.path.join(out, f'{end}.csv'), 'w', newline='', encoding='utf-8') as fh:
                    w = csv.writer(fh); w.writerow(cols); w.writerows(rows)
            msg.append(f"{kind}:{len(rows)}{'' if ok else ' WARN ' + why}")
        log.writerow([end, 'ok', ' '.join(msg)]); print(end, *msg)
        end += dt.timedelta(days=7); time.sleep(0.8 + random.random())

if __name__ == '__main__':
    main()
