/* Bilingual interface layer. Data values, URLs, downloads and user input never change. */
let locale=(()=>{try{return localStorage.getItem('wm_language')==='en'?'en':'he'}catch(e){return 'he'}})();
const dictionary={
'האזנה בישראל בזמן המלחמה – ספוטיפיי ויוטיוב':'Listening in Israel During the War – Spotify & YouTube',
'טוען…':'Loading…','בדיקת איכות נתונים: מקור אחד זוהה כלא תקין. פרטים בלשונית הסבר.':'Data-quality alert: a source did not pass validation. See Help.',
'ציר זמן חוקר · גררו לזום, לחצו על נקודה לפירוט':'Research timeline · drag to zoom, click a point to inspect', 'טווח קודם':'Previous range','הצג את כל התקופה':'Show full timeline','גרירה יוצרת תקופה להשוואה':'Drag to create comparison period','אחוזים':'Percentages','מספרים מוחלטים':'Absolute numbers','כללי':'Overview','השוואת תקופות':'Compare periods','שאלות':'Research questions','שירים':'Songs','יוצרים':'Artists','פילוחים':'Explore','אירועים':'Events','נתונים ומקורות':'Data & sources','הסבר':'Help',
'שיר':'Song','יוצר':'Artist','שפה':'Language','ז׳אנר':'Genre','מגדר':'Gender','מדינה':'Country','עיר מוצא':'Origin city','לייבל':'Label','סוג יוצר':'Artist type','עשור לידה':'Birth decade','גרסה':'Version','סולו/שיתוף':'Solo / collaboration','מקור':'Source','תקופה (מוגדרת)':'Defined period','חודש':'Month','שנה':'Year',
'סכום streams/views (לא משווים בין פלטפורמות)':'Total streams/views (not comparable across platforms)',
'מס׳ הופעות בטופ':'Chart appearances','שירים שונים':'Unique songs','כניסות חדשות':'New entries','דירוג ממוצע':'Average rank','דירוג הכי טוב':'Best rank','ממוצע ימים/שבועות בטופ':'Average days/weeks on chart',
'בחירת סדרות להשוואה – אפשר לבחור שתיים, שלוש או יותר':'Choose series to compare — select two, three or more',
'חיפוש שפה, ז׳אנר, שיר או יוצר':'Search language, genre, song or artist',
'הצג את המובילים':'Show top series','נקה בחירה':'Clear selection',
'אין סדרות מתאימות':'No matching series','אין נתונים לסינון הנוכחי':'No data for the current filters',
'נקה בחירה/הסתרה':'Reset selection / visibility','נתח בתוך כל מקור (%) – מומלץ להשוואה':'Share within each source (%) — recommended',
'ערכים גולמיים – לא לחיבור בין מקורות':'Raw values — do not add across sources','אינדקס (תקופה ראשונה=100)':'Index (first period = 100)','ציר לוגריתמי':'Logarithmic scale',
'פילוח':'Group by','פיצול משני':'Split by','מדד':'Measure','גרף':'Chart','נרמול':'Normalization','זמן':'Time','סדרות מובילות':'Top series',
'קווים':'Lines','שטח מוערם':'Stacked area','שטח 100%':'100% stacked area','שבוע (מיושר לחמישי)':'Week (aligned to Thursday)','גולמי (יום/שבוע)':'Original frequency (day/week)','חודש':'Month','שנה':'Year',
'מתאריך':'From','עד':'To','דירוג עד':'Rank up to','חיפוש (שיר/יוצר, | = או)':'Search (song/artist; | = OR)','אפס סינון':'Reset filters',
'נתח מההאזנה (%)':'Listening share (%)','נתח מההופעות (%)':'Chart-appearance share (%)','ממוצע ערך לשבוע/יום':'Average value per week/day',
'+ תקופה':'+ Period','איפוס תקופות':'Reset periods','CSV סיכום':'Summary CSV',
'תאריך':'Date','תיאור':'Description','הוסף':'Add','ייצוא':'Export','ייבוא':'Import',
'ייצוא יצירות':'Export works','ייצוא ביצועים':'Export recordings','הצלבה עם טבלת היצירות המעודכנת':'Crosswalk to the updated master list',
'קבצי המקור:':'Source files:','רשימת יוצרים':'Artist master list',
'CSV שורות':'Rows CSV','CSV קטלוג שירים (אחרי נירמול)':'Normalized song catalog CSV',
'תקופות:':'Periods:','לפני המלחמה':'Before the war','שבועות ראשונים':'First weeks','המשך המלחמה':'Later war period',
'שם':'Name','עד תאריך':'End date','ראשון':'First','אחרון':'Last','שיא':'Peak','סה״כ/ממוצע':'Total / average','לפני 7.10':'Before Oct 7','אחרי 7.10':'After Oct 7','גולמי':'Raw rows','הצג':'Explore',
'תקופה':'Period','ימים/שבועות':'Days/weeks','שורות':'Rows','שירים':'Songs','יוצרים':'Artists','סה״כ ערך גולמי (מקורות שונים; לא בר־השוואה)':'Total raw value (different sources; not comparable)',
'עברית':'Hebrew','לועזית':'Foreign language','ערבית':'Arabic','לא ידוע':'Unknown',
 'הפסקת אש ראשונה':'First ceasefire','מתקפת איראן':'Iranian attack','הפסקת אש':'Ceasefire','מלחמת 12 הימים':'Twelve-Day War',
 'בהשוואת תקופות, ״נתח״ מחושב בנפרד לכל מקור ולאחר מכן כממוצע בין המקורות. סיכומי צפיות והאזנות גולמיים אינם ניתנים לחיבור כמדד אחד. המספרים משקפים דירוגים, לא מדגם מלא של כל ההאזנה.':'In period comparisons, shares are calculated separately for each source and then averaged. Raw streams and views cannot be combined into one comparable total. Charts are ranked subsets, not a complete sample of listening.',
 'סינון מקור: השתמשו במסנן ״מקור״ מעל הגרף. כדי לראות כל מקור בקו נפרד, בחרו ״פיצול משני: מקור״. · ריחוף = הדגשה בגרף ובטבלה · לחיצה על קו/שורה = בחירה קבועה (★) · 👁 / מקרא = הסתרה והוספה · גרירה על הגרף = הגדרת תקופה להשוואה · «גולמי» = שורות המקור':'Use the Source filter above the chart, or choose Split by Source to draw separate lines. Hover to highlight; click a line or row to pin it (★); use the legend to toggle visibility; drag across the chart to define a period; Raw opens source rows.',
 'מודל זיהוי: יצירה (Work) ← הקלטה/ביצוע (Recording) ← הופעה בדירוג (Chart observation). קישור בין הקלטות ליצירות הוא הצעת התאמה ודורש בקרת חוקר.':'Identity model: Work → Recording/Performance → Chart observation. Proposed links between recordings and works must be reviewed by a researcher.',
 'כל פרמטר הוא סינון (ערכים מרובים מופרדים ב-;). api=series|rows. פרמטרים: grp, split, m, gran (w/m/y), src (0;1;2;3), lang, genre, gender, country, city, label, ent, dec, ver, collab, from, to, rank, q.':'Every parameter is a filter (separate multiple values with ;). api=series|rows. Parameters: grp, split, m, gran (w/m/y), src (0;1;2), lang, genre, gender, country, city, label, ent, dec, ver, collab, from, to, rank, q.',
 'מקור אחד זוהה כלא תקין':'One source failed quality checks',
'← השוואה בין התקופות':'Compare periods',
'איך השתנה חלק העברית/לועזית/ערבית?':'How did the balance of Hebrew, foreign-language and Arabic songs change?',
'האם היקף ההאזנה השתנה אחרי 7.10?':'Did listening patterns change after October 7?',
'האם השפה שונה בין Tracks ל-Videos?':'Does language vary between Tracks and Videos?',
'אילו שירים הובילו מיד אחרי 7.10?':'Which songs led immediately after October 7?',
'איך התנהגו שירי המלחמה לאורך זמן?':'How did war-related songs evolve over time?',
'אותו שיר: שמע מול וידאו':'Same song: audio versus video',
'מתי שירים ישנים חוזרים לטופ?':'When do older songs return to the charts?',
'מי האמנים המובילים?':'Who are the leading artists?',
'איך משתנה הרכב המגדר?':'How did the gender balance change?',
'מאיפה האמנים?':'Where are artists from?',
'איך משתנה חלוקת הז׳אנרים?':'How did genre shares change?',
'כמה שירים חדשים נכנסים בכל שבוע?':'How many new songs enter each week?',
'האם הטופ הפך מגוון או הומוגני?':'Did the charts become more or less diverse?',
'תחרות בין אמנים':'Competition among artists',
'מה נצרך בעיקר כווידאו?':'Which music is consumed primarily as video?',
'שירים ישנים מול חדשים':'Older versus newer songs',
'מה השתנה בין התקופות בכל הממדים?':'What changed between periods across all dimensions?',
'סולו מול שיתוף פעולה, אדם מול הרכב':'Solo versus collaboration, individuals versus groups',
'נתח הופעות לפי מקור':'Chart appearance share by source',
'הרכב שפות (100%) ביוטיוב Tracks':'Language composition (100%) in YouTube Tracks',
'שפה × מקור':'Language × source',
'טופ שירים אוקטובר–נובמבר 2023':'Top songs in October–November 2023',
'שיר מפוצל לפי מקור':'Songs split by source',
'דירוג שירים שיצאו לפני המלחמה (נמוך=טוב)':'Ranking of prewar songs (lower is better)',
'יוצרים לפי סכום האזנות':'Artists by total listening',
'מגדר (100%)':'Gender (100%)','מדינת מוצא (100%)':'Country of origin (100%)',
'ז׳אנר ראשי (100%)':'Primary genre (100%)','כניסות חדשות לפי מקור':'New entries by source',
'שירים שונים לפי חודש':'Unique songs by month','Tracks מול Videos לפי יוצר':'Tracks vs Videos by artist',
'ממוצע ימים בטופ לפי שפה':'Average days on chart by language',
'כל הממדים בבת אחת (ערכו תקופות)':'All dimensions at once (edit periods)',
'שיתופי פעולה לאורך זמן (100%)':'Collaborations over time (100%)',
};
const phrases=[
 ['מקור','Source'],['מוצגות','Showing'],['הסדרות המובילות','top series'],['ניתן להוסיף סדרות מתוך הרשימה.','You can add more series from the list.'],['סדרות נבחרו','series selected'],['תצפיות בדירוג','chart observations'],['קבוצות שירים','song groups'],['מסוננות:','filtered:'],['שורות תואמות לסינון','rows match the filters'],['מוצגות 300 הראשונות','showing first 300'],['פריט:','Item:'],['תקופה ','Period '],['סה״כ','Total'],['נתח','Share'],['הערת כיסוי:','Coverage note:'],['Spotify כולל ימים חסרים','Spotify has missing days'],['אין לפרש היעדר תצפיות כהיעדר האזנה.','Missing observations do not indicate zero listening.'],
];
const originals=new WeakMap();
function translateText(str){let v=dictionary[str];if(v!==undefined)return v;const t=str.trim();if(dictionary[t]!==undefined)return str.replace(t,dictionary[t]);for(const [he,en] of phrases)if(str.includes(he))str=str.replaceAll(he,en);return str}
let queued=false, translating=false;
function localize(){if(translating)return;translating=true;
 document.documentElement.lang=locale;document.documentElement.dir=locale==='en'?'ltr':'rtl';
 for(const code of ['he','en']){const b=document.getElementById('lang-'+code);if(b){b.classList.toggle('active',locale===code);b.setAttribute('aria-pressed',String(locale===code));}}
 const walk=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let node;
 while(node=walk.nextNode()){
  const el=node.parentElement;if(!el||el.closest('script,style,pre,code,#rt,#tb,#lg,#serieschoices,#tip,#pe,#cg,#ct,#pl,#et2,a[href^="data/"],#ex1'))continue;
  if(el.closest('input,textarea'))continue;
  let base=originals.get(node);if(base===undefined||node.nodeValue!==translateText(base)&&node.nodeValue!==base){base=node.nodeValue;originals.set(node,base)}
  const next=locale==='en'?translateText(base):base;
  if(node.nodeValue!==next)node.nodeValue=next;
 }
 for(const input of document.querySelectorAll('input[placeholder]')){
  if(!input.dataset.hePlaceholder)input.dataset.hePlaceholder=input.placeholder;
  input.placeholder=locale==='en'?translateText(input.dataset.hePlaceholder):input.dataset.hePlaceholder;
 }
 const frame=document.querySelector('#hp iframe');if(frame){const want=locale==='en'?'help-en.html':'help.html';if(frame.getAttribute('src')!==want)frame.setAttribute('src',want)}
 translating=false;
}
function scheduleLocale(){if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;localize()})}
function setLocale(next){locale=next==='en'?'en':'he';try{localStorage.setItem('wm_language',locale)}catch(e){}localize();window.dispatchEvent(new Event('languagechange'))}
document.addEventListener('DOMContentLoaded',()=>{
 for(const c of ['he','en']){const b=document.getElementById('lang-'+c);if(b)b.addEventListener('click',()=>setLocale(c))}
 const obs=new MutationObserver(()=>{if(!translating)scheduleLocale()});
 for(const id of ['nv','qs','fl','xc','method','seriescount','rawi','cs','ev','raw','ap','c','x']){const e=document.getElementById(id);if(e)obs.observe(e,{childList:true,subtree:true})}
 localize();
});
