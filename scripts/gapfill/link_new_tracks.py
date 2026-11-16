"""Link the gap-fill tracks (identity_status == 'gapfill_new_unmatched') in index.html to the existing catalog.

Level 1  same performance  : normalized title + version equal AND performer overlap with an existing track
                              -> observations are re-pointed to the existing track; the new track row is dropped.
Level 2  known performer   : >=1 performer resolves to a V21 entity (he/en/display/aliases)
                              -> new V21.performances entry (artists = entity ids); performer metadata columns
                                 copied from an existing track of the same lead entity; identity 'gapfill_artist_linked'.
Level 3  unmatched         : kept, identity 'gapfill_unmatched', listed for manual review.
Writes link_report.csv next to this script. Usage: python link_new_tracks.py [--html ../../index.html]
"""
import argparse, collections, csv, json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
NIK = re.compile('[֑-ׇً-ٟ‎‏‪-‮￼​]')
cl = lambda s: re.sub(r'\s+', ' ', NIK.sub('', unicodedata.normalize('NFKC', s or ''))).strip()
nk = lambda s: re.sub(r'[\W_]+', '', cl(s).casefold())
NOISE = re.compile(r'(?i)^(topic|official|vevo)$|הערוץ הרשמי|תאגיד השידור|^כאן( גימל| 11| 88)?$|^ערוץ \d+$|ערוץ רשמי')
TAIL = re.compile(r'(?i)\s*[-–]?\s*(official( channel| music)?|הערוץ הרשמי|ערוץ רשמי)\s*$')
VER = [('live', r'(?i)\b(live)\b|לייב|מנורה'), ('remix', r'(?i)remix|רימיקס'), ('edit', r'(?i)\bedit\b'), ('acoustic', r'(?i)acoustic|אקוסטי'), ('cover', r'(?i)\bcover\b|קאבר')]
META = ['gender', 'country', 'genre', 'city', 'ent', 'dec', 'genres', 'birth', 'desc']

def artists(raw):
    out = []
    for p in re.split(r',|&|\band\b| x | feat\.? | ft\.? ', raw or ''):
        p = TAIL.sub('', cl(p)).strip()
        if p and not NOISE.search(p): out.append(p)
    return out

