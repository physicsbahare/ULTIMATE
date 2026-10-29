"""Bounded official read-only ESO metadata queries; never downloads science pixels."""
from pathlib import Path
import urllib.request,urllib.parse,json,time
import pandas as pd
from astropy.io.votable import parse_single_table
O=Path(__file__).resolve().parent
queries={
'reduced_programme':('https://archive.eso.org/tap_obs/sync',"SELECT * FROM ivoa.ObsCore WHERE instrument_name='HAWKI' AND proposal_id='60.A-9475(A)' AND CONTAINS(POINT('ICRS',s_ra,s_dec),CIRCLE('ICRS',157.0,-43.9,0.2))=1"),
'raw_programme':('https://archive.eso.org/tap_raw/sync',"SELECT * FROM dbo.raw WHERE instrument='HAWKI' AND prog_id='60.A-9475(A)' AND date_obs BETWEEN '2018-01-01' AND '2018-02-01'"),
'calibration_near_dates':('https://archive.eso.org/tap_raw/sync',"SELECT TOP 1000 * FROM dbo.raw WHERE instrument='HAWKI' AND dp_cat='CALIB' AND date_obs BETWEEN '2018-01-01' AND '2018-01-08'")}
log=[]
for name,(endpoint,q) in queries.items():
 u=endpoint+'?'+urllib.parse.urlencode(dict(REQUEST='doQuery',LANG='ADQL',FORMAT='csv',QUERY=q))
 (O/(name+'.adql')).write_text(q+'\n');entry=dict(name=name,url=u,adql=q)
 try:
  with urllib.request.urlopen(u,timeout=60) as f:r=f.read(3000000)
  (O/(name+'.csv')).write_bytes(r);entry.update(bytes=len(r),status='ok');print(name,len(r),flush=True)
 except Exception as e:entry.update(status='failed',error=repr(e));print(entry,flush=True)
 log.append(entry)
 if name=='reduced_programme' and entry['status']=='ok':
  tab=pd.read_csv(O/(name+'.csv'))
  for dp in tab.dp_id:
   u='https://archive.eso.org/datalink/links?'+urllib.parse.urlencode({'ID':'ivo://eso.org/ID?'+dp})
   try:
    r=urllib.request.urlopen(u,timeout=40).read(1000000);path=O/('datalink_'+dp+'.xml');path.write_bytes(r)
    t=parse_single_table(path).to_table().to_pandas();t.to_csv(O/('datalink_'+dp+'.csv'),index=False)
    log.append(dict(name='datalink',dp_id=dp,url=u,bytes=len(r),status='ok'))
   except Exception as e:log.append(dict(name='datalink',dp_id=dp,url=u,error=repr(e),status='failed'))
(O/'archive_query_log.json').write_text(json.dumps(log,indent=2));print('DONE',flush=True)
