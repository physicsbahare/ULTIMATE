from pathlib import Path
import numpy as np,pandas as pd
from measure_psf import fit_star
O=Path(__file__).resolve().parent;s=pd.read_csv(O/'validated_stars.csv');rows=[];flags=[]
for field,a in s.groupby('field'):
 z=np.load(O/(field+'_stamps.npz'));lookup={int(i):j for j,i in enumerate(z['ids'])};use=a[a.primary_star].sort_values(['by','bx','peak_snr']).groupby(['bx','by']).head(1);use=use.iloc[np.linspace(0,len(use)-1,min(12,len(use))).astype(int)]
 for t in a[a.accepted].itertuples():
  j=lookup[int(t.source_local_id)];cut=z['cuts'][j][6:47,6:47];model=z['models'][j];top=np.unravel_index(np.argmax(model),model.shape);deficit=float((model[top]-cut[top])/t.amplitude);flags.append(dict(field=field,source_local_id=t.source_local_id,core_deficit_fraction=deficit,product_R2_Vega_magnitude=(28.0850955021825 if field=='tile0' else 28.0449210179296)-2.5*np.log10(t.flux_R2_ADU),flat_core_flag=bool(deficit>.05)))
 for t in use.itertuples():
  j=lookup[int(t.source_local_id)];large=z['cuts'][j]
  for radius in [13,20]:
   cut=large[26-radius:27+radius,26-radius:27+radius];r,_=fit_star(cut.astype(float),t.local_sigma_ADU,t.scale_arcsec);rows.append(dict(field=field,source_local_id=t.source_local_id,radius_pixels=radius,fwhm_arcsec=r['fwhm_arcsec'],beta=r['beta'],q=r['q'],accepted=r['accepted']))
pd.DataFrame(rows).to_csv(O/'fit_window_sensitivity.csv',index=False);pd.DataFrame(flags).to_csv(O/'saturation_profile_checks.csv',index=False);print('Fit-window sensitivity and conservative saturation checks complete')
