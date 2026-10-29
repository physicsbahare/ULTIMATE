from pathlib import Path
import urllib.request,urllib.parse,json
from astropy.io.votable import parse_single_table
O=Path(__file__).resolve().parent;out=[]
for dp in ['ADP.2021-12-16T10:45:25.739','ADP.2021-12-16T10:45:26.018']:
 url='https://archive.eso.org/datalink/links?'+urllib.parse.urlencode({'ID':'ivo://eso.org/ID?'+dp})
 try:
  raw=urllib.request.urlopen(url,timeout=30).read(2_000_000);p=O/(dp.replace(':','_')+'_datalink.xml');p.write_bytes(raw);t=parse_single_table(p).to_table().to_pandas();t.to_csv(p.with_suffix('.csv'),index=False);out.append(dict(id=dp,status='ok',url=url,rows=len(t)));print(t[['semantics','access_url','content_length','eso_category']].to_string(index=False))
 except Exception as ex:out.append(dict(id=dp,status='failed',url=url,error=repr(ex)));print(out[-1])
(O/'metadata_fetch.json').write_text(json.dumps(out,indent=2))
