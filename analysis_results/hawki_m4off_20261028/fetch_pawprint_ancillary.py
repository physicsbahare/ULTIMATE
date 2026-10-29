from pathlib import Path
import urllib.request,urllib.parse,json,hashlib
O=Path(__file__).resolve().parent;log=json.loads((O/'ancillary_download_log.json').read_text());total=sum(x.get('bytes',0) for x in log)
for j,(ra,dec) in enumerate([(245.96232,-26.54519),(245.88960,-26.54408),(245.96301,-26.48043),(245.89024,-26.47951)]):
 for typ,dp in [('variance','ADP.2021-12-16T10:45:25.740'),('confidence','ADP.2021-12-16T10:45:25.741')]:
  name=f'pawprint_{typ}_region{j}.fits';p=O/name
  if p.exists():continue
  url='https://dataportal.eso.org/dataPortal/soda/sync?'+urllib.parse.urlencode({'ID':'ivo://eso.org/ID?'+dp,'CIRCLE':f'{ra} {dec} 0.006'})
  try:
   r=urllib.request.urlopen(url,timeout=90).read(4*1024**2+1);assert r.startswith(b'SIMPLE') and len(r)<=4*1024**2 and total+len(r)<80*1024**2;p.write_bytes(r);total+=len(r);log.append(dict(path=name,url=url,bytes=len(r),sha256=hashlib.sha256(r).hexdigest(),status='ok'))
  except Exception as ex:log.append(dict(path=name,url=url,status='failed',error=repr(ex)))
  print(name,log[-1]['status'],flush=True)
(O/'ancillary_download_log.json').write_text(json.dumps(log,indent=2))
