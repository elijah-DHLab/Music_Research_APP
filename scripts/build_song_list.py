"""Build the song_list workbook (recordings / works / artists / performance_artists / coverage_summary)
from the data embedded in index.html (WM_DATA + WM_V21).
Usage: python build_song_list.py [--html ../index.html] [--out song_list.xlsx]
The Google Sheet "song_list" in the project Drive folder is this workbook.
"""
import argparse, collections, json, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PERIODS = [('P0_לפני_המלחמה', '2023-01-01', '2023-10-06'), ('P1_חודשיים_ראשונים', '2023-10-07', '2023-12-07'),
           ('P2_12.2023-6.2024', '2023-12-08', '2024-06-30'), ('P3_7.2024-6.2025', '2024-07-01', '2025-06-30'),
           ('P4_7.2025-11.2026', '2025-07-01', '2026-12-31')]
# entities flagged in the 2026-11-18 correction report (empty once corrected)
ENTITY_REVIEW = {'wd:Q54919': 'VIAF (כנראה V של BTS)', 'wd:Q65666015': "הלם תרבות (כינוי 'סטילה')"}
SAME_ARTIST = {'wd:Q65666015': 'ENT_a75278fcf85d987b50'}  # used only for flag_possible_duplicate_group
J = ' | '.join
LYR = ['lyrics_source', 'lyrics_file', 'lyrics_retrieved_on', 'lyrics_quality']
AUD = ['audio_source', 'audio_key', 'audio_mode', 'audio_bpm', 'audio_confidence']


def load(path):
    html = open(path, encoding='utf-8').read()
    o, _ = json.JSONDecoder().raw_decode(html[html.index('window.WM_DATA=') + 15:])
    V, _ = json.JSONDecoder().raw_decode(html[html.index('window.WM_V21=') + 14:])
    return o, V


