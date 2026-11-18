"""Identity and data corrections of 2026-11-18 (report: "דוח תיקונים לקופיילוט").

Patches the embedded window.WM_V21 / window.WM_DATA in index.html, plus data/v2/runtime/performances.json,
data/v2/runtime/entities.json, data/recordings.csv and data/works.csv. Run update_runtime.py afterwards.
Idempotent: a second run detects qa.fix_2026_11_18 and exits.

  1. Wrong Wikidata links  -> correct item (each verified on wikidata.org on 2026-11-18):
       V (BTS)        Q54919 (VIAF authority file)          -> Q18388296
       Static         Q15121683 (album by Cults)            -> Q26833615
       Ness           Q290264 (French rapper Nessbeal)       -> Q118289471 (+ local "נס", "Daniel Ness")
       Stilla         ENT_a752... / Q65666015 (הלם תרבות)    -> Q118289474
       Black Sabbath  Q742626 (Heaven & Hell)               -> Q47670
       Forever Tel-Aviv  Q5469449 (2007 album)               -> local entity (no Wikidata item)
  2. Duplicate entities merged (Ben El, Or Lasri, ...); compound credit entities ("A - B") removed where both
     artists are already credited, or mapped to the one artist they denote.
  3. Ness & Stilla performances that were split in two (Hebrew vs Latin credit) merged into one performance/track.
  4. Same track twice on one chart day/week (two URIs/videos merged into one track): one row per (source, date,
     track) -- value = sum, rank/peak = best of the two. Listed in qa.merged_duplicate_rows.
  5. Spotify 2026-07-13..18 row without metadata (spotify:track:3vuTjROEdeCq8V3c1cvlxJ) = "Self Aware" (Temper City):
     the previous_rank / days_on_chart chain continues exactly from 07-12 and into 07-19. Rows added.
     Rows that cannot be identified are listed in data/unresolved_rows.csv.
"""
import collections, csv, glob, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
RT = os.path.join(ROOT, 'data', 'v2', 'runtime'); FETCHED = os.path.join(HERE, 'fetched')
TAG = 'manual_fix_2026_11_18'
FTA = 'ENT_' + hashlib.sha1('Forever Tel-Aviv'.encode()).hexdigest()[:18]

