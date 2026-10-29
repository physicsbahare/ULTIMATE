"""Native seeing/GLAO adequacy sensitivity, not a new power forecast."""
import numpy as np,pandas as pd
import physical_model as p
from diagnose import failing_scene
from develop import get_observation,summary
from pilot import fit_pair

def run():
 clear,dust,anchor,_,_=failing_scene();uniform=clear*10**(-.4*p.e.kappa(p.e.WAVE)[:,None,None]*.15);rows=[]
 for mode in ['seeing','glao']:
  for field,bin_kpc in [('fine',1.5),('coarse',1.5),('fine',3.)]:
   model=p.ForwardModel(mode,field=field,bin_kpc=bin_kpc)
   for name,scene in [('uniform',uniform),('anchor',anchor)]:
    obs,_=get_observation(model,scene,365839);data,cov=obs[0];f0,f1=fit_pair(model,data,cov,True)
    for f in [f0,f1]:rows.append(dict(**summary(name,model,f,'contrasts'),bin_kpc=bin_kpc))
    print(mode,field,bin_kpc,name,[(f['chi2'],f['residual_dof'],f['ppp'],f['success']) for f in [f0,f1]],flush=True)
    pd.DataFrame(rows).to_csv(p.O/'native_adequacy_sensitivity.csv',index=False)
 return pd.DataFrame(rows)
if __name__=='__main__':run()
