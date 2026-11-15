

// Names V2.1: source-grounded identity labels and bilingual variants (no guessed Wikidata matches).
const V21=window.WM_V21||{entities:{},performances:{}};
let v21AutoTop=true;
let v21LastScope='';
const v21Entity=(id)=>V21.entities[id]||null;
const v21Dim=(k,v)=>{const d=V21.dimensions?.[k]?.[v];return d?(locale==='en'?(d.en||d.he||d.canonical):(d.he||d.en||d.canonical)):(v||UN)};
const v21Label=(id)=>{const x=v21Entity(id);return x?(locale==='en'?(x.en||x.he||x.display):(x.he||x.en||x.display)):(id||'(לא מזוהה)')};
const v21Perf=(t)=>V21.performances[t[19]]||null;
const v21ArtistKeys=t=>{const p=v21Perf(t);return p&&p.artists&&p.artists.length?p.artists:[]};
const v21Artists=t=>{const ids=v21ArtistKeys(t);return ids.length?ids.map(v21Label):[t[1]||UN]};
const v21SongName=t=>{const p=v21Perf(t);if(!p)return t[0];const title=locale==='en'?(p.en||p.he||p.title):(p.he||p.en||p.title);return title+' — '+(v21Artists(t).join(', ')||t[1])};
const v21ArtistHas=(i,name)=>v21Artists(T[D.t[i]]).includes(name);
const v21ArtistAliases=s=>{let m=V21.entities||{};for(const id in m){const x=m[id];if(x.he===s||x.en===s||x.display===s)return x.aliases||[]}return []};
const v21SeriesSearch=(ser,q)=>{if(ser.k.toLocaleLowerCase().includes(q))return true;if(X.grp==='artist')return v21ArtistAliases(ser.base).some(v=>v.toLocaleLowerCase().includes(q));if(X.grp==='song'){
 const t=T.find(t=>v21SongName(t)===ser.base);const p=t&&v21Perf(t);return p&&p.aliases.some(v=>v.toLocaleLowerCase().includes(q));
 }return false};

const stableColors={lang:{'עברית':'#c0392b','Hebrew':'#c0392b','ערבית':'#198f79','Arabic':'#198f79','אנגלית':'#286fb4','English':'#286fb4','לועזית':'#286fb4','Foreign language':'#286fb4','(לא ידוע)':'#89939d'},src:{'Spotify · יומי':'#1d9a65','YouTube · Tracks שבועי':'#b36b19','YouTube · Videos שבועי':'#7551b5'}};
const colorPalette=['#386cb0','#da6b36','#6d56a3','#269d86','#b84d81','#889f25','#a05b38','#487f97','#a78b2c','#5f8291','#91629a','#6a9b59'];
const stableHash=s=>{let h=2166136261;for(const ch of String(s)){h^=ch.codePointAt(0);h=Math.imul(h,16777619)}return h>>>0};
function stableColor(series){if(series.rest)return '#99a2ac';const parts=String(series.k).split(' | '),dims=[X.grp,X.split];for(let j=0;j<parts.length;j++){const d=dims[j];if(d==='lang'||d==='src'){const col=stableColors[d][parts[j]];if(col)return col}}const key=(X.grp==='artist'?Object.keys(V21.entities).find(id=>[V21.entities[id].he,V21.entities[id].en,V21.entities[id].display].includes(series.base)):null)||series.base;return colorPalette[stableHash((X.grp||'')+'|'+key)%colorPalette.length]}
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
window.addEventListener('languagechange',()=>{document.querySelectorAll('.dim-help[data-dim]').forEach(el=>{const pair=DIM_INFO[el.dataset.dim];if(!pair)return;const message=pair[locale==='en'?1:0];el.dataset.help=message;el.title=message;el.setAttribute('aria-label',(locale==='en'?'Explanation: ':'הסבר: ')+message)})});
function dimInfoButton(k){const d=DIM_INFO[k];if(!d)return '';const msg=d[locale==='en'?1:0];return `<span class="dim-help" data-dim="${esc(k)}" tabindex="0" role="note" aria-label="${esc((locale==='en'?'Explanation: ':'הסבר: ')+msg)}" title="${esc(msg)}" data-help="${esc(msg)}">i</span>`}

let zoomRange=null,zoomHistory=[],eventTypes=new Set(['war','hostage','casualty','regional','political','civil']);let activeDetail=null;
const SRC=['Spotify · יומי','YouTube · Tracks שבועי','YouTube · Videos שבועי'],A={lang:2,gender:3,country:4,genre:5,city:6,label:7,ent:8,dec:9,ver:13,collab:14},$=i=>document.getElementById(i),UN='(לא ידוע)',OUT='(מחוץ לתקופות)',PC=['#c0392b','#2e86c1','#27ae60','#d68910','#8e44ad','#16a085'];
const DN={song:'שיר',artist:'יוצר',lang:'שפה',genre:'ז׳אנר',gender:'מגדר',country:'מדינה',city:'עיר מוצא',label:'לייבל',ent:'סוג יוצר',dec:'עשור לידה',ver:'גרסה',collab:'סולו/שיתוף',src:'מקור',period:'תקופה (מוגדרת)',month:'חודש',year:'שנה'};
const TABS={g:['כללי',Object.keys(DN)],c:['השוואת תקופות',0],q:['שאלות',0],s:['שירים',['song','lang','label','ver','collab','src','period']],a:['יוצרים',['artist','gender','country','genre','city','ent','dec','collab','src','period']],p:['פילוחים',Object.keys(DN)],ev:['אירועים',0],raw:['נתונים ומקורות',0],ap:['API',0],hp:['הסבר',0],v2:['קטלוג ביצועים V2',0]},EX=['g','s','a','p'];
const MS={cm:'סכום streams/views (לא משווים בין פלטפורמות)',n:'מס׳ הופעות בטופ',songs:'שירים שונים',new:'כניסות חדשות',avg:'דירוג ממוצע',best:'דירוג הכי טוב',dc:'ממוצע ימים/שבועות בטופ'};
const defPer=()=>[['לפני המלחמה','2023-01-01','2023-10-06'],['שבועות ראשונים','2023-10-07','2023-11-24'],['המשך המלחמה','2023-11-25','2030-01-01']].map((p,i)=>({n:p[0],f:p[1],t:p[2],c:PC[i]}));
let D,T,EV=[],F={},X={grp:'lang',split:'',m:'n',ch:'line',gran:'w',n:8,nm:'share'},PIN=new Set,HID=new Set,HI=null,S=[],LB=[],TAB='g',G={},DLD=0,dr=null,PER,BAD=new Set(),WK=[];
try{PER=JSON.parse(localStorage.wm_per)}catch(e){}if(!PER||!PER.length)PER=defPer();const sp_=()=>{try{localStorage.wm_per=JSON.stringify(PER)}catch(e){}};
const perOf=d=>{const p=PER.find(p=>d>=p.f&&d<=p.t);return p?p.n:OUT};
const val=(i,k)=>{const t=T[D.t[i]],d=D.dates[D.d[i]];return k=='song'?v21SongName(t):k=='artist'?v21Artists(t)[0]:k=='src'?SRC[D.s[i]]:k=='period'?perOf(d):k=='month'?d.slice(0,7):k=='year'?d.slice(0,4):v21Dim(k,t[A[k]])};
function rows(f=F){const o=[],qs=f.q?f.q.toLowerCase().split('|').map(s=>s.trim()).filter(Boolean):0,fk=Object.keys(A).filter(k=>f[k]&&f[k].size);
 for(let i=0;i<D.t.length;i++){const d=D.dates[D.d[i]];if(D.status?.[i]&&!(f.includeSuspect&&TAB==='raw'))continue;if(f.src&&f.src.size?!f.src.has(''+D.s[i]):BAD.has(D.s[i]))continue;if(f.from&&d<f.from||f.to&&d>f.to||zoomRange&&(d<zoomRange[0]||d>zoomRange[1])||f.rank&&D.r[i]>+f.rank)continue;const t=T[D.t[i]];
 if(f.performanceId&&t[19]!==f.performanceId)continue;if(fk.some(k=>!f[k].has(t[A[k]]||UN))||qs&&!qs.some(q=>(t[0]+' '+t[1]).toLowerCase().includes(q))||f.item&&(f.item[0]==='artist'?!v21ArtistHas(i,f.item[1]):val(i,f.item[0])!=f.item[1]))continue;o.push(i)}return o}
const ld=s=>new Promise(r=>{const e=document.createElement('script');e.src=s;e.onload=r;e.onerror=()=>r(0);document.head.append(e)});
let loadPromise=null;
async function ensure(){if(D)return; if(!loadPromise)loadPromise=loadData();await loadPromise;}
async function loadData(){
  const status=$('info'); status.textContent=locale==='en'?'Loading research data…':'טוען נתוני מחקר…';if(window.WM_DATA){D=window.WM_DATA;return;}
  // HTTP: one compressed transfer; file://: a script fallback keeps unpacked ZIP usable.
  if(location.protocol!=='file:' && typeof DecompressionStream!=='undefined'){
    try{
      const res=await fetch('data/data.json.gz',{cache:'force-cache'});
      if(!res.ok)throw Error('HTTP '+res.status);
      const stream=res.body.pipeThrough(new DecompressionStream('gzip'));
      D=JSON.parse(await new Response(stream).text());return;
    }catch(e){console.warn('Compressed data unavailable; using JS fallback',e)}
  }
  if(!window.WM_DATA)await ld('data/data.js');
  D=window.WM_DATA;
  if(!D)throw Error('No research data available');
}

