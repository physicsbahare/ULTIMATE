"""Bounded independent diagnostics after failed absolute-colour gate."""
import numpy as np,pandas as pd,json,time
from scipy import linalg
from scipy.ndimage import gaussian_filter
import physical_model as p
from develop import get_observation,summary
from diagnose import failing_scene
O=p.O

def populations():
 clear,dust,anchor,f,d=failing_scene();tr=np.load(O/'stellar_training.npz');y,x=np.meshgrid(np.arange(400)*.1+.05-20,np.arange(400)*.1+.05-20,indexing='ij');V=tr['log_PC'];lam=tr['log_eigenvalue']
 rot=np.tanh((.65*(x-6)-.76*(y+1))/3.4)*np.sin((.76*x+.65*y)/5.5)
 delta=np.sqrt(lam[0])*V[0,:,None,None]*rot+2*np.sqrt(lam[2])*V[2,:,None,None]*np.cos((x-2*y)/4)
 new=clear*np.exp(delta)
 # Physically positive mixtures of independent training SOURCE SEDs, not a
 # target clear template. Ks amplitude is generator-only fixed morphology.
 rng=np.random.default_rng(618251);ids=rng.choice(len(tr['training_SEDs']),4,replace=False);T=tr['training_SEDs'][ids]
 pat=gaussian_filter(rng.normal(size=x.shape),17);pat/=pat.std();logits=np.stack([pat,-pat,np.sin(x/4+y/6),np.cos(x/6-y/4)])
 weights=p.special.softmax(logits,axis=0);sed=np.einsum('qb,qyx->byx',T,weights);transplant=clear[-1][None]*sed
 np.savez_compressed(O/'heldout_pattern_definitions.npz',rotated_field=rot,log_colour_delta=delta,transplant_template_indices=ids,transplant_weights=weights)
 # Undo ONLY the known uniform screen in the anchor GENERATOR to recover its
 # modified stellar scene; never used as a fitted template.
 anchor_clear=anchor/10**(-.4*p.e.kappa(p.e.WAVE)[:,None,None]*.15)
 return {'DR1':clear,'known_anchor':anchor_clear,'rotated_PC1_PC3':new,'training_SED_patch':transplant},dust

def scene_set():
 pops,dust=populations();y,x=np.meshgrid(np.arange(400)*.1+.05-20,np.arange(400)*.1+.05-20,indexing='ij');gradient=.15+.13*np.tanh((x-7)/3)
 rng=np.random.default_rng(915203);z=gaussian_filter(rng.normal(size=x.shape),12);z/=z.std();patch=.025+.25*p.special.expit(2*z)
 scenes={}
 for name,star in pops.items():
  for label,E in [('clear',np.zeros_like(x)),('uniform',np.full_like(x,.15)),('smooth',gradient),('patchy',patch)]:scenes[name,label]=star*np.exp(-.4*np.log(10)*p.e.kappa(p.e.WAVE)[:,None,None]*E)
 scenes['SKIRT','original']=dust
 return scenes

def fit_pair(model,data,cov,normalized,start0=None,start1=None):
 f0=model.fit(data,cov,normalized=normalized,start=None,max_nfev=240);f1=model.fit(data,cov,variable=True,normalized=normalized,start=f0['theta'],max_nfev=240)
 # A second start at the nested optimum ensures a nonnegative optimized
 # objective gain; this is an optimizer check, not a prior/model change.
 if f1['penalized_objective']>f0['penalized_objective']+1e-5:
  alt=model.fit(data,cov,variable=True,normalized=normalized,start=f0['theta'],max_nfev=300)
  if alt['penalized_objective']<f1['penalized_objective']:f1=alt
 return f0,f1

