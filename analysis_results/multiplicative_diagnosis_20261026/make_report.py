"""Figures and scientific decision from executed targeted tests."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/ultimate-mpl')
from pathlib import Path
import numpy as np,pandas as pd,json
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import physical_model as p
O=p.O
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})

def table(df):
 return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in r)+' |' for r in df.itertuples(index=False,name=None))

def figures():
 (O/'figures').mkdir(exist_ok=True);paths=[]
 def save(fig,name):
  for ext in ['png','pdf']:fig.savefig(O/f'figures/{name}.{ext}',dpi=220,bbox_inches='tight')
  paths.append(O/f'figures/{name}.png');plt.close(fig)
 d=pd.read_csv(O/'old_method_mechanism.csv');a=d[(d.strategy=='matched')&(d['mode']=='seeing')];fig,ax=plt.subplots(1,2,figsize=(11,4.5),layout='constrained');ax[0].bar(np.arange(4),a.noise_free_statistic,color=['#c65b21','#3776ab','#3776ab','#3776ab']);ax[0].axhline(a.threshold.iloc[0],ls='--',color='black',label='Previous calibrated cutoff');ax[0].set(xticks=np.arange(4),xticklabels=['Original prior','Population\nSD ×2','Explicit mode\n(diagnostic)','Short-correlation\nlimit'],ylabel='Old Gaussian score (2 log ratio)',title='Same noise-free stellar-only scene');ax[0].legend(fontsize=8)
 xx=np.linspace(30,330,400);ax[1].plot(xx,stats.chi2.pdf(xx,98),color='#3776ab',label='Gaussian prior-predictive reference');ax[1].axvline(a.iloc[0].prior_predictive_q_null,color='#c65b21',label='Original null, Q=286');ax[1].axvline(a.iloc[1].prior_predictive_q_null,color='gray',ls='--',label='Population SD ×2');ax[1].set(xlabel='Prior-whitened quadratic Q',ylabel='Density',title='The assumed population distribution is too restrictive');ax[1].legend(fontsize=8);fig.suptitle('Catastrophic false positive: prior / covariance misspecification, not a noise-covariance algebra error');save(fig,'01_false_positive_mechanism')
 z=np.load(O/'old_failure_components.npz');h=p.e.contrasts(15);g=p.e.geometry(.3,'seeing','matched');fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained');im=axes[0].imshow(z['pattern'],origin='lower',extent=[-20,20,-20,20],cmap='RdBu_r',vmin=-1,vmax=1);axes[0].set(xlim=(0,13),ylim=(-9,9),title='Imposed stellar-population field',xlabel='x [kpc]',ylabel='y [kpc]');fig.colorbar(im,ax=axes[0],shrink=.8)
 assigned=h.T@z['matched_seeing_dust'][:14];im=axes[1].scatter(g['coords'][:,0],g['coords'][:,1],c=assigned,cmap='RdBu_r',s=120,marker='s');axes[1].set(title='g flux contrast assigned to dust\nby the old model',xlabel='x [kpc]',ylabel='y [kpc]');fig.colorbar(im,ax=axes[1],shrink=.8,label='Normalized flux contrast')
 proj=pd.read_csv(O/'population_transform_projection.csv');b=proj[proj.n_PC==2];axes[2].bar(np.arange(3),100*b.residual_relative_norm,color='#6b3c89');axes[2].set(xticks=np.arange(3),xticklabels=['Log shift','Fractional\nmultiplier','SED-weighted\nmultiplier'],ylabel='Norm outside original two PCs [%]',title='Multiplication transforms the population direction');fig.suptitle('Spectral direction is represented; flux weighting creates small but significant extra components');save(fig,'02_population_field_and_spurious_dust')
 dev=pd.read_csv(O/'development_gate.csv');dev=dev[(dev.noise=='one_noise')&(dev.variable==False)];fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained');labels=['Uniform DR1','Known anchor','Model family']
 for kind,color,off in [('absolute','#c65b21',-.15),('contrasts','#3776ab',.15)]:
  vals=[];pp=[];xs=[]
  for i,name in enumerate(['DR1_uniform','problem_anchor','model_family_uniform']):
   r=dev[(dev.scene==name)&(dev.likelihood==kind)]
   if len(r):xs.append(i+off);vals.append(r.iloc[0].chi2);pp.append(r.iloc[0].ppp)
  axes[0].bar(xs,vals,width=.28,color=color,label=kind);axes[1].scatter(xs,pp,color=color,label=kind,s=70)
 for ax in axes:ax.set(xticks=np.arange(3),xticklabels=labels)
 axes[0].set(ylabel='Noise-whitened residual χ²',title='Positive uniform-screen fits');axes[0].legend();axes[1].axhline(.01,color='gray',ls=':');axes[1].set(ylabel='Local Laplace posterior-predictive probability',ylim=(-.03,1.03),title='Physical absolute-colour gate failed');save(fig,'03_positive_model_development_gate')
 rates=pd.read_csv(O/'heldout_pilot_rates.csv');norm=rates[rates.likelihood=='contrasts'];fig,axes=plt.subplots(2,2,figsize=(12,7),layout='constrained');pops=['DR1','known_anchor','rotated_PC1_PC3','training_SED_patch'];titles=['DR1 population','Known anchor (benchmark)','New rotated PC1 + PC3','New training-SED patches'];colors={'clear':'#3776ab','uniform':'#65a080','smooth':'#c65b21','patchy':'#6b3c89'}
 for ax,pop,title in zip(axes.ravel(),pops,titles):
  ds=norm[norm.population==pop].set_index('screen').loc[['clear','uniform','smooth','patchy']];ax.errorbar(np.arange(4),ds.rate,yerr=[ds.rate-ds.ci_low,ds.ci_high-ds.rate],fmt='o',capsize=4,color='black');
  for i,(_,r) in enumerate(ds.iterrows()):ax.text(i,min(1.13,r.rate+.11),f'{int(r.rejections)}/{int(r.n)}',ha='center',fontsize=9)
  ax.set(xticks=np.arange(4),xticklabels=['Clear null','Uniform null','Smooth dust','Patchy dust'],ylim=(-.05,1.2),title=title,ylabel='Pilot rejection fraction')
 fig.suptitle('Bounded held-out contrast pilot: 3 draws per scene, 95% exact binomial intervals\nKnown-family diagnostic cutoff; failed physical gate prevents a large validation or calibrated geometry claim',fontsize=11);save(fig,'04_heldout_scenarios_separately')
 nat=pd.read_csv(O/'native_adequacy_sensitivity.csv');nat=nat[(nat.variable==False)&(nat.bin_kpc==1.5)];fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
 for mode,color,off in [('seeing','#3776ab',-.1),('glao','#c65b21',.1)]:
  for field,marker in [('fine','o'),('coarse','s')]:
   ds=nat[(nat['mode']==mode)&(nat.field==field)].set_index('scene').loc[['uniform','anchor']];xs=np.arange(2)+off+(.035 if field=='coarse' else -.035);axes[0].scatter(xs,ds.ppp,s=65,color=color,marker=marker,label=f'{mode}, {field}');bad=~ds.success.to_numpy();axes[0].scatter(xs[bad],ds.ppp.to_numpy()[bad],s=120,color='black',marker='x',linewidths=1.4)
 axes[0].set(xticks=[0,1],xticklabels=['Uniform','Known anchor'],ylabel='Local posterior-predictive probability',title='Native-PSF null fits; × = nonconverged',ylim=(-.04,1.02));axes[0].legend(fontsize=8);axes[0].axhline(.01,ls=':',color='gray')
 info=pd.read_csv(O/'aperture_information_loss.csv');types=['original_15_apertures','pixels_inside_original_apertures','evaluation_rectangle_pixels']
 for mode,color,off in [('seeing','#3776ab',-.1),('glao','#c65b21',.1)]:
  ds=info[info['mode']==mode].set_index('data').loc[types];axes[1].scatter(np.arange(3)+off,ds.squared_mean_separation,s=70,color=color,label=mode)
 axes[1].set(xticks=np.arange(3),xticklabels=['15 summed\napertures','Same apertures,\nretain pixels','Region with\nfull coverage'],yscale='log',ylabel='Squared separation of a fixed positive model pair',title='Aperture compression discards useful structure');fig.suptitle('Adequacy and information checks, not an ULTIMATE performance forecast');save(fig,'05_native_PSF_and_aperture_information')
 fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained');inv=pd.read_csv(O/'absolute_information_invariance.csv').iloc[0];axes[0].bar(['Absolute flux','Normalized contrasts'],[inv.relative_absolute_flux_change_for_same_shift,inv.max_normalized_flux_change_for_uniform_E_shift],color=['#c65b21','#3776ab']);axes[0].set(ylabel='Relative response to the same uniform-E change',title='Normalization removes global attenuation information')
 coverage=pd.read_csv(O/'postfit_stellar_hull_coverage.csv');axes[1].hist(100*coverage.E0_fractional_rms,bins=18,color='#6b3c89',alpha=.8);axes[1].set(xlabel='Clear evaluation SED distance from training mixture hull [% RMS]',ylabel='One-kpc diagnostic regions',title='Evaluation clear SEDs are diagnostic only');fig.suptitle('Absolute colours contain information, but require a transferable population model');save(fig,'06_absolute_colours_and_population_coverage')
 return paths

def report():
 mech=pd.read_csv(O/'old_method_mechanism.csv');dev=pd.read_csv(O/'development_gate.csv');r=pd.read_csv(O/'heldout_pilot_rates.csv');bound=pd.read_csv(O/'conditional_identifiability_bound.csv');info=pd.read_csv(O/'aperture_information_loss.csv');iso=pd.read_csv(O/'absolute_failure_isolation.csv')
 pilot=r[(r.likelihood=='contrasts')].copy();pilot['result']=pilot.apply(lambda x:f'{int(x.rejections)}/{int(x.n)} [{100*x.ci_low:.1f}–{100*x.ci_high:.1f}%]',axis=1);pilot['adequacy']=pilot.apply(lambda x:f'{100*x.adequate_null_fraction:.0f}% / {100*x.adequate_alternative_fraction:.0f}%',axis=1);tab=table(pilot[['population','screen','result','adequacy']].rename(columns={'result':'rejections [95% CI]','adequacy':'null / alternative adequate'}))
 dd=dev[(dev.noise=='one_noise')&(~dev.variable)&(dev.likelihood=='absolute')].set_index('scene');co=dev[(dev.noise=='one_noise')&(~dev.variable)&(dev.likelihood=='contrasts')].set_index('scene');s=bound[bound['mode']=='seeing'].iloc[0];g=bound[bound['mode']=='glao'].iloc[0]
 failures=pd.read_csv(O/'heldout_pilot_per_draw.csv');failed_null=int((~failures.null_success).sum());failed_alt=int((~failures.variable_success).sum())
 text=f'''# Targeted physical-model diagnosis and scientific decision

**NO-GO for a robust broadband dust-geometry claim with the current inference pipeline.** This is not proof that full optical/NIR images are fundamentally incapable of dust discrimination. Both structural model errors and information discarded by the sparse measurements remain important. No full previous grid, large Monte Carlo, download, installation, DR2 work or ML was run.

## 1. Why the98.4% false-positive failure occurred
The exact named z=.3 matched/seeing benchmark reproduces492/500 rejections (98.4%;95% CI96.9–99.3%). Its imposed log-colour direction lies in the original two population PCs to relative precision3e-16, with95% squared overlap with the dust direction. The spatial response has full rank14 for14 contrasts and reconstructs the spatial test mode to4.5e-16. **Neither a missing log-colour PC nor an insufficient number of spatial basis vectors is the dominant failure.**

The old model instead gives the wrong probability/covariance to a brightness-weighted, multiplicative population field. The same noise-free source gives a Gaussian score85.45 above the previous69.59 cutoff. Doubling population SD changes it to-22.39; adding the actual spatial population mode diagnostically changes it to-41.79; a short-correlation covariance limit gives-42.60. Those are mechanism tests, not priors adopted to force controls to pass. Null prior-predictive Q falls from286 for98 contrasts to91 when population SD doubles. Exact photometric covariance propagation agrees with explicit matrix multiplication at~1e-20.

Multiplication adds curvature: the fractional multiplier has0.43% of its norm outside the first two PCs, rising to2.56% after weighting by the actual stellar colours, with maximum residual~3%. The additive Gaussian population covariance is not the correct forward push-forward of these source fields. Dust offers a cheap, strongly aligned colour mode and absorbs the discrepancy. This is **structural statistical-model inadequacy amplified by a real population–dust degeneracy**, not evidence for variable dust.

## 2. One improved positive model, and its limits
Implemented positive luminosity surface brightness × convex mixtures of seven independent training-region DR1 source SEDs × exp[-0.4 ln10 k(lambda) E(x)]. Stellar mixture weights and attenuation are spatial fields; E is bounded0–0.6. Luminosity is nuisance, with no known stellar mass or intrinsic target normalization. The same stellar model is used under uniform and variable attenuation. Band-specific PSFs, source-photon variance,60 split reads and full aperture covariance are preserved. The adjoint projection is validated against the original renderer; analytic derivatives and nesting/positivity pass tests.

Training uses x<-4kpc only. The target clear SEDs and physical maps are never fit inputs; they appear only in counterfactual generation/post-fit coverage diagnostics. These are physically positive *empirical broadband mixtures*, not a full SPS/SFH/age-metallicity inference. Model-family recovery succeeds, but absolute-colour physical nulls fail: χ²={dd.loc['DR1_uniform'].chi2:.1f} for the uniform DR1 source and{dd.loc['problem_anchor'].chi2:.1f} for the known anchor, with local predictive probabilities0. Normalized-contrast null fits instead have χ²={co.loc['DR1_uniform'].chi2:.1f}/{co.loc['problem_anchor'].chi2:.1f} and predictive probabilities{co.loc['DR1_uniform'].ppp:.3f}/{co.loc['problem_anchor'].ppp:.3f}.

Absolute colours retain information: changing uniform E alters raw fluxes by19%, while normalized contrasts change only at~1e-15. Yet using those colours requires a transferable population model. Independent-template coverage, spatial population constraints and source-grid approximations are audited in `absolute_failure_isolation.csv`; a good contrast fit cannot establish that the absolute stellar SED is correct. Grid-only error is not the complete explanation: fitting a source generated exactly on the model grid still gives null residual χ²443/881. A matched-PSF, unrestricted-per-aperture mixture *coverage diagnostic only* also retains large marginal weighted residuals; it is not the adopted inference model. Source Monte Carlo uncertainty and independent SPS/domain-transfer errors are not available as validated error maps; no discrepancy floor was invented to force acceptance. No global-colour or aperture freedom was added after seeing the held-out cases just to make them pass.

## 3. Challenging held-out pilot; no large evaluation after failed gate
The failed raw physical gate prohibited a large independent evaluation or new GLAO power claim. A bounded diagnostic pilot used19 known-family calibration noise draws and independent held-out observations: one absolute-colour and three contrast draws per scene. Each fit has a fixed data-initialized null start and nested alternative start, rather than sequential noise-dependent warm starts. The statistic is **penalized MAP objective improvement**, not a Bayes factor or unpenalized profile χ². A maximum-of19 cutoff is nominal5% only conditional on exchangeable scores for that one model-family null; it does not calibrate physical population robustness. Optimizer failures and predictive adequacy are saved per draw.

New population patterns include a shifted/rotated log-PC1+PC3 gradient and patchy mixtures drawn from the full independent training sample, not just the fitted prototypes. The known anchor is a development benchmark, not relabelled blind validation. Each stellar scene has paired clear, uniform, smooth and patchy screens; original SKIRT is separate. Each scenario remains separate below. Tiny-sample intervals are deliberately wide and **cannot certify an acceptable false-positive rate or reliable power**.

{tab}

Full absolute-colour results, optimizer flags and paired old-Gaussian diagnostics are in the CSV files. Local Laplace posterior checks are approximations; effective-dof χ² tail values are descriptive and not used as calibrated adequacy probabilities. There were{failed_null} nonconverged null fits and{failed_alt} nonconverged alternative fits among{len(failures)} fit pairs. They remain explicitly flagged; raw threshold crossings from those fits are not valid optimized detections. The primary physical gate remains failed, whatever individual pilot rejection counts show.

## 4. GLAO, aperture loss and identifiability
The native-resolution problem is **not resolved by the default fine-field model**. For the known stellar-only anchor, its seeing fit gives χ²62.17 and local predictive probability0.496, but does not converge; the GLAO fit gives χ²154.98 and probability0, and also does not converge. With the same1.5kpc apertures, the coarser population field converges for both seeing and GLAO, with χ²58.77/58.95 and predictive probabilities0.559/0.445. Thus more spatial flexibility did not automatically improve fitting; optimization and population regularization remain material limitations. Coarse/fine fields and3kpc apertures are adequacy sensitivity checks, not a post-hoc selection for claimed power. A classifier losing recovery with narrower PSFs is not proof of physical information loss. The previous8-percentage-point gain remains unvalidated as an instrument forecast.

A constructive positive pair demonstrates an important distinction. A stellar-mixture/morphology change of1.34 prior-standard-deviation norm can offset an E-field RMS change of0.0192 in the sparse data. Its15-aperture squared mean separation is{s.mean_separation_squared:.3f} seeing/{g.mean_separation_squared:.3f} GLAO. Even the optimal fixed-pair Gaussian test would then have only{100*s.optimal_simple_hypothesis_power_at_FPR05:.1f}%/{100*g.optimal_simple_hypothesis_power_at_FPR05:.1f}% power at5% false positives. These are conditional, optimistic known-pair bounds, not population-marginalized recovery rates.

**That degeneracy does not persist for this pair when retaining the spatial pixels.** The same evaluation rectangle gives squared separation33.13 seeing/33.66 GLAO. Thus the sparse apertures discarded discriminating information; a blanket claim of fundamental broadband non-identifiability would be unsupported. Full-pixel known-pair power saturates near100%, so this example cannot measure a useful GLAO power increment. A robust full-image model with unknown stellar populations has not been validated here.

## 5. Scientific decision and minimal next information
1. **Reliable uniform-versus-varying discrimination? No, not established.** The old catastrophic population error is diagnosed and the positive model improves contrast adequacy, but raw-colour model failure and tiny held-out counts prevent a reliable detection claim.
2. **Which variations remain ambiguous?** Dust-aligned stellar-colour gradients and positive mixtures can mimic varying attenuation in the compressed data. Global uniform attenuation is exactly unidentifiable from separately normalized bands. The present tests do not prove ambiguity in every full image or every allowed stellar population. The stellar-nuisance Jacobian locally spans the105 raw or98 contrast measurements, while regularization reduces effective fitted freedom; data-only local identification is therefore not supplied by these sparse measurements. This is not a claim about all possible full-image constraints.
3. **Robust GLAO advantage when fitting is adequate? Not demonstrated.** Conditional model-family/pixel information checks are consistent with a modest gain, but they are not a validated population-uncertain classification forecast. Failed raw fits prohibit that conclusion.
4. **What information is minimally needed next?** First retain existing image pixels or densely sampled PSF-aware spatial data—the information is already present for the constructed pair. Then validate an independent stellar SED library and spatial population model. Resolved absorption-feature/age/metallicity/SFH constraints, or bands demonstrated to constrain a direction distinct from reddening, are candidates; more continuum bands are not automatically sufficient. For the *sparse constructed pair only*, an ideal independent constraint on its coherent intrinsic g−Ks colour mode at roughly{s.illustrative_independent_coherent_colour_mode_sigma_for_80pct_power_mag:.3f}mag would reach80% idealized fixed-pair power. That number is not a spectroscopic exposure requirement, general threshold or ULTIMATE forecast. The minimal real band/spectrum requirement cannot yet be established from this inadequate model.

**Recommendation: NO-GO for broadband-only dust-geometry detections or ML training with the current pipeline. GO only for targeted full-image forward-model and independent stellar-population validation.** Rejection of a screen never identifies a unique3D geometry. Only galaxy294866 is local; no galaxy-to-galaxy generalization is tested.

## Observing scope
Actual DR1 griz and2MASS J/H/Ks retain their rest-band meaning. z=.3 specifies conditional matched-rest-band degradation with fixed intrinsic size/luminosity and I_nu/(1+z)^3; no exact observer-frame K correction is invented. Rest Ks would lie near2.81µm, outside ordinary Ks coverage. Nominal-band sky/throughput/PSFs remain provisional proxies; these results are not a realizable seven-filter ULTIMATE forecast. Existing HAWK-I checks and all previous experiments are preserved.
'''
 (O/'scientific_report.md').write_text(text);return text

def run():
 paths=figures();report();return paths
if __name__=='__main__':run()
