"""Targeted reproduction and mechanism diagnosis, not a full-grid rerun."""
from pathlib import Path
import sys,os,json,hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/ultimate-mpl')
sys.dont_write_bytecode=True
import numpy as np,pandas as pd
from scipy import linalg,stats
O=Path(__file__).resolve().parent;PREV=O.parent/'dr1_calibrated_screen_20261026'
sys.path.insert(0,str(PREV));import experiment as e

def failing_scene():
 clear,dust=e.load();p=np.load(PREV/'population_training.npz');v=p['eigenvectors'];ev=p['eigenvalues'];yy,xx=np.meshgrid((np.arange(400)+.5)*.1-20,(np.arange(400)+.5)*.1-20,indexing='ij');f=np.tanh((xx-7)/3)*np.cos(yy/6);d=-(v[:,0]*np.sqrt(ev[0])+.5*v[:,1]*np.sqrt(ev[1]));s=clear*np.exp(d[:,None,None]*f)*10**(-.4*e.kappa(e.WAVE)[:,None,None]*.15)
 return clear,dust,s,f,d

def run():
 clear,dust,scene,f,d=failing_scene();p=np.load(PREV/'population_training.npz');v=p['eigenvectors'];ev=p['eigenvalues'];cov=p['cov'];rows=[];examples={}
 # Does anchor direction lie outside first two training PCs? It does not in log perturbation.
 proj=v[:,:2]@v[:,:2].T@d
 spectral=dict(relative_outside_first2_norm=float(np.linalg.norm(d-proj)/np.linalg.norm(d)),dust_cosine_squared=float((e.contrasts(7)@d@ (e.contrasts(7)@e.kappa(e.WAVE)))**2/(np.linalg.norm(e.contrasts(7)@d)**2*np.linalg.norm(e.contrasts(7)@e.kappa(e.WAVE))**2)))
 for strategy in ['matched','native']:
  for mode in ['seeing','glao']:
   g=e.geometry(.3,mode,strategy);rate,_=e.render(scene,.3,g);draw,mean,cs,_=e.compressed_observation(rate,g,1.,e.seed_for(30,23),n=500)
   y,noise,h=e.prepare_data(draw,mean,cs,list(range(7)));k0,k1,kd=e.priors(g,cov,ev,v,list(range(7)),h,'PC2_residual');score,a,b=e.fit_statistics(y,noise,k0,k1)
   final=pd.read_csv(PREV/'FINAL_calibrated_rates.csv');cut=final[(final.z==.3)&(final.strategy==strategy)&(final['mode']==mode)&(final.bandset=='joint')].iloc[0].threshold
   count=int((score>cut).sum());lo,hi=e.binomial_ci(count,500)
   # Noise-free location tests separate systematic field from normalization noise.
   deterministic=np.tile(mean[None],(201,1,1));yc,nc,_=e.prepare_data(deterministic,mean,cs,list(range(7)));target=yc[0];n=nc[0]
   for variant,mult,extra in [('baseline',1.,None),('population_scale2',2.,None),('explicit_anchor_population_mode',1.,'anchor'),('smaller_spatial_RBF',1.,'spatial')]:
    kk0,kk1,dd=e.priors(g,cov,ev,v,list(range(7)),h,'PC2_residual',popscale=mult)
    if extra=='anchor':
     # Independent small response to known test mode, diagnostic only. It is NOT
     # added to the improved inference model or used to train on this case.
     eps=.01;pert=clear*np.exp(eps*d[:,None,None]*f)*10**(-.4*e.kappa(e.WAVE)[:,None,None]*.15)
     rr,_=e.render(pert,.3,g);_,mm,cc,_=e.compressed_observation(rr,g,1.,321,n=1)
     r0,_=e.render(clear*10**(-.4*e.kappa(e.WAVE)[:,None,None]*.15),.3,g);_,m0,c0,_=e.compressed_observation(r0,g,1.,321,n=1)
     yn,_,_=e.prepare_data(mm[None],mm,cc,list(range(7)));yn0,_,_=e.prepare_data(m0[None],m0,c0,list(range(7)))
     u=(yn[0]-yn0[0])/eps;kk0+=np.outer(u,u);kk1+=np.outer(u,u)
    if extra=='spatial':
     # Spatial flexibility sensitivity: shorter correlation by diagonal spatial
     # colour covariance, preserving measured spectral covariance. Diagnostic.
     pop=np.kron(cov,np.eye(14));kk0+=pop;kk1+=pop
    a0=e.GaussianModel(n,kk0);a1=e.GaussianModel(n,kk1);s=float(2*(a1.logpdf(target[None])-a0.logpdf(target[None]))[0]);q0=float(target@a0.inv@target);q1=float(target@a1.inv@target)
    p0,_,_=e.posterior_check(a0,target);p1,_,_=e.posterior_check(a1,target)
    rows.append(dict(strategy=strategy,mode=mode,variant=variant,noise_free_statistic=s,prior_predictive_q_null=q0,prior_predictive_q_variable=q1,dimension=len(target),posterior_predictive_null=p0,posterior_predictive_variable=p1,reproduced_FPR=count/500,ci_low=lo,ci_high=hi,threshold=cut,noise_free_score_above_threshold=s>cut))
   am=e.GaussianModel(n,k0);bm=e.GaussianModel(n,k1);dm=kd@bm.inv@target;post=kd-kd@bm.inv@kd
   # Residual shape after fitting and the prior-whitened offending direction.
   pred0=am.prior@am.inv@target;pred1=bm.prior@bm.inv@target
   examples[f'{strategy}_{mode}_data']=target;examples[f'{strategy}_{mode}_null']=pred0;examples[f'{strategy}_{mode}_alternative']=pred1;examples[f'{strategy}_{mode}_dust']=dm;examples[f'{strategy}_{mode}_noise_sd']=np.sqrt(np.diag(n))
   examples[f'{strategy}_{mode}_dust_sd']=np.sqrt(np.maximum(np.diag(post),0))
   # Verify normalized measurement covariance directly for the first observation.
   j=0;obs=draw[0,j];J=(np.eye(15)-obs[:,None]/obs.mean()/15)/obs.mean();explicit=h@J@cs[j]@J.T@h.T
   spectral[f'{strategy}_{mode}_covariance_max_error']=float(np.max(abs(explicit-noise[0,:14,:14])))
 pd.DataFrame(rows).to_csv(O/'old_method_mechanism.csv',index=False);np.savez_compressed(O/'old_failure_components.npz',**examples,pattern=f,log_population_direction=d)
 (O/'mechanism.json').write_text(json.dumps(spectral,indent=2));print(pd.DataFrame(rows).to_string(index=False));print(spectral)
 return pd.DataFrame(rows)
if __name__=='__main__':run()
