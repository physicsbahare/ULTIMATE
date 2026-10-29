"""Final calibrated population-uncertainty experiment; see FINAL_PROTOCOL.md."""
import numpy as np,pandas as pd
from scipy import linalg
from scipy.ndimage import gaussian_filter
import experiment as e
N=500

def fields():
 y,x=np.meshgrid((np.arange(400)+.5)*.1-20,(np.arange(400)+.5)*.1-20,indexing='ij')
 out=[np.tanh((x-7)/3),np.sin(y/5),np.cos((x+y)/6)]
 rng=np.random.default_rng(860142)
 for _ in range(3):
  a=gaussian_filter(rng.normal(size=x.shape),15);out.append(np.tanh(a/a.std()))
 return np.array(out)

def coefficients(n,stage):
 rng=np.random.default_rng(904672+stage*70001)
 coef=rng.normal(size=(n,2,6));coef/=np.sum(abs(coef),axis=2)[:,:,None]
 coef*=rng.uniform(.25,1.,size=(n,2,1))
 return coef.reshape(n,12)

def moments(rate,g,hours=1.):
 t=hours*3600;mu=[];cov=[]
 for r,b,w in zip(rate,g['inst'],g['weights']):
  ww=w.reshape(15,-1);mu.append(ww@r.ravel()*t)
  v=(r+b['background_e_s_pixel']+b['dark_e_s'])*t+60*hours*b['read_noise_e']**2
  cov.append((ww*v.ravel())@ww.T)
 return np.array(mu),np.array(cov)

def signed_moments(rate,g):
 mu=[];cov=[]
 for r,w in zip(rate,g['weights']):
  ww=w.reshape(15,-1);mu.append(ww@r.ravel()*3600);cov.append((ww*(r.ravel()*3600))@ww.T)
 return np.array(mu),np.array(cov)

def generate(base,pert,c,g,znoise):
 mu0,cv0=moments(base,g);mus=[];cvs=[]
 for r in pert:
  m,v=signed_moments(r,g);mus.append(m);cvs.append(v)
 mu=mu0[None]+np.einsum('nk,kba->nba',c,np.array(mus),optimize=True)
 cv=cv0[None]+np.einsum('nk,kbij->nbij',c,np.array(cvs),optimize=True)
 draw=np.empty_like(mu)
 for i in range(len(c)):
  for b in range(7):draw[i,b]=mu[i,b]+linalg.cholesky(cv[i,b],lower=True)@znoise[i,b]
 return draw,mu,cv

def prepare(draw,cv,ix):
 h=e.contrasts(15);ys=[];ns=[]
 for j in ix:
  avg=draw[:,j].mean(axis=1);profile=draw[:,j]/avg[:,None];jac=(np.eye(15)[None]-profile[:,:,None]/15)/avg[:,None,None]
  ns.append(np.einsum('ai,nij,njk,nlk,bl->nab',h,jac,cv[:,j],jac,h,optimize=True));ys.append(profile@h.T)
 noise=np.zeros((len(draw),len(ix)*14,len(ix)*14))
 for k,v in enumerate(ns):noise[:,k*14:(k+1)*14,k*14:(k+1)*14]=v
 return np.concatenate(ys,axis=1),noise,h

def statistics(y,noise,k0,k1):
 score=[]
 for v,n in zip(y,noise):
  ll=[]
  for prior in [k0,k1]:
   cf=linalg.cho_factor(n+prior,lower=True);ll.append(-.5*(v@linalg.cho_solve(cf,v)+2*np.log(np.diag(cf[0])).sum()))
  score.append(2*(ll[1]-ll[0]))
 return np.array(score)

