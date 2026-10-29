"""Post-fit identifiability, spectral coverage and absolute-colour diagnostics."""
import numpy as np,pandas as pd
from scipy import optimize,linalg,special
import physical_model as p
O=p.O

def run():
 model=p.ForwardModel('seeing');fits=np.load(O/'development_fits.npz');rows=[]
 for scene in ['DR1_uniform','problem_anchor']:
  for norm,kind in [(False,'absolute'),(True,'contrasts')]:
   name=f'{scene}_one_noise_{kind}';q=fits[name+'_theta_var'];data=fits[name+'_observed'];cov=fits[name+'_noise_cov'];f=model.fit(data,cov,True,norm,start=q,max_nfev=10)
   q=f['theta'];J=f['jacobian_data'];npop=model.ngray+model.npop;S=J[:,:npop];D=J[:,npop:];u,s,v=np.linalg.svd(S,full_matrices=False);rank=int(np.sum(s>s[0]*1e-8));orth=D-u[:,:rank]@(u[:,:rank].T@D)
   # Posterior E moments are local Laplace uncertainties, not calibrated
   # physical confidence intervals, especially for inadequate raw fits.
   amp,w,sed,E=model.unpack(q,True);dE=E*(1-E/.6);DE=dE[:,None]*model.B
   cv=f['parameter_covariance'][npop:,npop:];sd=np.sqrt(np.maximum(np.einsum('ni,ij,nj->n',DE,cv,DE),0))
   rows.append(dict(scene=scene,likelihood=kind,n_data=J.shape[0],n_stellar_parameters=S.shape[1],stellar_jacobian_rank=rank,dust_jacobian_relative_outside_stellar_span=np.linalg.norm(orth)/max(np.linalg.norm(D),1e-20),dust_jacobian_norm=np.linalg.norm(D),E_mean_MAP=E.mean(),E_range_MAP=np.ptp(E),E_mean_local_SD=float(np.mean(sd))))
 # Direct measurement invariance: uniform attenuation cancels exactly in every
 # normalized band; absolute flux changes. Same source, same physical model.
 q=model.initial();a=model.predict(q,False).reshape(7,15);qq=q.copy();qq[-1]+=1;b=model.predict(qq,False).reshape(7,15);relative_norm_change=np.max(abs(a/a.mean(axis=1)[:,None]-b/b.mean(axis=1)[:,None]));relative_raw_change=np.linalg.norm(a-b)/np.linalg.norm(a)
 pd.DataFrame(rows).to_csv(O/'parameter_identifiability.csv',index=False)
 pd.DataFrame([dict(max_normalized_flux_change_for_uniform_E_shift=relative_norm_change,relative_absolute_flux_change_for_same_shift=relative_raw_change)]).to_csv(O/'absolute_information_invariance.csv',index=False)
 # Clear evaluation spectra are used for POST-FIT coverage diagnosis ONLY.
 clear,_=p.e.load();blocks=clear.reshape(7,40,10,40,10).mean(axis=(2,4));xy=np.arange(40)+.5-20;yy,xx=np.meshgrid(xy,xy,indexing='ij');mask=(xx>=3)&(xx<12)&(abs(yy)<8)
 vals=blocks[:,mask].T;rat=vals/vals[:,-1,None];out=[]
 for i,r in enumerate(rat):
  candidates=[]
  for E in np.linspace(0,.6,61):
   T=model.templates*np.exp(-.4*np.log(10)*p.e.kappa(p.e.WAVE)[None,:]*E)
   coef,res=optimize.nnls(T.T/r[:,None],np.ones(7));prediction=coef@T;relative=prediction/r-1;candidates.append((res,E,np.sqrt(np.mean(relative*relative))))
  best=min(candidates);out.append(dict(x_kpc=xx[mask][i],y_kpc=yy[mask][i],clear_colour_best_screen_E=best[1],best_fractional_rms=best[2],E0_fractional_rms=candidates[0][2]))
 pd.DataFrame(out).to_csv(O/'postfit_stellar_hull_coverage.csv',index=False)
 print(pd.DataFrame(rows).to_string(index=False));print('uniform E invariance',relative_norm_change,relative_raw_change);print(pd.DataFrame(out).describe().to_string())
 return pd.DataFrame(rows)
if __name__=='__main__':run()
