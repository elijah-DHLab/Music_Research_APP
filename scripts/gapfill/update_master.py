"""Build all_works_and_performers_master_list_with_ids_V2.xlsx from the original master + the gap-fill delta.

Works sheet rows are (work_name, performer_name-as-in-source) with per-source appearance counts and platform ids.
Delta = rows of replaced periods in the ORIGINAL source files (subtracted) and rows of added/corrected periods in
the V2 files (added). Each source row is attributed to a works row by:
  1. platform id present in the row (prefer same performer string, then same work title);
  2. same normalized work title AND performer string -> the id is added to that row;
  3. otherwise a new works row (gapfill_status = new).
Performers sheet is recomputed from the works sheet (split performer_name on ','); new performer names are appended,
with Wikidata metadata copied when the name resolves to a known V21 entity / existing performer with that Wikidata id.
Also regenerates data/catalog_master_import.csv.
Usage: python update_master.py
"""
import collections, csv, json, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from link_new_tracks import cl, nk
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
CNT = ['spotify_daily_count', 'spotify_weekly_count', 'youtube_tracks_count', 'youtube_videos_count']
SRC = [('spotify_daily_count', 'Spotify-all_israel_charts_2023_to_today', 'chart_date', 'track_name', 'uri'),
       ('youtube_tracks_count', 'all_israel_youtube_charts_2023_to_today-TRACKS', 'end_date', 'track_name', 'youtube_url'),
       ('youtube_videos_count', 'all_israel_youtube_videos_2023_to_today-VIDEOS', 'end_date', 'video_title', 'video_id')]
UNTITLED = '(ללא שם יצירה)'

def pid(v):
    v = str(v or '')
    if v.startswith('spotify:track:'): return v
    m = re.search(r'v=([\w-]{11})', v)
    return m.group(1) if m else (v if re.fullmatch(r'[\w-]{11}', v) else None)

def clean_title(t):
    t = cl(t)
    t = re.sub(r'(?i)\s*[\(\[]\s*(prod\.?|music by|מתוך|official|lyric|קליפ|video|audio)[^\)\]]*[\)\]]', '', t)
    t = re.sub(r'(?i)\s*(official( music)? video|lyric video|קליפ רשמי)$', '', t)
    return t.split(' | ')[0].strip(' -–|') or t

