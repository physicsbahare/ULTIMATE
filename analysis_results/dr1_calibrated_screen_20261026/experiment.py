"""DR1 conditional, calibrated flux-contrast experiment. No evaluation truth in inference.
The inference is a linear Gaussian population/dust-colour FIELD approximation,
not a physical SPS fit. Exact generating screens precede the PSF.
"""
from pathlib import Path
import os,sys,json,hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/ultimate-mpl')
import numpy as np
import pandas as pd
from scipy import linalg,stats
from scipy.ndimage import gaussian_filter
from scipy.signal import fftconvolve
from astropy.io import fits
O=Path(__file__).resolve().parent
OLD=O.parent/'screen_test_20261026'
sys.dont_write_bytecode=True
sys.path.insert(0,str(OLD))
from forward_physics import cosmology,overlap_flux,ARCSEC_PER_RAD,specific_intensity_transfer,draw_exposures
from instrument import setup_instrument
BANDS=['LSST_g','LSST_r','LSST_i','LSST_z','2MASS_J','2MASS_H','2MASS_Ks']
LABELS=['g','r','i','z','J','H','Ks']
WAVE=np.array([.482,.622,.754,.869,1.235,1.662,2.159])
NTRAIN=200; NTEST=200

def seed_for(condition,stage): return 724091+100003*int(condition)+1009*int(stage)
def kappa(wave,n=1.):
 return (np.asarray(wave)/.55)**(-n)/((.44/.55)**(-n)-1)
def contrasts(n): return linalg.null_space(np.ones((1,n))).T
def threshold(x):
 # k=ceil((n+1)(1-alpha)); conservative finite calibration quantile.
 x=np.sort(x);k=int(np.ceil(.95*(len(x)+1)));return float(x[min(k-1,len(x)-1)])
def binomial_ci(k,n):
 return (0. if k==0 else float(stats.beta.ppf(.025,k,n-k+1)),1. if k==n else float(stats.beta.ppf(.975,k+1,n-k)))

class GaussianModel:
 def __init__(self,noise,prior):
  self.noise=noise;self.prior=prior;self.total=noise+prior
  self.cf=linalg.cho_factor(self.total,lower=True);self.inv=linalg.cho_solve(self.cf,np.eye(len(noise)))
  self.ld=2*np.log(np.diag(self.cf[0])).sum()
 def logpdf(self,y): return -.5*(np.einsum('ni,ij,nj->n',y,self.inv,y,optimize=True)+self.ld)
 def posterior(self,y):
  return self.prior@self.inv@y,self.prior-self.prior@self.inv@self.prior

def load(view='O1'):
 a=np.load(OLD/f'input_cache/{view}_structured_broadbands.npz')
 ix=[list(a['band']).index(b) for b in BANDS]
 # 40kpc field, native100pc. Images remain spatially structured.
 return a['clear'][ix,200:600,200:600].astype(float),a['dusty'][ix,200:600,200:600].astype(float)

def train_population(clear):
 # Nonoverlapping 1kpc bins; left half only. Fixed geometric training selection.
 blocks=clear.reshape(7,40,10,40,10).mean(axis=(2,4))
 xy=(np.arange(40)+.5)-20; yy,xx=np.meshgrid(xy,xy,indexing='ij')
 mask=(xx<-4)&(xx>-14)&(abs(yy)<10)
 vals=blocks[:,mask].T
 # TRAINING-only cut excludes near-empty template bins; no evaluation selection.
 good=(vals[:,-1]>np.median(vals[:,-1])*.1)&(vals>0).all(axis=1)
 vals=vals[good];rat=vals/vals[:,-1,None];center=np.median(rat,axis=0)
 frac=rat/center-1; frac-=np.mean(frac,axis=0)
 cov=np.cov(frac,rowvar=False);eig,vec=np.linalg.eigh(cov);order=np.argsort(eig)[::-1];eig=eig[order];vec=vec[:,order]
 np.savez_compressed(O/'population_training.npz',fractional_colours=frac,cov=cov,eigenvalues=eig,eigenvectors=vec,median_ratios=center,training_xy=np.column_stack([xx[mask][good],yy[mask][good]]))
 return cov,eig,vec,{'n_training_bins':len(vals),'training_x_kpc':[-14,-4],'evaluation_x_kpc':[4,10], 'training_bin_kpc':1.,'training_only_Ks_cut_fraction_of_median':.1}

