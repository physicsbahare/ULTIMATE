"""Positive stellar-mixture x attenuation model with band-dependent PSF operators.
Templates are independent spatial training spectra (broadbands only). No target
clear image, attenuation or physical map enters ForwardModel.fit().
"""
from pathlib import Path
import os,sys,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/ultimate-mpl');sys.dont_write_bytecode=True
import numpy as np
from scipy import linalg,optimize,special
from scipy.signal import fftconvolve
O=Path(__file__).resolve().parent;PREV=O.parent/'dr1_calibrated_screen_20261026'
sys.path.insert(0,str(PREV));import experiment as e
from forward_physics import overlap_matrix

def train_templates():
 clear,_=e.load();block=clear.reshape(7,40,10,40,10).mean(axis=(2,4));x=np.arange(40)+.5-20;yy,xx=np.meshgrid(x,x,indexing='ij');mask=(xx<-4)&(xx>-14)&(abs(yy)<10);val=block[:,mask].T;good=(val[:,-1]>.1*np.median(val[:,-1]))&(val>0).all(axis=1);val=val[good];xy=np.column_stack([xx[mask][good],yy[mask][good]]);rat=val/val[:,-1,None];logs=np.log(rat);center=logs.mean(axis=0);u,s,v=np.linalg.svd(logs-center,full_matrices=False);scores=(logs-center)@v[:3].T;ids=[]
 for j in range(3):ids.extend([int(scores[:,j].argmin()),int(scores[:,j].argmax())])
 ids=list(dict.fromkeys(ids));templates=np.vstack([rat[ids],rat.mean(axis=0)])
 np.savez_compressed(O/'stellar_training.npz',templates=templates,training_SEDs=rat,xy=xy,prototype_indices=ids,log_mean=center,log_PC=v,log_eigenvalue=s*s/(len(rat)-1),log_scores=scores)
 return templates

def invsoftplus(x):return np.log(np.expm1(np.maximum(x,1e-8)))