def main():
    raw = os.path.join(HERE, 'raw'); v2 = os.path.join(HERE, 'v2')
    x = pd.ExcelFile(os.path.join(raw, 'all_works_and_performers_master_list_with_ids.xlsx'))
    W = x.parse(0, dtype=str).fillna(''); P = x.parse(1, dtype=str).fillna('')
    for c in CNT + ['total_appearances']: W[c] = W[c].astype(int)
    W['gapfill_status'] = 'unchanged'
    ids = lambda r: re.findall(r'spotify:track:\w+', r['spotify_uris']) + re.findall(r'(?<![\w-])[\w-]{11}(?![\w-])', r['youtube_video_ids'])
    by_id = collections.defaultdict(list); by_wp = {}
    for k, r in W.iterrows():
        for i in ids(r): by_id[i].append(k)
        by_wp.setdefault((nk(r.work_name), nk(r.performer_name)), k)
    rows = W.to_dict('records'); st = collections.Counter()

    def attr(title, artist, p):
        title = title or ''; ck = (nk(clean_title(title)) if title else nk(UNTITLED), nk(artist))
        cand = by_id.get(p, []) if p else []
        if cand:
            for k in cand:
                if nk(rows[k]['performer_name']) == ck[1]: return k
            for k in cand:
                if nk(rows[k]['work_name']) == ck[0]: return k
            return cand[0]
        k = by_wp.get(ck)
        if k is None:
            rows.append({c: '' for c in W.columns} | {c: 0 for c in CNT + ['total_appearances']} |
                        {'work_name': clean_title(title) if title else UNTITLED, 'performer_name': artist, 'gapfill_status': 'new'})
            k = len(rows) - 1; by_wp[ck] = k; st['new_rows'] += 1
        if p:
            r = rows[k]; fld = 'spotify_uris' if p.startswith('spotify:') else 'youtube_video_ids'
            if p not in r[fld]: r[fld] = (r[fld] + ' | ' + p) if r[fld] else p
            by_id[p].append(k)
        return k

    for cc, name, dc, tc, idc in SRC:
        v = pd.read_excel(os.path.join(v2, name + '_V2.xlsx'), dtype=str, keep_default_na=False)
        repl = set(v.loc[v.fill_source.isin(['added', 'corrected']), dc])
        o = pd.read_excel([os.path.join(raw, f) for f in os.listdir(raw) if f.startswith(name)][0], dtype=str, keep_default_na=False)
        o[dc] = o[dc].str[:10]
        old_counted = o[o[dc].isin(repl)]  # the original master already excluded suspect rows -> subtract only counted ones
        if 'is_suspect_duplicate' in o: old_counted = old_counted[old_counted.is_suspect_duplicate.str.upper() != 'TRUE']
        for sign, df in ((-1, old_counted), (1, v[v[dc].isin(repl)])):
            for _, r in df.iterrows():
                k = attr(r[tc], r['artist_names'], pid(r[idc])); rows[k][cc] += sign; st[f'{cc}{"+" if sign > 0 else "-"}'] += 1
                if rows[k]['gapfill_status'] == 'unchanged': rows[k]['gapfill_status'] = 'updated'
                if sign > 0 and r[tc]:
                    var = rows[k]['original_titles_variants']
                    if r[tc] not in var.split(' | '): rows[k]['original_titles_variants'] = (var + ' | ' + r[tc]) if var else r[tc]
    W = pd.DataFrame(rows)
    neg = (W[CNT] < 0).any(axis=1).sum()
    W['total_appearances'] = W[CNT].sum(axis=1)
    W['performers_count_for_this_work'] = W.groupby('work_name')['work_name'].transform('size').astype(str)
    W['youtube_urls'] = W.youtube_video_ids.map(lambda s: ' | '.join('https://www.youtube.com/watch?v=' + i for i in re.findall(r'(?<![\w-])[\w-]{11}(?![\w-])', s)))
    # rows that dropped to 0 (only appeared in the fake 2023 YouTube snapshots) are kept for id stability, flagged
    W.loc[(W.total_appearances == 0) & (W.gapfill_status != 'unchanged'), 'gapfill_status'] = 'zero_after_correction'
    # performers
    split = lambda s: [a.strip() for a in s.split(',') if a.strip()]
    agg = collections.defaultdict(lambda: {'works': set(), 'rows': 0, 'tot': 0, 'sd': 0, 'sw': 0, 'yt': 0, 'yv': 0})
    for _, r in W.iterrows():
        for a in split(r.performer_name):
            if a.startswith('(ללא שם'): continue  # placeholder, not a performer (as in the original sheet)
            g = agg[a]; g['works'].add(r.work_name); g['rows'] += 1; g['tot'] += r.total_appearances
            g['sd'] += r.spotify_daily_count; g['sw'] += r.spotify_weekly_count; g['yt'] += r.youtube_tracks_count; g['yv'] += r.youtube_videos_count
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read(); j = html.index('window.WM_V21=') + 14
    V, _ = json.JSONDecoder().raw_decode(html[j:]); ent_by_alias = {}
    for e in V['entities'].values():
        for s in [e.get('he'), e.get('en'), e.get('display')] + list(e.get('aliases') or []):
            if s and e.get('wikidata'): ent_by_alias.setdefault(nk(s), e)
    P['gapfill_status'] = 'unchanged'; known = set(P.performer_name); by_wd = {r.wikidata_id: r for _, r in P.iterrows() if r.wikidata_id}
    new = []
    for a in agg:
        if a in known: continue
        row = {c: '' for c in P.columns}; row.update(performer_name=a, gapfill_status='new')
        e = ent_by_alias.get(nk(a))
        if e:
            src = by_wd.get(e['wikidata'])
            if src is not None:
                for c in P.columns[8:]: row[c] = src[c]
            else: row.update(wikidata_id=e['wikidata'], wikidata_url='https://www.wikidata.org/wiki/' + e['wikidata'], hewiki_title=e.get('he', ''))
        new.append(row)
    P = pd.concat([P, pd.DataFrame(new)], ignore_index=True)
    for k, r in P.iterrows():
        g = agg.get(r.performer_name)
        vals = dict(works_count=len(g['works']), rows_count=g['rows'], total_appearances=g['tot'], spotify_daily_total=g['sd'], spotify_weekly_total=g['sw'],
                    youtube_tracks_total=g['yt'], youtube_videos_total=g['yv']) if g else dict(works_count=0, rows_count=0, total_appearances=0, spotify_daily_total=0, spotify_weekly_total=0, youtube_tracks_total=0, youtube_videos_total=0)
        if r.gapfill_status == 'unchanged' and str(vals['total_appearances']) != str(r.total_appearances): P.at[k, 'gapfill_status'] = 'updated'
        for c, val in vals.items(): P.at[k, c] = val
    # keep original row order (MASTER:<row> ids stay stable); new rows are appended at the end
    out = os.path.join(v2, 'all_works_and_performers_master_list_with_ids_V2.xlsx')
    with pd.ExcelWriter(out) as xw:
        W.to_excel(xw, sheet_name='all_works_and_performers_master', index=False); P.to_excel(xw, sheet_name='performers', index=False)
    # catalog_master_import.csv for the app package
    with open(os.path.join(ROOT, 'data', 'catalog_master_import.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['catalog_row_id', 'source_row', 'work_name_source', 'performer_name_source', 'spotify_uris_source', 'youtube_video_ids_source', 'original_titles_variants', 'total_appearances_source', 'mapping_status'])
        for n, (_, r) in enumerate(W.iterrows(), start=2):
            w.writerow([f'MASTER:{n}', n, r.work_name, r.performer_name, r.spotify_uris, r.youtube_video_ids, r.original_titles_variants, r.total_appearances, 'not_yet_verified'])
    print(dict(st), 'negative-count rows', neg)
    print('works', len(W), dict(collections.Counter(W.gapfill_status)), 'performers', len(P), dict(collections.Counter(P.gapfill_status)))
    print('check totals: works', int(W.total_appearances.sum()), ' sources', int(W.spotify_daily_count.sum()), int(W.youtube_tracks_count.sum()), int(W.youtube_videos_count.sum()))

if __name__ == '__main__':
    main()
