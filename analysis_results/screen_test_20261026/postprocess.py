from pathlib import Path
import json,sys,importlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
O=Path(__file__).resolve().parent; F=O/'figures'; F.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':11,'axes.titlesize':12,'pdf.fonttype':42,'ps.fonttype':42,'savefig.dpi':300})
COL={'mixed_SKIRT':'#2166ac','uniform_control':'#555555','variable_control':'#b35806'}
LABEL={'mixed_SKIRT':'Mixed SKIRT','uniform_control':'Uniform-screen control','variable_control':'Variable-screen control'}
def save(fig,stem):
 for ext in ['png','pdf']:fig.savefig(F/f'{stem}.{ext}',bbox_inches='tight')
 plt.close(fig)
def mtable(df):
 return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in r)+' |' for r in df.itertuples(index=False,name=None))
x=pd.read_csv(O/'screen_model_results.csv'); good=x[x.status=='fit'].copy()
med=good.groupby(['orientation','z','hours','mode','truth','population_prior'],as_index=False).agg(logB_median=('log_B_variable_uniform','median'),logB_min=('log_B_variable_uniform','min'),logB_max=('log_B_variable_uniform','max'),n_apertures_median=('n_apertures','median'),colour_chi2_median=('constant_colour_chi2','median'),colour_dof_median=('constant_colour_dof','median'),oracle_snr=('oracle_NIR_separation_snr','median'))
med.to_csv(O/'screen_model_summary.csv',index=False)
rob=pd.read_csv(O/'robustness_results.csv'); psf=pd.read_csv(O/'psf_robustness_oracle.csv'); inst=pd.read_csv(O/'instrument_parameters.csv')
# 1: conditional evidence, INCLUDING physical null controls.
fig,axes=plt.subplots(3,4,figsize=(16,10),layout='constrained')
for i,truth in enumerate(LABEL):
 for j,(prior,mode) in enumerate([(p,m) for p in ['near_clear','broad'] for m in ['seeing','glao']]):
  q=med[(med.orientation=='O1')&(med.truth==truth)&(med.population_prior==prior)&(med['mode']==mode)]
  a=q.pivot(index='hours',columns='z',values='logB_median').reindex(index=[.25,1.,4.],columns=[.1,.3,.6,1.])
  im=axes[i,j].imshow(a,origin='lower',aspect='auto',cmap='RdBu_r',norm=TwoSlopeNorm(0,vmin=-35,vmax=35))
  for yy in range(3):
   for xx in range(4): axes[i,j].text(xx,yy,f'{a.iloc[yy,xx]:.1f}',ha='center',va='center',fontsize=10,color='white' if abs(a.iloc[yy,xx])>20 else 'black')
  axes[i,j].set_xticks(range(4),['0.1','0.3','0.6','1.0']); axes[i,j].set_yticks(range(3),['0.25','1','4'])
  axes[i,j].set(title=f'{prior.replace("_"," ")} | {mode}',xlabel='Artificial redshift',ylabel=f'{LABEL[truth]}\nHours per band')
fig.colorbar(im,ax=axes,label='ln evidence ratio: varying / uniform extra screen',shrink=.7)
fig.suptitle('Conditional screen-model comparison | O1 | medians of 3 noise draws\nPositive values in UNIFORM controls diagnose false physical rejection; not a geometry detection',fontsize=14)
save(fig,'screen_evidence_with_null_controls')
# 2: population/model-discrepancy robustness, same noise draws.
fig,axes=plt.subplots(1,3,figsize=(14,4.8),layout='constrained')
for ax,z in zip(axes,[.1,.3,.6]):
 for truth in LABEL:
  q=rob[(rob.orientation=='O1')&(rob.z==z)&(rob['mode']=='glao')&(rob.prior=='broad')&(rob.truth==truth)&(rob.experiment=='model_discrepancy')].sort_values('model_discrepancy_fraction')
  ax.plot(q.model_discrepancy_fraction*100,q.log_B_variable_uniform,marker='o',color=COL[truth],label=LABEL[truth])
 ax.axhline(0,color='black',lw=.7);ax.set(title=f'z = {z} | GLAO | 1 h',xlabel='Model-discrepancy prior (%)',ylabel='ln evidence ratio (varying / uniform)'); ax.grid(alpha=.2)
axes[0].legend(fontsize=8)
fig.suptitle('Model preference changes with assumed stellar/SED discrepancy | broad population prior\nThese percentages are inference assumptions, not measured calibration errors',fontsize=13)
save(fig,'model_discrepancy_robustness')
# 3: native expected/noisy morphology at same stretch; no dust-free fitting.
fig,axes=plt.subplots(2,3,figsize=(12,8),layout='constrained')
highs={}
for band in ['g','Y','Ks']:
 vals=[]
 for viewmode in ['seeing','glao']:
  ex=np.load(O/'examples'/f'mixed_SKIRT_{viewmode}.npz')
  vals.append(ex['rate'][['g','r','i','z','Y','J','H','Ks'].index(band)]*1e6/inst.set_index('band').loc[band,'flat_e_s_per_jy'])
 highs[band]=max(np.percentile(v,99.5) for v in vals)
