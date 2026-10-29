from pathlib import Path
import urllib.request,urllib.parse,hashlib,json
import pandas as pd
O=Path(__file__).resolve().parent;log=[];budget=80*1024**2;total=0

def get(name,url,limit):
 global total
 p=O/name
 if p.exists():return
 try:
  with urllib.request.urlopen(url,timeout=90) as f:r=f.read(limit+1)
  assert len(r)<=limit and total+len(r)<=budget
  if name.endswith('.fits'):assert r.startswith(b'SIMPLE')
  p.write_bytes(r);total+=len(r);log.append(dict(path=name,url=url,bytes=len(r),sha256=hashlib.sha256(r).hexdigest(),status='ok'))
 except Exception as ex:log.append(dict(path=name,url=url,status='failed',error=repr(ex)))
 print(log[-1]['path'],log[-1]['status'],flush=True)
get('tile_catalogue.fits','https://dataportal.eso.org/dataPortal/file/ADP.2021-12-16T10:45:25.815',20*1024**2)
# Four separated detector-centre regions, variance/confidence only. Science already local.
for j,(ra,dec) in enumerate([(245.96232,-26.54519),(245.88960,-26.54408),(245.96301,-26.48043),(245.89024,-26.47951)]):
 for typ,dp in [('variance','ADP.2021-12-16T10:45:26.019'),('confidence','ADP.2021-12-16T10:45:26.020')]:
  url='https://dataportal.eso.org/dataPortal/soda/sync?'+urllib.parse.urlencode({'ID':'ivo://eso.org/ID?'+dp,'CIRCLE':f'{ra} {dec} 0.010'})
  get(f'tile_{typ}_region{j}.fits',url,8*1024**2)
query="SELECT TOP 25000 source_id,ra,dec,pmra,pmdec,ref_epoch,phot_g_mean_mag,ruwe,parallax,parallax_error FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',245.9263,-26.51232,0.22)) AND phot_g_mean_mag<20 ORDER BY phot_g_mean_mag"
url='https://gea.esac.esa.int/tap-server/tap/sync?'+urllib.parse.urlencode({'REQUEST':'doQuery','LANG':'ADQL','FORMAT':'csv','QUERY':query});get('gaia_dr3.csv',url,6*1024**2)
(O/'ancillary_download_log.json').write_text(json.dumps(log,indent=2))