def screen_cases(clear,dusty,coefficient_offset=0):
 yy,xx=np.meshgrid((np.arange(400)+.5)*.1-20,(np.arange(400)+.5)*.1-20,indexing='ij')
 gradient=.15+.13*np.tanh((xx-7)/3)
 rng=np.random.default_rng(41523);patch=gaussian_filter(rng.normal(size=xx.shape),10);patch/=patch.std()
 patch=.025+.25/(1+np.exp(-2*patch))
 cases={'A_clear':clear,'B_uniform':clear*10**(-.4*kappa(WAVE)[:,None,None]*.15),
 'C_gradient':clear*10**(-.4*kappa(WAVE)[:,None,None]*gradient),
 'C_patchy':clear*10**(-.4*kappa(WAVE)[:,None,None]*patch),'D_SKIRT':dusty}
 # Extra nulls constrain calibration across global E and law, fixed a priori.
 for n in [.7,1.,1.3]:cases[f'B_highE_n{n}']=clear*10**(-.4*kappa(WAVE,n)[:,None,None]*.35)
 if coefficient_offset:
  # Fixed band-dependent effective-coefficient perturbation; not a random fit freedom.
  shift=1+coefficient_offset*np.array([1,-1,1,-1,1,-1,1])
  cases['C_gradient_coeff']=clear*10**(-.4*(kappa(WAVE)*shift)[:,None,None]*gradient)
 np.savez_compressed(O/'screen_definitions.npz',x_kpc=xx,y_kpc=yy,gradient_E=gradient,patchy_E=patch,k_lambda=kappa(WAVE),wave_um=WAVE)
 return cases

def kernel(width,pix,kind='gaussian'):
 if width<1e-8:return np.ones((1,1))
 if kind=='gaussian':
  sig=width/2.354820045/pix;half=int(np.ceil(6*sig));q=np.arange(-half,half+1);v=np.exp(-.5*(q/sig)**2);k=np.outer(v,v)
 else:
  beta=2.5;alpha=width/(2*np.sqrt(2**(1/(beta-1))-1))/pix;half=int(np.ceil(12*alpha));yy,xx=np.mgrid[-half:half+1,-half:half+1];k=(1+(xx*xx+yy*yy)/alpha**2)**-beta
 return k/k.sum()

