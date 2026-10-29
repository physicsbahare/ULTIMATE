"""Verify the completed nonfinal cache and frozen archive audit without unsealing final data."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
O=Path(__file__).resolve().parent;R=O.parents[2]
m=pd.read_csv(O/'frozen_galaxy_partitions.csv');a=pd.read_csv(O/'archive_inventory.csv');v=pd.read_csv(O/'available_galaxies.csv');f=pd.read_csv(O/'fits_inventory.csv');p=pd.read_csv(O/'physical_maps.csv')
assert len(m)==120 and len(a)==120 and len(v)==120
assert m.partition.value_counts().to_dict()=={'development':86,'final_test':20,'validation':14}
assert a.sha_matches.all() and a.size_matches.all() and a.recorded_gzip_CRC.eq('passed').all()
final=set(m[m.partition=='final_test'].subhalo_id);nonfinal=set(m[m.partition!='final_test'].subhalo_id)
assert len(final)==20 and len(nonfinal)==100
assert a[~a.sealed_final].current_gzip_CRC.eq('passed').all()
assert v[~v.sealed_final].cache_complete.all() and not v[v.sealed_final].cache_complete.any()
assert set(a[a.sealed_final].subhalo_id)==final and not a[a.sealed_final].science_opened.any()
assert not set(f.subhalo_id)&final and set(f.subhalo_id)==nonfinal
assert len(f)==24000 and len(p)==500 and f.header_valid.all() and f.grid_valid.all()
assert f.member_bytes.eq(10244160).all()
old=pd.read_csv(R/'analysis_results/multigalaxy_morphology_20261027/fits_inventory.csv')
expected_bands=set(old[old.scene=='dusty'].band)
assert len(expected_bands)==22
for sid,g in f.groupby('subhalo_id'):
 assert len(g)==240
 for view,h in g.groupby('view'):
  assert len(h)==48 and set(h[h.scene=='dusty'].band)==expected_bands and set(h[h.scene=='clear'].band)==expected_bands
  assert h.pixel_validated.sum()==7
keys={f'{s}_{b}' for s in ['dusty','clear'] for b in ['LSST_g','2MASS_J','2MASS_Ks']}|{'dust'}
cache_checks=[]
for sid in sorted(nonfinal):
 c=O/'cache'/str(sid);assert (c/'complete.json').exists()
 for view in [f'O{i}' for i in range(1,6)]:
  z=c/f'{view}.npz'
  with np.load(z) as images:
   assert set(images.files)==keys
   for key in keys:
    image=images[key]
    assert image.shape==(800,800) and image.dtype==np.dtype('float32') and np.isfinite(image).all()
    tol=float(f[(f.subhalo_id==sid)&(f.view==view)&(f.band=='dustmass')].roundoff_tolerance.iloc[0]) if key=='dust' else 0.
    assert image.min()>=-tol
  cache_checks.append(dict(subhalo_id=sid,view=view,bytes=z.stat().st_size,sha256=hashlib.sha256(z.read_bytes()).hexdigest(),passed=True))
for sid in final:assert not (O/'cache'/str(sid)).exists()
x=f.merge(old[['subhalo_id','member','member_sha256']],on=['subhalo_id','member'],suffixes=['_current','_prior'])
x['matches_prior_raw_hash']=x.member_sha256_current==x.member_sha256_prior
assert len(x)==26*240 and x.matches_prior_raw_hash.all()
x[['subhalo_id','member','member_sha256_current','member_sha256_prior','matches_prior_raw_hash']].to_csv(O/'original26_raw_hash_comparison.csv',index=False)
pd.DataFrame(cache_checks).to_csv(O/'cache_file_integrity.csv',index=False)
assert json.loads((O/'development_gate.json').read_text())['passed']
assert json.loads((O/'failures.json').read_text())==[]
result=dict(passed=True,total_archives=120,nonfinal_galaxies=100,sealed_final_integrity_only=20,nonfinal_views=500,FITS_headers=24000,selected_full_arrays_validated=3500,cache_arrays=3500,original26_raw_hash_matches=len(x),exact_zero_projected_dust_galaxies=sorted(int(sid) for sid,g in p.groupby('subhalo_id') if g.zero_projected_dust.all()),final_science_opened=False)
(O/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