class ForwardModel:
 def __init__(self,mode='seeing',strategy='native',field='fine',bin_kpc=1.5):
  self.mode=mode;self.strategy=strategy;self.bin_kpc=bin_kpc;self.g=e.geometry(.3,mode,strategy,bin_kpc=bin_kpc)
  self.templates=np.load(O/'stellar_training.npz')['templates'] if (O/'stellar_training.npz').exists() else train_templates();self.nt=len(self.templates)
  # One kpc cells; adjoint operator exactly matches rendering a piecewise
  # constant 100pc-grid scene. The real structured galaxy is never replaced
  # by this model in observation generation.
  y,x=np.meshgrid(np.arange(40)+.5-20,np.arange(40)+.5-20,indexing='ij');self.xy=np.column_stack([x.ravel(),y.ravel()]);self.ncell=len(self.xy)
  nodes=np.array([(xx,yy) for yy in np.arange(-12,13,2) for xx in np.arange(-4,17,2)])
  G=np.exp(-np.sum((self.xy[:,None,:]-nodes[None,:,:])**2,axis=2)/(2*.8**2));G/=G.sum(axis=1)[:,None];self.G=G;self.ngray=len(nodes)
  centers=self.g['coords'].copy()
  if field=='coarse':centers=centers[[0,2,6,8,12,14]]
  centers=np.vstack([centers,[[0,-8],[0,0],[0,8]]]);R=np.exp(-np.sum((self.xy[:,None,:]-centers[None,:,:])**2,axis=2)/(2*2.0**2));R/=np.maximum(R.sum(axis=1)[:,None],1e-30)
  self.B=np.column_stack([np.ones(self.ncell),R@e.contrasts(len(centers)).T]);self.nspatial=self.B.shape[1];self.npop=(self.nt-1)*self.nspatial
  self.response=self.operator() # e/s for intensity1 MJy/sr in each1kpc cell
  flat=np.array([b['flat_e_s_per_jy'] for b in self.g['inst']]);self.fluxresponse=self.response/flat[:,None,None]*1e6 # µJy
  # Fixed proper priors. Morphology is nuisance, smooth but not fixed to truth.
  base=self.ngray+self.npop+1
  mean=np.r_[np.full(self.ngray,-2.),np.zeros(self.npop),-1.1]
  sd=np.r_[np.full(self.ngray,3.),np.full(self.npop,2.),2.]
  rows=[np.diag(1/sd)];pairs=[]
  for i,(xx,yy) in enumerate(nodes):
   for delta in [(2,0),(0,2)]:
    hits=np.flatnonzero(np.all(nodes==[xx+delta[0],yy+delta[1]],axis=1))
    if len(hits):r=np.zeros(base);r[i]=.5;r[hits[0]]=-.5;pairs.append(r)
  self.prior_null=np.vstack(rows+[np.array(pairs)]);self.mean_null=mean
  self.field=field
 def operator(self):
  cache=O/(f'operator_{self.mode}_{self.strategy}_1kpc.npz' if self.bin_kpc==1.5 else f'operator_{self.mode}_{self.strategy}_1kpc_bin{self.bin_kpc}.npz')
  if cache.exists():return np.load(cache)['response']
  g=self.g;M=overlap_matrix(g['outedges'],g['edges'])/g['native'];out=[]
  for b,w,fw in zip(g['inst'],g['weights'],g['widths']):
   ar=[]
   for ww in w:
    adj=np.asarray((M.T@ww)@M)
    adj=fftconvolve(adj,e.kernel(fw,g['native']),mode='same')[80:480,80:480]
    ar.append(adj.reshape(40,10,40,10).sum(axis=(1,3)))
   factor=1e6*(g['native']/e.ARCSEC_PER_RAD)**2/(1.3**3)*b['flat_e_s_per_jy'];out.append(np.array(ar).reshape(15,1600)*factor)
  out=np.array(out);np.savez_compressed(cache,response=out);return out
 def initial(self,data=None):
  q=self.mean_null.copy()
  if data is not None:
   pred=self.predict(q,False).reshape(7,15);ratio=max(np.mean(data[-1])/np.mean(pred[-1]),1e-4);amp=special.softplus(q[:self.ngray]) if hasattr(special,'softplus') else np.logaddexp(0,q[:self.ngray]);q[:self.ngray]=invsoftplus(amp*ratio)
  return q
 def unpack(self,q,variable):
  m=q[:self.ngray];c=q[self.ngray:self.ngray+self.npop].reshape(self.nt-1,self.nspatial);d=q[self.ngray+self.npop:]
  amp=self.G@np.logaddexp(0,m);logits=np.vstack([c@self.B.T,np.zeros(self.ncell)]);w=special.softmax(logits,axis=0);sed=self.templates.T@w
  a=self.B@d if variable else np.full(self.ncell,d[0]);E=.6*special.expit(a)
  return amp,w,sed,E
 def predict(self,q,variable,jac=False):
  amp,w,sed,E=self.unpack(q,variable);att=np.exp(-.4*np.log(10)*e.kappa(e.WAVE)[:,None]*E);I=amp[None]*sed*att;f=np.einsum('ban,bn->ba',self.fluxresponse,I,optimize=True).ravel()
  if not jac:return f
  npar=len(q);J=np.empty((105,npar));m=q[:self.ngray];bd=self.B if variable else np.ones((self.ncell,1));de=E*(1-E/.6)
  for b in range(7):
   r=self.fluxresponse[b];jgray=(r@((sed[b]*att[b])[:,None]*self.G))*special.expit(m)[None]
   jp=[]
   for t in range(self.nt-1):jp.append(r@((amp*att[b]*w[t]*(self.templates[t,b]-sed[b]))[:,None]*self.B))
   jd=r@((-.4*np.log(10)*e.kappa(e.WAVE[b])*I[b]*de)[:,None]*bd)
   J[b*15:(b+1)*15]=np.column_stack([jgray,*jp,jd])
  return f,J
 def prior(self,variable):
  if not variable:return self.prior_null,self.mean_null
  n=self.nspatial-1;R=np.zeros((len(self.prior_null)+n,len(self.mean_null)+n));R[:len(self.prior_null),:len(self.mean_null)]=self.prior_null;R[len(self.prior_null):,len(self.mean_null):]=np.eye(n)/2
  return R,np.r_[self.mean_null,np.zeros(n)]
 def measurements(self,counts,covs,hours=1.):
  fac=1e6/(hours*3600*np.array([b['flat_e_s_per_jy'] for b in self.g['inst']]))
  return counts*fac[:,None],np.array([c*f*f for c,f in zip(covs,fac)])
 def fit(self,data,covs,variable=False,normalized=False,start=None,max_nfev=180):
  # Only observed fluxes and photometric covariance enter this API.
  C=linalg.block_diag(*covs);obs=data.ravel();h=e.contrasts(15)
  if normalized:
   obs,nn,_=e.prepare_data(data[None],None,covs,list(range(7)));obs=obs[0];C=nn[0]
  whiten=linalg.solve_triangular(linalg.cholesky(C,lower=True),np.eye(len(C)),lower=True)
  R,mean=self.prior(variable);q=self.initial(data) if start is None else start.copy()
  if variable and len(q)==len(self.mean_null):q=np.r_[q,np.zeros(self.nspatial-1)]
  def pred(theta,derivative=False):
   result=self.predict(theta,variable,derivative)
   if not normalized:return result
   if derivative:f,j=result
   else:f=result
   arr=f.reshape(7,15);parts=[];js=[]
   for b,ar in enumerate(arr):
    avg=ar.mean();profile=ar/avg;parts.append(h@profile)
    if derivative:js.append(h@(np.eye(15)-profile[:,None]/15)/avg@j[b*15:(b+1)*15])
   return (np.concatenate(parts),np.vstack(js)) if derivative else np.concatenate(parts)
  def fun(theta):return np.r_[whiten@(pred(theta)-obs),R@(theta-mean)]
  def jac(theta):return np.vstack([whiten@pred(theta,True)[1],R])
  result=optimize.least_squares(fun,q,jac=jac,method='lm',max_nfev=max_nfev,ftol=2e-7,xtol=2e-7,gtol=1e-6)
  theta=result.x;f,J=pred(theta,True);res=whiten@(f-obs);jdata=whiten@J;precision=jdata.T@jdata+R.T@R;cf=linalg.cho_factor(precision);pcov=linalg.cho_solve(cf,np.eye(len(theta)));hat=jdata@pcov@jdata.T;effective=float(np.trace(hat));df=float(len(obs)-2*effective+np.trace(hat@hat))
  # df is the noise-only expectation of a local penalized residual quadratic,
  # not a calibrated chi-square law; tail diagnostic never gates inference.
  # Posterior predictive discrepancy conditional on the SAME latent draw,
  # using local Laplace flux approximation. Exact nonlinear checks separate.
  latent_cov=jdata@pcov@jdata.T;val,vec=np.linalg.eigh((latent_cov+latent_cov.T)/2);rng=np.random.default_rng(8172);delta=rng.normal(size=(1000,len(obs)))@(vec*np.sqrt(np.maximum(val,0))).T;qobs=np.sum((res[None]+delta)**2,axis=1);qrep=rng.chisquare(len(obs),1000);pp=float(np.mean(qrep>=qobs))
  return dict(theta=theta,prediction=self.predict(theta,variable),chi2=float(res@res),penalized_objective=float(np.sum(fun(theta)**2)),effective_parameters=effective,residual_dof=df,ppp=pp,noise_tail_p=float(stats_chi2_sf(res@res,max(df,1))),success=bool(result.success),nfev=result.nfev,optimality=float(result.optimality),parameter_covariance=pcov,jacobian_data=jdata,flux_covariance=C,normalized=normalized,variable=variable)

def stats_chi2_sf(q,df):
 from scipy.stats import chi2
 return chi2.sf(q,df)