def geometry(z,mode,strategy,kind='gaussian',bin_kpc=1.5):
 inst=[b for b in setup_instrument() if b['band'] in LABELS]
 inst=[next(b for b in inst if b['band']==lab) for lab in LABELS]
 scale=cosmology.kpc_proper_per_arcmin(z).value/60
 pix=.1;native=.1/scale
 # Pad flux field by8kpc; Moffat finite wings all recorded.
 pad=80;n=560;edges=(np.arange(n+1)-n/2)*native
 outn=2*int(np.ceil(edges[-1]/pix));outedges=(np.arange(outn+1)-outn/2)*pix
 coords=np.array([(x,y) for y in [-6,-3,0,3,6] for x in [4,7,10]],float)
 widths=np.array([b['seeing_fwhm_arcsec'] if mode=='seeing' else b['glao_fwhm_arcsec'] for b in inst])
 # True common PSF for Moffat: convolve EVERY band with all other native kernels.
 # Broader than Gaussian common .8, but positive, normalized and exact (no deconvolution).
 ks=[kernel(w,pix,kind) for w in widths]
 if strategy=='matched':
  if kind=='gaussian':match=[kernel(np.sqrt(.8**2-w*w),pix) for w in widths]
  else:
   # Common target = product of all distinct native PSFs, same across seeing/glao.
   allw=sorted(set([.7]+[b['seeing_fwhm_arcsec'] for b in inst[4:]]+[b['glao_fwhm_arcsec'] for b in inst[4:]]))
   match=[]
   for w in widths:
    rem=allw.copy();rem.remove(float(w));k=np.ones((1,1))
    for other in rem:k=fftconvolve(k,kernel(other,pix,kind))
    match.append(k/k.sum())
 else:match=[np.ones((1,1)) for _ in widths]
 yy,xx=np.meshgrid((np.arange(outn)+.5-outn/2)*pix*scale,(np.arange(outn)+.5-outn/2)*pix*scale,indexing='ij')
 ap=[]
 for x,y in coords:ap.append(((abs(xx-x)<bin_kpc/2)&(abs(yy-y)<bin_kpc/2)).astype(float))
 ap=np.array(ap)
 if np.any(ap.sum(axis=(1,2))==0):raise ValueError('Empty aperture')
 weights=np.array([[fftconvolve(a,k,mode='same') for a in ap] for k in match])
 # Finite spatial field, 3kpc nodes, 1.8kpc RBF. Same latent population model in both modes.
 nodes=np.array([(x,y) for y in np.arange(-15,16,3) for x in np.arange(-15,16,3)])
 rbf=np.exp(-((xx[None]-nodes[:,0,None,None])**2+(yy[None]-nodes[:,1,None,None])**2)/(2*1.8**2))
 rbf/=np.maximum(rbf.sum(axis=0),1e-30)
 response=[]
 for k,w in zip(ks,weights):
  eff=np.array([fftconvolve(a,k,mode='same') for a in w])
  response.append(np.einsum('ayx,nyx->an',eff,rbf,optimize=True)/ap.sum(axis=(1,2))[:,None])
 response=np.array(response)
 return dict(inst=inst,scale=scale,native=native,pad=pad,edges=edges,outedges=outedges,nout=outn,coords=coords,weights=weights,response=response,kernels=ks,widths=widths,strategy=strategy,kind=kind,bin_kpc=bin_kpc)

def render(scene,z,g,signed=False):
 rates=[];errors=[]
 for s,b,w in zip(scene,g['inst'],g['widths']):
  flux=np.pad(s/(1+z)**3*1e6*(g['native']/ARCSEC_PER_RAD)**2,g['pad'])
  before=flux.sum();conv=fftconvolve(flux,kernel(w,g['native'],g['kind']),mode='same')
  out=overlap_flux(conv,g['edges'],g['outedges']);errors.append(out.sum()/before-1 if abs(before)>1e-20 else 0)
  rates.append((out if signed else np.maximum(out,0))*b['flat_e_s_per_jy'])
 return np.array(rates),float(max(abs(np.array(errors))))

def compressed_observation(rates,g,hours,seed,n=400):
 # Exact first two moments of summed split exposures. Gaussian draw is validated
 # against exact source+sky Poisson and read noise in validate_poisson().
 t=hours*3600;nexp=int(round(t/60));assert nexp*60==t
 rng=np.random.default_rng(seed);means=[];covs=[];draws=[];mincounts=[]
 for r,b,w in zip(rates,g['inst'],g['weights']):
  back=b['background_e_s_pixel']+b['dark_e_s'];v=(r+back)*t+nexp*b['read_noise_e']**2
  ww=w.reshape(15,-1);mean=ww@r.ravel()*t;cov=(ww*v.ravel())@ww.T
  noise=rng.standard_normal((n,15))@linalg.cholesky(cov,lower=True).T
  draws.append(mean[None]+noise);means.append(mean);covs.append(cov);mincounts.append(back*t)
 return np.array(draws).transpose(1,0,2),np.array(means),np.array(covs),min(mincounts)

def prepare_data(draws,means,covs,indices):
 # Inference sees measured fluxes and supplied photometric covariance ONLY.
 # Exact generating means are deliberately unused. Each draw has its own
 # observed delta-method Jacobian, including normalization-induced covariance.
 nbin=draws.shape[2];h=contrasts(nbin);ys=[];ns=[]
 for j in indices:
  average=draws[:,j].mean(axis=1);profile=draws[:,j]/average[:,None]
  jac=(np.eye(nbin)[None]-profile[:,:,None]/nbin)/average[:,None,None]
  ns.append(np.einsum('ai,nij,jk,nlk,bl->nab',h,jac,covs[j],jac,h,optimize=True))
  ys.append(profile@h.T)
 nobs=len(draws);width=len(h);noise=np.zeros((nobs,len(indices)*width,len(indices)*width))
 for k,v in enumerate(ns):noise[:,k*width:(k+1)*width,k*width:(k+1)*width]=v
 return np.concatenate(ys,axis=1),noise,h

