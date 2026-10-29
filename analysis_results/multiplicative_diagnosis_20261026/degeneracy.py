"""Finite positive counterexamples and local identifiability, not prior tuning."""
import numpy as np,pandas as pd
from scipy import linalg
import physical_model as p
from develop import get_observation

def run():
 m=p.ForwardModel('seeing');q=m.initial();q[:m.ngray]+=np.random.default_rng(5172).normal(0,.4,m.ngray);q[m.ngray:m.ngray+m.npop]=np.random.default_rng(174).normal(0,.3,m.npop);q=np.r_[q,np.zeros(m.nspatial-1)];nstar=m.ngray+m.npop
 clear,_=p.e.load();_,obs=get_observation(m,clear,77124);_,cov=obs;C=linalg.block_diag(*cov);W=linalg.solve_triangular(linalg.cholesky(C,lower=True),np.eye(105),lower=True)
 f,J=m.predict(q,True,True);R,mean=m.prior(True);P=R[:,:nstar].T@R[:,:nstar];L=linalg.cholesky(P,lower=True);transform=linalg.solve_triangular(L.T,np.eye(nstar),lower=False);S=W@J[:,:nstar]@transform
 amp,w,sed,E=m.unpack(q,True);mask=(m.xy[:,0]>=3)&(m.xy[:,0]<=12)&(abs(m.xy[:,1])<8);target=.03*np.tanh((m.xy[:,0]-7)/3)
 DE=(E*(1-E/.6))[:,None]*m.B[:,1:];coeff=np.linalg.lstsq(DE[mask],target[mask],rcond=None)[0];dd=np.r_[0.,coeff];d=W@J[:,nstar:]@dd
 rows=[];examples={}
 for lam in [1e-5,.001,.1,1.,10.]:
  du=-S.T@linalg.solve(S@S.T+np.eye(105)*lam,d,assume_a='pos');ds=transform@du;trial=q.copy();trial[:nstar]+=ds;trial[nstar:]+=dd;ff=m.predict(trial,True);res=W@(ff-f);_,ww,_,ee=m.unpack(trial,True)
  rows.append(dict(penalty=lam,population_shift_prior_sigma_norm=np.linalg.norm(du),linear_residual_chi2=np.sum((S@du+d)**2),exact_positive_forward_residual_chi2=res@res,number_photometric_data=105,E_variation_rms=float(np.sqrt(np.mean((ee[mask]-E[mask])**2))),minimum_stellar_mixture_fraction=float(ww.min()),maximum_stellar_mixture_fraction=float(ww.max()),minimum_source_intensity=float(np.min(m.G@np.logaddexp(0,trial[:m.ngray])))))
  examples[f'lambda_{lam}_prediction']=ff;examples[f'lambda_{lam}_parameters']=trial
 np.savez_compressed(p.O/'positive_degeneracy_examples.npz',base_prediction=f,base_parameters=q,noise_cov=C,**examples)
 pd.DataFrame(rows).to_csv(p.O/'positive_degeneracy_tradeoff.csv',index=False);print(pd.DataFrame(rows).to_string(index=False));return pd.DataFrame(rows)
if __name__=='__main__':run()
