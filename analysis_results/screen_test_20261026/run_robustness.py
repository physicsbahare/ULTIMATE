from pathlib import Path
import numpy as np,pandas as pd
from instrument import setup_instrument
from imaging import make_truths,project_scene,aperture_catalog,observe_apertures
from stellar_models import screen_shape_grid
from screen_inference import fit_screen_models,amplitude_marginal_likelihood
from scipy.special import logsumexp,ndtr
from forward_physics import ARCSEC_PER_RAD
O=Path(__file__).resolve().parent
inst=setup_instrument(); rows=[]; psfrows=[]; residuals=[]; interpolation=[]
for ori,z in [('O1',.1),('O1',.3),('O1',.6),('O1',1.),('O4',.3)]:
 cache=np.load(O/'input_cache'/f'{ori}_structured_broadbands.npz'); truths,_=make_truths(cache)
 for mode in ['seeing','glao']:
  for ti,(truth,cube) in enumerate(truths.items()):
   rate,fw,scale=project_scene(cube,cache['wave_um'],z,inst,mode)
   pos=aperture_catalog(rate.shape,scale['kpc_per_arcsec'])
   f,e,clean,_,_=observe_apertures(rate,fw,inst,1.,np.random.default_rng(7000+int(z*100)*100+ti),pos)
   keep=(f[:,1]/e[:,1]>5)&(f[:,-1]/e[:,-1]>5)
   for prior in ['near_clear','broad']:
    sh,nsl,nav,npop=screen_shape_grid(z,inst,prior)
    for floor in [.02,.05,.10]:
     var=e[keep]**2+(floor*np.maximum(abs(f[keep]),e[keep]))**2
     fit=fit_screen_models(f[keep],var,sh,nsl,nav,npop)
     rows.append({'orientation':ori,'z':z,'mode':mode,'truth':truth,'prior':prior,'model_discrepancy_fraction':floor,'experiment':'model_discrepancy','Av_grid_points':31,**fit})
     if z==.3 and floor==.05 and truth in ['mixed_SKIRT','uniform_control']:
      ll,chi,amp=amplitude_marginal_likelihood(f[keep],var,sh)
      ll=ll.reshape(len(amp),nsl,nav,npop); amps=amp.reshape(ll.shape)
      lpop=logsumexp(ll,axis=3); global_log=lpop.sum(axis=0); wg=np.exp(global_log-logsumexp(global_log))
      wp=np.exp(ll-lpop[:,:,:,None])
      weights=wp*wg[None,:,:,None]
      # Conditional amplitudes are positive and far from the prior bounds in these retained high-SNR apertures.
      predicted=np.einsum('csap,csap,sapb->cb',weights,amps,sh.reshape(nsl,nav,npop,8),optimize=True)
      for k,(yx,obs,err,model) in enumerate(zip(pos[keep],f[keep],np.sqrt(var),predicted)):
       for bi,b in enumerate(inst): residuals.append({'orientation':ori,'z':z,'mode':mode,'truth':truth,'prior':prior,'aperture':k,'x_kpc':(yx[1]-rate.shape[2]/2)*.1*scale['kpc_per_arcsec'],'y_kpc':(yx[0]-rate.shape[1]/2)*.1*scale['kpc_per_arcsec'],'band':b['band'],'observed_ujy':obs[bi],'sigma_with_model_discrepancy_ujy':err[bi],'uniform_posterior_mean_ujy':model[bi],'residual_sigma':(obs[bi]-model[bi])/err[bi]})
    if ori=='O1' and z==.6:
     sh2,ns2,na2,np2=screen_shape_grid(z,inst,prior,nav=61)
     var=e[keep]**2+(.05*np.maximum(abs(f[keep]),e[keep]))**2
     rows.append({'orientation':ori,'z':z,'mode':mode,'truth':truth,'prior':prior,'model_discrepancy_fraction':.05,'experiment':'Av_grid','Av_grid_points':61,**fit_screen_models(f[keep],var,sh2,ns2,na2,np2)})
   if ori=='O1' and z in [.3,.6] and truth=='mixed_SKIRT':
    alt,_,_=project_scene(cube,cache['wave_um'],z,inst,mode,coordinate='linear')
    altf,alte,_,_,_=observe_apertures(alt,fw,inst,1.,np.random.default_rng(7000+int(z*100)*100+ti),pos)
    for prior in ['near_clear','broad']:
     sh,nsl,nav,npop=screen_shape_grid(z,inst,prior)
     va=alte[keep]**2+(.05*np.maximum(abs(altf[keep]),alte[keep]))**2
     rows.append({'orientation':ori,'z':z,'mode':mode,'truth':truth,'prior':prior,'model_discrepancy_fraction':.05,'experiment':'linear_lambda_interpolation','Av_grid_points':31,**fit_screen_models(altf[keep],va,sh,nsl,nav,npop)})
    interpolation.append({'orientation':ori,'z':z,'mode':mode,'median_photometry_relative_change':float(np.median(abs((altf[keep]-f[keep])/f[keep]))),'max_photometry_relative_change':float(np.max(abs((altf[keep]-f[keep])/f[keep])))})
 print('Robustness',ori,z,'complete',flush=True)
# Native-NIR known-population separation vs PSF family. Does NOT infer dust from observed data.
for z in [.1,.3,.6,1.]:
 cache=np.load(O/'input_cache/O1_structured_broadbands.npz'); truths,_=make_truths(cache)
 for mode,kind in [('seeing','gaussian'),('glao','gaussian'),('optimistic','gaussian'),('seeing','moffat'),('glao','moffat')]:
  r,fw,sc=project_scene(truths['mixed_SKIRT'],cache['wave_um'],z,inst,mode,psf_kind=kind)
  u,_,_=project_scene(truths['uniform_control'],cache['wave_um'],z,inst,mode,psf_kind=kind)
  yy,xx=np.indices(r.shape[1:]); mask=np.hypot(yy-r.shape[1]/2,xx-r.shape[2]/2)*.1*sc['kpc_per_arcsec']<20
  d2=0
  for j,b in enumerate(inst[4:],4):
   var=(r[j]+b['background_e_s_pixel']+b['dark_e_s'])*3600+60*b['read_noise_e']**2
   a=u[j][mask]; v=r[j][mask]; w=3600**2/var[mask]; amplitude=np.sum(a*v*w)/np.sum(a*a*w)
   d2+=np.sum((v-amplitude*a)**2*w)
  psfrows.append({'z':z,'mode':mode,'PSF':kind,'hours':1.,'oracle_NIR_separation_snr':np.sqrt(d2),'Ks_D50_or_Gaussian_FWHM_arcsec':fw[-1],'flux_relative_error':sc['max_flux_relative_error']})
 print('PSF robustness',z,'complete',flush=True)
pd.DataFrame(rows).to_csv(O/'robustness_results.csv',index=False)
pd.DataFrame(psfrows).to_csv(O/'psf_robustness_oracle.csv',index=False)
pd.DataFrame(residuals).to_csv(O/'observable_uniform_screen_residuals.csv',index=False)
pd.DataFrame(interpolation).to_csv(O/'spectral_interpolation_sensitivity.csv',index=False)