def priors(g,cov,eig,vec,indices,h,hierarchy,popscale=1.,dustn=1.):
 if hierarchy=='constant':pop=np.zeros_like(cov)
 elif hierarchy=='PC1':pop=np.outer(vec[:,0],vec[:,0])*eig[0]
 else:pop=cov # first2 PCs + measured correlated residual; no tuned error floor
 pop=pop*popscale**2
 # RBF projection gives native band-specific PSFs inside the likelihood.
 r=np.array([h@g['response'][j] for j in indices])
 # One INTRINSIC coefficient normalization shared across PSFs, bands and z.
 nodes=np.array([(x,y) for y in np.arange(-15,16,3) for x in np.arange(-15,16,3)])
 center=np.exp(-np.sum(nodes*nodes,axis=1)/(2*1.8**2));center/=center.sum()
 r=r/np.sqrt(np.sum(center*center))
 d=len(indices)*len(h);gray=np.zeros((d,d));p=np.zeros((d,d));dust=np.zeros((d,d));k=kappa(WAVE,dustn);k=k-k.mean()
 for ai,a in enumerate(indices):
  for bi,b in enumerate(indices):
   s=r[ai]@r[bi].T;sl=np.s_[ai*len(h):(ai+1)*len(h),bi*len(h):(bi+1)*len(h)]
   gray[sl]=4*s # broad common-morphology coefficient prior, SD2 in fractional flux
   p[sl]=pop[a,b]*s
   dust[sl]=(.4*np.log(10)*.15)**2*k[a]*k[b]*s
 return gray+p,gray+p+dust,dust

def fit_statistics(y,noise,k0,k1):
 if noise.ndim==2:
  a=GaussianModel(noise,k0);b=GaussianModel(noise,k1)
  return 2*(b.logpdf(y)-a.logpdf(y)),a,b
 score=[]
 # Only a single RHS per covariance is needed for evidence. Materialize inverse
 # and posterior only for the prespecified first held-out draw.
 for v,n in zip(y,noise):
  ll=[]
  for prior in [k0,k1]:
   cf=linalg.cho_factor(n+prior,lower=True)
   ll.append(-.5*(v@linalg.cho_solve(cf,v)+2*np.log(np.diag(cf[0])).sum()))
  score.append(2*(ll[1]-ll[0]))
 return np.array(score),GaussianModel(noise[NTRAIN],k0),GaussianModel(noise[NTRAIN],k1)

def posterior_check(model,y,seed=944):
 # Bayesian posterior predictive discrepancy: SAME posterior latent field for
 # observed and replicated residuals, rather than plugging in posterior mean.
 mean,cov=model.posterior(y);cov=(cov+cov.T)/2
 cf=linalg.cho_factor(model.noise);ni=linalg.cho_solve(cf,np.eye(len(y)))
 rng=np.random.default_rng(seed);v,u=np.linalg.eigh(cov)
 latent=mean[None]+rng.normal(size=(1000,len(y)))@(u*np.sqrt(np.maximum(v,0))).T
 residual=y[None]-latent
 qobs=np.einsum('ni,ij,nj->n',residual,ni,residual,optimize=True)
 qrep=rng.chisquare(len(y),size=1000)
 return float(np.mean(qrep>=qobs)),float(np.median(qobs)),float(np.median(qrep))