const bs=b=>b.length==10?b:b.length==7?b+'-01':b+'-01-01',be=b=>b.length==10?b:b.length==7?b+'-31':b+'-12-31';
function build(){const R=rows(),g=X.grp,sp=X.split,m=X.m,bk=i=>{const d=D.dates[D.d[i]];return X.gran=='m'?d.slice(0,7):X.gran=='y'?d.slice(0,4):X.gran=='w'?WK[D.d[i]]:d},first=new Map,M=new Map,L=new Set,sh=X.nm=='share'&&(m=='cm'||m=='n'),TOT=new Map,nS=new Set(R.map(i=>D.s[i])).size||1;
 if(sh)for(const i of rows({src:F.src,from:F.from,to:F.to})){const k=D.s[i]+'|'+bk(i);let t=TOT.get(k);if(!t)TOT.set(k,t={v:0,n:0});t.v+=D.v[i];t.n++}
 const wt=(i,b)=>{const t=TOT.get(D.s[i]+'|'+b)||{v:1,n:1};return m=='cm'?D.v[i]/(t.v||1):1/(t.n||1)};
 if(m=='new')for(const i of R){const t=D.t[i]*4+D.s[i];if(!(first.get(t)<=D.d[i]))first.set(t,D.d[i])}
 for(const i of R){const b=bk(i),credits=g==='artist'?[...new Set(v21Artists(T[D.t[i]]))]:[val(i,g)];const factor=g==='artist'?1/credits.length:1;
 for(const base of credits){const k=sp?base+' | '+val(i,sp):base;L.add(b);let s=M.get(k);if(!s)M.set(k,s={k,base,c:new Map});let c=s.c.get(b);if(!c)s.c.set(b,c={sum:0,n:0,rs:0,dc:0,ws:0,best:999,z:new Set,nw:0});if(sh)c.ws+=wt(i,b)*factor;c.sum+=D.v[i]*factor;c.n+=factor;c.rs+=D.r[i]*factor;c.dc+=D.dc[i]*factor;c.best=Math.min(c.best,D.r[i]);c.z.add(D.t[i]);if(m=='new'&&first.get(D.t[i]*4+D.s[i])==D.d[i])c.nw+=factor;
 }}

 // Calendars come from actual observations, never invented zeros.
 const selectedSources=F.src&&F.src.size?[...F.src].map(Number):[0,1,2];
 const cover=new Map();const seenDates=new Set();
 for(let i=0;i<D.s.length;i++){
   if(D.status?.[i])continue;const sid=D.s[i],date=D.dates[D.d[i]];
   if(!selectedSources.includes(sid)||F.from&&date<F.from||F.to&&date>F.to||zoomRange&&(date<zoomRange[0]||date>zoomRange[1]))continue;
   const b=bk(i),key=sid+'|'+b;
   cover.set(key,true);L.add(b);
 }
 const hasCover=(k,b)=>{
   const parts=k.split(' | ');const sourceName=g==='src'?parts[0]:sp==='src'?parts[parts.length-1]:null;
   const ids=sourceName?selectedSources.filter(sid=>SRC[sid]===sourceName):selectedSources;
   return ids.some(sid=>cover.has(sid+'|'+b));
 };
 LB=[...L].sort();const rk=m=='avg'||m=='best',mv=(c,b)=>sh?c.ws/(sp==='src'||g==='src'?1:Math.max(1,selectedSources.filter(sid=>cover.has(sid+'|'+b)).length))*100:m=='cm'?c.sum:m=='n'?c.n:m=='songs'?c.z.size:m=='new'?c.nw:m=='best'?c.best:m=='dc'?c.dc/c.n:c.rs/c.n,add=!rk&&m!='songs'&&m!='dc',WR=b=>b<'2023-10-07'.slice(0,b.length);
 S=[...M.values()].map(s=>{s.v=LB.map(b=>{const c=s.c.get(b);return c?mv(c,b):sh&&hasCover(s.k,b)?0:null});if(X.nm=='index'&&!rk&&m!='songs'){const p0=PER[0],bv=s.v.filter((v,j)=>v!=null&&p0&&bs(LB[j])>=p0.f&&bs(LB[j])<=p0.t),bz=bv,base=bz.length?bz.reduce((a,b)=>a+b,0)/bz.length:0;s.v=s.v.map(v=>v==null||!base?null:v/base*100)}const nn=s.v.filter(v=>v!=null);s.tot=add?nn.reduce((a,b)=>a+b,0):nn.reduce((a,b)=>a+b,0)/(nn.length||1);
  const ag=a=>a.length?(m=='best'?Math.min(...a):add?a.reduce((x,y)=>x+y,0):a.reduce((x,y)=>x+y,0)/a.length):null;s.pre=ag(s.v.filter((v,j)=>v!=null&&WR(LB[j])));s.post=ag(s.v.filter((v,j)=>v!=null&&!WR(LB[j])));
  const pk=s.v.reduce((a,v,j)=>v!=null&&(a<0||(rk?v<s.v[a]:v>s.v[a]))?j:a,-1);s.pk=LB[pk];s.f=LB[s.v.findIndex(v=>v!=null)];s.l=LB[s.v.length-1-[...s.v].reverse().findIndex(v=>v!=null)];return s}).sort((a,b)=>rk?a.tot-b.tot:b.tot-a.tot);G={rk}}
const fx=v=>v==null?'':Math.abs(v)>=100?Math.round(v).toLocaleString():+v.toFixed(1),esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
function draw(){const c=$('cv'),W=c.width=c.clientWidth*2,H=c.height=720,x=c.getContext('2d'),fg=getComputedStyle(document.body).color,Lm=170,Rm=20,Tm=40,Bm=50,n=LB.length;x.clearRect(0,0,W,H);x.font='22px sans-serif';if(!n||!S.length){x.fillStyle=fg;x.fillText('אין נתונים לסינון הנוכחי',W/2-120,H/2);return}
 const ch=G.rk?'line':X.ch,base=S.filter(s=>!HID.has(s.k)),ser=PIN.size?base.filter(s=>PIN.has(s.k)):base.slice(0,X.n),tot=LB.map((_,j)=>S.reduce((a,s)=>a+(s.v[j]||0),0)),PX=j=>Lm+j/Math.max(1,n-1)*(W-Lm-Rm);let mx=1,mn=1;
 const all=ch=='line'?ser:[...ser,{k:'אחר',v:tot.map((t,j)=>t-ser.reduce((a,s)=>a+(s.v[j]||0),0)),rest:1}];
 if(ch=='line')ser.forEach(s=>s.v.forEach(v=>{if(v!=null&&Number.isFinite(v)){mx=Math.max(mx,v);mn=Math.min(mn,v)}}));else mx=ch=='share'?1:Math.max(1,...tot);
 const lg=X.nm=='log'&&!G.rk&&ch=='line';let mn0=Infinity;if(lg)ser.forEach(s=>s.v.forEach(v=>{if(v>0)mn0=Math.min(mn0,v)}));if(!isFinite(mn0)||mn0>=mx)mn0=Math.max(1e-6,mx/1000);
 const PY=v=>lg?H-Bm-(Math.log(Math.max(v,mn0))-Math.log(mn0))/(Math.log(mx)-Math.log(mn0)||1)*(H-Tm-Bm):G.rk?Tm+(v-mn)/Math.max(1,mx-mn)*(H-Tm-Bm):H-Bm-v/mx*(H-Tm-Bm);distinctSeriesColors(all);
 if(ch=='line')ser.forEach(s=>{s.y1=s.v.map(v=>v==null?null:PY(v))});else{const b=LB.map(()=>0);all.forEach(s=>{s.y0=s.v.map((v,j)=>PY(b[j]/(ch=='share'?tot[j]||1:1)));s.v.forEach((v,j)=>b[j]+=v||0);s.y1=s.v.map((v,j)=>PY(b[j]/(ch=='share'?tot[j]||1:1)))})}
 PER.forEach(p=>{const j0=LB.findIndex(b=>bs(b)>=p.f);let j1=-1;LB.forEach((b,j)=>{if(bs(b)<=p.t)j1=j});if(j0<0||j1<j0)return;x.globalAlpha=.09;x.fillStyle=p.c;x.fillRect(PX(j0),Tm-8,Math.max(4,PX(j1)-PX(j0)),H-Bm-Tm+8);x.globalAlpha=1;x.fillStyle=p.c;x.fillText(locale==='en'?translateText(p.n):p.n,PX(j0)+4,H-Bm-8)});
 x.fillStyle=fg;x.strokeStyle=fg;x.globalAlpha=.3;for(let t=0;t<=4;t++){const v=lg?mn0*Math.pow(mx/mn0,t/4):G.rk?mn+(mx-mn)*t/4:mx*t/4,y=PY(v);x.beginPath();x.moveTo(Lm,y);x.lineTo(W-Rm,y);x.stroke();x.globalAlpha=1;x.fillText(ch=='share'?Math.round(v*100)+'%':fx(v),4,y+6);x.globalAlpha=.3}x.globalAlpha=1;
 for(let t=0;t<=5;t++){const j=Math.round(t*(n-1)/5);x.fillText(LB[j],PX(j)-40,H-12)}
 EV.filter(e=>eventTypes.has(e.type||'war')).forEach((e,k)=>{const j=LB.findIndex(b=>b>=e.date.slice(0,b.length));if(j<0)return;x.strokeStyle=x.fillStyle=EVENT_COLORS[e.type||'war']||'#888';x.setLineDash([6,6]);x.beginPath();x.moveTo(PX(j),Tm-8);x.lineTo(PX(j),H-Bm);x.stroke();x.setLineDash([]);if(n<36||e.date==='2023-10-07')x.fillText(locale==='en'?(e.en||translateText(e.label)):e.label,PX(j)+4,18+(k%2)*16)});
 all.forEach(s=>{const hi=HI&&HI==s.k;x.globalAlpha=HI&&!hi?.25:1;x.fillStyle=x.strokeStyle=s.col;if(ch=='line'){x.lineWidth=hi?6:3;x.beginPath();let f=1;s.y1.forEach((y,j)=>{if(y==null){f=1;return}f?x.moveTo(PX(j),y):x.lineTo(PX(j),y);f=0});x.stroke();x.lineWidth=1}else{x.globalAlpha=HI&&!hi?.2:.8;x.beginPath();s.y1.forEach((y,j)=>j?x.lineTo(PX(j),y):x.moveTo(PX(j),y));for(let j=n-1;j>=0;j--)x.lineTo(PX(j),s.y0[j]);x.fill()}x.globalAlpha=1});
 if(dr&&dr.x1!=null){x.globalAlpha=.2;x.fillStyle='#888';x.fillRect(Math.min(dr.x,dr.x1),Tm-8,Math.abs(dr.x1-dr.x),H-Bm-Tm+8);x.globalAlpha=1}
 const hid=S.filter(s=>HID.has(s.k));$('lg').innerHTML=all.map(s=>`<span style="color:${s.col}${HI==s.k?';font-weight:700':''}" data-k="${esc(s.k)}">■ ${esc(s.k)}</span>`).join('')+hid.map(s=>`<span class=off data-k="${esc(s.k)}">${esc(s.k)}</span>`).join('');G.all=all;G.ch=ch;G.PX=PX;G.Lm=Lm;G.Rm=Rm;G.W=W}
const mxp=e=>{const r=$('cv').getBoundingClientRect();return[(e.clientX-r.left)*2,(e.clientY-r.top)*2]},jat=mx=>Math.max(0,Math.min(LB.length-1,Math.round((mx-G.Lm)/(G.W-G.Lm-G.Rm)*(LB.length-1))));
function hover(e){const[mx,my]=mxp(e),n=LB.length;if(!G.all||!n)return;if(dr){dr.x1=mx;draw();return}const j=jat(mx);let best=null,bd=1e9;
 G.all.forEach(s=>{if(s.rest&&G.ch=='line')return;const y=s.y1[j];if(y==null)return;const d=G.ch=='line'?Math.abs(y-my):(my>=y&&my<=s.y0[j]?0:1e9);if(d<bd){bd=d;best=s}});const k=bd<60&&best&&!best.rest?best.k:null,t=$('tip');
 if(k){t.style.display='block';t.style.left=e.clientX+12+'px';t.style.top=e.clientY+12+'px';t.textContent=`${k} · ${LB[j]} · ${fx(best.v[j])}`}else t.style.display='none';if(k!=HI){HI=k;draw();hl()}}
