"""Additional null stress tests with frozen thresholds; never used for tuning."""
import numpy as np,pandas as pd
import experiment as e

def run():
 clear,dusty=e.load();p=np.load(e.O/'population_training.npz');v=p['eigenvectors'];eig=p['eigenvalues'];cov=p['cov']
 yy,xx=np.meshgrid((np.arange(400)+.5)*.1-20,(np.arange(400)+.5)*.1-20,indexing='ij');pattern=np.tanh((xx-7)/3)*np.cos(yy/6)
 uniform=10**(-.4*e.kappa(e.WAVE)[:,None,None]*.15)
 cases={}
 # Controlled colour shifts limited to half/one training-PC standard deviation.
 # These are empirical SED perturbations, NOT claimed age/metallicity histories.
 for amp in [.5,1.]:
  for sign in [-1,1]:
   delta=sign*amp*(v[:,0]*np.sqrt(eig[0])+.5*v[:,1]*np.sqrt(eig[1]))
   cases[f'null_population_{amp}_{sign}']=clear*np.exp(delta[:,None,None]*pattern)*uniform
 # Uniform E, SED-dependent k_eff sensitivity from the external-template bracket.
 table=pd.read_csv(e.O/'within_band_SED_sensitivity.csv');bounds=table.groupby('band').relative_difference.agg(['min','max']).reindex(e.LABELS)
 color=np.log(np.maximum(clear[0],1e-20)/np.maximum(clear[-1],1e-20));q=np.quantile(color,[.1,.9]);blend=np.clip((color-q[0])/(q[1]-q[0]),0,1)
 offset=bounds['min'].to_numpy()[:,None,None]*(1-blend)+bounds['max'].to_numpy()[:,None,None]*blend
 cases['null_uniform_SED_coeff']=clear*10**(-.4*e.kappa(e.WAVE)[:,None,None]*(1+offset)*.15)
 for n in [.7,1.3]:cases[f'alt_gradient_n{n}']=clear*10**(-.4*e.kappa(e.WAVE,n)[:,None,None]*(.15+.13*np.tanh((xx-7)/3)))
 baseline=pd.read_csv(e.O/'calibrated_rates.csv');records=[];raw=[];pp=[]
 for cid in range(8):
  cfg=baseline[baseline.condition==cid].iloc[0];z=cfg.z;g=e.geometry(z,cfg['mode'],cfg.strategy);pairid=int(z*100)+100
  cache={}
  for name,scene in cases.items():
   rate,_=e.render(scene,z,g);draw,means,cs,_=e.compressed_observation(rate,g,1.,e.seed_for(pairid,7))
   cache[name]=(draw,means,cs)
  for bandset,ix in [('joint',list(range(7))),('optical',list(range(4))),('NIR',[4,5,6])]:
   for hierarchy in ['constant','PC1','PC2_residual']:
    group=dict(condition=cid,view='O1',z=z,mode=cfg['mode'],strategy=cfg.strategy,bandset=bandset,population=hierarchy)
    ref=baseline[(baseline.condition==cid)&(baseline.bandset==bandset)&(baseline.population==hierarchy)&(baseline.popscale==1)&(baseline.dust_slope==1)].iloc[0];cut=ref.threshold
    for name,vals in cache.items():
     y,noise,h=e.prepare_data(*vals,ix);k0,k1,_=e.priors(g,cov,eig,v,ix,h,hierarchy)
     score,a,b=e.fit_statistics(y,noise,k0,k1);ev=score[e.NTRAIN:];hit=ev>cut;k=int(hit.sum());lo,hi=e.binomial_ci(k,len(ev))
     records.append(dict(**group,truth=name,n_evaluation=len(ev),threshold=cut,detections=k,rate=k/len(ev),ci_low=lo,ci_high=hi))
     raw.extend(dict(**group,truth=name,noise_index=i,detected=bool(d),score=s) for i,(d,s) in enumerate(zip(hit,ev)))
     if bandset=='joint' and hierarchy=='PC2_residual':
      p0,_,_=e.posterior_check(a,y[e.NTRAIN]);p1,_,_=e.posterior_check(b,y[e.NTRAIN]);pp.append(dict(**group,truth=name,uniform_ppp=p0,variable_ppp=p1))
  print('stress condition',cid,flush=True)
  pd.DataFrame(records).to_csv(e.O/'population_stress_rates.csv',index=False)
 pd.DataFrame(raw).to_csv(e.O/'population_stress_statistics.csv.gz',index=False)
 pd.DataFrame(pp).to_csv(e.O/'population_stress_posterior.csv',index=False)
 return pd.DataFrame(records)
if __name__=='__main__':run()