for i,mode in enumerate(['seeing','glao']):
 e=np.load(O/'examples'/f'mixed_SKIRT_{mode}.npz'); kpc=float(e['kpc_per_arcsec']); n=e['rate'].shape[-1]; half=int(20/(.1*kpc)); mid=n//2;sl=np.s_[mid-half:mid+half,mid-half:mid+half]
 for j,b in enumerate(['g','Y','Ks']):
  arr=e[f'image_{b}_ujy'][sl]; clean=e['rate'][['g','r','i','z','Y','J','H','Ks'].index(b)][sl]*1e6/inst.set_index('band').loc[b,'flat_e_s_per_jy']
  high=highs[b]; s=high/8; im=axes[i,j].imshow(np.arcsinh(arr/s),origin='lower',extent=(-20,20,-20,20),cmap='gray',vmin=0,vmax=np.arcsinh(high/s))
  axes[i,j].set(title=f'{b} | {mode}',xlabel='x (kpc)',ylabel='y (kpc)')
fig.suptitle('Static O1 at z=0.3 | 1 h per band | instrument-informed synthetic noise\nNative per-band PSFs; separate stretch by band; no intrinsic size/luminosity evolution',fontsize=13)
save(fig,'synthetic_observed_images')
# 4: observable colour structure and model residuals (same band-matched PSF).
r=pd.read_csv(O/'observable_uniform_screen_residuals.csv')
fig,axes=plt.subplots(2,3,figsize=(12,8),layout='constrained')
for i,truth in enumerate(['mixed_SKIRT','uniform_control']):
 for j,prior in enumerate(['near_clear','broad']):
  rr=r[(r.orientation=='O1')&(r['mode']=='glao')&(r.truth==truth)&(r.prior==prior)]
  wide=rr.pivot(index=['aperture','x_kpc','y_kpc'],columns='band',values=['observed_ujy','uniform_posterior_mean_ujy'])
  xy=wide.index.to_frame(index=False)
  col=-2.5*np.log10(wide['observed_ujy']['r']/wide['observed_ujy']['Ks'])
  model=-2.5*np.log10(wide['uniform_posterior_mean_ujy']['r']/wide['uniform_posterior_mean_ujy']['Ks'])
  if j==0:
   im=axes[i,0].scatter(xy.x_kpc,xy.y_kpc,c=col,cmap='viridis',vmin=0,vmax=3,marker='s',s=300)
   fig.colorbar(im,ax=axes[i,0],label='Observed r − Ks (AB mag)',shrink=.7)
  im=axes[i,j+1].scatter(xy.x_kpc,xy.y_kpc,c=col-model,cmap='RdBu_r',vmin=-.3,vmax=.3,marker='s',s=300)
  fig.colorbar(im,ax=axes[i,j+1],label='Colour residual (mag)',shrink=.7,extend='both')
 for j,ax in enumerate(axes[i]): ax.set(xlim=(-20,20),ylim=(-20,20),aspect='equal',xlabel='x (kpc)',ylabel='y (kpc)',title=LABEL[truth]+'\n'+['Observed colour','Uniform fit: near-clear prior','Uniform fit: broad prior'][j])
fig.suptitle('Observable colours and uniform-screen posterior-mean residuals | z=0.3 | GLAO | 1 h\n0.8-arcsec common Gaussian PSF; sparse, separated apertures; residuals are not dust-geometry maps',fontsize=13)
save(fig,'observable_colour_and_screen_residuals')
# 5: known-population upper-bound GLAO gains, not measured observational discrimination.
fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
for kind,ls in [('gaussian','-'),('moffat','--')]:
 q=psf[psf.PSF==kind]
 for mode,col in [('seeing','#666666'),('glao','#2166ac')]:
  a=q[q['mode']==mode];axes[0].plot(a.z,a.oracle_NIR_separation_snr,ls=ls,marker='o',color=col,label=f'{mode}, {kind}')
 w=q.pivot(index='z',columns='mode',values='oracle_NIR_separation_snr');axes[1].plot(w.index,w.glao/w.seeing,ls=ls,marker='o',label=kind)
