"""Same observed draws and known-family pilot calibration for old Gaussian model."""
import numpy as np,pandas as pd
from scipy import linalg
import physical_model as p
from develop import get_observation
from pilot import scene_set

def run():
 m=p.ForwardModel('seeing');scenes=scene_set();prior=np.load(p.PREV/'population_training.npz');h=p.e.contrasts(15);k0,k1,_=p.e.priors(m.g,prior['cov'],prior['eigenvalues'],prior['eigenvectors'],list(range(7)),h,'PC2_residual')
 def score(data,cov):
  y,n,_=p.e.prepare_data(data[None],None,cov,list(range(7)));a=p.e.GaussianModel(n[0],k0);b=p.e.GaussianModel(n[0],k1);s=float(2*(b.logpdf(y)-a.logpdf(y))[0]);p0,_,_=p.e.posterior_check(a,y[0]);p1,_,_=p.e.posterior_check(b,y[0]);return s,p0,p1
 q=m.initial();q[:m.ngray]+=np.random.default_rng(72184).normal(0,.4,m.ngray);q[m.ngray:m.ngray+m.npop]=np.random.default_rng(27189).normal(0,.3,m.npop);truth=m.predict(q,False).reshape(7,15);_,obs0=get_observation(m,scenes['DR1','uniform'],133181);_,cov=obs0;L=linalg.cholesky(linalg.block_diag(*cov),lower=True);rng=np.random.default_rng(74398);cal=[]
 for i in range(19):
  data=truth+(L@rng.normal(size=105)).reshape(7,15);s,p0,p1=score(data,cov);cal.append(s)
 cut=max(cal);pd.DataFrame({'statistic':cal}).to_csv(p.O/'old_gaussian_pilot_calibration.csv',index=False)
 published=pd.read_csv(p.PREV/'FINAL_calibrated_rates.csv');oldcut=published[(published.z==.3)&(published.strategy=='native')&(published['mode']=='seeing')&(published.bandset=='joint')].iloc[0].threshold;rows=[]
 for number,((population,screen),scene) in enumerate(scenes.items()):
  draws,_=get_observation(m,scene,519873+number,n=3)
  for i,(data,cov) in enumerate(draws):
   s,p0,p1=score(data,cov);rows.append(dict(population=population,screen=screen,noise_index=i,statistic=s,pilot_cutoff=cut,pilot_rejected=s>cut,previous_published_cutoff=oldcut,published_rejected=s>oldcut,null_ppp=p0,variable_ppp=p1))
 pd.DataFrame(rows).to_csv(p.O/'old_gaussian_same_pilot.csv',index=False);return pd.DataFrame(rows)
if __name__=='__main__':run()
