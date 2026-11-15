# Usage: python build_data.py <dir with the 5 xlsx files>  -> ../data/{data.json,data.js,daily.js,events.js} + ../help.html
import pandas as pd, json, re, sys, glob, os, unicodedata, html
from collections import Counter, defaultdict
src = sys.argv[1] if len(sys.argv) > 1 else '.'
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'data')
rd = lambda p, **k: pd.read_excel(glob.glob(os.path.join(src, p))[0], **k)
sd = rd('Spotify-all_israel_charts*'); yt = rd('*TRACKS*'); yv = rd('*VIDEOS*'); perf = rd('*master_list*', sheet_name='performers'); master_works = rd('*master_list*', sheet_name=0)
vid = lambda u: (re.search(r'v=([\w-]{6,})', u) or [None, None])[1] if isinstance(u, str) else None
def frame(d, s, dc, tc, idf):
    o = pd.DataFrame({'date': d[dc], 'src': s, 'rank': d['rank'], 'raw_title': d[tc], 'raw_artist': d['artist_names']})
    o['v'] = d['streams'] if s in (0, 3) else d['views']
    o['pk'] = d['peak_rank'] if 'peak_rank' in d else 0; o['pr'] = d['previous_rank']; o['dc'] = d['days_on_chart'] if 'days_on_chart' in d else d['weeks_on_chart']
    o['label'] = d['source'] if 'source' in d else ''; o['id'] = idf(d); return o
F = [frame(sd, 0, 'chart_date', 'track_name', lambda d: 'sp:' + d.uri),
     frame(yt, 1, 'end_date', 'track_name', lambda d: d.youtube_url.map(vid).map(lambda v: 'yt:' + v if isinstance(v, str) else None)),
     frame(yv, 2, 'end_date', 'video_title', lambda d: d.video_id.map(lambda v: 'yt:' + v if isinstance(v, str) else None))]
n_raw = sum(len(f) for f in F); df = pd.concat(F, ignore_index=True)
n_notitle = int(df.raw_title.isna().sum()); df = df.dropna(subset=['raw_title']).copy()
df['raw_title'] = df.raw_title.astype(str); df['raw_artist'] = df.raw_artist.fillna('').astype(str)
df['id'] = df['id'].where(df['id'].notna(), 'x:' + df.raw_title + '|' + df.raw_artist)
for c in ['pk', 'pr', 'dc']: df[c] = df[c].fillna(0).astype(int)
# ---------- text cleaning ----------
NIK = re.compile('[\u0591-\u05c7\u064b-\u065f\u200e\u200f\u202a-\u202e\ufffc\u200b]')
cl = lambda s: re.sub(r'\s+', ' ', NIK.sub('', unicodedata.normalize('NFKC', s))).strip()
nk = lambda s: re.sub(r'[\W_]+', '', cl(s).casefold())
lat = lambda s: bool(re.search('[A-Za-z]', s))
NOISE = re.compile(r'(?i)^(topic|official|vevo)$|הערוץ הרשמי|תאגיד השידור|^כאן( גימל| 11| 88)?$|^ערוץ \d+$|ערוץ רשמי')
TAIL = re.compile(r'(?i)\s*[-–]?\s*(official( channel| music)?|הערוץ הרשמי|ערוץ רשמי)\s*$')
def artists(raw):
    out = []
    for p in re.split(r',|&|\band\b| x | feat\.? | ft\.? ', raw):
        p = TAIL.sub('', cl(p)).strip()
        if not p or NOISE.search(p): continue
        out.append(p)
    return out
VW = r'(official( music)?( video| audio)?|lyrics?( video)?|audio|video|clip|music video|קליפ( רשמי)?|וידאו|אודיו|מילים|prod\.?\s*by.*|music\.?\s*by.*|feat\.?.*|ft\.?.*|with .*|הצצה.*|\d{4})'
VER = [('live', r'(?i)\b(live)\b|לייב|מנורה'), ('remix', r'(?i)remix|רימיקס'), ('edit', r'(?i)\bedit\b'), ('acoustic', r'(?i)acoustic|אקוסטי'), ('cover', r'(?i)\bcover\b|קאבר')]
def title(raw, known):
    t = cl(raw); ver = 'original'
    for n, p in VER:
        if re.search(p, t): ver = n; break
    t = t.split('|')[0] if len(t.split('|')[0].strip()) > 1 else t
    t = re.sub(r'(?i)\s*[\(\[][^\)\]]*[\)\]]', lambda m: '' if re.search(r'(?i)^\s*[\(\[]\s*(' + VW + r'|live|לייב|remix|edit|acoustic|cover|קאבר|מנורה|from .*|.*remix.*|.*live.*|.*prod.*|.*version.*|.*extended.*|.*\d{4}.*)[\s\)\]]*$', m.group(0)) else m.group(0), t)
    t = re.sub(r'(?i)\s*[-–]\s*(live|edit|remix|acoustic|from .*|official.*|.*version.*)$', '', t)
    t = re.sub(r'(?i)\s*(official( music)? video|lyric video|\(?קליפ רשמי\)?|\(official.*)$', '', t)
    if re.search(r'\s[-–]\s', t):
        a, b = [x.strip() for x in re.split(r'\s[-–]\s', t, 1)]
        if nk(a) in known and b: t = b
        elif nk(b) in known and a: t = a
    return t.strip(' -–|,'), ver
