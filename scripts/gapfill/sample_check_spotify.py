"""Spot-check existing Spotify days: refetch N random days that already exist and compare rank+streams+uri-count with the app snapshot.
Usage: SPOTIFY_TOKEN=... python sample_check_spotify.py [--n 30] [--seed 1]"""
import argparse, json, os, random, sys, time, collections, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_spotify import API, rows_from
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=30); ap.add_argument('--seed', type=int, default=1); a = ap.parse_args()
s = open(os.path.join(HERE, '..', '..', 'index.html'), encoding='utf-8').read(); i = s.index('window.WM_DATA=') + 15
o, _ = json.JSONDecoder().raw_decode(s[i:]); D = o['dates']; old = collections.defaultdict(list)
for d, r, src, v in zip(o['d'], o['r'], o['s'], o['v']):
    if src == 0: old[D[d]].append((r, v))
days = sorted(random.Random(a.seed).sample(sorted(old), a.n)); tok = os.environ['SPOTIFY_TOKEN'].replace('Bearer ', '').strip(); res = collections.Counter()
for d in days:
    js = json.load(urllib.request.urlopen(urllib.request.Request(API.format(d), headers={'Authorization': 'Bearer ' + tok}), timeout=30))
    new = sorted((int(r[1]), int(r[9])) for r in rows_from(js, d)); same = sum(1 for x, y in zip(new, sorted(old[d])) if x == y)
    res['identical' if same == 200 else 'differs'] += 1; print(d, f'{same}/200 rows identical'); time.sleep(2.5)
print(dict(res))
