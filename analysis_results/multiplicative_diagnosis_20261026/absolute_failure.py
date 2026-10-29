"""Isolate grid error versus SED-library coverage; diagnostic bounds only."""
import numpy as np,pandas as pd
from scipy import optimize,linalg
import physical_model as p
from develop import get_observation
from diagnose import failing_scene

def run():
 clear,dust,anchor,_,_=failing_scene();rows=[];m=p.ForwardModel('seeing')
 for name,star in [('uniform',clear*10**(-.4*p.e.kappa(p.e.WAVE)[:,None,None]*.15)),('anchor',anchor)]:
  coarse=star.reshape(7,40,10,40,10).mean(axis=(2,4)).repeat(10,axis=1).repeat(10,axis=2)
  _,full=get_observation(m,star,91853);_,averaged=get_observation(m,coarse,91853);data,C=full;dc,_=averaged;noise=linalg.block_diag(*C);difference=(data-dc).ravel();gridchi=float(difference@linalg.solve(noise,difference,assume_a='pos'))
  f=m.fit(dc,C);rows.append(dict(scene=name,diagnostic='exact_grid_source_absolute_null',chi2=f['chi2'],ppp=f['ppp'],success=f['success'],grid_projection_difference_chi2=gridchi))
  # Matched PSFs allow a convex local template-mixture lower-bound check.
  mm=p.ForwardModel('seeing',strategy='matched');_,(obs,cov)=get_observation(mm,star,91853);best=None
  # Independently fitting each aperture is only an optimistic SED-coverage
  # diagnostic, NEVER the inference model used for FPR or power.
  for E in np.linspace(0,.6,121):
   T=mm.templates*np.exp(-.4*np.log(10)*p.e.kappa(p.e.WAVE)[None,:]*E);total=0.
   for i in range(15):
    sig=np.sqrt(cov[:,i,i]);coef,res=optimize.nnls(T.T/sig[:,None],obs[:,i]/sig);total+=res*res
   if best is None or total<best[0]:best=(total,E)
  rows.append(dict(scene=name,diagnostic='matched_PSF_independent_mixture_coverage_bound',chi2=best[0],best_global_E=best[1],ppp=np.nan,success=True,grid_projection_difference_chi2=gridchi))
  print(name,rows[-2:],flush=True)
 pd.DataFrame(rows).to_csv(p.O/'absolute_failure_isolation.csv',index=False);return pd.DataFrame(rows)
if __name__=='__main__':run()
