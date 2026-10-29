"""Deterministic spatial transfer, paired morphology bias, and control incidence."""
import pilot as p
import numpy as np,pandas as pd
from scipy import stats,signal

def run():
 tr=pd.read_csv(p.O/'transfer_validation.csv');conditions=tr[['view','z','mode','hours','kind']].drop_duplicates();rows=[];base=[]
 # Transfer is independent of exposure duration; evaluate once at each PSF/distance/view.
 for view,z,mode,kind in conditions[['view','z','mode','kind']].drop_duplicates().itertuples(index=False,name=None):
  clear,dusty,dust=p.load(view);g=p.make_geometry(z,mode,kind);cc,_=p.render(clear,g);dd,_=p.render(dusty,g);intrc,_=p.render(clear,g,False);intrd,_=p.render(dusty,g,False)
  valid=g['roi']&(intrc>1e-4*intrc.max(axis=(1,2))[:,None,None]).all(axis=0)
  # Surface density after area-overlap averaging, NOT inferred from attenuation.
  mass=p.overlap_flux(np.pad(dust,80),g['edges'],g['outedges'])[g['sl'],g['sl']]*(g['native']/g['pixel'])**2
  for method in (p.METHODS if kind=='gaussian' else ['Ks_native']):
   for size in p.SCALES:
    zero=dict(g);zero['widths']=np.array([.8]*3) if method=='g_Ks_matched' else np.array([.7]*3)
    dc=p.truth_maps(dd,g,method,size)-p.truth_maps(cc,g,method,size);di=p.truth_maps(intrd,zero,method,size)-p.truth_maps(intrc,zero,method,size)
    amp=.03 if method=='Ks_native' else .05;truth=valid&(di>amp);limited=valid&(dc>amp)
    rms0=np.sqrt(np.mean(di[valid]**2));rms=np.sqrt(np.mean(dc[valid]**2));corr=np.corrcoef(dc[valid],di[valid])[0,1]
    plan=p.FilterPlan(g,method,size);plan.prepare(p.variance(dd,1.));_,sigma,_,_=plan.measure(dd,g['roi'])
    smoothmass=signal.fftconvolve(mass,p.gaussian_kernel(size/(g['pixel']*g['scale'])/2.35482),mode='same');broadmass=signal.fftconvolve(mass,p.gaussian_kernel(3*size/(g['pixel']*g['scale'])/2.35482),mode='same')
    rho=stats.spearmanr(di[valid],(smoothmass-broadmass)[valid]).statistic
    rows.append(dict(view=view,z=z,mode=mode,kind=kind,method=method,scale_kpc=size,physical_PSFD50_kpc=plan.target*g['scale'],combined_fwhm_kpc=np.hypot(plan.target*g['scale'],size),intrinsic_dust_structure_RMS=rms0,observed_dust_structure_RMS=rms,RMS_retention=rms/rms0,truth_spatial_correlation=corr,truth_above_amplitude_area_kpc2=truth.sum()*(g['pixel']*g['scale'])**2,PSF_limited_above_amplitude_area_kpc2=limited.sum()*(g['pixel']*g['scale'])**2,PSF_limited_area_completeness=(limited&truth).sum()/truth.sum() if truth.sum() else np.nan,median_local_imprint_SNR_known_counterpart_1h=float(np.median(abs(dc[valid])/sigma[valid])),rho_structure_projected_dust=rho))
  # Physical attenuation relation is a separate diagnostic from structure attribution.
  for j,b in enumerate(p.BANDS):
   eff=-p.AMAG*np.log(np.maximum(intrd[j],1e-40)/np.maximum(intrc[j],1e-40));base.append(dict(view=view,z=z,mode=mode,kind=kind,band=b,rho_Aeff_projected_dust=stats.spearmanr(eff[valid],mass[valid]).statistic,negative_Aeff_fraction=np.mean(eff[valid]<0)))
 pd.DataFrame(rows).to_csv(p.O/'scale_transfer.csv',index=False);pd.DataFrame(base).to_csv(p.O/'projected_dust_checks.csv',index=False)
 m=pd.read_csv(p.O/'morphology_draws.csv');keys=['view','z','mode','hours','kind','draw','band'];metrics=['C','A','R50','axis_ratio'];piv=m.pivot(index=keys,columns='scene',values=metrics)
 diff=pd.DataFrame({x:piv[x]['SKIRT']-piv[x]['clear'] for x in metrics}).reset_index();diff.to_csv(p.O/'dust_morphology_paired_draws.csv',index=False)
 p.summarize(diff[diff.draw>=0],[x for x in keys if x!='draw'],metrics).to_csv(p.O/'dust_morphology_bias_summary.csv',index=False)
 # Measurement-minus-noiseless bias, separate from causal dusty-minus-clear changes.
 noisebias=m[m.draw>=0].copy()
 for x in metrics:noisebias[x]=noisebias[x]-noisebias[f'noiseless_{x}']
 p.summarize(noisebias,['view','z','mode','hours','kind','scene','band'],metrics).to_csv(p.O/'morphology_noise_bias.csv',index=False)
 # Total observational morphology bias relative to the same sampled image
 # without an observational PSF. Truth enters scoring only.
 identity=['view','z','mode','hours','kind','scene','band']
 intrinsic=m[m.draw==-1][identity+metrics].rename(columns={x:x+'_intrinsic' for x in metrics})
 totalbias=m[m.draw>=0].merge(intrinsic,on=identity,validate='many_to_one')
 for x in metrics:totalbias[x]=totalbias[x]-totalbias[x+'_intrinsic']
 p.summarize(totalbias,identity,metrics).to_csv(p.O/'PSF_morphology_bias_summary.csv',index=False)
 f=pd.read_csv(p.O/'feature_draws.csv');incs=[]
 for keys,g in f[f.scene!='SKIRT'].groupby(['view','z','mode','hours','kind','scene','method','scale_kpc']):
  n=len(g);k=int(g.any_component.sum());lo=0 if k==0 else stats.beta.ppf(.025,k,n-k+1);hi=1 if k==n else stats.beta.ppf(.975,k+1,n-k)
  incs.append(dict(zip(['view','z','mode','hours','kind','scene','method','scale_kpc'],keys),n=n,draws_with_structure=k,incidence=k/n,ci_low=lo,ci_high=hi))
 pd.DataFrame(incs).to_csv(p.O/'control_structure_incidence.csv',index=False)
 components=[]
 for keys,g in f.groupby(['view','z','mode','hours','kind','scene','method','scale_kpc']):
  n=len(g);k=int(g.any_component.sum());lo=0 if k==0 else stats.beta.ppf(.025,k,n-k+1);hi=1 if k==n else stats.beta.ppf(.975,k+1,n-k)
  components.append(dict(zip(['view','z','mode','hours','kind','scene','method','scale_kpc'],keys),n=n,draws_with_scale_sized_component=k,incidence=k/n,ci_low=lo,ci_high=hi))
 pd.DataFrame(components).to_csv(p.O/'component_incidence.csv',index=False)
 # Explicit detectable-scale decision is conditional on BOTH area recovery and purity.
 s=pd.read_csv(p.O/'feature_summary.csv');d=s[s.scene=='SKIRT'].copy();d['passes_50percent_completeness_and_contamination']= (d.completeness>=.5)&(d.contamination<=.5);d.to_csv(p.O/'conditional_scale_recoverability.csv',index=False)
if __name__=='__main__':run()