NEW = {  # entities created by this fix
    'wd:Q18388296': dict(he='V', en='V', kind='person', aliases=['V', 'Kim Taehyung', 'קים טה-היונג']),
    'wd:Q26833615': dict(he='סטטיק', en='Static', kind='person', aliases=['Static', 'סטטיק', 'Statboy']),
    'wd:Q118289471': dict(he='נס', en='Ness', kind='person', aliases=['Ness', 'נס', 'Daniel Ness']),
    'wd:Q118289474': dict(he='סטילה', en='Stilla', kind='person', aliases=['STILLA', 'Stilla', 'סטילה']),
    'wd:Q47670': dict(he="בלאק סאבת'", en='Black Sabbath', kind='ensemble', aliases=['Black Sabbath', "בלאק סאבת'"]),
    FTA: dict(he='', en='Forever Tel-Aviv', kind='unknown', aliases=['Forever Tel-Aviv', 'Forever Tel Aviv'], wikidata=''),
}
REMAP = {
    'wd:Q54919': 'wd:Q18388296', 'wd:Q15121683': 'wd:Q26833615',
    'wd:Q290264': 'wd:Q118289471', 'ENT_18d1faf13078ecec50': 'wd:Q118289471', 'ENT_356a2de2613e6763db': 'wd:Q118289471',
    'ENT_a75278fcf85d987b50': 'wd:Q118289474', 'wd:Q65666015': 'wd:Q118289474',
    'wd:Q742626': 'wd:Q47670', 'wd:Q5469449': FTA,
    # duplicates of the same artist
    'ENT_3497668f68ebd66145': 'wd:Q26265599', 'ENT_82178659c9e27ab8d7': 'wd:Q26265599',          # Ben El / בן אל
    'ENT_501c593a9fe556fd45': 'wd:Q46247565',                                                      # Static And Ben El
    'ENT_9d0d1832f985efa3f6': 'ENT_bef5497f2bc98684b6', 'ENT_e05ee798aad45b6444': 'ENT_bef5497f2bc98684b6',
    'ENT_7d57f4197170e872db': 'ENT_bef5497f2bc98684b6',                                            # אור לסרי
    'ENT_b0ae95658990604258': 'ENT_99bef10b093e4c55d1',                                            # יובל מזרחי
    'ENT_4389c421654a2e98cf': 'ENT_73e69cce027cabfc5d',                                            # מני הולנדר
    'ENT_5e37c7fc49119ebfa5': 'wd:Q5445674',                                                       # פסטיגל
    'ENT_2f048d5e530f3b7504': 'ENT_baa9dec3b7b9dd5f43',                                            # Mohamed El Shiekh
    'ENT_08487797faf7da735b': 'ENT_67e6fd51d53eda8e5b',                                            # כפיר עזרן
    'ENT_14d78f103f474ab7b7': 'wd:Q139718142',                                                     # מישל פרו
    'ENT_eac7498d580a8d90d3': 'ENT_052448bd4529351494', 'ENT_118c2ce3dd4bf3f986': 'ENT_052448bd4529351494',  # يزن حمدان
    'ENT_d9a7e67b7749d10b5b': 'wd:Q6816901',   # "יניב בן משיח - Moshe Peretz": Moshe Peretz is already credited
}
NO_ALIAS = {'VIAF', 'הלם תרבות', 'Heaven & Hell'}  # aliases of wrong items that must not follow the remap
# compound "A - B" entities whose two artists are already credited separately on every performance
DROP = {'ENT_9f9ef9086064debea8', 'ENT_9aec4e3da5663fd638', 'ENT_48e36916065d24bdf4', 'ENT_098a4e11c1878fbf8e',
        'ENT_7891ded9b6d0e55158', 'ENT_6445343c68f9a01a3b', 'ENT_ccbc7eec1b7b9e4cb6'}
META = {  # track metadata (same columns as apply_performers.app_meta) for tracks whose lead artist changed
    'wd:Q18388296': dict(gender='זכר', country='קוריאה הדרומית', genre='קיי-פופ', city='טגו', ent='אדם', dec='1990s',
                         genres='קיי-פופ | נאו סול', birth='1995', desc='זמר, מלחין ורקדן דרום-קוריאני, חבר בלהקת הקיי-פופ BTS'),
    'wd:Q26833615': dict(gender='זכר', country='ישראל', genre='מוזיקת פופ', city='', ent='אדם', dec='1990s',
                         genres='מוזיקת פופ', birth='1990', desc='זמר פופ וראפר ישראלי'),
    'wd:Q118289471': dict(gender='נקבה', country='ישראל', genre='', city='אשדוד', ent='אדם', dec='2000s',
                          genres='', birth='2002', desc='ראפרית ישראלית'),
    'wd:Q118289474': dict(gender='זכר', country='ישראל', genre='', city='', ent='אדם', dec='1990s',
                          genres='', birth='1998', desc='ראפר ישראלי'),
    'wd:Q47670': dict(gender='', ent='להקה / הרכב', dec='', birth='', desc='להקת הבי מטאל בריטית'),
}
NESS_TITLES = ['תיק קטן', 'חרבו דרבו', 'באמפרים', 'מי כמוני', 'מונולוג', 'מגדלים', 'רשימת קניות']
LIVE_PAIR = ('PERF_142fb998801bf7d140', 'PERF_bd95f288eeac08691c')  # "מגדלים - לייב מבריכת הסולטן" = "מגדלים (Live)"
SELF_AWARE = ('PERF_9e7ee426e743441729', 'spotify:track:3vuTjROEdeCq8V3c1cvlxJ')
dedupe = lambda xs: list(dict.fromkeys(xs))


