"""Conditional best-test bound for an explicit pair of positive scenes."""
import numpy as np,pandas as pd
from scipy import linalg,stats
import physical_model as p

def source(model,q):
 a,w,s,E=model.unpack(q,True);return (a[None]*s*np.exp(-.4*np.log(10)*p.e.kappa(p.e.WAVE)[:,None]*E)).reshape(7,40,40).repeat(10,axis=1).repeat(10,axis=2)

def run():
 saved=np.load(p.O/'positive_degeneracy_examples.npz');q=saved['base_parameters'];trial=saved['lambda_0.1_parameters'];rows=[]
 for mode in ['seeing','glao']:
  m=p.ForwardModel(mode);f0=m.predict(q,True);f1=m.predict(trial,True);rates,_=p.e.render(source(m,q),.3,m.g);_,means,cv,_=p.e.compressed_observation(rates,m.g,1.,71839,n=1);_,cov=m.measurements(means,cv);C=linalg.block_diag(*cov);delta=f1-f0;d2=delta@linalg.solve(C,delta,assume_a='pos');separation=np.sqrt(d2);power=stats.norm.sf(stats.norm.ppf(.95)-separation)
  a,w,s0,E0=m.unpack(q,True);aa,ww,s1,E1=m.unpack(trial,True);mask=(m.xy[:,0]>=3)&(m.xy[:,0]<=12)&(abs(m.xy[:,1])<8);color0=-2.5*np.log10(s0[0]/s0[-1]);color1=-2.5*np.log10(s1[0]/s1[-1]);dc=np.sqrt(np.mean((color1[mask]-color0[mask])**2));need=np.sqrt(max((stats.norm.ppf(.95)+stats.norm.ppf(.8))**2-d2,0))
  rows.append(dict(mode=mode,mean_separation_squared=d2,optimal_simple_hypothesis_power_at_FPR05=power,optimal_equal_prior_error=stats.norm.cdf(-separation/2),E_rms_difference=np.sqrt(np.mean((E1[mask]-E0[mask])**2)),intrinsic_g_Ks_colour_rms_difference_mag=dc,illustrative_independent_coherent_colour_mode_sigma_for_80pct_power_mag=dc/need if need else np.nan))
 pd.DataFrame(rows).to_csv(p.O/'conditional_identifiability_bound.csv',index=False);print(pd.DataFrame(rows).to_string(index=False));return pd.DataFrame(rows)
if __name__=='__main__':run()