function hl(){document.querySelectorAll('#tb tr[data-k]').forEach(r=>r.classList.toggle('h',r.dataset.k==HI))}
const tog=k=>{PIN.has(k)?PIN.delete(k):PIN.add(k);draw();tbl();renderSeriesPicker()},hide=k=>{HID.has(k)?HID.delete(k):HID.add(k);draw();tbl()};
function addP(a,b){[a,b]=[Math.min(a,b),Math.max(a,b)];PER.push({n:'תקופה '+(PER.length+1),f:firstDateInBucket(LB[a]),t:be(LB[b]),c:PC[PER.length%PC.length]});sp_();draw();pl()}
function pl(){$('pl').innerHTML='<b>תקופות:</b> '+PER.map((p,i)=>`<span style="color:${p.c}">■ ${esc(p.n)} (${p.f} – ${p.t.slice(0,10)}) <a data-dp=${i}>✕</a></span>`).join('')+' <a href="#" data-go=c>→ השוואה בין התקופות</a>'}
function tbl(){const h=['','#',DN[X.grp]+(X.split?' | '+DN[X.split]:''),'סה״כ/ממוצע','לפני 7.10','אחרי 7.10','שיא','ראשון','אחרון',''];$('tb').innerHTML='<tr>'+h.map(x=>`<th>${x}</th>`).join('')+'</tr>'+S.slice(0,300).map((s,i)=>`<tr data-k="${esc(s.k)}" class="${PIN.has(s.k)?'p':''} ${HID.has(s.k)?'x':''}"><td data-h=1 style=cursor:pointer>${HID.has(s.k)?'–':'👁'}</td><td>${PIN.has(s.k)?'★':i+1}</td><td>${esc(s.k)}</td><td>${fx(s.tot)}</td><td>${fx(s.pre)}</td><td>${fx(s.post)}</td><td>${s.pk||''}</td><td>${s.f||''}</td><td>${s.l||''}</td><td><a href="#" data-r="${i}">גולמי</a></td></tr>`).join('');hl()}
function xc(){const dims=TABS[TAB][1],o=(a,b)=>a.map(k=>`<option value=${k}${b==k?' selected':''}>${DN[k]}</option>`).join('');
 $('xc').innerHTML=`<label>פילוח<select id=xg>${o(dims,X.grp)}</select></label>${dimInfoButton(X.grp)}<label>פיצול משני<select id=xs><option value="">—</option>${o(Object.keys(DN),X.split)}</select></label><label>מדד<select id=xm>${Object.entries(MS).map(([k,v])=>`<option value=${k}${X.m==k?' selected':''}>${v}</option>`).join('')}</select></label><label>גרף<select id=xh>${[['line','קווים'],['area','שטח מוערם'],['share','שטח 100%']].map(([k,v])=>`<option value=${k}${X.ch==k?' selected':''}>${v}</option>`)}</select></label><label>נרמול<select id=xn2>${[['share','נתח בתוך כל מקור (%) – מומלץ להשוואה'],['none','ערכים גולמיים – לא לחיבור בין מקורות'],['index','אינדקס (תקופה ראשונה=100)'],['log','ציר לוגריתמי']].map(([k,v])=>`<option value=${k}${X.nm==k?' selected':''}>${v}</option>`)}</select></label><label>זמן<select id=xt>${[['w','שבוע (מיושר לחמישי)'],['d','גולמי (יום/שבוע)'],['m','חודש'],['y','שנה']].map(([k,v])=>`<option value=${k}${X.gran==k?' selected':''}>${v}</option>`)}</select></label><label>סדרות מובילות<input id=xn type=number min=1 max=40 value=${X.n} style=width:55px></label><button id=xr>נקה בחירה/הסתרה</button><button id=xcsv>CSV</button>`;
 $('xc').onchange=e=>{X={grp:$('xg').value,split:$('xs').value,m:$('xm').value,ch:$('xh').value,gran:$('xt').value,n:+$('xn').value||8,nm:$('xn2').value};PIN.clear();HID.clear();v21AutoTop=true;zoomText();if(e.target.id=='xg'||e.target.id=='xs')for(const k of[X.grp,X.split]){if(!k)continue;const d=document.querySelector(`#fl details[data-k=${k}]`);if(d)d.open=true}run()};$('xr').onclick=()=>{PIN.clear();HID.clear();draw();tbl();renderSeriesPicker()};$('xcsv').onclick=()=>dl('series.csv',csv(tableRows()),'text/csv')}
const tableRows=()=>S.map(s=>({series:s.k,total:s.tot,pre_war:s.pre,post_war:s.post,peak:s.pk,first:s.f,last:s.l,...Object.fromEntries(LB.map((b,j)=>[b,s.v[j]]))}));
function csv(a){if(!a.length)return'';const k=Object.keys(a[0]);return'\ufeff'+[k.join(','),...a.map(r=>k.map(c=>JSON.stringify(r[c]??'')).join(','))].join('\n')}
const dl=(n,s,t)=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([s],{type:t}));a.download=n;a.click()};
function renderSeriesPicker(){
 const el=$('serieschoices'),q=($('seriessearch').value||'').toLocaleLowerCase();
 const entries=S.filter(v=>v21SeriesSearch(v,q)).slice(0,120);
 el.innerHTML=entries.map(s=>`<label class="${PIN.has(s.k)?'chosen':''}"><input type="checkbox" data-series="${esc(s.k)}" ${PIN.has(s.k)?'checked':''}>${esc(s.k)}</label>`).join('')||'אין סדרות מתאימות';
 $('seriescount').textContent=PIN.size?`${PIN.size} סדרות נבחרו`: `מוצגות ${Math.min(X.n,S.length)} הסדרות המובילות. ניתן להוסיף סדרות מתוך הרשימה.`;
}

function renderV21Insights(){
 const el=$('v21-insights');if(!el)return;const isArtist=TAB==='a'&&X.grp==='artist',isSong=TAB==='s'&&X.grp==='song';el.hidden=!(isArtist||isSong);if(el.hidden)return;
 const en=locale==='en';const isMixed=(F.src?F.src.size>1:!BAD.size);const values=S.map(s=>Math.max(0,Number(s.tot)||0));const all=values.reduce((a,b)=>a+b,0);
 const top=S.slice(0,10);const selected=PIN.size?S.filter(s=>PIN.has(s.k)):S.slice(0,10);
 const totals=top.map(s=>Math.max(0,Number(s.tot)||0));const other=Math.max(0,all-totals.reduce((a,b)=>a+b,0));
 const nice=n=>Number(n||0).toLocaleString(en?'en-US':'he-IL',{maximumFractionDigits:1});
 const avg=S.length?all/S.length:0;const share=all?100*top.reduce((a,s)=>a+Math.max(0,Number(s.tot)||0),0)/all:0;
 const title=isArtist?(en?'Creators ranked within your selection':'דירוג יוצרים לפי הסינון והתקופה'):(en?'Songs ranked within your selection':'דירוג שירים לפי הסינון והתקופה');
 const subtitle=en?'Top 10 are selected automatically; search above to add or replace series. Ranking refreshes whenever time range, source, language or type changes.':'עשרת המובילים מסומנים אוטומטית. ניתן לחפש למעלה ולבחור אחרים. הדירוג מחושב מחדש עם כל שינוי בתקופה, בשפה, בסוג או במקור.';
 el.innerHTML=`<h3>${title}</h3><div class="v21-sub">${subtitle}</div><div class="v21-rank">${top.map((s,i)=>`<button type="button" class="v21-chip ${PIN.has(s.k)?'selected':''}" data-v21-rank="${i}" title="${esc(s.k)}"><span class="v21-dot" style="background:${stableColor(s)}"></span><span>${i+1}. ${esc(s.k)}</span><strong>${nice(s.tot)}</strong></button>`).join('')}</div><div class="v21-stats"><div class="v21-stat">${en?'Distinct series in selection':'סדרות שונות בתקופה'}<strong>${nice(S.length)}</strong></div><div class="v21-stat">${en?'Top ten share of displayed aggregate':'נתח עשרת המובילים במדד המצטבר'}<strong>${nice(share)}%</strong></div><div class="v21-stat">${en?'Mean aggregate per series':'ממוצע מדד מצטבר לסדרה'}<strong>${nice(avg)}</strong></div></div><h4 class="v21-section">${en?'Composition and distribution':'התפלגות והרכב'}</h4><div class="v21-pie-layout"><canvas id="v21-pie" width="440" height="440" aria-label="${en?'Composition chart':'תרשים התפלגות'}"></canvas><div class="v21-pie-list">${top.slice(0,8).map((s,i)=>`<div><span><span class="v21-dot" style="background:${stableColor(s)}"></span> ${esc(s.k)}</span><b>${nice(all?100*Number(s.tot)/all:0)}%</b></div>`).join('')}<div><span>${en?'Others':'אחרים'}</span><b>${nice(all?100*other/all:0)}%</b></div></div></div><div class="v21-sub">${en?'Percentages summarize the selected chart metric across observed periods (not a population survey). Collaborative credits receive fractional allocation. Spotify streams and YouTube views are never treated as the same physical unit; select a source for absolute-volume comparisons. Unknown or missing coverage is not zero.':'האחוזים מסכמים את המדד שנבחר לאורך התקופות שבהן יש כיסוי, ולא סקר האזנות. בקרדיטים משותפים התרומה מתחלקת בין היוצרים. האזנות Spotify וצפיות YouTube אינן יחידת מדידה משותפת; להשוואת כמויות יש לבחור מקור אחד. חוסר נתונים אינו אפס.'}</div>`;
 const canvas=$('v21-pie');if(canvas&&all){const x=canvas.getContext('2d'),r=175,cx=220,cy=220;let angle=-Math.PI/2;const sizes=top.map(s=>Math.max(0,Number(s.tot)||0)).concat([other]);sizes.forEach((v,i)=>{if(!v)return;const sweep=2*Math.PI*v/all;x.beginPath();x.moveTo(cx,cy);x.arc(cx,cy,r,angle,angle+sweep);x.closePath();x.fillStyle=i===top.length?'#637382':stableColor(top[i]);x.fill();angle+=sweep});x.beginPath();x.arc(cx,cy,93,0,2*Math.PI);x.fillStyle='#1b222a';x.fill();x.font='bold 26px sans-serif';x.textAlign='center';x.fillStyle='#eaf0f5';x.fillText(nice(share)+'%',cx,cy+8);}
 el.querySelectorAll('[data-v21-rank]').forEach(btn=>btn.onclick=()=>{v21AutoTop=false;const k=top[+btn.dataset.v21Rank]?.k;if(!k)return;PIN.has(k)?PIN.delete(k):PIN.add(k);renderSeriesPicker();draw();tbl();renderV21Insights()});
}

