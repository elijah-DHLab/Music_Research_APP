# השלמת חוסרים — Spotify / YouTube

| קובץ | תפקיד |
|---|---|
| `gap_list.py` | מחשב את רשימת התאריכים החסרים והחשודים (מ־index.html או מקובצי ה־Drive) |
| `missing_spotify_days.csv` | 502 ימים חסרים (עד 2026-11-14) |
| `missing_youtube_weeks.csv` | 80 שבועות-צילום משוכפלים (2023-01-05…2023-10-05, ×2 קבצים) + 2026-11-12 |
| `rank_holes.csv` | שבועות עם דירוג חסר (למשל 89) |
| `fetch_spotify.py` | מוריד רק את הימים החסרים; דורש טוקן של התחברות אישית ל־charts.spotify.com; שומר רק ימים עם 200 דירוגים מלאים |
| `fetch_youtube.py` | מוריד את כל השבועות מ־charts.youtube.com לפי מזהה שבוע מפורש; בודק תאריך, 100 דירוגים ושאין שבוע זהה לאחר |
| `sample_check_spotify.py` | בדיקה מדגמית של ימי Spotify קיימים מול המקור |
| `assemble_v2.py` | בונה את קובצי ה־V2 (עמודת `fill_source`: unchanged / added / corrected) ומאמת |
| `update_app_data.py` | מעדכן את הנתונים המוטמעים ב־index.html בלי לאבד את שדות הזהות של V2.1 |
| `link_new_tracks.py` | מקשר הקלטות חדשות לביצועים/מבצעים קיימים באפליקציה → `link_report.csv` |
| `update_runtime.py` | בונה מחדש את `data/v2/runtime` ו־`data/recordings.csv` |
| `update_master.py` | בונה את קובץ היצירות והמבצעים V2 ואת `data/catalog_master_import.csv` |
| `wikidata_enrich.py` | מאתר מבצעים חדשים ב־Wikidata (התאמת שם מדויקת + עיסוק מוזיקלי/הרכב) → `wikidata_enrich.json` |
| `apply_performers.py` | מחיל את המטא־דאטה על גיליון המבצעים V2 ועל האפליקציה |
| `fix_identities_2026_11_18.py` | תיקוני זהויות ונתונים מ־18.11.2026 (ראו `CHANGELOG.md`); להריץ אחריו `update_runtime.py` |
| `validate_app.py` | בדיקות קבועות על index.html (VIAF/פריטים דחויים, ביצועים מפוצלים, קרדיט מורכב, שורות כפולות, תרשימים מלאים); exit 1 בכשל |
| `merge_validate.py` | ממזג את מה שהורד לקובצי ה־Drive, מוסיף עמודת `fill_source`, ועוצר (exit 1) אם נשארו חורים/שבועות זהים |

## סדר הרצה
1. להוריד מה־Drive את 3 הגיליונות כ־xlsx לתיקייה אחת (למשל `raw/`).
2. `python gap_list.py --raw raw` — אימות הרשימה מול המקור.
3. `$env:SPOTIFY_TOKEN='...'; python fetch_spotify.py` — חוזרים עם טוקן חדש בכל פעם שמתקבל 401 (ההתקדמות נשמרת).
4. YouTube: קובצי שבוע בפורמט הגיליון אל `fetched/youtube_tracks/` ו־`fetched/youtube_videos/`.
5. `python merge_validate.py --raw raw` → `merged/` + `merged_report.json`.
6. להעלות את `merged/*.xlsx` ל־Drive במקום הקיימים, ולהריץ `scripts/build_data.py`.

## הרצה שבוצעה ב־16.11.2026
* Spotify: 502 ימים הורדו (100% עם 200 דירוגים); 30/30 ימים קיימים במדגם זהים למקור.
* YouTube: 202 שבועות × 2; 156 זהים לקיים, 41 נוספו (כולל 40 השבועות המשוכפלים של 2023), 5 תוקנו (שיוויון דירוג שבו נשמטה שורה).
* דירוג "חסר" כמו 89 = שוויון במקור (שני שירים באותו דירוג); זה מצב המקור ולא תקלה.
* `assemble_v2.py --spotify-old raw/Spotify-all_israel_charts_2023_to_today.xlsx` → `v2/*_V2.xlsx`, 0 בעיות אימות.
* `update_app_data.py` → index.html: 323,170 תצפיות, 895 ביצועים חדשים לבדיקה (`gapfill_new_unmatched`).
* `update_master.py` → `v2/all_works_and_performers_master_list_with_ids_V2.xlsx`: 4,927 יצירות (653 חדשות), 1,818 מבצעים (188 חדשים, דורשים Wikidata). הקטלוג המקורי לא ספר את השבועות החשודים — לכן מופחתות רק שורות שנספרו.
* מבצעים חדשים (188): 88 הושלמו מ־Wikidata, 6 זוהו כמבצע קיים באיות אחר, 94 לא נמצאו (`performers_not_found.csv`). נדחו ידנית 5 התאמות שגויות (`REJECT` ב־wikidata_enrich.py).
