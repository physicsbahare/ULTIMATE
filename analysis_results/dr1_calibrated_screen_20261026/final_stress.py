"""New-noise evaluation of fixed population anchors, with FINAL thresholds frozen."""
import numpy as np,pandas as pd
import experiment as e

def run():
 clear,_=e.load();p=np.load(e.O/'population_training.npz');v=p['eigenvectors'];eig=p['eigenvalues'];cov=p['cov'];yy,xx=np.meshgrid((np.arange(400)+.5)*.1-20,(np.arange(400)+.5)*.1-20,indexing='ij');pattern=np.tanh((xx-7)/3)*np.cos(yy/6);uniform=10**(-.4*e.kappa(e.WAVE)[:,None,None]*.15)
 cases={}
 for amp in [.5,1.]:
  for sign in [-1,1]:
   delta=sign*amp*(v[:,0]*np.sqrt(eig[0])+.5*v[:,1]*np.sqrt(eig[1]));cases[f'null_population_{amp}_{sign}']=clear*np.exp(delta[:,None,None]*pattern)*uniform
 table=pd.read_csv(e.O/'within_band_SED_sensitivity.csv');bounds=table.groupby('band').relative_difference.agg(['min','max']).reindex(e.LABELS);color=np.log(np.maximum(clear[0],1e-20)/np.maximum(clear[-1],1e-20));q=np.quantile(color,[.1,.9]);blend=np.clip((color-q[0])/(q[1]-q[0]),0,1);offset=bounds['min'].to_numpy()[:,None,None]*(1-blend)+bounds['max'].to_numpy()[:,None,None]*blend
 cases['null_uniform_SED_coeff']=clear*10**(-.4*e.kappa(e.WAVE)[:,None,None]*(1+offset)*.15)
 final=pd.read_csv(e.O/'FINAL_calibrated_rates.csv');rows=[]
 for cid in range(8):
  cfg=final[final.condition==cid].iloc[0];g=e.geometry(cfg.z,cfg['mode'],cfg.strategy)
  for name,scene in cases.items():
   rate,_=e.render(scene,cfg.z,g);draw,mean,cs,_=e.compressed_observation(rate,g,1.,e.seed_for(int(cfg.z*100),23),n=500)
   for bandset,ix in [('joint',list(range(7))),('optical',list(range(4))),('NIR',[4,5,6])]:
    y,n,h=e.prepare_data(draw,mean,cs,ix);k0,k1,_=e.priors(g,cov,eig,v,ix,h,'PC2_residual');score,_,_=e.fit_statistics(y,n,k0,k1)
    cut=final[(final.condition==cid)&(final.bandset==bandset)].iloc[0].threshold;hit=score>cut;k=int(hit.sum());lo,hi=e.binomial_ci(k,500)
    rows.append(dict(condition=cid,z=cfg.z,strategy=cfg.strategy,mode=cfg['mode'],bandset=bandset,truth=name,n=500,detections=k,rate=k/500,ci_low=lo,ci_high=hi))
  print('final anchor stress',cid,flush=True)
 pd.DataFrame(rows).to_csv(e.O/'FINAL_population_anchor_stress.csv',index=False)
 return pd.DataFrame(rows)
if __name__=='__main__':run()