q=psf[(psf.PSF=='gaussian')&(psf['mode']=='optimistic')];axes[0].plot(q.z,q.oracle_NIR_separation_snr,':^',color='#b35806',label='optimistic 0.2 arcsec')
axes[0].set(yscale='log',xlabel='Artificial redshift',ylabel='Known-population separation / noise',title='NIR mixed versus matched-g uniform control')
axes[1].axhline(1,color='gray',lw=.7);axes[1].set(xlabel='Artificial redshift',ylabel='GLAO / seeing separation ratio',title='PSF-dependent conditional gain')
for ax in axes:ax.legend(fontsize=9);ax.grid(alpha=.2)
fig.suptitle('Oracle sensitivity bound ONLY | intrinsic populations held known | 1 h\nAmplitude optimized separately in each NIR band; does not marginalize population/geometry uncertainty',fontsize=13)
save(fig,'glao_oracle_upper_bound')
# 6: reconstructed design noise and corrected limits.
lims=pd.read_csv(O/'corrected_point_source_sensitivity.csv')
fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
nir=inst.iloc[4:]; inds=np.arange(4); sky=nir.sky_e_s_arcsec2.to_numpy(); therm=nir.thermal_e_s_arcsec2.to_numpy(); moon=nir.moon_e_s_arcsec2.to_numpy()
axes[0].bar(inds,sky,label='Sky');axes[0].bar(inds,therm,bottom=sky,label='Telescope thermal');axes[0].bar(inds,moon,bottom=sky+therm,label='Bundled moon')
axes[0].set_xticks(inds,nir.band);axes[0].set(ylabel='Electrons s⁻¹ arcsec⁻²',title='Corrected calculator background rates');axes[0].legend(fontsize=9)
for mode,marker in [('seeing','s'),('glao','o')]:
 q=lims[(lims['mode']==mode)&(lims.hours==1)];axes[1].plot(q.band,q.limit_AB_5sigma_50pct_aperture,marker=marker,label=mode)
axes[1].set(ylabel='5σ point-source AB limit',title='1 h: 60 independent reads + source Poisson');axes[1].legend();axes[1].grid(alpha=.2)
fig.suptitle('Instrument-informed design scenario | provisional operational parameters\nTop-hat passbands; source e− conversion and exposure splitting audited',fontsize=13)
save(fig,'instrument_noise_audit')
# Summary tables for the narrative.
chosen=med[(med.orientation=='O1')&(med.hours==1)&(med['mode']=='glao')&(med.truth.isin(['mixed_SKIRT','uniform_control']))][['z','truth','population_prior','logB_median','n_apertures_median']].copy()
chosen=chosen.round(3); chosen.to_csv(O/'workshop_evidence_table.csv',index=False)
ratio=psf[psf.PSF=='gaussian'].pivot(index='z',columns='mode',values='oracle_NIR_separation_snr'); ratio['GLAO_gain_percent']=(ratio.glao/ratio.seeing-1)*100;ratio.to_csv(O/'glao_oracle_gain.csv')
prov={'experiment':'static observational transfer of fixed TNG50 SKIRT DR1 subhalo 294866','date':'2026-10-26','environment':sys.executable,'intrinsic_size_evolution':False,'intrinsic_luminosity_evolution':False,'stellar_population_evolution':False,'dust_distribution_evolution':False,'cosmology':{'H0_km_s_Mpc':70.,'Om0':.3,'Tcmb0_K':2.725},'redshifts_O1':[.1,.3,.6,1.],'other_views_redshift':.3,'exposure_hours_per_band':[.25,1.,4.],'DIT_seconds':60,'draws_per_case':3,'image_pixel_arcsec':.1,'native_pixel_pc':100,'input_crop_kpc':80,'analysis_radius_kpc':18,'oracle_radius_kpc':20,'aperture_square_arcsec':.5,'aperture_lattice_spacing_arcsec':2.,'all_band_matched_PSF_arcsec':.8,'source_sed_reconstruction':'linear Fnu versus log emitted wavelength between approximate broadband pivots; no extrapolation','screen_law':'A_lambda=Av*(lambda_rest/0.55um)^(-slope)','slope_prior':[.7,1.,1.3],'Av_prior':'31 uniformly weighted points from 0 to 3 mag; 61-point robustness','amplitude_prior':'uniform positive 0 to 1e6 microJy at emitted 1um normalization; analytically marginalized','population_priors':{'near_clear':'FSPS templates whose supplied effective Av<0.15, pair mixtures and continuum tilts ±0.15','broad':'all 12 FSPS templates, 48 fixed pair mixtures and same tilts; includes template reddening as conservative degeneracy allowance'},'discrepancy_fraction':.05,'discrepancy_robustness':[.02,.05,.1],'aperture_selection':'observed r and Ks SNR>5; include other nondetections in linear-flux likelihood','selection_likelihood_limit':'no truncation conditioning; marginal z=1 results not calibrated','PSF_provenance':'calculator median D50 mapped to Gaussian FWHM; optimistic 0.2arcsec and beta2.5 Moffat alternatives explicitly assumed','noise':'sum of independent Poisson source+sky+thermal+moon+dark counts plus N independent Gaussian reads; mean sky known; no real-background injection','inference_inputs':'observed aperture flux/errors, observer filters, external SED templates and priors only','not_established':['a unique 3D geometry','robust physical uniform-screen rejection','a finalized ULTIMATE sensitivity forecast','an exact DR2 endpoint','exact K corrections from spectral cubes']}
prov['versions']={name:importlib.import_module(name).__version__ for name in ['numpy','scipy','astropy','matplotlib','pandas','nbformat','nbclient']}
(O/'parameter_provenance.json').write_text(json.dumps(prov,indent=2))
print('Saved six paired figures and summaries.')