def validate_poisson():
 g=geometry(.3,'glao','matched');clear,_=load();rates,_=render(clear,.3,g)
 rng=np.random.default_rng(61812);rows=[]
 # Project exact count distributions through matching/aperture weights for two
 # bands; reduce to nonzero weight footprint, retain all significant weights.
 for j in [0,6]:
  w=g['weights'][j,7].ravel();sel=w>1e-9;w=w[sel];r=rates[j].ravel()[sel];b=g['inst'][j];back=b['background_e_s_pixel']+b['dark_e_s'];t=3600
  target=np.sum(w*r*t);variance=np.sum(w*w*((r+back)*t+60*b['read_noise_e']**2));samples=[]
  for start in range(0,1000,25):
   x=rng.poisson((r+back)*t,size=(25,len(r)))+rng.normal(0,np.sqrt(60)*b['read_noise_e'],size=(25,len(r)))-back*t
   samples.extend((x@w-target)/np.sqrt(variance))
  z=np.array(samples);test=stats.kstest(z,'norm');rows.append(dict(band=LABELS[j],n=1000,mean_standardized=z.mean(),variance_standardized=z.var(),ks_p=test.pvalue,skew=stats.skew(z)))
 pd.DataFrame(rows).to_csv(O/'exact_poisson_validation.csv',index=False)
 return rows

def run_condition(cid,view,z,mode,strategy,cases,cov,eig,vec,hours=1.,kind='gaussian',bin_kpc=1.5,robust=False):
 g=geometry(z,mode,strategy,kind,bin_kpc);rows=[];raw=[];ppc=[];trans=[]
 bands={'joint':list(range(7)),'optical':list(range(4)),'NIR':[4,5,6]}
 nulls=[x for x in cases if x.startswith('A_') or x.startswith('B_')]
 cache={}
 # Same standard normal draws across truths AND observing strategies/modes at
 # fixed z/view: paired Gaussian noise, correct per-scene Poisson variances.
 pairid=int(view[1:])*100+int(z*100)+int(hours*10)+int(bin_kpc*10)+(1000 if kind!='gaussian' else 0)
 for name,scene in cases.items():
  rate,err=render(scene,z,g);draw,means,cs,mincounts=compressed_observation(rate,g,hours,seed_for(pairid,0))
  trans.append(dict(condition=cid,view=view,z=z,mode=mode,strategy=strategy,kind=kind,width_metric='Gaussian FWHM=D50; Moffat equal D50',truth=name,max_crop_flux_loss=err,min_background_e_total=mincounts,min_aperture_snr=float(np.min(means/np.sqrt(np.diagonal(cs,axis1=1,axis2=2))))))
  cache[name]=(draw,means,cs)
 for bandset,ix in bands.items():
  prepared={name:prepare_data(*v,ix) for name,v in cache.items()}
  for hierarchy in ['constant','PC1','PC2_residual']:
   scales=[1.] if not robust or hierarchy!='PC2_residual' else [.5,1.,2.]
   laws=[1.] if not robust or hierarchy!='PC2_residual' else [.7,1.,1.3]
   for popscale,dustn in [(s,n) for s in scales for n in laws if s==1 or n==1]:
    h=next(iter(prepared.values()))[2];k0,k1,kdust=priors(g,cov,eig,vec,ix,h,hierarchy,popscale,dustn)
    fitted={name:fit_statistics(y,noise,k0,k1) for name,(y,noise,h) in prepared.items()}
    cut=max(threshold(fitted[name][0][:NTRAIN]) for name in nulls)
    group=dict(condition=cid,view=view,z=z,mode=mode,strategy=strategy,psf_kind=kind,hours_per_band=hours,bin_kpc=bin_kpc,bandset=bandset,population=hierarchy,popscale=popscale,dust_slope=dustn)
    for name,(score,a,b) in fitted.items():
     ev=score[NTRAIN:];hit=ev>cut;k=int(hit.sum());lo,hi=binomial_ci(k,len(ev))
     rows.append(dict(**group,truth=name,n_calibration_per_null=NTRAIN,n_calibration_nulls=len(nulls),n_evaluation=len(ev),threshold=cut,detections=k,rate=k/len(ev),ci_low=lo,ci_high=hi,score_median=float(np.median(ev))))
     for i,(s,d) in enumerate(zip(ev,hit)):raw.append(dict(**group,truth=name,noise_index=i,score=s,detected=bool(d)))
     # Full noise-level posterior predictive check is expensive: prespecified
     # first held-out draw, not a selected success or extreme observation.
     if bandset=='joint' and popscale==1 and dustn==1:
      y=prepared[name][0][NTRAIN];p0,q0,rep0=posterior_check(a,y);p1,q1,rep1=posterior_check(b,y)
      dm=kdust@b.inv@y;dc=kdust-kdust@b.inv@kdust
      ppc.append(dict(**group,truth=name,uniform_ppp=p0,variable_ppp=p1,uniform_residual_q=q0,variable_residual_q=q1,uniform_rep_q=rep0,variable_rep_q=rep1,dust_contrast_posterior_rms=float(np.sqrt(np.mean(dm*dm))),dust_contrast_sd_rms=float(np.sqrt(np.mean(np.diag(dc))))))
 print(f'condition {cid}: {view} z={z} {mode} {strategy} {kind}, {len(rows)} summary rows',flush=True)
 return rows,raw,ppc,trans