def run():
 model=p.ForwardModel('seeing');scenes=scene_set();rows=[];cal=[];saved={};start=time.time()
 # Known-family source, independent from the development test coefficients.
 q=model.initial();q[:model.ngray]+=np.random.default_rng(72184).normal(0,.4,model.ngray);q[model.ngray:model.ngray+model.npop]=np.random.default_rng(27189).normal(0,.3,model.npop);truth=model.predict(q,False).reshape(7,15)
 # Photometric covariance is an observing-error model, no source truth template.
 _,obs0=get_observation(model,scenes['DR1','uniform'],133181);_,cov=obs0;C=linalg.block_diag(*cov);L=linalg.cholesky(C,lower=True);rng=np.random.default_rng(74398)
 # Fixed independent initialization policy; no sequential warm starts.
 for i in range(19):
  data=truth+(L@rng.normal(size=105)).reshape(7,15)
  for norm in [False,True]:
   f0,f1=fit_pair(model,data,cov,norm);score=f0['penalized_objective']-f1['penalized_objective'];cal.append(dict(noise_index=i,likelihood='contrasts' if norm else 'absolute',statistic=score,null_success=f0['success'],variable_success=f1['success'],null_ppp=f0['ppp'],variable_ppp=f1['ppp']))
  print('pilot calibration',i,'seconds',round(time.time()-start,1),flush=True)
  pd.DataFrame(cal).to_csv(O/'pilot_calibration.csv',index=False)
 cuts=pd.DataFrame(cal).groupby('likelihood').statistic.max().to_dict();(O/'pilot_thresholds.json').write_text(json.dumps(cuts,indent=2))
 for number,((population,screen),scene) in enumerate(scenes.items()):
  draws,_=get_observation(model,scene,519873+number,n=3);# Fixed independent initialization policy; no sequential warm starts.
  for i,(data,cov) in enumerate(draws):
   for norm in ([False,True] if i==0 else [True]):
    f0,f1=fit_pair(model,data,cov,norm);likelihood='contrasts' if norm else 'absolute';score=f0['penalized_objective']-f1['penalized_objective'];record=dict(population=population,screen=screen,noise_index=i,likelihood=likelihood,statistic=score,cutoff=cuts[likelihood],rejected=score>cuts[likelihood],null_ppp=f0['ppp'],variable_ppp=f1['ppp'],null_success=f0['success'],variable_success=f1['success'],null_chi2=f0['chi2'],variable_chi2=f1['chi2'],null_residual_dof=f0['residual_dof'],variable_residual_dof=f1['residual_dof'],null_noise_tail=f0['noise_tail_p'],variable_noise_tail=f1['noise_tail_p'])
    # A result is never a usable detection if either model optimizer failed or
    # the alternative is predictively inadequate. Save raw flags too.
    record['adequate_alternative']=bool(f1['success'] and f1['ppp']>=.01);record['adequate_null']=bool(f0['success'] and f0['ppp']>=.01)
    rows.append(record)
    if i==0:
     label=f'{population}_{screen}_{likelihood}';saved[label+'_obs']=data;saved[label+'_cov']=cov;saved[label+'_theta_null']=f0['theta'];saved[label+'_theta_var']=f1['theta'];saved[label+'_pred_null']=f0['prediction'];saved[label+'_pred_var']=f1['prediction'];saved[label+'_paramcov_var']=f1['parameter_covariance']
  print('pilot evaluation',population,screen,'seconds',round(time.time()-start,1),flush=True)
  pd.DataFrame(rows).to_csv(O/'heldout_pilot_per_draw.csv',index=False)
 np.savez_compressed(O/'heldout_pilot_fits.npz',**saved)
 table=pd.DataFrame(rows);summ=[]
 for key,g in table.groupby(['population','screen','likelihood']):
  k=int(g.rejected.sum());lo,hi=p.e.binomial_ci(k,len(g));summ.append(dict(population=key[0],screen=key[1],likelihood=key[2],n=len(g),rejections=k,rate=k/len(g),ci_low=lo,ci_high=hi,adequate_null_fraction=g.adequate_null.mean(),adequate_alternative_fraction=g.adequate_alternative.mean(),all_optimizers_success=bool(g.null_success.all() and g.variable_success.all())))
 pd.DataFrame(summ).to_csv(O/'heldout_pilot_rates.csv',index=False)
 return table
if __name__=='__main__':run()
