from pathlib import Path
import urllib.request,urllib.parse,json
import pandas as pd
O=Path(__file__).resolve().parent
q="SELECT designation,ra,dec,k_m,k_cmsig,j_m,h_m,ph_qual,cc_flg,rd_flg,prox FROM fp_psc WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',156.96365,-43.90355,0.055))=1"
urls={'irsa_2mass.csv':'https://irsa.ipac.caltech.edu/TAP/sync?'+urllib.parse.urlencode(dict(REQUEST='doQuery',LANG='ADQL',FORMAT='csv',QUERY=q)),'eso_jan6_source_catalogue.fits':'https://dataportal.eso.org/dataPortal/file/ADP.2018-02-14T09:20:46.487'}
t=pd.read_csv(next(O.glob('cal_association_HAWKI.2018-01-06*.csv')));row=t[t.eso_category=='PHOTCAL_TAB'].iloc[0];urls['associated_photcal.fits']=row.access_url
log=[]
for name,u in urls.items():
 try:
  r=urllib.request.urlopen(u,timeout=45).read(8*1024*1024+1)
  if len(r)>8*1024*1024:raise ValueError('8MiB individual bound')
  (O/name).write_bytes(r);entry=dict(name=name,url=u,bytes=len(r),status='ok')
 except Exception as e:entry=dict(name=name,url=u,status='failed',error=repr(e))
 log.append(entry);print(entry,flush=True)
(O/'catalogue_download_log.json').write_text(json.dumps(log,indent=2));(O/'irsa_2mass.adql').write_text(q)
