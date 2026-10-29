"""Explain non-monotone depth completeness without changing thresholds."""
import pilot as p
import numpy as np,pandas as pd
from scipy import stats

def run():
 f=pd.read_csv(p.O/'feature_summary.csv');rows=[]
 for mode in ['seeing','glao']:
  for hours in [.25,1.,4.]:
   a=np.load(p.O/f'observations/O1_z0.1_{mode}_{hours}h_gaussian.npz');g=p.make_geometry(.1,mode);plan=p.FilterPlan(g,'J_Ks_NIR',1);plan.prepare(a['SKIRT_rate_variance']);v,s,mask,_=plan.measure(a['SKIRT_expected_rate'],g['roi']);ref=(a['J_Ks_NIR_reference']>.05)&a['valid_truth'];cut=np.maximum(.05,3*s);pred=stats.norm.sf((cut[ref]-v[ref])/s[ref]).mean();r=f.query('view=="O1" and z==0.1 and kind=="gaussian" and scene=="SKIRT" and method=="J_Ks_NIR" and scale_kpc==1');r=r[(r['mode']==mode)&(r.hours==hours)].iloc[0]
   rows.append(dict(mode=mode,hours=hours,n_reference_pixels=ref.sum(),median_noiseless_observable_structure=float(np.median(v[ref])),noiseless_pixels_above_amplitude=int((ref&(v>.05)).sum()),linearized_expected_threshold_crossing_completeness=pred,evaluation_completeness=r.completeness,MC_mean_low=r.completeness_lo,MC_mean_high=r.completeness_hi,explanation='PSF and stellar colour reduce observable contrast; noise can scatter it across fixed amplitude threshold'))
 d=pd.DataFrame(rows);d.to_csv(p.O/'depth_threshold_diagnostic.csv',index=False);print(d.to_string(index=False));return d
if __name__=='__main__':run()
