from pathlib import Path
import urllib.request,urllib.parse,json,hashlib
from astropy.io.votable import parse_single_table
O=Path(__file__).resolve().parent
# Jan6 tile plus its corresponding variance and confidence; bounded target region.
dps=['ADP.2018-02-14T09:20:46.500','ADP.2018-02-14T09:20:46.501','ADP.2018-02-14T09:20:46.502']
u='https://archive.eso.org/datalink/links?'+urllib.parse.urlencode({'ID':'ivo://eso.org/ID?'+dps[0]})
r=urllib.request.urlopen(u,timeout=40).read(1000000);(O/'jan6_tile_datalink.xml').write_bytes(r);t=parse_single_table(O/'jan6_tile_datalink.xml').to_table().to_pandas();t.to_csv(O/'jan6_tile_datalink.csv',index=False)
products=t[t.eso_category.isin(['SCIENCE.IMAGE','ANCILLARY.VARMAP','ANCILLARY.WEIGHTMAP'])];log=[]
for _,row in products.iterrows():
 dp=row.access_url.rsplit('/',1)[-1];url='https://dataportal.eso.org/dataPortal/soda/sync?'+urllib.parse.urlencode({'ID':'ivo://eso.org/ID?'+dp,'CIRCLE':'156.96365 -43.90355 0.035'})
 path=O/('reduced_jan6_'+row.eso_category.split('.')[-1].lower()+'.fits');entry=dict(dp_id=dp,url=url,category=row.eso_category,path=str(path),region='CIRCLE 156.96365 -43.90355 0.035 deg')
 try:
  with urllib.request.urlopen(url,timeout=100) as f:r=f.read(70*1024*1024+1)
  if len(r)>70*1024*1024:raise ValueError('70MiB per-product limit exceeded')
  if not r.startswith(b'SIMPLE'):raise ValueError('Not FITS: '+r[:300].decode(errors='replace'))
  path.write_bytes(r);entry.update(bytes=len(r),sha256=hashlib.sha256(r).hexdigest(),status='ok')
 except Exception as e:entry.update(status='failed',error=repr(e))
 log.append(entry);print(entry,flush=True)
(O/'reduced_download_log.json').write_text(json.dumps(log,indent=2))
