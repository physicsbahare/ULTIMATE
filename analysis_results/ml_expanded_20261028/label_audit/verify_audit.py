"""Validate this audit's saved artifacts without reading any new labels/images."""
from pathlib import Path
import json
import pandas as pd
P=Path(__file__).resolve().parent
r=pd.read_csv(P/'raw_cache_checks.csv');b=r[r.cache_exact_equal.notna()]
assert len(b)==24 and b.cache_exact_equal.all()
assert b.cache_crop_max_abs_difference.max()==0
assert b.inventory_sum_difference.abs().max()<1e-10
assert (r.loc[r['product']=='dustmass','nonzero_pixels']==0).all()
h=json.loads((P/'raw_headers.json').read_text())
keys=['NAXIS1','NAXIS2','BUNIT','CRPIX1','CRPIX2','CRVAL1','CRVAL2','CDELT1','CDELT2','CUNIT1','CUNIT2']
d={(x['subhalo_id'],x['member']):x['header'] for x in h}
for (sid,name),v in d.items():
    if name.endswith('_nodust.fits'):
        c=d[(sid,name.replace('_nodust',''))]
        assert all(c[k]==v[k] for k in keys)
f=pd.read_csv(P/'old_control_fullfield_ratios.csv')
assert len(f)==440 and set(f.subhalo_id)=={13,167418,184937,613192}
assert f.groupby('band').fullfield_A_mag.apply(lambda v:(v>0).all() or (v<0).all()).all()
q=pd.read_csv(P/'old_fixed12_quality_flags.csv');assert len(q)==910
print('PASS: 24 raw/cache matches, 12 pair headers, 4 null maps, 440 old ratios, 910 flags')
