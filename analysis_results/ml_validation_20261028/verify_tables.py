from pathlib import Path
import json,hashlib
import pandas as pd,numpy as np
O=Path(__file__).resolve().parent;S=O.parent/'ml_expanded_20261028';meta=pd.read_csv(S/'data_audit/frozen_galaxy_partitions.csv');final=set(meta[meta.partition=='final_test'].subhalo_id)
f=pd.read_csv(S/'data_audit/fits_inventory.csv');p=pd.read_csv(S/'data_audit/physical_maps.csv');assert len(f)==24000 and len(p)==500 and f.header_valid.all() and f.grid_valid.all()
assert not set(f.subhalo_id)&final and not set(p.subhalo_id)&final
assert f.groupby(['subhalo_id','view']).size().eq(48).all();assert f.groupby(['subhalo_id','view']).pixel_validated.sum().eq(7).all()
assert f[f.scene.isin(['clear','dusty'])].unit.eq('MJy/sr').all()
assert not any((S/'data_audit/cache'/str(s)).exists() for s in final)
old=pd.read_csv(O.parent/'multigalaxy_morphology_20261027/fits_inventory.csv');x=f.merge(old[['subhalo_id','member','member_sha256']],on=['subhalo_id','member'],suffixes=['_new','_old']);assert len(x)==6240 and (x.member_sha256_new==x.member_sha256_old).all()
assert json.loads((S/'data_audit/failures.json').read_text())==[]
# Independent cache content check, including shape/finite intensity, on all 500 views.
n=0
for sid in meta[meta.partition!='final_test'].subhalo_id:
 assert (S/'data_audit/cache'/str(sid)/'complete.json').exists()
 for view in range(1,6):
  with np.load(S/'data_audit/cache'/str(sid)/f'O{view}.npz') as z:
   assert len(z.files)==7
   for key in z.files:
    a=z[key];assert a.shape==(800,800) and np.isfinite(a).all()
    if key!='dust':assert a.min()>=0
   n+=1
f.to_csv(O/'verified_FITS_inventory.csv.gz',index=False);p.to_csv(O/'physical_diagnostic_metadata.csv',index=False)
result={'nonfinal_galaxies':100,'views':n,'FITS_headers':len(f),'source_selected_full_arrays':3500,'cache_arrays_checked':3500,'old26_member_hash_matches':len(x),'final_science_opened':False,'source_failures':0,'zero_projected_dust_galaxies':int(p.groupby('subhalo_id').zero_projected_dust.all().sum())}
(O/'data_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