def run():
 clear,dusty=e.load();p=np.load(e.O/'population_training.npz');cov=p['cov'];eig=p['eigenvalues'];vec=p['eigenvectors'];modes=fields()
 pop=np.array([np.sqrt(eig[j])*vec[:,j,None,None]*mode[None] for j in range(2) for mode in modes])
 # Positivity is guaranteed for every bounded coefficient realization.
 bound=np.sum(np.sqrt(eig[:2])[None,:]*abs(vec[:,:2]),axis=1);assert bound.max()<1
 np.savez_compressed(e.O/'final_population_ensemble_definition.npz',fields=modes,spectral_PC1=vec[:,0],spectral_PC2=vec[:,1],eigenvalues=eig[:2],calibration_coefficients=coefficients(N,0),evaluation_coefficients=coefficients(N,1))
 cases=e.screen_cases(clear,dusty);names=[k for k in cases if k!='C_gradient_coeff']
 nulls=[k for k in names if k.startswith('A_') or k.startswith('B_')]
 rows=[];raw=[];pp=[];calraw=[]
 for cid,(z,strategy,mode) in enumerate((z,s,m) for z in [.1,.3] for s in ['matched','native'] for m in ['seeing','glao']):
  g=e.geometry(z,mode,strategy);scores={b:{} for b in ['joint','optical','NIR']};cache={}
  znoise={}
  for stage in [0,1]:znoise[stage]=np.random.default_rng(510031+stage*900019+int(z*100)).normal(size=(N,7,15))
  for name in names:
   scene=cases[name];base,_=e.render(scene,z,g)
   if name=='D_SKIRT':pert=np.zeros((12,)+base.shape)
   else:
    # Matched multiplicative population shifts BEFORE screen and PSF.
    pert=np.array([e.render(scene*delta,z,g,signed=True)[0] for delta in pop])
   for stage in ([0,1] if name in nulls else [1]):
    c=coefficients(N,stage)
    draw,mu,cv=generate(base,pert,c,g,znoise[stage]);cache[name,stage]=(draw,cv)
   for bandset,ix in [('joint',list(range(7))),('optical',list(range(4))),('NIR',[4,5,6])]:
    for stage in ([0,1] if name in nulls else [1]):
     draw,cv=cache[name,stage];y,noise,h=prepare(draw,cv,ix);k0,k1,_=e.priors(g,cov,eig,vec,ix,h,'PC2_residual')
     scores[bandset][name,stage]=statistics(y,noise,k0,k1)
     if stage==1 and bandset=='joint':
      a=e.GaussianModel(noise[0],k0);b=e.GaussianModel(noise[0],k1);p0,_,_=e.posterior_check(a,y[0]);p1,_,_=e.posterior_check(b,y[0]);pp.append(dict(condition=cid,z=z,strategy=strategy,mode=mode,truth=name,uniform_ppp=p0,variable_ppp=p1))
  for bandset,d in scores.items():
   cut=max(e.threshold(d[name,0]) for name in nulls)
   for name in nulls:
    calraw.extend(dict(condition=cid,z=z,strategy=strategy,mode=mode,bandset=bandset,truth=name,noise_index=i,score=v) for i,v in enumerate(d[name,0]))
   for name in names:
    s=d[name,1];hit=s>cut;k=int(hit.sum());lo,hi=e.binomial_ci(k,N);group=dict(condition=cid,z=z,mode=mode,strategy=strategy,bandset=bandset,truth=name)
    rows.append(dict(**group,n_calibration_per_null=N,n_calibration_nulls=len(nulls),n_evaluation=N,threshold=cut,detections=k,rate=k/N,ci_low=lo,ci_high=hi,median_statistic=float(np.median(s))))
    raw.extend(dict(**group,noise_index=i,score=v,detected=bool(h)) for i,(v,h) in enumerate(zip(s,hit)))
  pd.DataFrame(rows).to_csv(e.O/'FINAL_calibrated_rates.csv',index=False)
  pd.DataFrame(pp).to_csv(e.O/'FINAL_posterior_predictive.csv',index=False)
  print('FINAL condition',cid,z,strategy,mode,flush=True)
 pd.DataFrame(raw).to_csv(e.O/'FINAL_evaluation_statistics.csv.gz',index=False)
 pd.DataFrame(calraw).to_csv(e.O/'FINAL_calibration_statistics.csv.gz',index=False)
 return pd.DataFrame(rows)
if __name__=='__main__':run()