function renderMethod(){const v=$('method');if(!v)return;
 v.textContent=X.nm==='share'?'השוואה מנורמלת: כל ערך הוא אחוז מתוך כלל ההאזנות/ההופעות של אותו מקור באותו פרק זמן. אם מאחדים מקורות, מחשבים ממוצע של נתחיהם – ולא מחברים צפיות להאזנות. Spotify יומי, YouTube שבועי.':X.nm==='none'?'הצגה גולמית: מספר ההופעות היומיות ב־Spotify אינו שקול למספר ההופעות השבועיות ב־YouTube; streams ו־views הם מדדים שונים. יש לפצל לפי מקור.':X.nm==='index'?'אינדקס יחסי לקו בסיס – מגמות בלבד. מקורות אינם שקולים במונחי כמות.':'ציר לוגריתמי לנתונים גולמיים; השוואות בין פלטפורמות דורשות זהירות.';v.textContent+=' הערת כיסוי: Spotify כולל ימים חסרים (912 ימים לאורך התקופה), ובפרט פערי כיסוי גדולים מסוף 2025. אין לפרש היעדר תצפיות כהיעדר האזנה.';if(locale==='en')v.textContent=X.nm==='share'?'Normalized comparison: each value is a share of all streams/chart appearances in the same source and time bucket. Combined sources are averaged, not summed. Spotify is daily; YouTube is weekly.':X.nm==='none'?'Raw values: Spotify daily observations and YouTube weekly observations are not equivalent. Streams and views must not be added. Split by source.':X.nm==='index'?'Baseline index: compare relative trends only, not absolute totals.':'Log scale for raw data: cross-platform totals are not comparable.';if(locale==='en')v.textContent+=' Coverage: Spotify has observations on only 912 days across the period, with especially large gaps since late 2025. Missing observations are not zero listening.';
}
async function run(){await ensure();build();if((TAB==='s'||TAB==='a')&&v21AutoTop){PIN.clear();S.slice(0,10).forEach(s=>PIN.add(s.k))}renderMethod();renderSeriesPicker();draw();renderV21Insights();tbl();pl();info()}
const info=()=>$('info').textContent=`${D.t.length.toLocaleString()} תצפיות בדירוג · ${T.length.toLocaleString()} קבוצות שירים · ${D.dates[0]} – ${D.dates.at(-1)} · מסוננות: ${rows().length.toLocaleString()}`;
async function raw(){await ensure();const R=rows();$('rawi').textContent=`${R.length.toLocaleString()} שורות תואמות לסינון${F.item?` (פריט: ${F.item[1]})`:F.performanceId?` (ביצוע: ${F.performanceId})`:''} – מוצגות 300 הראשונות`;const toRaw=i=>{const t=T[D.t[i]];return{date:D.dates[D.d[i]],source:SRC[D.s[i]],rank:D.r[i],value:D.v[i],peak_rank:D.pk[i],prev_rank:D.pr[i],days_or_weeks_on_chart:D.dc[i],name:t[0],artist:t[1],lang:t[2],gender:t[3],country:t[4],genre:t[5],city:t[6],label:t[7],entity_type:t[8],birth_decade:t[9],version:t[13],collab:t[14],spotify_uri:t[15],youtube_id:t[16],raw_title_artist:t[17],matched_by:t[18],performance_id:t[19],work_id:t[20],identity_status:t[21],review_status:t[22],data_status:D.status?.[i]?'suspect_repeated_snapshot':'observed'}};window.rawA=()=>R.map(toRaw);const a=R.slice(0,300).map(toRaw);
 $('rt').innerHTML='<tr>'+Object.keys(a[0]||{}).map(k=>`<th>${k}</th>`).join('')+'</tr>'+a.slice(0,300).map(r=>'<tr>'+Object.entries(r).map(([k,v])=>`<td>${k==='spotify_uri'||k==='youtube_id'?(k==='spotify_uri'&&sourceLinks([,,,,,,,,,,,,,,,v,''])[0]?linksHtml([,,,,,,,,,,,,,,,v,'']):k==='youtube_id'?linksHtml([,,,,,,,,,,,,,,,null,v]):esc(v??'')):esc(v??'')}</td>`).join('')+'</tr>').join('')}
const DL2=['src','lang','genre','gender','country','city','ent','dec','collab','ver','label'];
function pe(){$('pe').innerHTML='<table><tr><th>שם<th>מתאריך<th>עד תאריך<th></tr>'+PER.map((p,i)=>`<tr><td><input data-pi=${i} data-pf=n value="${esc(p.n)}"><td><input type=date data-pi=${i} data-pf=f value="${p.f}"><td><input type=date data-pi=${i} data-pf=t value="${p.t.slice(0,10)}"><td><span style="color:${p.c}">■</span> <a data-dp=${i}>✕</a></tr>`).join('')+'</table>'}
async function cmp(){await ensure();pe();const R=rows(),P=PER.filter(p=>R.some(i=>{const d=D.dates[D.d[i]];return d>=p.f&&d<=p.t;})),M=$('cm').value,mk=()=>({v:0,n:0,z:new Set,by:{}}),T0=P.map(()=>({v:0,n:0,z:new Set,a:new Set,d:new Set,by:{}})),DM={},SA={song:new Map,artist:new Map};DL2.forEach(k=>DM[k]=new Map);
 if(!P.length){$('cs').innerHTML='<div class="missing-explain">'+(locale==='en'?'No observed data for the selected periods and sources. Missing ≠ zero.':'אין תצפיות בתקופות ובמקורות שנבחרו. נתון חסר אינו אפס.')+'</div>';$('cg').innerHTML='';$('ct').innerHTML='';return;}
 for(const i of R){const d=D.dates[D.d[i]];for(let p=0;p<P.length;p++){if(d<P[p].f||d>P[p].t)continue;const t=T0[p],v=D.v[i];t.v+=v;t.n++;const sid=D.s[i];(t.by[sid]??={v:0,n:0}).v+=v;t.by[sid].n++;t.z.add(D.t[i]);t.d.add(d);t.a.add(T[D.t[i]][1]);
  for(const k of DL2){const x=val(i,k);let m=DM[k].get(x);if(!m)DM[k].set(x,m=P.map(mk));const c=m[p];c.v+=v;c.n++;(c.by[sid]??={v:0,n:0}).v+=v;c.by[sid].n++;c.z.add(D.t[i])}
  for(const k of['song','artist']){const x=val(i,k);let m=SA[k].get(x);if(!m)SA[k].set(x,m=P.map(()=>({v:0,by:{}})));m[p].v+=v;(m[p].by[sid]??={v:0,n:0}).v+=v}}}
 const sh=M[0]=='s'&&M!='sg',mv=(c,p)=>M=='shv'||M=='shn'?Object.keys(T0[p].by).reduce((acc,sid)=>acc+((c.by[sid]?.[M=='shv'?'v':'n']||0)/(T0[p].by[sid][M=='shv'?'v':'n']||1)),0)/(Object.keys(T0[p].by).length||1):M=='wk'?c.v/(T0[p].d.size||1):c.z.size,fm=x=>sh?(x*100).toFixed(1)+'%':fx(x),dt=(a,b)=>sh?((b-a)*100).toFixed(1)+'pp':a?((b/a-1)*100).toFixed(0)+'%':'—';
 $('cs').innerHTML='<div class=w><table><tr><th>תקופה<th>ימים/שבועות<th>שורות<th>סה״כ ערך גולמי (מקורות שונים; לא בר־השוואה)<th>שירים<th>יוצרים</tr>'+P.map((p,i)=>`<tr><td style="color:${p.c}">■ ${p.n}<td>${T0[i].d.size}<td>${T0[i].n.toLocaleString()}<td>${T0[i].v.toLocaleString()}<td>${T0[i].z.size}<td>${T0[i].a.size}`).join('')+'</table></div>';window.cmpRows=[];
 $('cg').innerHTML=DL2.map(k=>{const E=[...DM[k]].map(([x,m])=>({x,v:P.map((_,p)=>mv(m[p],p))})).sort((a,b)=>b.v.reduce((s,y)=>s+y,0)-a.v.reduce((s,y)=>s+y,0)).slice(0,10),mx=Math.max(1e-9,...E.flatMap(e=>e.v));
  E.forEach(e=>P.forEach((p,i)=>cmpRows.push({dim:DN[k],value:e.x,period:p.n,measure:e.v[i]})));return`<div class=pn><b>${DN[k]}</b>`+E.map(e=>`<div class=br><span>${e.x}<u>${P.length>1?'Δ '+dt(e.v[0],e.v.at(-1)):''}</u></span><div>`+e.v.map((v,i)=>`<i title="${P[i].n}: ${fm(v)}" style="width:${v/mx*100}%;background:${P[i].c}"></i>`).join('')+'</div></div>').join('')+'</div>'}).join('');
 const chg=k=>{const E=[...SA[k]].map(([x,m])=>({x,s:P.map((_,p)=>Object.keys(T0[p].by).reduce((acc,sid)=>acc+(m[p].by[sid]?.v||0)/(T0[p].by[sid].v||1),0)/(Object.keys(T0[p].by).length||1))})).sort((a,b)=>Math.abs(b.s.at(-1)-b.s[0])-Math.abs(a.s.at(-1)-a.s[0])).slice(0,12);return`<h4>${DN[k]}ים עם השינוי הגדול ביותר בנתח ההאזנה (ראשונה→אחרונה)</h4><div class=w><table><tr><th>${DN[k]}`+P.map(p=>`<th style="color:${p.c}">${p.n}`).join('')+'<th>Δ</tr>'+E.map(e=>`<tr><td>${e.x}`+e.s.map(v=>`<td>${(v*100).toFixed(2)}%`).join('')+`<td>${((e.s.at(-1)-e.s[0])*100).toFixed(2)}pp`).join('')+'</table></div>'};
 $('ct').innerHTML=P.length>1?chg('song')+chg('artist'):'';
 const absent=PER.filter(p=>!P.includes(p));if(absent.length)$('cs').insertAdjacentHTML('afterbegin','<div class="missing-explain">'+(locale==='en'?'Excluded periods with no observations (not zero): ':'תקופות ללא תצפיות הושמטו מההשוואה (לא נרשם אפס): ')+absent.map(p=>esc(p.n)).join(', ')+'</div>');} 
function ms(k,l,o){return`<details class=ms data-k=${k}><summary aria-label="${esc(l)}">${esc(l)}</summary>${dimInfoButton(k)}<div><div class=filter-tools><input class=filter-search type=search placeholder="${locale==='en'?'Find option':'חיפוש אפשרות'}" aria-label="${locale==='en'?'Search filter options':'חיפוש בתוך המסנן'}"><button type=button class=filter-select-all>${locale==='en'?'Select visible':'בחר גלויים'}</button><button type=button class=filter-select-none>${locale==='en'?'Clear':'נקה'}</button></div>${o.map(([v,t])=>`<label class=c><input type=checkbox value="${esc(v)}">${esc(t)}</label>`).join('')}</div></details>`}
function filters(){const u=k=>[...new Set(T.map(t=>t[A[k]]||UN))].sort().map(v=>[v,v]);$('fl').innerHTML=ms('src','מקור',SRC.map((s,i)=>[i,s]))+Object.keys(A).map(k=>ms(k,DN[k],u(k))).join('')+`<label>מתאריך<input type=date data-k=from></label><label>עד<input type=date data-k=to></label><label>דירוג עד<input type=number data-k=rank style=width:60px></label><label>חיפוש (שיר/יוצר, | = או)<input data-k=q style=width:150px></label><label style="color:#e4b577"><input type=checkbox id=v2-suspect> הצג גם נתוני YouTube חשודים (לבקרה בלבד)</label><button id=fr>אפס סינון</button>`;
 const rd=()=>{F={};F.includeSuspect=!!$('v2-suspect')?.checked;document.querySelectorAll('#fl details').forEach(d=>{const v=[...d.querySelectorAll('input:checked')].map(i=>i.value);d.querySelector('summary').textContent=(DN[d.dataset.k]||'מקור')+(v.length?` (${v.length})`:'');if(v.length)F[d.dataset.k]=new Set(v)});document.querySelectorAll('#fl input[data-k]').forEach(i=>{if(i.value)F[i.dataset.k]=i.value});PIN.clear();HID.clear();v21AutoTop=true;go()};
 $('fl').onchange=e=>{if(e.target.classList.contains('filter-search'))return;rd();updateResetStatus()};
 $('fl').oninput=e=>{if(e.target.classList.contains('filter-search')){const term=e.target.value.trim().toLocaleLowerCase();e.target.closest('details').querySelectorAll('label.c').forEach(l=>{l.hidden=!l.textContent.toLocaleLowerCase().includes(term)});return}if(e.target.dataset.k=='q'){rd();updateResetStatus()}};
 $('fl').onclick=e=>{const btn=e.target.closest('.filter-select-all,.filter-select-none');if(!btn)return;e.preventDefault();const d=btn.closest('details');d.querySelectorAll('label.c').forEach(l=>{if(!l.hidden)l.querySelector('input').checked=btn.classList.contains('filter-select-all')});rd();updateResetStatus()};$('fr').onclick=()=>{$('fl').querySelectorAll('input').forEach(i=>i.type=='checkbox'?i.checked=false:i.value='');rd();updateResetStatus()};
 window.setF=f=>{$('fl').querySelectorAll('input').forEach(i=>i.type=='checkbox'?i.checked=false:i.value='');for(const[k,v]of Object.entries(f)){if(Array.isArray(v))v.forEach(x=>{const i=$('fl').querySelector(`details[data-k=${k}] input[value="${x}"]`);if(i)i.checked=true});else $('fl').querySelector(`input[data-k=${k}]`).value=v}rd()}}
