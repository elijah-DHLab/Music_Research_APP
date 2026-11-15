#!/usr/bin/env python3
"""Static regression/integrity checks; requires Python 3 only."""
import gzip,json,pathlib,re,sys,hashlib
P=pathlib.Path(__file__).resolve().parent.parent
j=P/'data/data.json';g=P/'data/data.json.gz';js=P/'data/data.js';index=P/'index.html'
assert j.exists() and g.exists() and js.exists() and index.exists()
plain=j.read_bytes();assert gzip.decompress(g.read_bytes())==plain, 'Compressed data out of sync: rebuild data'
d=json.loads(plain);assert js.read_text('utf8')=='window.WM_DATA='+plain.decode('utf8')+';', 'JS fallback out of sync'
N=len(d['t']);assert N==214548,('unexpected dataset size',N)
assert all(len(d[k])==N for k in ('d','r','t','v','pk','pr','dc','s'))
assert all(0<=k<len(d['tracks']) for k in d['t'])
assert all(0<=k<len(d['dates']) for k in d['d'])
assert set(d['s'])=={0,1,2},'Unexpected source codes'
for f in ['help.html','help-en.html','i18n.js','data/works.csv','data/recordings.csv','data/master_crosswalk.csv','data/events.js']:
 assert (P/f).exists(),f
html=index.read_text('utf8')
for src in re.findall(r'(?:src|href)="(data/[^"?]+|help(?:-en)?.html|i18n.js)"',html):
 assert (P/src).exists(),src
print('PASS gzip/JSON/JS source parity; observations:',N,'tracks:',len(d['tracks']),'dates:',len(d['dates']))
print('PASS source IDs, ranges, bilingual help and all static links')
print('Compressed payload:',round(g.stat().st_size/1024/1024,2),'MiB; raw:',round(j.stat().st_size/1024/1024,2),'MiB')
