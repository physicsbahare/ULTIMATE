"""Independent 11x11 pixel integration tests of the 3x3 fitting approximation."""
from pathlib import Path
import numpy as np,pandas as pd
import measure_psf as m
O=Path(__file__).resolve().parent;rows=[];y,x=np.indices((41,41))
for fw in [.22,.30,.40]:
 for beta in [2.5,4.]:
  for q in [.8,1.]:
   scale=.10656;a=fw/(2*np.sqrt(2**(1/beta)-1)*scale);ax=a/np.sqrt(q);ay=a*np.sqrt(q);cut=np.zeros((41,41));theta=.4
   for oy in (np.arange(11)+.5)/11-.5:
    for ox in (np.arange(11)+.5)/11-.5:
     u=(x+ox-20.23)*np.cos(theta)+(y+oy-19.73)*np.sin(theta);v=-(x+ox-20.23)*np.sin(theta)+(y+oy-19.73)*np.cos(theta);cut+=2000*(1+(u/ax)**2+(v/ay)**2)**(-beta)/121
   r,_=m.fit_star(cut,1,scale);rows.append(dict(truth_FWHM_arcsec=fw,truth_beta=beta,truth_q=q,fitted_FWHM_arcsec=r['fwhm_arcsec'],delta_FWHM_arcsec=r['fwhm_arcsec']-fw,fractional_FWHM_bias=r['fwhm_arcsec']/fw-1,fitted_beta=r['beta'],fitted_q=r['q'],accepted=r['accepted']))
pd.DataFrame(rows).to_csv(O/'quadrature_sensitivity.csv',index=False);print(pd.DataFrame(rows).to_string(index=False));assert all(r['accepted'] for r in rows)