def build(o, V):
    E, P, T, D = V['entities'], V['performances'], o['tracks'], o['dates']; C = {c: k for k, c in enumerate(o['cols'])}
    # per-track statistics
    st = [dict(sp=collections.Counter(), sp_rank=None, peak=None, yt1=[set(), 0], yt2=[set(), 0]) for _ in T]
    for d, r, t, v, s in zip(o['d'], o['r'], o['t'], o['v'], o['s']):
        x = st[t]; day = D[d]
        if s == 0:
            x['sp'][day] += v; x['sp_rank'] = r if x['sp_rank'] is None else min(x['sp_rank'], r)
            if x['peak'] is None or v > x['peak'][1]: x['peak'] = (day, v)  # single chart row, not the day's sum
        else:
            y = x['yt1' if s == 1 else 'yt2']; y[0].add(day); y[1] += v
    lab = lambda e: (E[e].get('display') or E[e].get('he') or E[e].get('en')) if e in E else e
    uri_count = collections.Counter(u for t in T for u in set(t[C['uri']].split()))
    rec = []
    for k, t in enumerate(T):
        pid = t[C['performance_id']]; p = P.get(pid); arts = list(p['artists']) if p else []
        wid = (p or {}).get('work_id') or t[C['work_id']]
        sp = st[k]['sp']; peak = st[k]['peak']
        uris = sorted(t[C['uri']].split())
        rec.append({
            'performance_id': pid, 'work_id': wid or 'NOWORK_' + pid, 'title': t[C['name']], 'title_en': (p or {}).get('en', ''),
            'artist_entity_ids': J(arts), 'artist_labels': J(lab(a) for a in arts), 'n_artists': len(arts),
            'artist_raw_credit': t[C['artist']],
            'artist_link_status': 'no_identity_entry' if p is None else 'linked' if arts else 'fallback_only',
            'spotify_uris': J(uris), 'youtube_ref': 0, 'isrc': '', 'language': t[C['lang']], 'genre': t[C['genre']],
            'version': t[C['ver']], 'identity_status': t[C['identity_status']], 'review_status': t[C['review_status']],
            'records_merged': 1, 'work_id_missing': not wid, 'flag_no_title': not t[C['name']],
            'spotify_first_date': min(sp) if sp else '', 'spotify_last_date': max(sp) if sp else '', 'spotify_days': len(sp),
            'spotify_total_streams': sum(sp.values()), 'spotify_best_rank': st[k]['sp_rank'] if sp else '',
            'spotify_peak_daily_streams': peak[1] if peak else 0, 'spotify_peak_date': peak[0] if peak else '',
            'youtube_tracks_weeks': len(st[k]['yt1'][0]), 'youtube_tracks_total_views': st[k]['yt1'][1],
            'youtube_videos_weeks': len(st[k]['yt2'][0]), 'youtube_videos_total_views': st[k]['yt2'][1],
            '_dupkey': (t[C['name']], frozenset(SAME_ARTIST.get(a, a) for a in arts)),
            'flag_uri_in_several_recordings': any(uri_count[u] > 1 for u in uris), 'flag_merged_uris': len(uris) > 1,
            'flag_entity_review': J(ENTITY_REVIEW[a] for a in arts if a in ENTITY_REVIEW), '_sp': sp, '_arts': arts})
    dup = collections.Counter(r['_dupkey'] for r in rec if r['_dupkey'])
    for r in rec: r['flag_possible_duplicate_group'] = bool(r['_dupkey']) and dup[r['_dupkey']] > 1

    # works
    works = collections.OrderedDict()
    for r in rec: works.setdefault(r['work_id'], []).append(r)
    per_tot, wrows = {}, []
    for name, a, b in PERIODS:
        per_tot[name] = sum(v for r in rec for d, v in r['_sp'].items() if a <= d <= b)
    for wid, rs in works.items():
        arts = list(dict.fromkeys(a for r in rs for a in r['_arts']))
        sp = collections.Counter()
        for r in rs: sp.update(r['_sp'])
        w = {'work_id': wid, 'title': rs[0]['title'], 'n_recordings': len(rs), 'performance_ids': J(r['performance_id'] for r in rs),
             'artist_labels': J(lab(a) for a in arts), 'artist_entity_ids': J(arts),
             'languages': J(dict.fromkeys(r['language'] for r in rs if r['language'])), 'genres': J(dict.fromkeys(r['genre'] for r in rs if r['genre'])),
             'spotify_total_streams': sum(sp.values()), 'spotify_peak_daily_streams': max(r['spotify_peak_daily_streams'] for r in rs),
             'youtube_tracks_total_views': sum(r['youtube_tracks_total_views'] for r in rs),
             'youtube_videos_total_views': sum(r['youtube_videos_total_views'] for r in rs),
             'spotify_first_date': min(sp) if sp else '', 'spotify_last_date': max(sp) if sp else '', '_sp': sp}
        for name, a, b in PERIODS: w['_' + name] = sum(v for d, v in sp.items() if a <= d <= b)
        wrows.append(w)
    cov = []
    for name, a, b in PERIODS:
        ws = sorted((w for w in wrows if w['_' + name] > 0), key=lambda w: -w['_' + name]); tot = per_tot[name]; cum = 0; top = set()
        for w in ws:
            if cum >= 0.8 * tot: break
            top.add(w['work_id']); cum += w['_' + name]
        for w in wrows:
            if not w['_sp']: w['in_top80_' + name] = ''; w['share_' + name] = ''
            else: w['in_top80_' + name] = w['work_id'] in top; w['share_' + name] = w['_' + name] / tot if tot else 0
        cov.append({'period': name, 'from': a, 'to': b, 'works_in_period': len(ws), 'works_for_80pct': len(top), 'total_streams': tot})
    for w in wrows: w['in_any_top80'] = any(w['in_top80_' + n] is True for n, _, _ in PERIODS)
    top_any = {w['work_id'] for w in wrows if w['in_any_top80']}
    for r in rec: r['work_in_any_top80'] = r['work_id'] in top_any

    # artists and bridge table
    pa, ast = [], collections.defaultdict(lambda: dict(rec=0, works=set(), full=0, split=0.0))
    for r in rec:
        n = len(r['_arts']); s = r['spotify_total_streams']
        for i, a in enumerate(r['_arts'], 1):
            raw_wid = '' if r['work_id_missing'] else r['work_id']  # the bridge table keeps the source work_id (empty if none)
            pa.append({'performance_id': r['performance_id'], 'work_id': raw_wid, 'artist_entity_id': a, 'credit_order': i,
                       'n_artists_on_recording': n, 'spotify_streams_split_equal': s / n})
            x = ast[a]; x['rec'] += 1; x['works'].add(raw_wid); x['full'] += s; x['split'] += s / n
    arows = []
    for eid, e in E.items():
        x = ast[eid]; label = e.get('display') or e.get('he') or e.get('en') or ''
        arows.append({'artist_entity_id': eid, 'label_he': e.get('he', ''), 'label_en': e.get('en', ''), 'display': e.get('display', ''),
                      'aliases': J(e.get('aliases') or []), 'kind': e.get('kind', ''), 'wikidata': e.get('wikidata', ''), 'status': e.get('status', ''),
                      'flag_review': ENTITY_REVIEW.get(eid, ''), 'n_recordings': x['rec'], 'n_works': len(x['works']),
                      'spotify_streams_full_credit': x['full'], 'spotify_streams_split_equal': x['split'], 'flag_compound_label': ' - ' in label})

    key = lambda r: (-r['spotify_total_streams'], -(r['youtube_tracks_total_views'] + r['youtube_videos_total_views']))
    rec.sort(key=key); wrows.sort(key=key); arows.sort(key=lambda a: (-a['spotify_streams_full_credit'], -a['n_recordings']))
    RC = ['performance_id', 'work_id', 'title', 'title_en', 'artist_entity_ids', 'artist_labels', 'n_artists', 'artist_raw_credit', 'artist_link_status',
          'spotify_uris', 'youtube_ref', 'isrc', 'language', 'genre', 'version', 'identity_status', 'review_status', 'records_merged', 'work_id_missing',
          'flag_no_title', 'spotify_first_date', 'spotify_last_date', 'spotify_days', 'spotify_total_streams', 'spotify_best_rank',
          'spotify_peak_daily_streams', 'spotify_peak_date', 'youtube_tracks_weeks', 'youtube_tracks_total_views', 'youtube_videos_weeks',
          'youtube_videos_total_views', 'flag_possible_duplicate_group', 'flag_uri_in_several_recordings', 'flag_merged_uris', 'flag_entity_review',
          'work_in_any_top80'] + LYR + AUD
    WC = ['work_id', 'title', 'n_recordings', 'performance_ids', 'artist_labels', 'artist_entity_ids', 'languages', 'genres', 'spotify_total_streams',
          'spotify_peak_daily_streams', 'youtube_tracks_total_views', 'youtube_videos_total_views', 'spotify_first_date', 'spotify_last_date'] + \
         [c for n, _, _ in PERIODS for c in ('in_top80_' + n, 'share_' + n)] + ['in_any_top80'] + LYR
    tab = lambda rows, cols: pd.DataFrame([{c: r.get(c, '') for c in cols} for r in rows], columns=cols)
    return {'recordings': tab(rec, RC), 'works': tab(wrows, WC), 'artists': pd.DataFrame(arows), 'performance_artists': pd.DataFrame(pa),
            'coverage_summary': pd.DataFrame(cov)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--html', default=os.path.join(HERE, '..', 'index.html'))
    ap.add_argument('--out', default='song_list.xlsx'); a = ap.parse_args()
    tabs = build(*load(a.html))
    with pd.ExcelWriter(a.out) as xw:
        for k, df in tabs.items(): df.to_excel(xw, sheet_name=k, index=False)
    print({k: df.shape for k, df in tabs.items()})


if __name__ == '__main__':
    main()