# ---------- artist aliases (union-find) ----------
par = {}
def f(x):
    par.setdefault(x, x)
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
def u(a, b): par[f(a)] = f(b)
disp = defaultdict(Counter); P = {}
for _, r in perf.iterrows():
    if not isinstance(r.performer_name, str) or not r.performer_name.strip(): continue
    k = nk(r.performer_name); P[k] = r; disp[k][r.performer_name] += 100
    if isinstance(r.hewiki_title, str): u(nk(r.hewiki_title), k); disp[nk(r.hewiki_title)][r.hewiki_title] += 1
raw_ar = Counter(df.raw_artist); n_bil = 0
for a, c in raw_ar.items():
    for p in artists(a):
        disp[nk(p)][p] += c
        m = re.split(r'\s[-–]\s|\s*[-–]\s*(?=[\u0590-\u05ff\u0600-\u06ff])', p)
        if len(m) == 2 and all(len(x.strip()) > 1 for x in m) and lat(m[0]) != lat(m[1]) or (len(m) == 2 and re.search('[\u0590-\u06ff]', m[0]) and re.search('[\u0590-\u06ff]', m[1]) is None):
            u(nk(m[0]), nk(m[1])); n_bil += 1; disp[nk(m[0])][m[0].strip()] += c; disp[nk(m[1])][m[1].strip()] += c
members = defaultdict(set)
for k in list(par): members[f(k)].add(k)
canon = {}
for r, ms in members.items():
    ms = list(ms); pf = [m for m in ms if m in P and disp[m]]
    best = lambda cands: max(cands, key=lambda m: sum(disp[m].values()))
    pick = best(pf) if pf else best([m for m in ms if disp[m] and lat(disp[m].most_common(1)[0][0])] or [m for m in ms if disp[m]] or ms)
    for m in ms: canon[m] = pick
name_of = lambda k: disp[canon.get(k, k)].most_common(1)[0][0] if disp[canon.get(k, k)] else k
def akeys(raw):
    o = []
    for p in artists(raw):
        parts = [x.strip() for x in re.split(r'\s[-–]\s', p)]
        k = canon.get(nk(parts[0]), nk(parts[0])) if parts else ''
        if k and k not in o: o.append(k)
    return o
known = set(canon) | set(nk(a) for a in P)
# ---------- entities (one per YouTube video-id / Spotify uri) ----------
PRI = {0: 0, 3: 0, 1: 1, 2: 2}
ent = {}
for (i, s, t, a), c in df.groupby(['id', 'src', 'raw_title', 'raw_artist']).size().items():
    e = ent.setdefault(i, {'id': i, 'c': Counter(), 'srcs': set()}); e['c'][(PRI[s], -c, t, a)] += 1; e['srcs'].add(s)
for e in ent.values():
    _, _, t, a = min(e['c']); e['raw_t'], e['raw_a'] = t, a
    e['t'], e['ver'] = title(t, known); e['ak'] = akeys(a)
    if e['srcs'] & {2}: e['ak'] += [k for k in [nk(p) for p in re.split(r'\s[-–]\s', cl(t))[:1]] if k in known and canon.get(k, k) not in e['ak']]
    e['tk'] = nk(e['t']) or nk(t)
# ---------- cluster entities into songs ----------
par2 = {}
def f2(x):
    par2.setdefault(x, x)
    while par2[x] != x: par2[x] = par2[par2[x]]; x = par2[x]
    return x