def title_key(raw, known):
    t = cl(raw); ver = 'original'
    for n, p in VER:
        if re.search(p, t): ver = n; break
    t = t.split('|')[0] if len(t.split('|')[0].strip()) > 1 else t
    t = re.sub(r'(?i)\s*[\(\[][^\)\]]*[\)\]]', '', t)
    t = re.sub(r'(?i)\s*[-–]\s*(live|edit|remix|acoustic|from .*|official.*|.*version.*)$', '', t)
    t = re.sub(r'(?i)\s*(official( music)? video|lyric video|קליפ רשמי)$', '', t)
    if re.search(r'\s[-–]\s', t):
        a, b = [x.strip() for x in re.split(r'\s[-–]\s', t, maxsplit=1)]
        if nk(a) in known and b: t = b
        elif nk(b) in known and a: t = a
    return nk(t), ver

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--html', default=os.path.join(HERE, '..', '..', 'index.html')); a = ap.parse_args()
    html = open(a.html, encoding='utf-8').read()
    i0 = html.index('window.WM_DATA=') + 15; o, n = json.JSONDecoder().raw_decode(html[i0:]); i1 = i0 + n
    j0 = html.index('window.WM_V21=') + 14; V, m = json.JSONDecoder().raw_decode(html[j0:]); j1 = j0 + m
    C = {c: k for k, c in enumerate(o['cols'])}; T = o['tracks']
    alias = {}
    for eid, e in V['entities'].items():
        for s in [e.get('he'), e.get('en'), e.get('display')] + list(e.get('aliases') or []):
            if s: alias.setdefault(nk(s), eid)
    known = set(alias)
    def ents(raw):
        out = []
        for p in artists(raw):
            for part in [p] + [x.strip() for x in re.split(r'\s[-–]\s', p)]:
                e = alias.get(nk(part))
                if e and e not in out: out.append(e); break
        return out
    is_new = lambda t: t[C['identity_status']] == 'gapfill_new_unmatched'
    # index existing tracks
    by_key = collections.defaultdict(list); meta_by_ent = {}
    for k, t in enumerate(T):
        if is_new(t): continue
        p = V['performances'].get(t[C['performance_id']]) or {}
        es = list(p.get('artists') or []) or ents(t[C['artist']])
        tk = title_key(t[C['name']], known)
        by_key[(tk[0], t[C['ver']] or tk[1])].append((k, set(es), {nk(x) for x in artists(t[C['artist']])}))
        if es and any(t[C[c]] for c in META): meta_by_ent.setdefault(es[0], [t[C[c]] for c in META])
    remap = {}; rep = []; cnt = collections.Counter(); new_by_key = collections.defaultdict(list)
    for k, t in enumerate(T):
        if not is_new(t): continue
        es = ents(t[C['artist']]); an = {nk(x) for x in artists(t[C['artist']])}
        tk = title_key(t[C['name']], known); hit = None
        for (ek, ees, ean) in by_key.get(tk, []):
            if (es and ees & set(es)) or (an & ean): hit = ek; break
        if hit is None:  # same new song already seen from another platform/id in this gap-fill
            for (ek, ees, ean) in new_by_key.get(tk, []):
                if (es and ees & set(es)) or (an & ean): hit = ek; cnt['merged_new_duplicate'] += 1; break
            if hit is not None:
                remap[k] = hit; rep.append([t[C['name']], t[C['artist']], t[C['uri']], t[C['yt']], 'merged_into_other_new', T[hit][C['name']] + ' / ' + T[hit][C['artist']], T[hit][C['performance_id']]]); continue
            new_by_key[tk].append((k, set(es), an))
        if hit is not None:
            remap[k] = hit; cnt['level1_same_performance'] += 1
            rep.append([t[C['name']], t[C['artist']], t[C['uri']], t[C['yt']], 'level1_same_performance', T[hit][C['name']] + ' / ' + T[hit][C['artist']], T[hit][C['performance_id']]]); continue
        if es:
            pid = t[C['performance_id']]
            V['performances'][pid] = {'he': '', 'en': '', 'title': t[C['name']], 'artists': es, 'fallback_artist': t[C['artist']], 'aliases': [t[C['name']]], 'work_id': ''}
            for c, v in zip(META, meta_by_ent.get(es[0], [''] * len(META))): t[C[c]] = v
            t[C['collab']] = 'שיתוף פעולה' if len(es) > 1 or ',' in t[C['artist']] else 'סולו'
            t[C['identity_status']] = 'gapfill_artist_linked'; t[C['review_status']] = 'needs_review'; cnt['level2_artist_linked'] += 1
            rep.append([t[C['name']], t[C['artist']], t[C['uri']], t[C['yt']], 'level2_artist_linked', ' | '.join(V['entities'][e].get('display', e) for e in es), pid])
        else:
            t[C['identity_status']] = 'gapfill_unmatched'; t[C['review_status']] = 'needs_review'; cnt['level3_unmatched'] += 1
            rep.append([t[C['name']], t[C['artist']], t[C['uri']], t[C['yt']], 'level3_unmatched', '', t[C['performance_id']]])
    # merge level-1 tracks, compact track table
    for k, hit in remap.items():
        h = T[hit]
        if T[k][C['uri']] and T[k][C['uri']] not in h[C['uri']]: h[C['uri']] = (h[C['uri']] + ' ' + T[k][C['uri']]).strip()
        if T[k][C['yt']] and T[k][C['yt']] not in h[C['yt']]: h[C['yt']] = (h[C['yt']] + ' ' + T[k][C['yt']]).strip()
    keep = [k for k in range(len(T)) if k not in remap]; newix = {k: i for i, k in enumerate(keep)}
    o['t'] = [newix[remap.get(t, t)] for t in o['t']]; o['tracks'] = [T[k] for k in keep]
    html = html[:j0] + json.dumps(V, ensure_ascii=False, separators=(',', ':')) + html[j1:]
    i0 = html.index('window.WM_DATA=') + 15; _, n = json.JSONDecoder().raw_decode(html[i0:])
    html = html[:i0] + json.dumps(o, ensure_ascii=False, separators=(',', ':')) + html[i0 + n:]
    open(a.html, 'w', encoding='utf-8', newline='').write(html)
    with open(os.path.join(HERE, 'link_report.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['title', 'artist', 'spotify_uri', 'youtube_id', 'result', 'linked_to', 'performance_id']); w.writerows(sorted(rep, key=lambda r: (r[4], r[1])))
    print(dict(cnt), 'tracks now', len(o['tracks']))

if __name__ == '__main__':
    main()