const QS=[['האם היקף ההאזנה השתנה אחרי 7.10?','נתח הופעות לפי מקור','g',{grp:'src',m:'n',nm:'share'},{}],['איך השתנה חלק העברית/לועזית/ערבית?','הרכב שפות (100%) ביוטיוב Tracks','g',{grp:'lang',m:'n',ch:'share'},{src:['1']}],['האם השפה שונה בין Tracks ל-Videos?','שפה × מקור','g',{grp:'lang',split:'src',m:'n',ch:'share'},{src:['1','2']}],['אילו שירים הובילו מיד אחרי 7.10?','טופ שירים אוקטובר–נובמבר 2023','s',{grp:'song',m:'cm'},{from:'2023-10-05',to:'2023-11-30'}],['איך התנהגו שירי המלחמה לאורך זמן?','עם ישראל חי, חרבו דרבו, גיבורי על…','s',{grp:'song',m:'cm',n:12},{q:'עם ישראל חי|חרבו דרבו|גיבורי על|לא תנצחו|תמיד אוהב אותי'}],['אותו שיר: שמע מול וידאו','שיר מפוצל לפי מקור','s',{grp:'song',split:'src',m:'cm',n:12},{q:'עם ישראל חי|חרבו דרבו|תמיד אוהב אותי',src:['1','2']}],['מתי שירים ישנים חוזרים לטופ?','דירוג שירים שיצאו לפני המלחמה (נמוך=טוב)','s',{grp:'song',m:'best'},{q:'לצאת מדיכאון|לשוב הביתה|לחזור הביתה|המנון הלוחם'}],['מי האמנים המובילים?','יוצרים לפי סכום האזנות','a',{grp:'artist',m:'cm',n:10},{}],['איך משתנה הרכב המגדר?','מגדר (100%)','a',{grp:'gender',m:'n',ch:'share'},{src:['1']}],['מאיפה האמנים?','מדינת מוצא (100%)','a',{grp:'country',m:'n',ch:'share',n:6},{src:['1']}],['איך משתנה חלוקת הז׳אנרים?','ז׳אנר ראשי (100%)','a',{grp:'genre',m:'n',ch:'share',n:8},{src:['1']}],['כמה שירים חדשים נכנסים בכל שבוע?','כניסות חדשות לפי מקור','g',{grp:'src',m:'new'},{}],['האם הטופ הפך מגוון או הומוגני?','שירים שונים לפי חודש','g',{grp:'src',m:'songs',gran:'m'},{}],['תחרות בין אמנים','עומר אדם, אייל גולן, ששון, איתי לוי…','a',{grp:'artist',m:'cm',n:8},{q:'Omer Adam|Eyal Golan|ששון|Itay Levi|Noa Kirel|Eden Hason'}],['מה נצרך בעיקר כווידאו?','Tracks מול Videos לפי יוצר','a',{grp:'artist',split:'src',m:'cm',n:10},{src:['1','2']}],['שירים ישנים מול חדשים','ממוצע ימים בטופ לפי שפה','g',{grp:'lang',m:'dc'},{src:['1']}],['מה השתנה בין התקופות בכל הממדים?','כל הממדים בבת אחת (ערכו תקופות)','c',{},{}],['סולו מול שיתוף פעולה, אדם מול הרכב','שיתופי פעולה לאורך זמן (100%)','a',{grp:'collab',m:'n',ch:'share'},{src:['1']}]];

