from pathlib import Path
p=Path('/mnt/data/v23_fix/index.html'); s=p.read_text()
start=s.rfind('<script>',0,s.index('function stableColor(series)'))
end=s.index('</script>',start)
js=s[start+8:end]
old="function stableColor(series){if(series.rest)return '#99a2ac';const parts=String(series.k).split(' | '),dims=[X.grp,X.split];for(let j=0;j<parts.length;j++){const d=dims[j];if(d==='lang'||d==='src'){const col=stableColors[d][parts[j]];if(col)return col}}const key=(X.grp==='artist'?Object.keys(V21.entities).find(id=>[V21.entities[id].he,V21.entities[id].en,V21.entities[id].display].includes(series.base)):null)||series.base;return colorPalette[stableHash((X.grp||'')+'|'+key)%colorPalette.length]}"
new="""function stableColor(series){if(series.rest)return '#99a2ac';const parts=String(series.k).split(' | '),dims=[X.grp,X.split];for(let j=0;j<parts.length;j++){const d=dims[j];if(d==='lang'||d==='src'){const col=stableColors[d][parts[j]];if(col)return col}}const key=(X.grp==='artist'?Object.keys(V21.entities).find(id=>[V21.entities[id].he,V21.entities[id].en,V21.entities[id].display].includes(series.base)):null)||series.base;return colorPalette[stableHash((X.grp||'')+'|'+key)%colorPalette.length]}
// The palette is fixed across views. Resolve exact collisions in the visible chart
// deterministically, preferring semantic language/source colours before hash colours.
function distinctSeriesColors(series){
 const priority=s=>{const p=String(s.k).split(' | ');return p.some((v,i)=>([X.grp,X.split][i]==='lang'||[X.grp,X.split][i]==='src')&&stableColors[[X.grp,X.split][i]]?.[v])?0:1};
 const ordered=[...series].sort((a,b)=>Number(!!a.rest)-Number(!!b.rest)||priority(a)-priority(b)||String(a.k).localeCompare(String(b.k)));
 const used=new Set();
 for(const item of ordered){let color=stableColor(item);if(used.has(color.toLowerCase())){
  const h=stableHash((X.grp||'')+'|'+(X.split||'')+'|'+item.k);
  for(let n=0;n<360;n++){const hue=(h%360+n*137.508)%360;const candidate=`hsl(${hue.toFixed(2)} 65% ${n%2?69:57}%)`;if(!used.has(candidate.toLowerCase())){color=candidate;break}}
 }item.col=color;used.add(color.toLowerCase())}
}
const DIM_INFO={
 country:['ארץ לידה לאדם; ארץ מוצא או ייסוד להרכב/גוף, לפי שדה birth_or_origin_country בקטלוג. אינה אזרחות, מקום השמעה או מקום הפקה.','Birth country for people; origin or formation country for groups/organizations (source field: birth_or_origin_country). Not citizenship, listening location, or production location.'],
 city:['עיר לידה לאדם או עיר מוצא/ייסוד להרכב, לפי קטלוג היוצרים.','Birth city for a person or origin/formation city for a group, as recorded in the creator catalogue.'],
 genre:['סיווג ז׳אנר של היוצר מתוך המטא־נתונים; אינו בהכרח סיווג של השיר עצמו.','Creator genre from the source metadata, not necessarily the genre of the particular track.'],
 gender:['מגדר היוצר לפי הקטלוג; אינו מעיד על מגדר המאזינים או על כל חברי ההרכב.','Creator gender metadata, not listener gender or necessarily all group members.'],
 lang:['שפת השיר כפי שסווגה בנתונים. חלק מהסיווגים נגזרים מכתב הכותרת וטעונים אימות.','Song language as classified in the data; some labels are inferred from the title script and require verification.'],
 artist:['הצגה לפי זהות יוצר מאוחדת; שיתופי פעולה עשויים להיות משויכים ליותר מיוצר אחד.','Unified creator identity; collaborations may be attributed to more than one creator.'],
 song:['שם הביצוע המאוחד; קאברים וגרסאות שונות עשויים להישאר כרשומות נפרדות.','Unified performance title; covers and alternate recordings may remain separate.'],
 src:['Spotify הוא דירוג יומי; YouTube Tracks ו־Videos הם דירוגים שבועיים. לא מחברים צפיות והאזנות כמדד משותף.','Spotify is daily; YouTube Tracks and Videos are weekly. Streams and views must not be summed as equivalent units.'],
 ent:['סוג הישות: אדם, הרכב, גוף או פרויקט; יש סיווגים שעדיין דורשים בדיקת חוקר.','Entity type: person, group, organization or project; some classifications still need review.'],
 label:['חברת תקליטים או לייבל על פי נתוני המקור; ייתכנו חוסרים.','Record label as provided by the source; may be missing.'],
 dec:['עשור לידה של האדם, או שנות ייסוד כאשר המקור מתייחס להרכב.','Birth decade for people; formation period where the source describes a group.'],
 collab:['חלוקת סולו/שיתוף על פי הקרדיטים הרשומים, ולא בהכרח על פי כלל המשתתפים.','Solo/collaboration based on credited performers, not necessarily every participant.'],
 ver:['סוג גרסת הביצוע לפי הסיווג הזמין; הזיהוי עדיין עשוי לדרוש אימות.','Recording/version classification when available; identity may require verification.'],
 period:['התקופות מוגדרות לצורך מחקר וניתנות לעריכה; היעדר נתונים אינו אפס.','Research-defined, editable periods; missing observations are not zero.'],
};
function dimInfoButton(k){const d=DIM_INFO[k];if(!d)return '';const msg=d[locale==='en'?1:0];return `<span class="dim-help" tabindex="0" role="note" aria-label="${esc((locale==='en'?'Explanation: ':'הסבר: ')+msg)}" title="${esc(msg)}" data-help="${esc(msg)}">i</span>`}
"""
assert old in js
js=js.replace(old,new)
assert 'all.forEach(s=>{s.col=stableColor(s)});' in js
js=js.replace('all.forEach(s=>{s.col=stableColor(s)});','distinctSeriesColors(all);')
old_ms='`<details class=ms data-k=${k}><summary aria-label="${esc(l)}">${esc(l)}</summary>'
new_ms='`<details class=ms data-k=${k}><summary aria-label="${esc(l)}">${esc(l)}</summary>${dimInfoButton(k)}'
assert old_ms in js
js=js.replace(old_ms,new_ms)
# Add a hint near group selection, just outside the label so that it does not intercept selects.
js=js.replace('`<label>פילוח<select id=xg>${o(dims,X.grp)}</select></label><label>פיצול משני<select id=xs>', '`<label>פילוח<select id=xg>${o(dims,X.grp)}</select></label>${dimInfoButton(X.grp)}<label>פיצול משני<select id=xs>')
# Make filter summary rebuild preserve the information icon as sibling (not lost when summary text reset).
# Descriptive legend for a current selection.
js=js.replace('`<label>מדד<select id=xm>', '`${dimInfoButton(X.split)}<label>מדד<select id=xm>')
# Update tooltip when language changes; filter controls rebuilt by filters() on language change in original app.
style='''\n/* Research context help: low-contrast, unobtrusive and keyboard-readable. */\n.dim-help{display:inline-flex;align-items:center;justify-content:center;vertical-align:middle;flex:0 0 auto;width:17px;height:17px;margin-inline:5px;border:1px solid #7793a8;border-radius:50%;font:600 11px/1 system-ui,sans-serif;color:#b9cedd;background:#21303c;cursor:help;position:relative;z-index:3;user-select:none}.dim-help:focus-visible{outline:2px solid #88c4ff;outline-offset:2px}.dim-help:hover,.dim-help:focus{border-color:#c0d9e8;color:white}.dim-help[data-help]:hover:after,.dim-help[data-help]:focus:after{content:attr(data-help);position:absolute;z-index:1000;top:calc(100% + 8px);inset-inline-start:0;width:min(290px,70vw);padding:10px 12px;white-space:normal;line-height:1.65;direction:inherit;text-align:start;font:13px/1.6 'Heebo',system-ui,sans-serif;color:#eef5fa;background:#263745;box-shadow:0 6px 25px #000a;border:1px solid #5f788b;border-radius:8px;pointer-events:none}.ms>.dim-help{position:absolute;top:8px;inset-inline-end:6px;margin:0}.ms>summary{padding-inline-end:24px!important}#xc>.dim-help{align-self:center;margin-inline-start:-8px;margin-inline-end:8px}@media(max-width:600px){.dim-help[data-help]:hover:after,.dim-help[data-help]:focus:after{width:min(240px,70vw)}}\n'''
s=s[:start+8]+js+s[end:]
s=s.replace('</style></head><body>',style+'</style></head><body>',1)
p.write_text(s)
print('patched',len(s),'js',len(js))
