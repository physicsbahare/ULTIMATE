from pathlib import Path
import json,shutil
import numpy as np,pandas as pd
from astropy.io import fits
R=Path('/home/bahareh/ULTIMATE');O=Path(__file__).resolve().parent
rows=[]
for p in R.rglob('*.fits'):
 if any(x in p.parts for x in ['.venv','.git']) or O in p.parents:continue
 try:
  with fits.open(p,mode='readonly',memmap=True) as f:
   h=f[0].header;rows.append(dict(path=str(p.relative_to(R)),instrument=h.get('INSTRUME'),category=h.get('ESO DPR CATG'),type=h.get('ESO DPR TYPE'),pro_catg=h.get('ESO PRO CATG'),programme=h.get('ESO OBS PROG ID'),object=h.get('OBJECT')))
 except Exception as e:rows.append(dict(path=str(p.relative_to(R)),error=repr(e)))
pd.DataFrame(rows).to_csv(O/'local_fits_inventory.csv',index=False)
r=pd.read_csv(O/'raw_programme.csv');local={p.stem for p in (R/'HAWKI_GRAAL/NGC3256').glob('*.fits')};ng=r[r.object.str.replace(' ','').str.upper()=='NGC3256'];ids=set(ng.dp_id)
c=pd.read_csv(O/'calibration_near_dates.csv');c['day']=c.date_obs.str[:10];c.groupby(['day','dp_type','det_dit','det_ndit','filter_path'],dropna=False).size().rename('n').to_csv(O/'raw_calibration_counts.csv')
masters=[]
for p in O.glob('cal_association_*.csv'):
 t=pd.read_csv(p);t['association_file']=p.name;masters.append(t)
m=pd.concat(masters,ignore_index=True);m.to_csv(O/'calibration_association_manifest.csv',index=False)
red=pd.read_csv(O/'reduced_programme.csv');red['form']=np.where(red.dataproduct_subtype=='srctbl','catalogue',np.where(red.dataproduct_subtype=='pawprint','pawprint','tile'));red[['dp_id','form','proposal_id','target_name','obs_id','n_obs','t_exptime','s_resolution','s_pixel_scale','access_estsize','t_min','t_max','obs_creator_did']].to_csv(O/'reduced_product_manifest.csv',index=False)
summary=dict(local_hawki_files=len(local),archive_jan2018_ngc3256=len(ids),missing_local=sorted(ids-local),extra_local=sorted(local-ids),reduced_count=len(red),reduced_forms=red.form.value_counts().to_dict(),raw_calibration_near_dates_count=len(c),matching_1p7s_darks=int(((c.dp_type=='DARK')&np.isclose(c.det_dit,1.7)).sum()),ks_flats=int(((c.dp_type=='FLAT')&c.filter_path.str.contains('KS',case=False,na=False)).sum()),esorex_on_path=shutil.which('esorex'),association_status=[str(pd.read_csv(p).iloc[0].description) for p in O.glob('cal_association_*.csv')])
(O/'archive_summary.json').write_text(json.dumps(summary,indent=2));print(summary)