const QUESTION_DETAILS=[
 ['scope','not','דירוגים מאפשרים השוואה של הרכב הטופ, לא של כלל ההאזנות בישראל. אין להסיק על סך ההאזנה מכמות הופעות ברשימת דירוג.','Use chart composition, not overall listening volume; chart appearances are not the population-wide listening total.'],
 ['identity','finding','בחלון שלפני המלחמה (12.8–6.10.2023), נתח ההאזנות לשירים המסווגים בעברית בטופ 200 של Spotify היה 71.8%; בשמונת השבועות שאחריו (7.10–1.12) הוא היה 79.0%. זהו ממצא תיאורי, לא הוכחת סיבתיות.','Hebrew-classified Spotify Top 200 streaming share rose from 71.8% (Aug 12–Oct 6) to 79.0% (Oct 7–Dec 1), descriptively, not causally.'],
 ['platforms','finding','בשמונת השבועות הראשונים המכוסים ביוטיוב, השירים המסווגים בעברית היו כ־84.8% מערכי דירוג Tracks וכ־88.3% מערכי Videos. ההבדל מתאר שתי רשימות טופ בלבד.','In the first eight observed YouTube weeks, Hebrew-classified tracks represented ~84.8% of Tracks-chart values and ~88.3% of Videos-chart values; these are top-chart figures only.'],
 ['repertoire','finding','בחלון 7.10–1.12.2023 הובילו ב־Spotify, לפי סכום האזנות בתוך הטופ: ״יהיה טוב״, ״לצאת מדיכאון״ ו״יהיה טוב & מים שקופים״. יש לבדוק גרסאות ושיוך יצירה.','Within Spotify Top 200 during Oct 7–Dec 1, leading titles by charted streams included ״יהיה טוב״, ״לצאת מדיכאון״ and ״יהיה טוב & מים שקופים״; recordings still need validation.'],
 ['repertoire','partial','אפשר לראות מסלולי הופעה ושיא בדירוג לשירים שהוגדרו כדוגמאות לשירי מלחמה; כדי להגדיר את כל הקטגוריה יש צורך בתיוג תוכן ידני ואימות תאריכי יציאה.','Chart trajectories can be examined for candidate war songs, but the category requires manual content labeling and release-date verification.'],
 ['platforms','partial','אפשר להציב אותו שם שיר בשני מקורות זה לצד זה; זיהוי הקלטות שונות אינו ודאי, ונתוני צפייה והאזנה אינם ניתנים לחיבור.','Titles may be compared across sources, but recording identity remains uncertain and views cannot be added to streams.'],
 ['repertoire','partial','הופעה של יצירה ותיקה בדירוג מצביעה על נוכחות בטופ; היא אינה מעידה לבדה על נוסטלגיה. נדרשים תאריכי יצירה/הקלטה מהימנים והשוואת רקע.','Old-song chart entries indicate chart visibility, not nostalgia by themselves; verified release dates and a baseline are needed.'],
 ['artists','partial','אפשר לדרג יוצרים לפי מדדים בתוך כל מקור בנפרד; צירוף Spotify ו־YouTube בסכום גולמי אינו תקף.','Artist rankings are possible per source; raw Spotify and YouTube totals must not be pooled.'],
 ['artists','partial','נתוני מגדר במאגר שייכים לתיוג היוצרים, לא למגדר המאזינים; הם מאפשרים ניתוח של ייצוג בטופ בלבד.','Artist gender labels support chart-representation analysis, not claims about listeners’ gender.'],
 ['artists','partial','מדינת המוצא מתייחסת ליוצר המסווג; אינה בהכרח מקום ההפקה, שפת ההאזנה או זהות המאזין.','Artist country labels are not production locations or listener identities.'],
 ['identity','partial','אפשר לראות שינויים יחסיים בקטגוריות ז׳אנר, אך חלק ניכר מהשורות חסר תיוג ז׳אנר ולכן חובה להציג גם ״לא ידוע״.','Genre shifts can be explored, but many observations have missing genre metadata: display Unknown explicitly.'],
 ['repertoire','partial','כניסה חדשה לדירוג אינה בהכרח שיר חדש שיצא לאור; היא רק הופעה ראשונה בטבלה הנצפית.','A new chart entry is not necessarily a newly released song.'],
 ['repertoire','partial','מספר שירים שונים בטופ הוא מדד בסיסי למגוון, אך אינו מדד מלא של ריכוזיות. יש לשקלל גם נתחי האזנה ולבדוק יציבות כיסוי.','Unique charted songs offer a basic diversity signal, not a complete concentration index.'],
 ['artists','partial','דפוסי תחרות אפשר לבחון בתוך אותו מקור ואותו חלון זמן, לאחר אחידות מזהי יוצרים וביצועים.','Artist competition should be examined within the same source and date window with normalized identities.'],
 ['platforms','partial','הבדלים בין שתי רשימות YouTube יכולים לרמוז על דפוסי צריכה, אך Tracks ו־Videos אינן מייצגות שימוש אישי מול צפייה באופן חד־חד־ערכי.','Tracks/Videos contrasts are suggestive, not an exact audio/video behavior split.'],
 ['repertoire','not','משך ההופעה בטופ אינו מעיד אם שיר ישן או חדש: נדרשים תאריכי יציאה אמינים.','Chart tenure is not song age; verified release dates are needed.'],
 ['timing','partial','יש להתנות כל השוואת תקופות בכיסוי אמיתי של כל מקור. ב־YouTube אין בסיס לפני 7.10, וב־Spotify קיימים ימים חסרים.','All period comparisons require observed coverage. YouTube has no pre-Oct 7 baseline, and Spotify has missing days.'],
 ['artists','partial','אפשר להשוות נתח ייצוג של ביצועי סולו ושיתופי פעולה, אך התיוג עלול להיות תלוי באופן הצגת שמות מבצעים.','Solo/collaboration shares can be compared, subject to contributor-label accuracy.'],
 // Ten additional original research questions
 ['identity','finding','הפער בשיעור העברית ב־Spotify בטופ 200 בין החלונות שנבדקו הוא כ־7.2 נקודות אחוז. נדרשת בדיקה אם הוא נשמר מעבר לתקופה הראשונה ואם הוא עמיד לשינוי חלון הזמן.','Spotify Hebrew-classified chart-share differed by about 7.2 percentage points between the two windows. Persistence and window sensitivity remain to be tested.'],
 ['identity','partial','בשמונת השבועות הראשונים: בשני מדדי YouTube, נתח העברית גבוה מ־84%; בחלון המאוחר ינואר–פברואר 2024 הוא כ־85.5% ב־Tracks וכ־85.8% ב־Videos. זהו תיאור של מדדי הדירוג, לא מבחן שינוי מובהק.','Hebrew-classified share exceeded 84% in both YouTube charts in the first eight weeks; in Jan–Feb 2024 it was ~85.5% for Tracks and ~85.8% for Videos, descriptively.'],
 ['repertoire','partial','ב־Spotify שיר כמו ״לצאת מדיכאון״ מופיע בין המובילים בתחילת המלחמה אף שיצא קודם לכן. כדי לבדוק ״שימוש מחודש״ צריך להצליב תאריך פרסום, ביצוע והקו שלפני האירוע.','״לצאת מדיכאון״ appears among early-war Spotify leaders despite its earlier release; a revival claim requires verified release and pre-event trajectory.'],
 ['platforms','finding','בחלון המלחמה המוקדם YouTube Tracks הציג כ־84.8% עברית מול כ־88.3% ב־Videos (במדד ערכי הטופ). יש לבדוק אם ההבדל עקבי בהמשך ולא לייחס אותו ישירות למניעי הצופים.','Early-war YouTube Hebrew share was ~84.8% in Tracks vs ~88.3% in Videos, measured within chart totals; audience motives cannot be inferred.'],
 ['timing','not','אין בסיס נתוני YouTube לפני 7 באוקטובר. לכן לא ניתן לחשב שינוי בעקבות 7.10 ממקור זה, גם אם עמודות קודמות בגרף ריקות.','YouTube lacks a pre-Oct 7 baseline. No pre/post estimate can be computed from those data.'],
 ['timing','partial','אפשר להשוות חלונות סביב תאריכים מוגדרים, אך נדרשים חלון ביקורת, בדיקת טרנדים קודמים וכיסוי עקבי; מתאם בזמן אינו מעיד שהאירוע גרם לשינוי.','Event-window comparisons need coverage, pre-trend checks and a comparison baseline; timing alone does not establish causality.'],
 ['repertoire','not','אין כיום במאגר שדה מהימן ל־valence, tempo או energy. אי אפשר להציג שינוי במצב הרוח המוזיקלי מתוך ז׳אנר או שפה כתחליף למדידה.','Valence, tempo and energy are not reliably available in this dataset. Genre or language is not a substitute for emotion measurement.'],
 ['repertoire','partial','על סמך דירוגי הטופ ניתן למדוד את התחלפות השירים לאורך הזמן; יש להבחין בין יצירה אחת עם ביצועים שונים לבין שירים חדשים באמת.','Chart turnover can be measured, but work-level and recording-level turnover must be distinguished.'],
 ['artists','partial','אפשר לחשב ריכוזיות לפי נתח האזנה של חמשת היוצרים המובילים בכל תקופה; היעדר יוצר/ז׳אנר מקוטלג יחייב קטגוריית ״לא ידוע״.','Top-five artist share can quantify concentration, provided uncategorized identities are retained as Unknown.'],
 ['platforms','not','אין כרגע נתוני רדיו, Shazam, TikTok או חיפוש משולבים. לא ניתן לבדוק התפשטות בין מדיות או מי הוביל את מי לפני צירוף נתונים חיצוניים.','Radio, Shazam, TikTok and search series are not integrated, so cross-media diffusion cannot yet be established.']
];
const NEW_QUESTIONS=[
 ['האם העלייה בחלקם של שירים בעברית ב־Spotify הייתה זמנית או נמשכת?','השוואת חלונות זמן ומעקב אחרי נתח העברית','g',{grp:'lang',m:'cm',ch:'line',nm:'share'},{src:['0']}],
 ['האם הרכב השפות ב־YouTube התייצב אחרי השבועות הראשונים?','שפת שירים לאורך הזמן בכל אחת מרשימות YouTube','g',{grp:'lang',split:'src',m:'cm',nm:'share'},{src:['1','2']}],
 ['האם ניכרת חזרה לרפרטואר שקדם למלחמה?','מסלולי שירים שקדמו לאוקטובר 2023','s',{grp:'song',m:'cm',nm:'share'},{q:'לצאת מדיכאון|לשוב הביתה|לחזור הביתה',src:['0']}],
 ['האם וידאו מדגיש שירים בעברית יותר מרשימת Tracks?','שפה לפי מקור, ערכים יחסיים','g',{grp:'lang',split:'src',m:'cm',nm:'share'},{src:['1','2']}],
 ['אפשר למדוד שינוי ב־YouTube לעומת השבוע שלפני 7 באוקטובר?','בדיקת כיסוי: אין תקופת בסיס','g',{grp:'src',m:'n',nm:'share'},{src:['1','2']}],
 ['כיצד משתנה הרפרטואר סביב אירועים מרכזיים במהלך המלחמה?','סדרות חודשיות והגדרת תקופות השוואה','c',{},{}],
 ['האם המוזיקה נעשתה שמחה, עצובה, מהירה או אנרגטית יותר?','נדרשים נתוני audio features שטרם קיימים','g',{grp:'genre',m:'n',nm:'share'},{src:['0']}],
 ['האם קצב התחלופה של שירים בראש הדירוג השתנה?','כניסות חדשות ומשך הופעה בטופ','g',{grp:'src',m:'new',gran:'w'},{src:['0']}],
 ['האם האזנות מתרכזות במספר קטן של יוצרים בשעת משבר?','יוצרים: השוואת התפלגות לאורך זמן','a',{grp:'artist',m:'cm',nm:'share',n:12},{src:['0']}],
 ['האם שיר מתפשט קודם ב־Shazam, ברדיו או ביוטיוב?','נדרש איסוף נתונים חיצוניים והשוואת תזמונים','s',{grp:'song',split:'src',m:'n',nm:'share'},{src:['0','1','2']}]
];
const ALLQ=QS.concat(NEW_QUESTIONS);
window.translateText=typeof translateText==='function'?translateText:x=>x;
const GROUPS={scope:['גבולות המדידה','Measurement limits'],identity:['שפה וזהות','Language & identity'],platforms:['בין פלטפורמות','Platforms'],repertoire:['שירים ורפרטואר','Songs & repertoire'],artists:['יוצרים וז׳אנרים','Artists & genres'],timing:['זמן ואירועים','Time & events']};
const QEN=[
 'Was the rise in Hebrew-language share on Spotify temporary or sustained?',
 'Did the language composition of YouTube stabilize after the early weeks?',
 'Was there a return to the prewar repertoire?',
 'Does the Videos chart place more emphasis on Hebrew than Tracks?',
 'Can YouTube show changes compared to the week before October 7?',
 'How does repertoire change around major events during the war?',
 'Did music become happier, sadder, faster or more energetic?',
 'Did top-chart turnover change?',
 'Did listening become concentrated among a small group of artists?',
 'Does a song spread first on Shazam, radio or YouTube?'
];
let qFilter='all';
function qcards(){
 const en=locale==='en',term=($('question-search')?.value||'').toLowerCase().trim();
 const selectors=[['all',en?'All subjects':'כל הנושאים'],...Object.entries(GROUPS).map(([k,v])=>[k,v[en?1:0]])];
 $('question-categories').innerHTML=selectors.map(([k,v])=>`<button type="button" class="${qFilter===k?'on':''}" data-qcat="${k}" aria-pressed="${qFilter===k}">${v}</button>`).join(' ');
 const visible=ALLQ.map((q,i)=>({q,i,d:QUESTION_DETAILS[i]})).filter(x=>(qFilter==='all'||x.d[0]===qFilter)&&(!term||(x.q[0]+' '+x.q[1]+' '+x.d[2]+' '+x.d[3]+' '+(QEN[x.i-18]||'')).toLowerCase().includes(term)));
 $('question-count').textContent=(en?'Showing ':'מוצגות ')+visible.length+'/'+ALLQ.length;
 const status={finding:[en?'Measured finding':'ממצא מדוד','finding'],partial:[en?'Partial evidence':'ממצא חלקי','partial'],not:[en?'Not answerable':'לא ניתן לקבוע','not']};
 $('qs').innerHTML=visible.map(({q,i,d})=>{const name=en?(i>=18?QEN[i-18]:(window.translateText?translateText(q[0]):q[0])):q[0];return `<article class="question-card"><div class="qmeta"><span>${i+1} · ${GROUPS[d[0]][en?1:0]} ${i>=18?' · '+(en?'NEW':'חדש'):''}</span><span class="qstatus">${status[d[1]][0]}</span></div><b class="qtitle">${esc(name)}</b><p class="qanswer">${esc(en?d[3]:d[2])}</p><small class="qmethod">${en?'Evidence to inspect':'ראיות לבדיקה'}: ${esc(en?(i>=18?['Time-series comparison','Compare sources','Compare repertoire','Cross-source shares','Coverage check','Event window','Missing audio metadata','New chart entries','Artist shares','Additional data needed'][i-18]:q[1]):q[1])}</small><div class="qactions"><button data-q="${i}" type="button">${en?'Explore data':'פתחו בגרף'}</button></div></article>`}).join('');
}
window.addEventListener('languagechange',()=>{if(D){coverageUI();if(TAB==='a'||TAB==='s'){PIN.clear();v21AutoTop=true;run()}}});
function coverageUI(){
 const en=locale==='en';const counts=[new Set(),new Set(),new Set()];for(let i=0;i<D.s.length;i++){if(D.status?.[i])continue;counts[D.s[i]].add(D.dates[D.d[i]]);}
 $('coverage').innerHTML=counts.map((v,i)=>{const d=[...v].sort();return `<div class="coverage-card"><strong>${['Spotify · daily','YouTube · Tracks / weekly','YouTube · Videos / weekly'][i]}</strong><span dir="ltr">${d[0]} → ${d[d.length-1]}</span> · ${d.length} ${en?'observed dates':'תאריכים נצפים'}</div>`}).join('');
 $('research-heading').textContent=en?'Research questions: what do the charts actually tell us?':'שאלות מחקר: מה אפשר ללמוד מן הדירוגים?';
 $('research-lede').textContent=en?'Start with a question, read the provisional answer and its limits, then inspect the chart. Unknowns are not replaced with guesses.':'התחילו בשאלה, קראו תשובה ראשונית ואת גבולותיה, ואז פתחו את הראיות בגרף. שאלות שאי אפשר לענות עליהן לא מקבלות תשובה מדומה.';
 $('missing-note').textContent=en?'Missing data ≠ zero. YouTube contains 40 suspected duplicated pre-October weeks, excluded by default; missing coverage is never zero.':'אין נתונים ≠ אפס. 40 השבועות המוקדמים של YouTube משוכפלים ומוחרגים כברירת מחדל; היעדר נתונים אינו אפס.';
 $('question-search').placeholder=en?'Search research questions':'חיפוש בתוך שאלות המחקר';qcards();
}
function updateResetStatus(){const el=$('active-filters');if(!el)return;const chosen=[...document.querySelectorAll('#fl details')].reduce((n,d)=>n+d.querySelectorAll('input:checked').length,0);const dates=!!(F.from||F.to||zoomRange);el.textContent=(locale==='en'?'Sources and filters selected: ':'מקורות ומסננים מסומנים: ')+chosen+(dates?(locale==='en'?' · date range active':' · טווח תאריכים פעיל'):'')}
function resetAll(){
 zoomRange=null;zoomHistory=[];activeDetail=null;const panel=$('data-detail');if(panel)panel.hidden=true;
 PER=defPer();sp_();F={src:new Set(['0','1','2'])};X={grp:'lang',split:'',m:'n',ch:'line',gran:'w',n:8,nm:'share'};
 PIN.clear();HID.clear();HI=null;v21AutoTop=true;BAD=new Set((D.qa||{}).bad||[]);
 $('seriessearch').value='';$('question-search').value='';$('v2-search').value='';qFilter='all';
 $('dragperiod').checked=false;document.querySelectorAll('#fl details').forEach(d=>{d.open=false;d.querySelectorAll('input[type=checkbox]').forEach(i=>i.checked=d.dataset.k==='src')});
 document.querySelectorAll('#fl input[data-k]').forEach(i=>i.value='');$('v2-suspect').checked=false;
 $('v2-banner').open=false;document.querySelectorAll('#fl details').forEach(d=>{const n=d.querySelectorAll('input:checked').length;d.querySelector('summary').textContent=(DN[d.dataset.k]||'מקור')+(n?' ('+n+')':'')});tab('g');updateResetStatus();coverageUI();
}
function go(){TAB=='raw'?raw():TAB=='c'?cmp():TAB=='v2'?showV2():EX.includes(TAB)?run():0}
function tab(t){TAB=t;$('fl').hidden=['q','hp','ap','ev','v2'].includes(t);document.querySelectorAll('#nv button').forEach(b=>b.classList.toggle('on',b.dataset.t==t));const ex=EX.includes(t);['q','x','c','ev','raw','ap','hp','v2-screen'].forEach(s=>$(s).hidden=s!=(ex?'x':t==='v2'?'v2-screen':t));if(ex){zoomText();if(!TABS[t][1].includes(X.grp))X.grp=TABS[t][1][0];v21AutoTop=(t==='a'||t==='s');PIN.clear();xc();run();zoomText()}if(t=='raw')raw();if(t=='c')cmp();if(t=='ev')renderEvents();if(t==='v2')showV2()}

