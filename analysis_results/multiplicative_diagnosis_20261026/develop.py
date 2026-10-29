"""Small development gate; no held-out pattern tuning."""
import numpy as np,pandas as pd,json,time
import physical_model as p
from diagnose import failing_scene
O=p.O

def summary(name,model,fit,likelihood):
 return dict(scene=name,mode=model.mode,strategy=model.strategy,field=model.field,likelihood=likelihood,variable=fit['variable'],success=fit['success'],chi2=fit['chi2'],effective_parameters=fit['effective_parameters'],residual_dof=fit['residual_dof'],ppp=fit['ppp'],noise_tail_p=fit['noise_tail_p'],penalized_objective=fit['penalized_objective'],nfev=fit['nfev'],optimality=fit['optimality'])

def get_observation(model,scene,seed,n=1):
 rate,_=p.e.render(scene,.3,model.g);draw,mu,covs,_=p.e.compressed_observation(rate,model.g,1.,seed,n=n)
 return [model.measurements(d,covs) for d in draw],model.measurements(mu,covs)

def run():
 model=p.ForwardModel('seeing');clear,dust,anchor,pattern,direction=failing_scene();scenes={'DR1_uniform':clear*10**(-.4*p.e.kappa(p.e.WAVE)[:,None,None]*.15),'problem_anchor':anchor}
 rows=[];saved={};started=time.time()
 for name,scene in scenes.items():
  obs,noiseless=get_observation(model,scene,921835)
  for kind,(data,covs) in [('noise_free',noiseless),('one_noise',obs[0])]:
   for normalized in [False,True]:
    fit0=model.fit(data,covs,normalized=normalized);fit1=model.fit(data,covs,variable=True,normalized=normalized,start=fit0['theta']);label=f'{name}_{kind}_{"contrasts" if normalized else "absolute"}'
    for fit in [fit0,fit1]:rows.append(dict(**summary(name,model,fit,'contrasts' if normalized else 'absolute'),noise=kind))
    saved[f'{label}_theta_null']=fit0['theta'];saved[f'{label}_theta_var']=fit1['theta'];saved[f'{label}_prediction_null']=fit0['prediction'];saved[f'{label}_prediction_var']=fit1['prediction'];saved[f'{label}_observed']=data;saved[f'{label}_noise_cov']=covs
    print(label,[(f['success'],round(f['chi2'],2),round(f['residual_dof'],2),f['ppp'],f['nfev']) for f in [fit0,fit1]],'seconds',round(time.time()-started,1),flush=True)
  pd.DataFrame(rows).to_csv(O/'development_gate.csv',index=False)
 np.savez_compressed(O/'development_fits.npz',**saved)
 # Known-family fitting check, independent coefficients not any target truth.
 q=model.initial();q[:model.ngray]+=np.random.default_rng(5172).normal(0,.4,model.ngray);q[model.ngray:model.ngray+model.npop]=np.random.default_rng(174).normal(0,.3,model.npop)
 data=model.predict(q,False).reshape(7,15);_,covs=noiseless;z=np.random.default_rng(98237).normal(size=105);C=p.linalg.block_diag(*covs);data_noisy=data+(p.linalg.cholesky(C,lower=True)@z).reshape(7,15)
 for noise,dd in [('noise_free',data),('one_noise',data_noisy)]:
  fit0=model.fit(dd,covs);fit1=model.fit(dd,covs,True,start=fit0['theta'])
  for fit in [fit0,fit1]:rows.append(dict(**summary('model_family_uniform',model,fit,'absolute'),noise=noise))
  print('model family',noise,[(f['success'],f['chi2'],f['ppp']) for f in [fit0,fit1]],flush=True)
 table=pd.DataFrame(rows);table.to_csv(O/'development_gate.csv',index=False)
 physical=table[(table.likelihood=='absolute')&(table.variable==False)&(table.noise=='one_noise')&(table.scene!='model_family_uniform')]
 passed=bool(physical.success.all() and (physical.ppp>=.01).all())
 (O/'development_gate.json').write_text(json.dumps(dict(physical_null_gate_passed=passed,criteria='optimizer success and local posterior predictive p>=.01 on both prespecified native seeing nulls; effective-dof chi-square tails descriptive only',larger_evaluation_permitted=passed,elapsed_seconds=time.time()-started),indent=2))
 return table
if __name__=='__main__':run()
