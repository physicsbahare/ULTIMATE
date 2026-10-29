from pathlib import Path
import json,urllib.request,urllib.parse
O=Path(__file__).resolve().parent; key=(Path.home()/'.tng_api_key').read_text().strip()
urls=['https://www.tng-project.org/api/TNG50-1/files/skirt_atlas/','https://www.tng-project.org/api/TNG50-1/files/','https://www.tng-project.org/data/docs/specifications/']
rows=[]
for j,url in enumerate(urls):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'API-Key':key}),timeout=30) as r:
   raw=r.read(3_000_001); ct=r.headers.get('Content-Type',''); assert len(raw)<=3_000_000
  (O/'sources'/f'tng_catalogue_probe_{j}.txt').write_bytes(raw)
  text=raw.decode(errors='replace'); print(url,ct,'bytes',len(raw),flush=True)
  if 'json' in ct:
   data=json.loads(text)
   if j==0: print(str(data)[:4000])
   else: print(str(data)[:1000])
  else:
   import re
   print('\n'.join(x[:1000] for x in text.splitlines() if any(w in x.lower() for w in ['dr2','skirt','broadband'])))
  rows.append({'url':url,'status':'success','content_type':ct,'bytes':len(raw)})
 except Exception as e: rows.append({'url':url,'error':str(e)}); print(type(e).__name__,str(e),flush=True)
(O/'tng_catalogue_probe.json').write_text(json.dumps(rows,indent=2))
