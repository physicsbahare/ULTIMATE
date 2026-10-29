"""Empirical residual audit on zero projected-dust objects. No tuning/subtraction of truth."""
from pathlib import Path
import pandas as pd,numpy as np
from scipy import ndimage as ndi
from morphology import Geometry,measure
O=Path(__file__).resolve().parent

def run():
 meta=pd.read_csv(O/'galaxy_inventory.csv');zero=meta[meta.dust_mass_field_Msun==0].subhalo_id.to_numpy();rows=[];noise=[];g=Geometry(400,.1,12)
 for sid in zero:
  for view in [f'O{i}' for i in range(1,6)]:
   with np.load(O/'cache'/str(sid)/f'{view}.npz') as z:
    for band in ['LSST_g','2MASS_J','2MASS_Ks']:
     c=z[f'clear_{band}'].astype(float);d=z[f'dusty_{band}'].astype(float);amp=d[g.mask].sum()/c[g.mask].sum();valid=g.mask&(c>1e-4*c.max())
     for fwhm in [0.,.5,1.]:
      cs=ndi.gaussian_filter(c,fwhm/.1/2.35482) if fwhm else c;ds=ndi.gaussian_filter(d,fwhm/.1/2.35482) if fwhm else d
      a,b=measure(cs,g),measure(ds,g)
      rows.append(dict(subhalo_id=sid,view=view,band=band,smoothing_FWHM_kpc=fwhm,zero_projected_dust=True,normalization=amp,integrated_pair_attenuation_mag=-2.5*np.log10(amp),shape_residual_RMS_fraction_of_clear_RMS=float(np.sqrt(np.mean((ds[valid]/amp-cs[valid])**2)/np.mean(cs[valid]**2))),**{'delta_'+k:b[k]-a[k] for k in ['R50','C','A','q']},fractional_R50_change=(b['R50']-a['R50'])/a['R50']))
 r=pd.DataFrame(rows);r.to_csv(O/'zero_projected_dust_residuals.csv',index=False)
 summary=r.groupby(['band','smoothing_FWHM_kpc']).agg(n_galaxies=('subhalo_id','nunique'),attenuation_median=('integrated_pair_attenuation_mag','median'),attenuation_min=('integrated_pair_attenuation_mag','min'),attenuation_max=('integrated_pair_attenuation_mag','max'),median_shape_residual_RMS=('shape_residual_RMS_fraction_of_clear_RMS','median'),median_abs_delta_R50=('delta_R50',lambda x:abs(x).median()),max_abs_delta_R50=('delta_R50',lambda x:abs(x).max()),median_abs_delta_C=('delta_C',lambda x:abs(x).median()),max_abs_delta_C=('delta_C',lambda x:abs(x).max()),median_abs_delta_A=('delta_A',lambda x:abs(x).median()),max_abs_delta_A=('delta_A',lambda x:abs(x).max()),median_abs_fractional_R50=('fractional_R50_change',lambda x:abs(x).median())).reset_index();summary.to_csv(O/'zero_projected_dust_summary.csv',index=False)
 return summary
if __name__=='__main__':print(run().to_string(index=False))
