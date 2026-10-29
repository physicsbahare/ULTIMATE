from pathlib import Path
import urllib.request,urllib.parse,json
O=Path(__file__).resolve().parent;log=[]
for name in ['raw_programme','calibration_near_dates']:
 q=(O/(name+'.adql')).read_text();u='https://archive.eso.org/tap_obs/sync?'+urllib.parse.urlencode(dict(REQUEST='doQuery',LANG='ADQL',FORMAT='csv',QUERY=q));entry=dict(name=name,url=u,adql=q)
 try:
  r=urllib.request.urlopen(u,timeout=60).read(3000000);(O/(name+'.csv')).write_bytes(r);entry.update(bytes=len(r),status='ok')
 except Exception as e:entry.update(status='failed',error=repr(e))
 log.append(entry);print(entry,flush=True)
(O/'raw_query_log.json').write_text(json.dumps(log,indent=2))
