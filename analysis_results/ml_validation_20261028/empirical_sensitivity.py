"""Image-level PSF/noise stresses; no physical dust calibration from HAWK-I."""
from pathlib import Path
import sys,json,time
import numpy as np,pandas as pd
from scipy import signal,ndimage as ndi
O=Path(__file__).resolve().parent;S=O.parent/'ml_expanded_20261028';sys.path.insert(0,str(S));import expanded_features as e
meta=pd.read_csv(e.PART);dev=meta[meta.partition=='development'].sort_values('log10_stellar_mass')
ids=sorted(set(dev.iloc[np.linspace(0,len(dev)-1,12).astype(int)].subhalo_id)|{13,167418,184937,613192}|set(meta[meta.partition=='validation'].subhalo_id))
pd.DataFrame({'subhalo_id':ids,'view':'O1'}).merge(meta[['subhalo_id','partition']]).to_csv(O/'sensitivity_sample.csv',index=False)
original=e.old.p.psf_kernel

def elliptical(width,pixel,beta=3.7415,q=.8199,actual_fwhm=False):
 if actual_fwhm:alpha=width/(2*np.sqrt(2**(1/beta)-1))/pixel
 else:alpha=width/(2*np.sqrt(2**(1/(beta-1))-1))/pixel
 aa=alpha/np.sqrt(q);bb=alpha*np.sqrt(q);axis=np.arange(-int(np.ceil(12*aa)),int(np.ceil(12*aa))+1);y,x=np.meshgrid(axis,axis,indexing='ij');k=(1+(x/aa)**2+(y/bb)**2)**(-beta);return k/k.sum()

def correlated(z,long=False):
 a=[]
 for rho in [.2753,.2932]:a.append((1-np.sqrt(1-2*rho*rho))/(2*rho))
 kx=np.array([a[0],1,a[0]]);kx/=np.linalg.norm(kx);ky=np.array([a[1],1,a[1]]);ky/=np.linalg.norm(ky)
 local=ndi.convolve1d(ndi.convolve1d(z,kx,axis=-1,mode='reflect'),ky,axis=-2,mode='reflect')
 if not long:return local
 # Independent long-scale component. This is an explicit stress, not a fitted ESO covariance.
 sigma=5.;b=np.arange(-25,26);v=np.exp(-.5*(b/sigma)**2);v/=np.linalg.norm(v)
 independent=np.roll(z,(127,143),axis=(-2,-1));broad=ndi.convolve1d(ndi.convolve1d(independent,v,axis=-1,mode='reflect'),v,axis=-2,mode='reflect')
 return np.sqrt(.98)*local+np.sqrt(.02)*broad

def run():
 out=O/'sensitivity_features';out.mkdir(exist_ok=True);checks=[]
 for sid in ids:
  dest=out/f'{sid}.csv.gz'
  if dest.exists():continue
  path=S/'data_audit/cache'/str(sid)
  while not (path/'complete.json').exists():time.sleep(20)
  with np.load(path/'O1.npz') as z:dusty=np.array([z['dusty_'+b] for b in e.SOURCE],float)
  radius,_=e.aperture_policy(dusty);rows=[]
  for scenario in ['nominal','local_covariance','long_covariance','elliptical_wings','hawki_shape','coarse_sampling','low_surface_brightness']:
   for mode in ['seeing','glao']:
    g=e.geometry(mode,pixel=.2 if scenario=='coarse_sampling' else .1)
    if scenario in ['elliptical_wings','hawki_shape']:
     g['kind']='empirical'
     # Only NIR shape changes; optical g remains the same seeing Gaussian.
     optical=float(g['widths'][0]);nir=[float(v) for v in g['widths'][1:]]
     if scenario=='hawki_shape' and mode=='glao':g['widths'][2]=.2935
     def kernel(w,pixel,kind):
      if w==optical:return original(w,pixel,'gaussian')
      actual=scenario=='hawki_shape' and mode=='glao' and abs(w-.2935)<1e-8
      return elliptical(w,pixel,actual_fwhm=actual)
     e.old.p.psf_kernel=kernel
    else:e.old.p.psf_kernel=original
    rate,loss=e.old.p.render(dusty,g);assert loss<2e-4
    if scenario=='low_surface_brightness':rate=rate*.25
    t=3600;variance=np.array([(r+b['background_e_s_pixel']*(g['pixel']/.1)**2+b['dark_e_s'])*t+60*b['read_noise_e']**2 for r,b in zip(rate,e.old.p.INST)])/t**2
    plans={ap:e.FeaturePlan(g,r) for ap,r in [('fixed12',12.),('adaptive',radius)]}
    rng=np.random.default_rng(20261028+int(sid)*101)
    for draw in range(2):
     z=rng.normal(size=rate.shape)
     if scenario=='local_covariance':z[1:]=correlated(z[1:])
     if scenario=='long_covariance':z[1:]=correlated(z[1:],True)
     im=rate+np.sqrt(variance)*z
     for ap,plan in plans.items():rows.append(dict(subhalo_id=sid,view='O1',draw=draw,scenario=scenario,mode=mode,aperture=ap,**plan(im)))
    checks.append(dict(subhalo_id=sid,scenario=scenario,mode=mode,pixel_arcsec=g['pixel'],g_width=g['widths'][0],Ks_width=g['widths'][2],padded_flux_loss=loss))
   e.old.p.psf_kernel=original
  pd.DataFrame(rows).to_csv(dest,index=False);print('Sensitivity',sid,flush=True)
 pd.DataFrame(checks).to_csv(O/'sensitivity_render_checks.csv',index=False)
 # Stationary white-noise response diagnostics independent of galaxy science.
 rng=np.random.default_rng(8821);z=rng.normal(size=(1,1024,1024));noise=[]
 for name,zz in [('white',z),('local_covariance',correlated(z)),('long_covariance',correlated(z,True))]:
  a=zz[0];a=a/a.std();entry=dict(scenario=name,rho_x=np.corrcoef(a[:,:-1].ravel(),a[:,1:].ravel())[0,1],rho_y=np.corrcoef(a[:-1].ravel(),a[1:].ravel())[0,1])
  for r in [2,4,8,16,32]:
   yy,xx=np.mgrid[-r:r+1,-r:r+1];k=(xx*xx+yy*yy<r*r);sums=signal.fftconvolve(a,k,mode='valid');entry['aperture_ratio_R'+str(r)]=float(sums.std()/np.sqrt(k.sum()))
  noise.append(entry)
 pd.DataFrame(noise).to_csv(O/'sensitivity_noise_response.csv',index=False)
if __name__=='__main__':run()
