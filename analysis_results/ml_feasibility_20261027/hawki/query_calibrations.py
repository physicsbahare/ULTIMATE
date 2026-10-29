from pathlib import Path
import urllib.request,urllib.parse,json
from astropy.io.votable import parse_single_table
O=Path(__file__).resolve().parent
ids=['HAWKI.2018-01-03T08:22:19.465','HAWKI.2018-01-03T08:38:05.077','HAWKI.2018-01-06T08:25:19.803'];log=[]
for dp in ids:
 for fmt in ['votable','xml']:
  u='https://archive.eso.org/calselector/v1/associations?'+urllib.parse.urlencode(dict(dp_id=dp,mode='Raw2Master',responseformat=fmt))
  try:
   r=urllib.request.urlopen(u,timeout=60).read(2000000);p=O/('cal_association_'+dp+'_'+fmt+'.xml');p.write_bytes(r)
   if fmt=='votable':parse_single_table(p).to_table().to_pandas().to_csv(O/('cal_association_'+dp+'.csv'),index=False)
   log.append(dict(dp_id=dp,url=u,bytes=len(r),status='ok'))
  except Exception as e:log.append(dict(dp_id=dp,url=u,status='failed',error=repr(e)))
  print(log[-1],flush=True)
(O/'calibration_query_log.json').write_text(json.dumps(log,indent=2))