def run():
 clear,dusty=load();cov,eig,vec,trainmeta=train_population(clear)
 cases=screen_cases(clear,dusty,coefficient_offset=.05)
 np.savez_compressed(O/'matched_DR1_scenes_O1.npz',bands=np.array(BANDS),wave_um=WAVE,**{k:v.astype('f4') for k,v in cases.items() if k in ['A_clear','B_uniform','C_gradient','C_patchy','D_SKIRT','C_gradient_coeff']})
 pd.DataFrame({'band':LABELS,'DR1_band':BANDS,'lambda_um':WAVE,'k_n07':kappa(WAVE,.7),'k_n1':kappa(WAVE),'k_n13':kappa(WAVE,1.3)}).to_csv(O/'attenuation_coefficients.csv',index=False)
 configs=[]
 for z in [.1,.3]:
  for strategy in ['matched','native']:
   for mode in ['seeing','glao']:configs.append(('O1',z,mode,strategy,1.,'gaussian',1.5,True))
 # Prespecified sensitivities, not tuned after seeing results.
 for mode in ['seeing','glao']:
  configs.extend([('O1',.3,mode,'native',1.,'moffat',1.5,False),('O1',.3,mode,'native',.25,'gaussian',1.5,False),('O1',.3,mode,'native',4.,'gaussian',1.5,False),('O1',.3,mode,'native',1.,'gaussian',3.,False)])
 for view in ['O2','O3','O4','O5']:
  for mode in ['seeing','glao']:configs.append((view,.3,mode,'native',1.,'gaussian',1.5,False))
 allrows=[];allraw=[];allppc=[];alltrans=[]
 for cid,(view,z,mode,strategy,hours,kind,bin_kpc,robust) in enumerate(configs):
  if view=='O1':c=cases
  else:
   cc,dd=load(view);c=screen_cases(cc,dd)
   # Screen geometry files only saved for O1 after execution; generators frozen.
  result=run_condition(cid,view,z,mode,strategy,c,cov,eig,vec,hours,kind,bin_kpc,robust)
  for dest,part in zip([allrows,allraw,allppc,alltrans],result):dest.extend(part)
  pd.DataFrame(allrows).to_csv(O/'calibrated_rates.csv',index=False)
  pd.DataFrame(allppc).to_csv(O/'posterior_predictive.csv',index=False)
  pd.DataFrame(alltrans).to_csv(O/'transfer_validation.csv',index=False)
 pd.DataFrame(allraw).to_csv(O/'evaluation_statistics.csv.gz',index=False)
 # Restore original O1 definitions after views.
 screen_cases(clear,dusty,coefficient_offset=.05)
 meta=dict(seed_base=724091,n_calibration_per_null=NTRAIN,n_evaluation_per_truth=NTEST,training=trainmeta,conditions=configs,noise='Gaussian compressed flux with exact split-exposure first two moments; exact Poisson validation separate',dust_E_rms_prior=.15,common_morphology_sigma=2,spatial_RBF_width_kpc=1.8,node_spacing_kpc=3,normalization='per-band mean, delta-method covariance; absolute E unidentifiable',primary='matched-rest-band image degradation, no K correction or intrinsic evolution')
 (O/'parameters.json').write_text(json.dumps(meta,indent=2))
 validate_poisson()
 return pd.DataFrame(allrows)
if __name__=='__main__': run()
