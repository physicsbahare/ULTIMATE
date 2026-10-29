"""Independent calibration and numerical checks, not threshold tuning."""
import pilot as p
import numpy as np,pandas as pd,json
from scipy import signal,stats

def run():
 g=p.make_geometry(.1,'glao');clear,dusty,dust=p.load('O1');rates,loss=p.render(clear,g);var=p.variance(rates,1.)
 # Constant multiplicative band scaling cancels local normalized structures.
 checks=[]
 for method in p.METHODS:
  plan=p.FilterPlan(g,method,1.);plan.prepare(var)
  val,_,mask,_=plan.measure(rates,g['roi']);scaled=rates*np.array([.7,.9,.95])[:,None,None]
  v2,_,_,_=plan.measure(scaled,g['roi']);err=np.max(abs(val[mask]-v2[mask]));assert err<1e-10
  checks.append(dict(test='uniform_screen_structure_invariance',method=method,max_error=err))
 # Finite-difference scalar derivatives and full smoothing covariance calibration.
 rng=np.random.default_rng(p.CAL_SEED);rows=[]
 # 40 independent calibration observations of the same fixed clear scene.
 for method in p.METHODS:
  plan=p.FilterPlan(g,method,1.);plan.prepare(var);base,sigma,mask,_=plan.measure(rates,g['roi'])
  deviations=[];exactdev=[];roi=mask&(g['r']<10)
  for draw in range(40):
   obs=rates+np.sqrt(var)*rng.standard_normal(rates.shape);v,s,sel,_=plan.measure(obs,g['roi']);deviations.append((v-base)[roi]/sigma[roi])
   exact=[]
   for r,b in zip(rates,p.INST):
    t=3600.;back=b['background_e_s_pixel']+b['dark_e_s'];exact.append((rng.poisson((r+back)*t)+rng.normal(0,np.sqrt(60)*b['read_noise_e'],r.shape)-back*t)/t)
   ve,_,_,_=plan.measure(np.array(exact),g['roi']);exactdev.append((ve-base)[roi]/sigma[roi])
  for name,d in [('Gaussian_moments',deviations),('exact_aggregate_Poisson_read',exactdev)]:
   d=np.array(d);ratio=np.mean(np.var(d,axis=0,ddof=1));bias=np.mean(d);rows.append(dict(method=method,noise=name,n_independent_draws=40,mean_standardized_residual=bias,empirical_to_propagated_variance=ratio));assert .8<ratio<1.2
 # Split exposure variance accounting, including the factor N on read variance.
 for hours in [.25,1.,4.]:
  t=hours*3600;n=int(t/60);b=p.INST[-1];manual=((rates[-1]+b['background_e_s_pixel']+b['dark_e_s'])*t+n*b['read_noise_e']**2)/t**2
  assert np.allclose(p.variance(rates,hours)[-1],manual)
 # Circular image has zero noiseless asymmetry and uniform dimming invariant morphology.
 im=np.exp(-g['r']/3);m=p.morph(im,np.zeros_like(im),g);mm=p.morph(.1*im,np.zeros_like(im),g);assert abs(m['A'])<1e-12 and abs(m['C']-mm['C'])<1e-12
 # Flux-conserving area overlap separately from PSF/crop losses.
 source=np.zeros((400,400));source[180:220,180:220]=1;scene=np.stack([source]*3);r,_=p.render(scene,g,False)
 expected=source.sum()/(1.1**3)*1e6*(g['native']/p.ARCSEC_PER_RAD)**2*p.INST[0]['flat_e_s_per_jy'];assert abs(r[0].sum()/expected-1)<1e-12
 pd.DataFrame(rows).to_csv(p.O/'noise_covariance_validation.csv',index=False)
 (p.O/'numerical_validation.json').write_text(json.dumps(dict(checks=checks,noise_covariance_calibration_passed=True,split_read_variance_passed=True,area_overlap_flux_conservation_passed=True,morphology_uniform_scaling_passed=True,PSF_padded_flux_loss=loss,calibration_seed=p.CAL_SEED,evaluation_seed=p.EVAL_SEED),indent=2));print(pd.DataFrame(rows).to_string(index=False),flush=True)
def psf_check():
 rows=[]
 for z in [.05,.1]:
  for mode in ['seeing','glao']:
   g=p.make_geometry(z,mode);source=np.zeros((3,400,400));source[:,199:201,199:201]=.25;rate,_=p.render(source,g)
   for method in p.METHODS:
    plan=p.FilterPlan(g,method,1.)
    for i in plan.indices:
     match=np.sqrt(max(0,plan.target**2-g['widths'][i]**2));im=signal.fftconvolve(rate[i],p.gaussian_kernel(match/g['pixel']/2.354820045),mode='same');total=im.sum();xs=g['x']/g['scale'];ys=g['y']/g['scale'];mx=(im*xs).sum()/total;my=(im*ys).sum()/total;sig=np.sqrt((im*((xs-mx)**2+(ys-my)**2)).sum()/total/2)
     rows.append(dict(z=z,mode=mode,method=method,band=p.BANDS[i],nominal_Gaussian_FWHM_arcsec=plan.target,measured_second_moment_equivalent_FWHM=2.354820045*sig,point_source='two-by-two central source pixels; finite100pc source sampling included'))
 d=pd.DataFrame(rows);d.to_csv(p.O/'PSF_matching_validation.csv',index=False)
 for _,g in d[d.method!='Ks_native'].groupby(['z','mode','method']):assert np.ptp(g.measured_second_moment_equivalent_FWHM)/g.measured_second_moment_equivalent_FWHM.mean()<.002
 return d
if __name__=='__main__':run();psf_check()