def main():
    path = os.path.join(ROOT, 'index.html'); html = open(path, encoding='utf-8').read()
    j0 = html.index('window.WM_V21=') + 14; V, m = json.JSONDecoder().raw_decode(html[j0:])
    i0 = html.index('window.WM_DATA=') + 15; o, n = json.JSONDecoder().raw_decode(html[i0:])
    if 'fix_2026_11_18' in o['qa']: print('already applied'); return
    E, P = V['entities'], V['performances']; T = o['tracks']; C = {c: k for k, c in enumerate(o['cols'])}
    log = collections.Counter()

    # ---- 1-2. entities ----
    for eid, d in NEW.items():
        E[eid] = {'he': d['he'], 'en': d['en'], 'display': d['he'] or d['en'], 'aliases': list(d['aliases']), 'kind': d['kind'],
                  'wikidata': d.get('wikidata', eid[3:] if eid.startswith('wd:') else ''), 'status': TAG}
    for old, new in REMAP.items():
        src, dst = E.get(old), E[new]
        if not src: continue
        if new not in NEW:  # merge into an existing entity: carry labels/aliases
            if not dst.get('en') and src.get('en') and ' - ' not in src['en']: dst['en'] = src['en']
        dst['aliases'] = dedupe(dst['aliases'] + [a for a in src.get('aliases', []) + [src.get('display', '')] if a and a not in NO_ALIAS])
    if 'ENT_052448bd4529351494' in E: E['ENT_052448bd4529351494']['en'] = 'Yazan Hamdan'
    # September: "Earth, Wind & Fire" split on its commas into extra entities "Wind" / "Fire"
    split_ewf = {k for k, e in E.items() if e.get('display') in ('Wind', 'Fire') and not e.get('wikidata')}
    if 'wd:Q28974' in E: E['wd:Q28974']['en'] = 'Earth, Wind & Fire'; E['wd:Q28974']['aliases'] = ['Earth, Wind & Fire']

    old_lead = {}
    for pid, p in P.items():
        a0 = p['artists'][:1]
        kept = [x for x in p['artists'] if x not in DROP and not (x in split_ewf and 'wd:Q28974' in p['artists'])]
        if len(kept) < len(p['artists']): log['compound_removed_from_perf'] += 1
        new = dedupe(REMAP.get(x, x) for x in kept)
        if new != p['artists']: log['perf_artists_changed'] += 1; old_lead[pid] = a0[0] if a0 else ''
        p['artists'] = new
    used = {x for p in P.values() for x in p['artists']}
    for k in list(E):
        if (k in REMAP or k in DROP or k in split_ewf) and k not in used: del E[k]; log['entities_removed'] += 1

    # ---- 3. merge split Ness & Stilla performances (one track row per performance) ----
    pairs = []
    for title in NESS_TITLES:
        ids = [pid for pid, p in P.items() if p['title'] == title and 'wd:Q118289471' in p['artists']]
        if len(ids) == 2:
            ids.sort(key=lambda x: 'wd:Q118289474' != P[x]['artists'][0])  # keep the STILLA-credited (Spotify) record
            pairs.append(tuple(ids))
    if LIVE_PAIR[0] in P and LIVE_PAIR[1] in P: pairs.append(LIVE_PAIR)
    row_of = {t[C['performance_id']]: k for k, t in enumerate(T)}
    drop_rows, remap_rows, dropped_perfs = set(), {}, {}
    for keep, drop in pairs:
        kp, dp = P[keep], P[drop]
        kp['artists'] = dedupe(kp['artists'] + dp['artists'])
        kp['aliases'] = dedupe(kp.get('aliases', []) + dp.get('aliases', []) + [dp['title']])
        kr, dr = T[row_of[keep]], T[row_of[drop]]
        for c in ('uri', 'yt'): kr[C[c]] = ' '.join(dedupe((kr[C[c]] + ' ' + dr[C[c]]).split()))
        kr[C['collab']] = 'שיתוף פעולה'
        remap_rows[row_of[drop]] = row_of[keep]; drop_rows.add(row_of[drop]); dropped_perfs[drop] = (keep, dp.get('work_id', ''))
        del P[drop]; log['performances_merged'] += 1

    # track metadata where the lead artist was a wrong item
    for t in T:
        pid = t[C['performance_id']]; p = P.get(pid)
        if p and pid in old_lead and old_lead[pid] in REMAP and p['artists'] and p['artists'][0] in META:
            for c, v in META[p['artists'][0]].items(): t[C[c]] = v
            log['track_metadata_fixed'] += 1
    # fallback_artist text of changed performances
    lab = lambda x: E[x].get('display') or E[x].get('en') if x in E else x
    for pid in old_lead:
        if pid in P: P[pid]['fallback_artist'] = ' · '.join(lab(x) for x in P[pid]['artists'])

    # ---- observations ----
    F = ['d', 'r', 't', 'v', 'pk', 'pr', 'dc', 's', 'status']; D = o['dates']
    obs = [dict(zip(F, x)) for x in zip(*(o[f] for f in F))]
    for x in obs: x['t'] = remap_rows.get(x['t'], x['t'])
    # 5. Self Aware rows (Spotify 2026-07-13..18)
    sa = row_of[SELF_AWARE[0]]; added = 0
    for f in sorted(glob.glob(os.path.join(FETCHED, 'spotify', '2026-07-1*.csv'))):
        for r in csv.DictReader(open(f, encoding='utf-8-sig')):
            if r['uri'] == SELF_AWARE[1] and not r['track_name']:
                obs.append(dict(d=D.index(r['chart_date']), r=int(r['rank']), t=sa, v=int(r['streams']), pk=int(r['peak_rank']),
                                pr=int(r['previous_rank'] or 0), dc=int(r['days_on_chart']), s=0, status=0)); added += 1
    T[sa][C['uri']] = ' '.join(dedupe(T[sa][C['uri']].split() + [SELF_AWARE[1]]))
    log['self_aware_rows_added'] = added
    # 4. one row per (source, date, track)
    groups = collections.defaultdict(list)
    for x in obs: groups[(x['s'], x['d'], x['t'])].append(x)
    merged_log, out = [], []
    for key, xs in groups.items():
        if len(xs) == 1: out.append(xs[0]); continue
        xs.sort(key=lambda x: x['r']); b = dict(xs[0])
        b['v'] = sum(x['v'] for x in xs); b['pk'] = min((x['pk'] for x in xs if x['pk']), default=0)
        b['status'] = max(x['status'] for x in xs); out.append(b)
        merged_log.append([key[0], D[key[1]], T[key[2]][C['performance_id']], [x['r'] for x in xs], [x['v'] for x in xs]])
    log['duplicate_rows_merged'] = sum(len(m[3]) - 1 for m in merged_log)
    # drop merged track rows and reindex
    keep_idx = [k for k in range(len(T)) if k not in drop_rows]; new_idx = {k: j for j, k in enumerate(keep_idx)}
    o['tracks'] = [T[k] for k in keep_idx]
    for x in out: x['t'] = new_idx[x['t']]
    out.sort(key=lambda x: (x['s'], x['d'], x['r']))
    for f in F: o[f] = [x[f] for x in out]

    # unresolved rows: untitled rows kept in the app + untitled source rows that are not in the app
    T2 = o['tracks']; unres = []
    for x in out:
        if not T2[x['t']][C['name']]: unres.append([x['s'], D[x['d']], x['r'], x['v'], 'yes', 'untitled in source (removed video / no id); counted in totals as an untitled item'])
    in_app = {(r[0], r[1], r[2]) for r in unres}
    for src, sub, title in ((1, 'youtube_tracks', 'track_name'), (2, 'youtube_videos', 'video_title'), (0, 'spotify', 'track_name')):
        for f in sorted(glob.glob(os.path.join(FETCHED, sub, '*.csv'))):
            for r in csv.DictReader(open(f, encoding='utf-8-sig')):
                if r.get(title): continue
                if src == 0 and r.get('uri') == SELF_AWARE[1]: continue
                day = r.get('end_date') or r.get('chart_date')
                if (src, day, int(r['rank'])) in in_app: continue
                unres.append([src, day, int(r['rank']), int(float(r.get('views') or r.get('streams') or 0)), 'no',
                              'untitled in source with no id; not in the app'])
    SRC = {0: 'spotify_daily', 1: 'youtube_tracks_weekly', 2: 'youtube_videos_weekly'}
    with open(os.path.join(ROOT, 'data', 'unresolved_rows.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['source', 'date', 'rank', 'value', 'in_app', 'reason'])
        for r in sorted(unres, key=lambda r: (r[0], r[1], r[2])): w.writerow([SRC[r[0]]] + r[1:])
    log['unresolved_rows'] = len(unres)

    o['qa']['fix_2026_11_18'] = dict(log)
    o['qa']['merged_duplicate_rows'] = merged_log
    o['qa']['merged_performances'] = {d: k for d, (k, _) in dropped_perfs.items()}
    html = html[:j0] + json.dumps(V, ensure_ascii=False, separators=(',', ':')) + html[j0 + m:]
    i0 = html.index('window.WM_DATA=') + 15; _, n = json.JSONDecoder().raw_decode(html[i0:])
    html = html[:i0] + json.dumps(o, ensure_ascii=False, separators=(',', ':')) + html[i0 + n:]
    open(path, 'w', encoding='utf-8', newline='').write(html)

    # ---- companion catalog files ----
    dump = lambda p, x: json.dump(x, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    pf = json.load(open(os.path.join(RT, 'performances.json'), encoding='utf-8'))
    pf = [r for r in pf if r['id'] not in dropped_perfs]
    for r in pf:
        if r['id'] in P: r['entities'] = list(P[r['id']]['artists']) if r['id'] in old_lead or r['id'] in {k for k, _ in dropped_perfs.values()} \
            else dedupe(REMAP.get(x, x) for x in r.get('entities', []) if x not in DROP)
    dump(os.path.join(RT, 'performances.json'), pf)
    ej = json.load(open(os.path.join(RT, 'entities.json'), encoding='utf-8')); have = set()
    ej2 = []
    for r in ej:
        if r['id'] in REMAP or r['id'] in DROP: continue
        ej2.append(r); have.add(r['id'])
    for eid in NEW:
        if eid not in have: ej2.append({'id': eid, 'name': E[eid]['display'], 'kind': E[eid]['kind'], 'review': TAG, 'genres_source': ''})
    dump(os.path.join(RT, 'entities.json'), ej2)
    rp = os.path.join(ROOT, 'data', 'recordings.csv'); rows = list(csv.reader(open(rp, encoding='utf-8-sig')))
    with open(rp, 'w', newline='', encoding='utf-8-sig') as fh: csv.writer(fh).writerows(r for r in rows if r[0] not in dropped_perfs)
    live_works = {p.get('work_id') for p in P.values()}
    wp = os.path.join(ROOT, 'data', 'works.csv'); rows = list(csv.reader(open(wp, encoding='utf-8-sig')))
    gone = {w for _, w in dropped_perfs.values() if w and w not in live_works}
    with open(wp, 'w', newline='', encoding='utf-8-sig') as fh: csv.writer(fh).writerows(r for r in rows if r[0] not in gone)
    print(dict(log), 'observations', len(out), 'tracks', len(T2))


if __name__ == '__main__':
    main()