groups = defaultdict(list)
for e in ent.values(): groups[(e['tk'], e['ver'])].append(e)
merged_title = 0
for g in groups.values():
    for e in g: f2(e['id'])
    for i, a in enumerate(g):
        for b in g[i + 1:]:
            if (set(a['ak']) & set(b['ak'])) or (not a['ak'] or not b['ak']) and len(set(map(lambda z: tuple(z['ak']), g))) <= 2:
                if f2(a['id']) != f2(b['id']): u2 = par2.__setitem__(f2(a['id']), f2(b['id'])); merged_title += 1
clusters = defaultdict(list)
for e in ent.values(): clusters[f2(e['id'])].append(e)
ymap = {}
def enrich(aks):
    for k in aks:
        r = P.get(k)
        if r is not None:
            g = lambda c: '' if pd.isna(r[c]) else str(r[c]); b = r['birth_or_inception_year']
            return [g('gender'), g('birth_or_origin_country'), g('genres').split(' | ')[0], g('birth_or_formation_city'), g('entity_type'), (str(int(b) // 10 * 10) + 's') if pd.notna(b) else '', g('genres'), '' if pd.isna(b) else str(int(b)), g('wikidata_description')]
    return [''] * 9
def langof(s):
    h = len(re.findall('[\u0590-\u05ff]', s)); a = len(re.findall('[\u0600-\u06ff]', s)); l = len(re.findall('[A-Za-z]', s))
    return 'עברית' if h and h >= a else 'ערבית' if a > h and a >= l else 'לועזית' if l else 'אחר'
lab = df[df.src.isin([0, 3])].dropna(subset=['label']).drop_duplicates('id').set_index('id')['label']
tracks = []; tid = {}
for ci, (root, es) in enumerate(clusters.items()):
    es.sort(key=lambda e: min(PRI[s] for s in e['srcs'])); e0 = es[0]
    aks = []; [aks.append(k) for e in es for k in e['ak'] if k not in aks]
    en = enrich(aks); how = sorted({'uri' if e['id'].startswith('sp:') else 'video_id' if e['id'].startswith('yt:') else 'name' for e in es}) + (['title+artist'] if len(es) > 1 else [])
    ids = [e['id'] for e in es]
    tracks.append([e0['t'], ', '.join(name_of(k) for k in aks) or e0['raw_a'] or '?', langof(e0['t'])] + en[:4] + [lab.get(next((i for i in ids if i in lab.index), ''), '') if any(i in lab.index for i in ids) else '', en[4], en[5], en[6], en[7], en[8], e0['ver'], 'שיתוף פעולה' if len(aks) > 1 else 'סולו',
        ' '.join(i[3:] for i in ids if i.startswith('sp:'))[:60], ' '.join(i[3:] for i in ids if i.startswith('yt:'))[:60], ' ¦ '.join(sorted({e['raw_t'] + ' / ' + e['raw_a'] for e in es}))[:300], '+'.join(how)])
    for e in es: tid[e['id']] = ci
# Work vs recording registry: recording identifiers retain platform identity; work grouping is explicitly provisional.
import csv
# An independent crosswalk sourced from the UPDATED master works tab.
master_ids = defaultdict(list)
for mi,r in master_works.iterrows():
    for uri in re.findall(r'spotify:track:[A-Za-z0-9]+', str(r.get('spotify_uris', ''))):
        master_ids['sp:'+uri].append((mi,str(r.get('work_name','')),str(r.get('performer_name',''))))
    for vid in re.findall(r'(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{11}(?![A-Za-z0-9_-])',str(r.get('youtube_video_ids',''))):
        master_ids['yt:'+vid].append((mi,str(r.get('work_name','')),str(r.get('performer_name',''))))
with open(os.path.join(OUT, 'master_crosswalk.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    wr=csv.writer(fh);wr.writerow(['recording_id','computed_work_cluster_id','master_work_row','master_work_name','master_performer','review_status'])
    for rid,links in master_ids.items():
        if rid not in tid: continue
        for mi,wn,pn in links:
            wr.writerow([rid, f'W{tid[rid]:05d}', mi+2, wn, pn, 'review_conflict' if len(links)>1 else 'linked_by_source_id'])

with open(os.path.join(OUT, 'recordings.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    wr = csv.writer(fh); wr.writerow(['recording_id','work_cluster_id','canonical_work_title','canonical_performers','source','raw_title','raw_artist','version','matching_basis','review_status'])
    for e in ent.values():
        ti=tid[e['id']]; track=tracks[ti]
        basis='same platform recording identifier' if len(clusters[f2(e['id'])])==1 else 'normalized title + shared artist (provisional)'
        wr.writerow([e['id'],f'W{ti:05d}',track[0],track[1],','.join(str(i) for i in sorted(e['srcs'])),e['raw_t'],e['raw_a'],e['ver'],basis,'verify' if len(clusters[f2(e['id'])])>1 else 'single-recording'])
with open(os.path.join(OUT, 'works.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    wr=csv.writer(fh);wr.writerow(['work_cluster_id','canonical_title','canonical_artists','language_estimated_by_title','creator_genre','recording_count','source_ids','review_status'])
    for ti,track in enumerate(tracks):
        es=clusters[next(k for k,v in clusters.items() if any(tid[e['id']]==ti for e in v))]
        wr.writerow([f'W{ti:05d}',track[0],track[1],track[2],track[5],len(es),' | '.join(e['id'] for e in es),'verify' if len(es)>1 else 'single-recording'])
df['t'] = df['id'].map(tid)
fmt = lambda s: s.dt.strftime('%Y-%m-%d')
def pack(d, dates=None):
    dates = dates or sorted(fmt(d['date']).unique()); ix = {x: i for i, x in enumerate(dates)}
    return dates, {'d': fmt(d['date']).map(ix).tolist(), 'r': d['rank'].astype(int).tolist(), 't': d['t'].tolist(), 'v': d['v'].astype(int).tolist(), 'pk': d['pk'].tolist(), 'pr': d['pr'].tolist(), 'dc': d['dc'].tolist()}
dw, W = pack(df); W['s'] = df['src'].tolist()
# ---------- data-quality check: is each Spotify chart a real time series? ----------
qa = {'bad': [], 'notes': {}}
for s in (0,):
    g = df[df.src == s]; pairs = int(g[['rank', 't']].drop_duplicates().shape[0]); per = len(g) / g.date.nunique()
    qa['notes'][s] = dict(dates=int(g.date.nunique()), pairs=pairs, per_day=int(per), rank1_tracks=int(g[g['rank'] == 1].t.nunique()), streams_per_rank_max=int(g.groupby('rank').v.nunique().max()))
    if pairs <= 1.2 * per: qa['bad'].append(s)
qa['weekly_eq_daily'] = None
out = {'cols': ['name', 'artist', 'lang', 'gender', 'country', 'genre', 'city', 'label', 'ent', 'dec', 'genres', 'birth', 'desc', 'ver', 'collab', 'uri', 'yt', 'raw', 'how'], 'tracks': tracks, 'dates': dw, **W, 'qa': qa}
dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
w = lambda n, s: open(os.path.join(OUT, n), 'w', encoding='utf-8').write(s)
w('data.json', dump(out)); w('data.js', 'window.WM_DATA=' + dump(out) + ';')
import gzip
with open(os.path.join(OUT, 'data.json.gz'), 'wb') as gz: gz.write(gzip.compress(dump(out).encode('utf-8'), compresslevel=9, mtime=0))
for fn in ('daily.js', 'daily.json'):
    if os.path.exists(os.path.join(OUT, fn)): os.remove(os.path.join(OUT, fn))
ev = os.path.join(OUT, 'events.json')
if os.path.exists(ev): w('events.js', 'window.WM_EVENTS=' + open(ev, encoding='utf-8').read() + ';')
# ---------- report + help ----------
raw_titles = df.drop_duplicates(['src', 'raw_title', 'raw_artist']).shape[0]
n0 = qa['notes'][0]; rep = dict(sp_dates=n0['dates'], sp_pairs=n0['pairs'], sp_per=n0['per_day'], sp_rank1=n0['rank1_tracks'], sp_eq='לא נכלל', rows=n_raw, dropped=n_notitle, ents=len(ent), songs=len(tracks), raw_titles=raw_titles, merged_title=merged_title, bil=n_bil, enriched=sum(1 for t in tracks if t[3] or t[4]),
           multi=[t[0] + ' ← ' + t[17] for t in tracks if t[18].count('+') >= 2][:6], noisy=sum(1 for e in ent.values() if e['t'] != cl(e['raw_t'])))
json.dump(rep, open(os.path.join(HERE, 'report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
tpl = open(os.path.join(HERE, 'help_template.html'), encoding='utf-8').read()
for k, v in rep.items(): tpl = tpl.replace('{' + k + '}', html.escape('<br>'.join(v) if isinstance(v, list) else f'{v:,}' if isinstance(v, int) else str(v)).replace('&lt;br&gt;', '<br>'))
open(os.path.join(HERE, '..', 'help.html'), 'w', encoding='utf-8').write(tpl)
print(rep)