const EVENT_LABELS={war:['לחימה ומבצעים','War & operations'],hostage:['חטופים והסכמים','Hostages & agreements'],casualty:['אסונות ואבדות','Losses & disasters'],regional:['הסלמה אזורית','Regional escalation'],political:['התפתחויות מדיניות','Political developments'],civil:['חברה והנצחה','Society & commemoration']};
const EVENT_COLORS={war:'#5f7482',hostage:'#27847e',casualty:'#b45a59',regional:'#a76b22',political:'#715db0',civil:'#647e48'};
const bucketRows=(b)=>rows().filter(i=>{const date=D.dates[D.d[i]];return X.gran==='d'?date===b:X.gran==='m'?date.slice(0,7)===b:X.gran==='y'?date.slice(0,4)===b:WK[D.d[i]]===b});
function zoomText(){if($('metric-share')){$('metric-share').classList.toggle('on',X.nm==='share');$('metric-abs').classList.toggle('on',X.nm!=='share')}const el=$('zoom-status');if(!el)return;el.textContent=zoomRange?(locale==='en'?'Zoomed: ':'תצוגה מוגדלת: ')+zoomRange[0]+' — '+zoomRange[1]:(locale==='en'?'Full time range; drag to zoom, click a point to explore underlying songs.':'כל התקופה; גררו כדי להתקרב, לחצו על נקודה כדי לראות את השירים שמרכיבים אותה.');}
function firstDateInBucket(b){if(X.gran==='w'){const d=new Date(b+'T00:00:00Z');d.setUTCDate(d.getUTCDate()-6);return d.toISOString().slice(0,10)}return bs(b)}
function applyZoom(a,b){if(!LB[a]||!LB[b])return;zoomHistory.push(zoomRange);zoomRange=[firstDateInBucket(LB[a]),be(LB[b])];activeDetail=null;$('data-detail').hidden=true;run();zoomText()}
function resetZoom(){zoomHistory=[];zoomRange=null;activeDetail=null;$('data-detail').hidden=true;run();zoomText()}
function zoomBack(){zoomRange=zoomHistory.length?zoomHistory.pop():null;activeDetail=null;$('data-detail').hidden=true;run();zoomText()}
const detailDims=['lang','genre','gender','country','artist','src'];
const sumBy=(R,dim)=>{const m=new Map;for(const i of R){const k=val(i,dim);let p=m.get(k);if(!p)m.set(k,p={name:k,n:0,v:0});p.n++;p.v+=D.v[i]}return [...m.values()].sort((a,b)=>b.n-a.n)};
function showDetail(j,seriesKey){const b=LB[j];if(!b)return;const matches=bucketRows(b);const selected=seriesKey?S.find(s=>s.k===seriesKey):null;
const filtered=selected?matches.filter(i=>{const parts=selected.k.split(' | ');return (X.grp==='artist'?v21ArtistHas(i,parts[0]):val(i,X.grp)===parts[0])&&(!X.split||val(i,X.split)===parts[1])}):matches;
activeDetail={bucket:b,series:seriesKey||null};const panel=$('data-detail');panel.hidden=false;
const periodLabel=X.gran==='w'?(locale==='en'?'Week ending ':'שבוע המסתיים ב־')+b:b;
const tr=(locale==='en'?['Song','Artist','Source','Date','Rank','Raw value','Language','Genre','Recordings']:['שיר','יוצר','מקור','תאריך','דירוג','ערך גולמי','שפה','ז׳אנר','קישורים']);
const songrows=[...filtered].sort((a,b)=>D.s[a]-D.s[b]||D.r[a]-D.r[b]||D.d[a]-D.d[b]);
const counts=sumBy(filtered,'song');const total=filtered.reduce((a,i)=>a+D.v[i],0);
const sources=new Set(filtered.map(i=>D.s[i]));const cross=sources.size>1;
const notice=cross?(locale==='en'?'Values are source-specific; Spotify streams and YouTube views are not added into a comparable measure.':'הערכים שייכים למקורות שונים; אין לפרש סכום streams וצפיות כמדד משותף.'):(locale==='en'?'Raw measured values of the selected source.':'ערכים גולמיים של המקור שנבחר.');
const heading=(locale==='en'?'Exploring ':'פירוט הנתון: ')+periodLabel+(seriesKey?' · '+esc(seriesKey):'');const plotted=selected?selected.v[j]:null;
const dimension=detailDims.map(dim=>{const vals=sumBy(filtered,dim).slice(0,10);return `<div class="detail-dim"><b>${locale==='en'?translateText(DN[dim]):DN[dim]}</b>${vals.map(v=>`<div class="detail-row"><span>${esc(v.name)}</span><span>${v.n.toLocaleString()} · ${(v.n/Math.max(1,filtered.length)*100).toFixed(1)}%</span></div>`).join('')}</div>`}).join('');
panel.innerHTML=`<div class="detail-head"><h3>${heading}</h3><button type="button" id="detail-close">✕</button></div><p>${plotted!=null?(locale==='en'?'Chart value: ':'ערך בגרף: ')+fx(plotted)+(X.nm==='share'?'%':'')+' · ':''}${locale==='en'?'Observed chart rows':'תצפיות דירוג'}: <b>${filtered.length.toLocaleString()}</b> · ${locale==='en'?'Distinct titles':'שירים שונים'}: <b>${counts.length.toLocaleString()}</b> · ${locale==='en'?'Sources':'מקורות'}: <b>${sources.size}</b></p><div class="layoutnote">${notice}</div><div class="detail-dims">${dimension}</div><h4>${locale==='en'?'Contributing songs and observations':'השירים והתצפיות שמרכיבים את הנתון'} (${songrows.length.toLocaleString()})</h4><div class="detail-actions"><button id="detail-csv">${locale==='en'?'Export matching observations CSV':'ייצוא כל התצפיות (CSV)'}</button><button id="detail-raw">${locale==='en'?'Open source rows':'פתח את הנתונים הגולמיים'}</button></div><div class="detail-table-wrap"><table><thead><tr>${tr.map(v=>`<th>${v}</th>`).join('')}</tr></thead><tbody>${songrows.slice(0,100).map(i=>{const t=T[D.t[i]];return `<tr>${[v21SongName(t),v21Artists(t).join(', '),SRC[D.s[i]],D.dates[D.d[i]],D.r[i],D.v[i].toLocaleString(),t[2],t[5]].map(v=>`<td>${esc(v??'')}</td>`).join('')+`<td>${linksHtml(t)}</td>`}</tr>`}).join('')}</tbody></table></div><p class="layoutnote">${locale==='en'?'Showing first 100 rows, CSV contains all matches. Percentages above are shares of observed chart appearances, not all listening.':'מוצגות 100 רשומות ראשונות; ה־CSV כולל את כולן. האחוזים בפילוחים הם מתוך הופעות בדירוג בלבד, ולא מכלל ההאזנה.'}</p>`;
panel.querySelector('#detail-close').onclick=()=>{panel.hidden=true;activeDetail=null};
panel.querySelector('#detail-raw').onclick=()=>{F.from=firstDateInBucket(b);F.to=be(b);if(seriesKey){F.item=[X.grp,selected.base]}tab('raw')};
panel.querySelector('#detail-csv').onclick=()=>dl('observations_'+b+'.csv',csv(songrows.map(i=>({date:D.dates[D.d[i]],source:SRC[D.s[i]],song:T[D.t[i]][0],artist:T[D.t[i]][1],rank:D.r[i],value:D.v[i],language:T[D.t[i]][2],genre:T[D.t[i]][5],performance_id:T[D.t[i]][19],data_status:D.status?.[i]?'suspect_repeated_snapshot':'observed'}))),'text/csv');
panel.scrollIntoView({behavior:'smooth',block:'nearest'});
}
function renderEvents(){const en=locale==='en';$('event-guide').textContent=en?'Filter event categories; select an event to explore a surrounding window. Events are contextual markers, not proof of causation.':'סננו אירועים לפי סוג. בחירת אירוע תפתח חלון זמן סביבו בגרף. אירועים הם נקודות הקשר, לא הוכחה לסיבתיות.';
$('event-types').innerHTML=Object.entries(EVENT_LABELS).map(([k,v])=>`<label style="border-color:${EVENT_COLORS[k]}"><input type="checkbox" data-event-type="${k}" ${eventTypes.has(k)?'checked':''}><span style="color:${EVENT_COLORS[k]}">●</span> ${v[en?1:0]}</label>`).join('');
$('et2').innerHTML='<thead><tr><th>'+(en?'Date':'תאריך')+'</th><th>'+(en?'Category':'סוג')+'</th><th>'+(en?'Event':'אירוע')+'</th><th></th></tr></thead><tbody>'+EV.filter(e=>eventTypes.has(e.type||'war')).sort((a,b)=>a.date.localeCompare(b.date)).map((e)=>`<tr><td>${esc(e.date)}</td><td>${EVENT_LABELS[e.type||'war']?.[en?1:0]||'—'}</td><td>${esc(en?(e.en||e.label):e.label)}</td><td><button data-event-date="${e.date}">${en?'Explore ± 4 weeks':'חקור ± 4 שבועות'}</button> ${e.url?`<a target="_blank" rel="noopener" href="${esc(e.url)}">${en?'Source':'מקור'}</a>`:''}</td></tr>`).join('')+'</tbody>';
}
function exploreEvent(date){const d=new Date(date+'T00:00:00Z');const start=new Date(d),end=new Date(d);start.setUTCDate(d.getUTCDate()-28);end.setUTCDate(d.getUTCDate()+28);zoomHistory.push(zoomRange);zoomRange=[start.toISOString().slice(0,10),end.toISOString().slice(0,10)];tab('g');zoomText()}


