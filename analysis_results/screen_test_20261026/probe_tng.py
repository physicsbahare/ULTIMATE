from pathlib import Path
import urllib.request,json,urllib.error
O=Path(__file__).resolve().parent
key=(Path.home()/'.tng_api_key').read_text().strip()
url='https://www.tng-project.org/api/TNG50-1/snapshots/99/subhalos/294866/'
r=urllib.request.Request(url,headers={'API-Key':key})
try:
 with urllib.request.urlopen(r,timeout=30) as response:
  raw=response.read(2_000_001)
  if len(raw)>2_000_000: raise ValueError('Metadata response exceeds safety bound')
  data=json.loads(raw)
 (O/'sources/tng_subhalo_metadata.json').write_text(json.dumps(data,indent=2))
 print(json.dumps({k:v for k,v in data.items() if any(x in k.lower() for x in ['supp','url','skirt','related'])},indent=2))
except Exception as e:
 print(type(e).__name__,str(e))
