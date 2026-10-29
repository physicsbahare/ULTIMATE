"""Bounded code/curve retrieval and authenticated metadata, never galaxy archive downloads."""
from pathlib import Path
import urllib.request,json,hashlib
O=Path(__file__).resolve().parent; S=O/'sources'
tree=json.loads((S/'calculator_tree.json').read_text()); commit=tree['sha']
paths=['sensitivity/MaunaKea_Sky/ultimate/mk_skybg_zm_16_10_ph_wo_skybb.txt','sensitivity/MaunaKea_Sky/ultimate/mktrans_zm_16_10.txt','sensitivity/MaunaKea_Sky/ultimate/moon.txt']
manifest=[]
for p in paths:
 entry=next(x for x in tree['tree'] if x['path']==p); assert entry['size']<10_000_000
 dest=S/'calculator'/p; dest.parent.mkdir(parents=True,exist_ok=True)
 url=f'https://raw.githubusercontent.com/sali131/ULTIMATE-Subaru-Sensitivity-Calculator/{commit}/{p}'
 if not dest.exists():
  with urllib.request.urlopen(url,timeout=60) as r: raw=r.read(entry['size']+1)
  assert len(raw)==entry['size']
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['sha']
  dest.write_bytes(raw)
 raw=dest.read_bytes(); manifest.append({'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob_sha1':entry['sha']})
 print(p,len(raw),flush=True)
(S/'curve_download_manifest.json').write_text(json.dumps(manifest,indent=2))
key=(Path.home()/'.tng_api_key').read_text().strip()
url='https://www.tng-project.org/api/TNG50-1/snapshots/99/subhalos/294866/'
try:
 with urllib.request.urlopen(urllib.request.Request(url,headers={'API-Key':key}),timeout=30) as r:
  raw=r.read(2_000_001); assert len(raw)<=2_000_000; data=json.loads(raw)
 (S/'tng_subhalo_metadata.json').write_text(json.dumps(data,indent=2))
 print('Authenticated metadata succeeded; relevant fields:')
 print(json.dumps({k:v for k,v in data.items() if any(x in k.lower() for x in ['supp','url','skirt','related'])},indent=2))
except Exception as e: print('TNG metadata error:',type(e).__name__,str(e))