function sourceLinks(t){
 const a=[];const spotify=String(t[15]||'').trim();const youtube=String(t[16]||'').trim();
 const sm=spotify.match(/(?:spotify:track:|open\.spotify\.com\/track\/)([a-zA-Z0-9]{22})/);
 if(sm)a.push(['Spotify','https://open.spotify.com/track/'+sm[1]]);
 const ym=youtube.match(/(?:[?&]v=|youtu\.be\/|youtube\.com\/shorts\/)?([a-zA-Z0-9_-]{11})(?:[?&].*)?$/);
 if(ym&&/^[a-zA-Z0-9_-]{11}$/.test(ym[1]))a.push(['YouTube','https://www.youtube.com/watch?v='+ym[1]]);
 return a;
}
function linksHtml(t){const a=sourceLinks(t);return a.length?`<div class=recording-links>${a.map(([n,url])=>`<a class=source-link href="${esc(url)}" target=_blank rel="noopener noreferrer">↗ ${n}</a>`).join('')}</div>`:`<span class=link-empty>${locale==='en'?'No verified platform link in this record':'אין מזהה פלטפורמה ברשומה זו'}</span>`}
function performanceLinks(pid){const found=new Map();for(const t of T){if(t[19]!==pid)continue;for(const [n,url] of sourceLinks(t))found.set(n+'|'+url,[n,url]);}return [...found.values()];}
function showV2(){
 const q=($('v2-search')?.value||'').trim().toLowerCase();
 const a=T.map((t,i)=>({t,i})).filter(({t})=>!q||(t[0]+' '+t[1]+' '+t[19]).toLowerCase().includes(q));
 $('v2-count').textContent=(locale==='en'?'Performances matching: ':'ביצועים תואמים: ')+a.length.toLocaleString()+' / '+T.length.toLocaleString();
 $('v2-result').innerHTML=a.slice(0,250).map(({t,i})=>`<div class="v2-resultrow"><div><strong>${esc(t[0])}</strong>${esc(t[1])}<div class=v2-source-links>${performanceLinks(t[19]).map(([n,url])=>`<a class=source-link href="${esc(url)}" rel="noopener noreferrer" target=_blank>↗ ${n}</a>`).join('')||`<span class=link-empty>${locale==='en'?'No direct link':'ללא קישור ישיר'}</span>`}</div></div><div><small>Performance ID</small><div dir="ltr">${esc(t[19])}</div></div><div><span class="v2-chip">${esc(t[21]||'provisional')}</span> <button data-v2-song="${i}">${locale==='en'?'Explore observations':'חיפוש בכל התצפיות'}</button></div></div>`).join('');
}

async function init(){await ensure();T=D.tracks;try{EV=window.WM_EVENTS||await (await fetch('data/events.json')).json()}catch(e){}try{EV=EV.concat(JSON.parse(localStorage.wm_ev||'[]'))}catch(e){}
 filters();F.src=new Set(['0','1','2']);document.querySelectorAll('#fl details[data-k=src] input').forEach(i=>i.checked=F.src.has(i.value));document.querySelector('#fl details[data-k=src] summary').textContent='מקור (3)';coverageUI();$('nv').innerHTML=Object.entries(TABS).map(([k,v])=>`<button data-t=${k}>${v[0]}</button>`).join('');
 const P=new URLSearchParams(location.search);for(const[k,v]of P)if(k in A||k=='src')F[k]=new Set(v.split(';'));else if(['q','from','to','rank'].includes(k))F[k]=v;for(const k of['grp','split','m','ch','gran'])if(P.get(k))X[k]=P.get(k);if(P.get('nm'))X.nm=P.get('nm');BAD=new Set((D.qa||{}).bad||[]);WK=D.dates.map(d=>{const t=new Date(d+'T00:00:00Z'),k=(4-t.getUTCDay()+7)%7;t.setUTCDate(t.getUTCDate()+k);return t.toISOString().slice(0,10)});if(BAD.size)$('bn').hidden=false;
 window.WM={rows:(f=F)=>rows(f),series:async()=>{await ensure();build();return tableRows()}};
 if(P.get('api')){await ensure();const r=P.get('api')=='rows'?rows().map(i=>({date:D.dates[D.d[i]],source:SRC[D.s[i]],rank:D.r[i],value:D.v[i],name:T[D.t[i]][0],artist:T[D.t[i]][1]})):await WM.series();document.body.innerHTML='<pre>'+(P.get('format')=='csv'?csv(r):JSON.stringify(r,null,1))+'</pre>';return}
 $('reset-all').onclick=resetAll; $('reset-all').textContent=locale==='en'?'↺ Reset everything':'↺ איפוס הכול'; $('zoomout').onclick=zoomBack;$('zoomreset').onclick=resetZoom;$('metric-share').onclick=()=>{X.nm='share';if(!['cm','n'].includes(X.m))X.m='n';xc();run();zoomText()};$('metric-abs').onclick=()=>{X.nm='none';xc();run();zoomText()};$('event-types').onchange=e=>{const k=e.target.dataset.eventType;if(k){e.target.checked?eventTypes.add(k):eventTypes.delete(k);renderEvents();if(EX.includes(TAB))draw()}};$('et2').onclick=e=>{const b=e.target.closest('[data-event-date]');if(b)exploreEvent(b.dataset.eventDate)};window.addEventListener('languagechange',()=>{$('reset-all').textContent=locale==='en'?'↺ Reset everything':'↺ איפוס הכול';updateResetStatus();if(TAB==='ev')renderEvents();zoomText();if(activeDetail){const j=LB.indexOf(activeDetail.bucket);if(j>=0)showDetail(j,activeDetail.series)}});$('nv').onclick=e=>e.target.dataset.t&&tab(e.target.dataset.t); $('fl').addEventListener('toggle',e=>{const d=e.target;if(d?.matches?.('details.ms')&&d.open){document.querySelectorAll('#fl details.ms[open]').forEach(other=>{if(other!==d)other.open=false})}},true);
 $('v2-search').oninput=showV2;$('v2-result').onclick=e=>{const b=e.target.closest('[data-v2-song]');if(!b)return;const t=T[+b.dataset.v2Song];F={src:new Set(['0','1','2']),performanceId:t[19]};tab('raw')};$('question-search').oninput=qcards;$('question-categories').onclick=e=>{const b=e.target.closest('[data-qcat]');if(b){qFilter=b.dataset.qcat;qcards()}};
 $('qs').onclick=e=>{const i=e.target.dataset.q;if(i==null)return;const q=ALLQ[i];X={grp:'lang',split:'',m:'n',ch:'line',gran:'w',n:8,nm:'share',...q[3]};PIN.clear();HID.clear();tab(q[2]);setF(q[4])};
 $('seriessearch').oninput=renderSeriesPicker; $('serieschoices').onchange=e=>{const k=e.target.dataset.series;if(!k)return;v21AutoTop=false;e.target.checked?PIN.add(k):PIN.delete(k);renderSeriesPicker();draw();renderV21Insights();tbl()};$('seriesclear').onclick=()=>{v21AutoTop=false;PIN.clear();draw();tbl();renderSeriesPicker();renderV21Insights()};$('seriesall').onclick=()=>{v21AutoTop=(TAB==='a'||TAB==='s');PIN.clear();$('seriessearch').value='';if(v21AutoTop)S.slice(0,10).forEach(s=>PIN.add(s.k));renderSeriesPicker();draw();tbl();renderV21Insights()};
 $('lg').onclick=e=>e.target.dataset.k&&hide(e.target.dataset.k);$('lg').onmouseover=e=>{if(e.target.dataset.k&&e.target.dataset.k!=HI){HI=e.target.dataset.k;draw();hl()}};
 const cv=$('cv');cv.onmousemove=hover;cv.onmouseleave=()=>{$('tip').style.display='none';HI=null;if(!dr){draw();hl()}};cv.onmousedown=e=>{const[mx]=mxp(e);dr={x:mx,j:jat(mx)}};cv.onmouseup=e=>{if(!dr)return;const[mx]=mxp(e);if(Math.abs(mx-dr.x)>24){const a=Math.min(dr.j,jat(mx)),b=Math.max(dr.j,jat(mx));if($('dragperiod').checked)addP(a,b);else applyZoom(a,b)}else showDetail(jat(mx),HI);dr=null;draw()};
 $('tb').onmouseover=e=>{const r=e.target.closest('tr[data-k]');if(r&&r.dataset.k!=HI){HI=r.dataset.k;draw();hl()}};$('tb').onclick=e=>{const r=e.target.closest('tr[data-k]');if(!r)return;e.preventDefault();if(e.target.dataset.h)return hide(r.dataset.k);if(e.target.dataset.r){F.item=[X.grp,S[e.target.dataset.r].base];tab('raw');return}tog(r.dataset.k)};
 document.body.addEventListener('click',e=>{const t=e.target;if(t.dataset.dp!=null){PER.splice(+t.dataset.dp,1);sp_();TAB=='c'?cmp():(pl(),draw())}if(t.dataset.go){e.preventDefault();tab('c')}if(!t.closest('#fl'))document.querySelectorAll('#fl details[open]').forEach(d=>d.open=false)});
 $('pe').oninput=e=>{const t=e.target,p=PER[t.dataset.pi];if(p){p[t.dataset.pf]=t.value;sp_()}};$('pe').onchange=cmp;$('cm').onchange=cmp;$('pa').onclick=()=>{PER.push({n:'תקופה '+(PER.length+1),f:'2024-01-01',t:'2024-06-30',c:PC[PER.length%PC.length]});sp_();cmp()};$('pd').onclick=()=>{PER=defPer();sp_();cmp()};$('cb').onclick=()=>dl('compare.csv',csv(window.cmpRows||[]),'text/csv');
 $('ea').onclick=()=>{if(!$('ed').value)return;const l=JSON.parse(localStorage.wm_ev||'[]');l.push({date:$('ed').value,label:$('et').value,type:$('event-new-type').value});localStorage.wm_ev=JSON.stringify(l);EV.push(l.at(-1));tab('ev')};$('ex').onclick=()=>dl('events.json',JSON.stringify(EV,null,1),'application/json');$('ei').onchange=async e=>{EV=JSON.parse(await e.target.files[0].text());localStorage.wm_ev=JSON.stringify(EV);tab('ev')};
 $('rc').onclick=()=>dl('raw_rows.csv',csv(typeof window.rawA==='function'?window.rawA():[]),'text/csv');$('rk').onclick=()=>dl('catalog.csv',csv(T.map(t=>Object.fromEntries(D.cols.map((c,i)=>[c,t[i]])))),'text/csv');
 const u=location.origin+location.pathname;$('ex1').textContent=`${u}?api=series&grp=artist&m=cm&src=0;1&format=csv\n${u}?api=series&grp=gender&split=src&m=n&gran=m&format=json\n${u}?api=rows&q=עם ישראל חי&format=csv`;tab('g');info();localize();updateResetStatus();}
init().catch(e=>{console.error(e);$('info').textContent=(locale==='en'?'Failed to load: ':'שגיאת טעינה: ')+e.message;$('bn').hidden=false;$('bn').textContent=$('info').textContent});
