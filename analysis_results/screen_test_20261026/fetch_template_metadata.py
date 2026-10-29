from pathlib import Path
import urllib.request,json,hashlib
O=Path(__file__).resolve().parent; S=O/'sources'; tree=json.loads((S/'stellar_template_tree.json').read_text())
for p in ['templates/fsps_full/fsps_QSF_12_v3.param.fits','templates/fsps_full/fsps_QSF_12_v3.sfh.fits']:
 e=next(x for x in tree['tree'] if x['path']==p)
 url=f"https://raw.githubusercontent.com/gbrammer/eazy-photoz/{tree['sha']}/{p}"
 with urllib.request.urlopen(url,timeout=30) as r: raw=r.read(e['size']+1)
 assert len(raw)==e['size'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['sha']
 dest=S/'eazy'/p; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(raw)
from astropy.io import fits
with fits.open(S/'eazy/templates/fsps_full/fsps_QSF_12_v3.param.fits') as h:
 h.info(); print(h[1].columns); print(h[1].data)
