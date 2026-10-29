"""Source-backed tables, plots and scientific interpretation; no fit tuning."""
from pathlib import Path
import json,hashlib,sys,os
import numpy as np,pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import experiment as e
O=e.O
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight','figure.dpi':120,'pdf.fonttype':42})
COLORS={'seeing':'#3776ab','glao':'#c65b21'}

def mdtable(df):
 return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(str(x) for x in row)+' |' for row in df.itertuples(index=False,name=None))

def paired_comparison():
 raw=pd.read_csv(O/'FINAL_evaluation_statistics.csv.gz');rates=pd.read_csv(O/'FINAL_calibrated_rates.csv');has=(O/'FINAL_calibration_statistics.csv.gz').exists();cal=pd.read_csv(O/'FINAL_calibration_statistics.csv.gz') if has else None
 out=[];rng=np.random.default_rng(833108)
 for (z,strategy,bandset,truth),g in raw[raw.truth.isin(['C_gradient','C_patchy','D_SKIRT'])].groupby(['z','strategy','bandset','truth']):
  d={m:a.sort_values('noise_index') for m,a in g.groupby('mode')};a=d['seeing'].detected.to_numpy(dtype=bool);b=d['glao'].detected.to_numpy(dtype=bool);n=len(a);plus=int((b&~a).sum());minus=int((a&~b).sum())
  def ci(k):return (0 if k==0 else stats.beta.ppf(.0125,k,n-k+1),1 if k==n else stats.beta.ppf(.9875,k+1,n-k))
  lp,hp=ci(plus);lm,hm=ci(minus);p=stats.binomtest(plus,plus+minus,.5).pvalue if plus+minus else 1.
  rec=dict(z=z,strategy=strategy,bandset=bandset,truth=truth,n=n,seeing_power=a.mean(),glao_power=b.mean(),difference=b.mean()-a.mean(),paired_ci_low=lp-hm,paired_ci_high=hp-lm,mcnemar_p=p,mcnemar_bonferroni12_p=min(1.,p*12),glao_only=plus,seeing_only=minus)
  if has:
   arrays={}
   for mode in ['seeing','glao']:
    cg=cal[(cal.z==z)&(cal.strategy==strategy)&(cal.bandset==bandset)&(cal['mode']==mode)]
    arrays[mode]=np.array([v.sort_values('noise_index').score.to_numpy() for _,v in cg.groupby('truth')])
   boot=[]
   for _ in range(1000):
    ic=rng.integers(0,n,n);ie=rng.integers(0,n,n);pr={}
    for mode in ['seeing','glao']:
     ar=arrays[mode][:,ic];k=int(np.ceil(.95*(n+1)))-1;cut=np.partition(ar,k,axis=1)[:,k].max();pr[mode]=np.mean(d[mode].score.to_numpy()[ie]>cut)
    boot.append(pr['glao']-pr['seeing'])
   rec.update(calibration_bootstrap_ci_low=np.quantile(boot,.025),calibration_bootstrap_ci_high=np.quantile(boot,.975))
  out.append(rec)
 df=pd.DataFrame(out);df.to_csv(O/'GLAO_power_comparison.csv',index=False);return df

def primary_truth_table():
 a=np.load(O/'matched_DR1_scenes_O1.npz');yy,xx=np.meshgrid((np.arange(400)+.5)*.1-20,(np.arange(400)+.5)*.1-20,indexing='ij');mask=np.hypot(xx,yy)<18;rows=[];clear=a['A_clear']
 for truth in ['A_clear','B_uniform','C_gradient','C_patchy','D_SKIRT']:
  im=a[truth]
  for j,band in enumerate(e.LABELS):
   good=mask&(clear[j]>clear[j].max()*1e-5)&(im[j]>0);att=-2.5*np.log10(im[j][good]/clear[j][good]);rows.append(dict(truth=truth,band=band,integrated_R18_attenuation_mag=-2.5*np.log10(im[j][mask].sum()/clear[j][mask].sum()),resolved_attenuation_median_mag=np.median(att),resolved_attenuation_p16=np.quantile(att,.16),resolved_attenuation_p84=np.quantile(att,.84),negative_attenuation_fraction=np.mean(att<0),n_mask_pixels=good.sum()))
 df=pd.DataFrame(rows);df.to_csv(O/'DR1_physical_control_summary.csv',index=False);return df

def figures():
 (O/'figures').mkdir(exist_ok=True);paths=[]
 def save(fig,name):
  fig.savefig(O/f'figures/{name}.png',dpi=220);fig.savefig(O/f'figures/{name}.pdf');paths.append(O/f'figures/{name}.png');plt.close(fig)
 a=np.load(O/'matched_DR1_scenes_O1.npz');names=['A_clear','B_uniform','C_gradient','C_patchy','D_SKIRT'];titles=['A: DR1 clear','B: uniform screen','C: smooth screen','C: patchy screen','D: SKIRT dusty'];fig,ax=plt.subplots(2,5,figsize=(14,6),layout='constrained')
 for j,(name,title) in enumerate(zip(names,titles)):
  im=a[name];v=np.log10(np.maximum(im[0],1e-7));im0=ax[0,j].imshow(v,origin='lower',extent=[-20,20,-20,20],cmap='magma',vmin=-3,vmax=0)
  color=-2.5*np.log10(np.maximum(im[0],1e-10)/np.maximum(im[-1],1e-10));color[im[-1]<np.max(im[-1])*1e-4]=np.nan
  im1=ax[1,j].imshow(color,origin='lower',extent=[-20,20,-20,20],cmap='viridis',vmin=1,vmax=4)
  ax[0,j].set_title(title);ax[0,j].add_patch(Rectangle((-14,-10),10,20,fill=False,ec='cyan',lw=1))
  for y in [-6,-3,0,3,6]:
   for x in [4,7,10]:ax[0,j].add_patch(Rectangle((x-.75,y-.75),1.5,1.5,fill=False,ec='white',lw=.4))
  for axes in ax[:,j]:axes.set(xlim=(-15,15),ylim=(-12,12),xlabel='x [kpc]')
 ax[0,0].set_ylabel('y [kpc]');ax[1,0].set_ylabel('y [kpc]');fig.colorbar(im0,ax=ax[0,:],label='log10 g intensity [MJy/sr]',shrink=.75);fig.colorbar(im1,ax=ax[1,:],label='g - Ks [AB mag]',shrink=.75);fig.suptitle('Physical DR1 scenes: same stellar structure; training block cyan, evaluation apertures white\nIntrinsic displays are generator/diagnostic inputs, never observational templates',fontsize=12);save(fig,'01_matched_DR1_controls')
 rates=pd.read_csv(O/'FINAL_calibrated_rates.csv');joint=rates[rates.bandset=='joint'];fig,axes=plt.subplots(2,2,figsize=(11,7),sharey=True,layout='constrained')
 cats=['B_uniform','C_gradient','C_patchy','D_SKIRT'];labels=['Uniform null','Smooth screen','Patchy screen','SKIRT complex']
 for i,z in enumerate([.1,.3]):
  for j,strategy in enumerate(['matched','native']):
   ax=axes[i,j]
   for mode,offset in [('seeing',-.12),('glao',.12)]:
    d=joint[(joint.z==z)&(joint.strategy==strategy)&(joint['mode']==mode)].set_index('truth').loc[cats];ax.errorbar(np.arange(4)+offset,d.rate,yerr=np.array([d.rate-d.ci_low,d.ci_high-d.rate]),fmt='o',capsize=3,label=mode,color=COLORS[mode])
   ax.axhline(.05,ls=':',color='gray',lw=1);ax.set(xticks=np.arange(4),xticklabels=labels,ylim=(-.04,1.06),title=f'z={z}, {strategy} PSF strategy');ax.tick_params(axis='x',rotation=15)
 axes[0,0].legend();axes[0,0].set_ylabel('Held-out rejection fraction');axes[1,0].set_ylabel('Held-out rejection fraction');fig.suptitle('Final conditional calibration: 500 evaluation draws per scene; 95% exact binomial intervals\nSKIRT rejection is not a screen-model power or a geometry detection',fontsize=12);save(fig,'02_final_calibrated_rates')
 anchor=pd.read_csv(O/'FINAL_population_anchor_stress.csv');d=anchor[(anchor.bandset=='joint')&anchor.truth.str.contains('population')];fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
 for ax,z in zip(axes,[.1,.3]):
  for mode,offset in [('seeing',-.1),('glao',.1)]:
   values=[];lo=[];hi=[]
   for strategy in ['matched','native']:
    rows=d[(d.z==z)&(d.strategy==strategy)&(d['mode']==mode)];r=rows.loc[rows.rate.idxmax()];values.append(r.rate);lo.append(r.rate-r.ci_low);hi.append(r.ci_high-r.rate)
   ax.errorbar(np.arange(2)+offset,values,yerr=[lo,hi],fmt='o',capsize=3,label=mode,color=COLORS[mode])
  ax.axhline(.05,color='gray',ls=':');ax.set(title=f'z={z}: worst tested population anchor',xticks=[0,1],xticklabels=['PSF matched','Native NIR'],ylim=(-.03,1.05),ylabel='False-positive fraction')
 axes[0].legend();fig.suptitle('New-noise stress tests of frozen FINAL thresholds\nEnsemble-average calibration does not guarantee control for every plausible stellar-colour field',fontsize=12);save(fig,'03_population_false_positive_robustness')
 power=pd.read_csv(O/'GLAO_power_comparison.csv');d=power[(power.bandset=='joint')&(power.z==.3)];fig,ax=plt.subplots(figsize=(10,5),layout='constrained');ylabs=[]
 for rownum,(strategy,truth) in enumerate((s,t) for s in ['matched','native'] for t in ['C_gradient','C_patchy','D_SKIRT']):
  r=d[(d.strategy==strategy)&(d.truth==truth)].iloc[0];lo=r.get('calibration_bootstrap_ci_low',r.paired_ci_low);hi=r.get('calibration_bootstrap_ci_high',r.paired_ci_high)
  if np.isclose(lo,hi):lo,hi=r.paired_ci_low,r.paired_ci_high
  ax.errorbar(r.difference*100,rownum,xerr=[[max(0,(r.difference-lo)*100)],[max(0,(hi-r.difference)*100)]],fmt='o',capsize=3,color='#6b3c89');ylabs.append(f'{strategy}: {truth.replace("C_", "").replace("D_", "")}')
 ax.axvline(0,color='gray',ls=':');ax.set(yticks=np.arange(len(ylabs)),yticklabels=ylabs,xlabel='GLAO minus seeing: percentage points',title='z=0.3: bootstrap 95% intervals; conservative exact bound at saturated power');fig.suptitle('A conditional numerical gain is not a validated ULTIMATE performance forecast',fontsize=12);save(fig,'04_GLAO_power_difference')
 p=np.load(O/'population_training.npz');fig,ax=plt.subplots(1,2,figsize=(11,4.5),layout='constrained');h=e.contrasts(7)
 dust=e.kappa(e.WAVE);dust-=dust.mean();dust/=np.linalg.norm(dust)
 for n in range(2):
  pc=p['eigenvectors'][:,n];pc=pc-pc.mean();pc/=np.linalg.norm(pc);ax[0].plot(e.WAVE,pc,'o-',label=f'Population PC{n+1}')
 ax[0].plot(e.WAVE,dust,'s--',label='Dust-law direction');ax[0].set(xlabel='DR1 band pivot [µm]',ylabel='Centered unit colour direction',title='Dust and population directions nearly overlap');ax[0].legend()
 se=pd.read_csv(O/'within_band_SED_sensitivity.csv');q=se.groupby('band').relative_difference.agg(['min','max']).reindex(e.LABELS);ax[1].vlines(np.arange(7),100*q['min'],100*q['max'],lw=5,color='#3776ab');ax[1].axhline(0,color='gray',ls=':');ax[1].set(xticks=np.arange(7),xticklabels=e.LABELS,ylabel='Effective k minus pivot k [%]',title='External-SED finite-band coefficient bracket\nProxy top hats, E=.05/.15/.35');save(fig,'05_population_and_band_law_degeneracy')
 pp=pd.read_csv(O/'FINAL_posterior_predictive.csv');fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
 for ax,col,title in zip(axes,['uniform_ppp','variable_ppp'],['Uniform model','Variable-colour model']):
  ar=np.array([pp[(pp.condition==i)].set_index('truth').loc[cats,col] for i in range(8)]);im=ax.imshow(ar,vmin=0,vmax=1,cmap='cividis',aspect='auto');ax.set(xticks=np.arange(4),xticklabels=['Uniform','Smooth','Patchy','SKIRT'],yticks=np.arange(8),yticklabels=[f'{z} {s} {m}' for z in [.1,.3] for s in ['matched','native'] for m in ['seeing','GLAO']],title=title)
  for i in range(8):
   for j in range(4):ax.text(j,i,f'{ar[i,j]:.3f}',ha='center',va='center',color='white' if ar[i,j]<.4 else 'black',fontsize=8)
 fig.colorbar(im,ax=axes,label='Posterior predictive probability');fig.suptitle('First prespecified evaluation draw: adequacy diagnostic, not detection significance\nNative z=0.3 and SKIRT failures limit physical interpretation',fontsize=12);save(fig,'06_posterior_predictive_checks')
 fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
 for ax,strategy in zip(axes,['matched','native']):
  for mode,offset in [('seeing',-.12),('glao',.12)]:
   d=rates[(rates.z==.3)&(rates.strategy==strategy)&(rates['mode']==mode)&(rates.truth=='C_patchy')].set_index('bandset').loc[['optical','NIR','joint']];ax.errorbar(np.arange(3)+offset,d.rate,yerr=[d.rate-d.ci_low,d.ci_high-d.rate],fmt='o',capsize=3,color=COLORS[mode],label=mode)
  ax.set(xticks=np.arange(3),xticklabels=['griz only','JHKs only','Joint'],ylim=(-.03,1.05),title=f'z=.3 patchy screen, {strategy}',ylabel='Conditional recovery fraction')
 axes[0].legend();fig.suptitle('Added bands improve conditional information but do not remove population ambiguity',fontsize=12);save(fig,'07_optical_NIR_joint_information')
 return paths

def reports():
 rates=pd.read_csv(O/'FINAL_calibrated_rates.csv');power=pd.read_csv(O/'GLAO_power_comparison.csv');anchor=pd.read_csv(O/'FINAL_population_anchor_stress.csv');pp=pd.read_csv(O/'FINAL_posterior_predictive.csv')
 joint=rates[rates.bandset=='joint'];null=joint[joint.truth.str.startswith(('A_','B_'))];summ=[]
 for cid,g in joint.groupby('condition'):
  base=g.iloc[0];d=g.set_index('truth');n=g[g.truth.str.startswith(('A_','B_'))];r=n.loc[n.rate.idxmax()]
  def cell(name):
   v=d.loc[name];return f'{100*v.rate:.1f}% [{100*v.ci_low:.1f}, {100*v.ci_high:.1f}]'
  summ.append({'z':str(base.z),'PSF':base.strategy,'mode':base['mode'],'worst null':f'{100*r.rate:.1f}% [{100*r.ci_low:.1f}, {100*r.ci_high:.1f}]','smooth':cell('C_gradient'),'patchy':cell('C_patchy'),'SKIRT rejection':cell('D_SKIRT')})
 tab=mdtable(pd.DataFrame(summ));stress=anchor[(anchor.bandset=='joint')&anchor.truth.str.contains('population')];worst=stress.loc[stress.rate.idxmax()]
 interesting=power[(power.z==.3)&(power.strategy=='matched')&(power.bandset=='joint')&(power.truth=='C_patchy')].iloc[0]
 bp=interesting.get('calibration_bootstrap_ci_low',np.nan);bh=interesting.get('calibration_bootstrap_ci_high',np.nan)
 maxnull=null.loc[null.rate.idxmax()];deg=pd.read_csv(O/'population_dust_identifiability.csv').iloc[0]
 text=f'''# Calibrated DR1 dust-screen experiment: scientific report
Executed in the existing phd environment; previous data/results preserved. No DR2 work, downloads, installations or ML.

## Scientific conclusion
**The false-positive problem is exposed and conditionally calibrated, but not generally solved.** Known smooth/patchy screens remain detectable under a declared bounded population ensemble. However, stellar-population shifts outside its typical draws can still cause false dust claims, and model inadequacy affects the real SKIRT images. A robust observational identification of non-uniform dust, unique mixed geometry, or general GLAO advantage is **not demonstrated**.

## What was completed
Actual DR1 griz and 2MASS J/H/Ks images of galaxy294866 were used, with the clear/original dusty pair and independent smooth/patchy image-level screens. The local archive has240 members,22 band pairs per orientation including extra Euclid products, and no second galaxy. O1–O5 are correlated views, never five independent galaxies. Original HAWK-I data and prior inspection are unchanged; raw compact-source PSFs remain provisional, not ULTIMATE measurements.

A spatially separated, training-only empirical population hierarchy replaced the old aperture-independent template catalogue. Flux contrasts are fitted with each band's covariance/PSF, normalized using observed fluxes. Exact clear counterparts and physical maps are not inference inputs. Priors, code tests, attenuation law, seeds and exposure splitting are explicit. This is a regularized Gaussian colour-field approximation, not full physical SPS/SFH or exact nonlinear dust geometry fitting. The first population PC explains {100*deg.training_variance_fraction:.2f}% of training colour variance and contains {100*deg.dust_direction_squared_projection:.2f}% of the centered dust direction, a strong identifiability warning.

## Independent calibration and final evaluation
Development:200 calibration plus200 evaluation noise draws per fixed scene; optical-only/NIR-only/joint, population and law priors, PSF shape, bin size, depth, all five views. Additional population stress tests failed at z=.3, so those outputs are retained as development evidence.

Final: frozen full-population model, five global-screen nulls,500 calibration draws **per null**, then500 independent population/noise draws **per scene**. The bounded generator varies two empirical population PCs over six fixed smooth/patch fields. Higher residual population PCs are in the likelihood but not generated. Calibration/evaluation coefficients and noises are separate; modes and controls use paired common random numbers. Threshold is the largest finite-sample95% null order statistic. Exact binomial intervals below condition on that threshold and chosen population ensemble; bootstrap intervals for GLAO also resample calibration and evaluation indices.

{tab}

Entries are rejection fractions with95% exact binomial intervals; SKIRT rejection is not a true-positive rate for a simple-screen family. The worst joint null across these final conditions is {100*maxnull.rate:.1f}% [{100*maxnull.ci_low:.1f}, {100*maxnull.ci_high:.1f}], with500 draws in that condition. Finite confidence intervals do not certify a universal rate below5%. Results cannot be pooled across bands, controls, orientations or modes as independent objects.

## Remaining false positives and GLAO benefit
A new500-noise evaluation of fixed population anchors uses the FINAL cutoffs without adjustment. The worst joint anchor is {worst.truth}, z={worst.z}, {worst.strategy}/{worst['mode']}: **{100*worst.rate:.1f}% false positives [{100*worst.ci_low:.1f}, {100*worst.ci_high:.1f}]**. These anchors are empirical colour perturbations, not verified SFH realizations; their failure is sufficient to reject a claim of robust population-independent calibration. Ensemble-average error control is different from protection at every plausible population setting.

For the z=.3 matched-PSF patchy case, conditional power is {100*interesting.seeing_power:.1f}% seeing versus {100*interesting.glao_power:.1f}% GLAO: **{100*interesting.difference:+.1f} percentage points**, calibration+evaluation bootstrap95% interval [{100*bp:.1f}, {100*bh:.1f}] points. This is a conditional numerical comparison, not a validated instrument gain. Other controls/strategies do not show a consistent improvement. Native z=.3 posterior predictions are inadequate; the narrower PSF exposes structure beyond this model. A worse classifier outcome does not mean GLAO destroys information. Model approximation and conservative cutoffs can prevent it from using the extra information.

At z=.1 all controlled screen powers in the joint primary cases saturate at100% (500/500; interval99.26–100%), so these bright controls cannot measure a positive GLAO power increment. The original SKIRT images fail the posterior predictive model in several cases; rejection cannot be promoted to a recovered geometry. Full tables preserve optical-only/NIR-only comparisons, sensitivity cases, posterior contrast amplitudes and predictive checks.

## Physical and observational limitations
- All fits use actual rest DR1 bands. z=.1/.3 mean **matched-rest-band image degradation** with fixed intrinsic size/luminosity/population/dust, frequency-specific I_nu/(1+z)^3, angular resampling and provisional electron/noise proxies. There is no exact observer-filter synthetic photometry or hidden K correction.
- Rest Ks would be observed near2.807µm at z=.3, beyond ordinary Ks coverage. Keeping its nominal Ks noise/throughput is a conditional proxy, not a realizable seven-band ULTIMATE forecast. This materially prevents a general observing-performance conclusion.
- Screen law is explicitly E*k(lambda), n=1 primary; within-band SED effects and n=.7/1.3 are sensitivities. Broadband screens do not reproduce wavelength-resolved radiative transfer. Scattering in SKIRT can create negative local attenuation; such complexity is retained, not clipped into a screen.
- Normalized contrasts discard absolute stellar colours and uniform E. Dust-like and population directions nearly coincide; posterior field amplitudes are not physical dust parameters. Physical source-SPS/birth-cloud uncertainties remain beyond the empirical hierarchy.
- Noise uses known sky mean, provisional throughput/sky/thermal/dark/read settings and60s reads. Exact first/second moments, full aperture covariance and bounded Poisson/normalization checks pass; unknown reduction and calibration systematics are absent.
- Only one galaxy and a limited spatial train/evaluation split are available. No independent-galaxy validation, arbitrary spectral recovery, unique3D geometry or physical high-z evolution is established.

## Safe workshop statement and next experiments
Present the matched controls, original false-positive failure, population/dust direction overlap, and the distinction between conditional recovery and robust physical inference. Show the numerical GLAO comparison only with its bandpass, population and adequacy qualifications. The supported overall conclusion is that **these data and the current empirical inference do not yet robustly separate non-uniform dust from all plausible population changes**.

Priorities: (1) improve physically positive, multiplicative spatial population+attenuation forward modelling and validate on held-out population anchors; (2) retain joint band-specific PSFs and require predictive adequacy; (3) obtain supported observer-band mappings or resolved spectra and final instrument/sky calibrations before forecasting ULTIMATE; (4) validate on an independent locally supplied galaxy before generalizing; (5) only then consider ML. No further data acquisition is required to reproduce this result.

## Reproduction and files
`README.md`, `Calibrated_DR1_screen_experiment.ipynb`, `experiment.py`, `final_ensemble.py`, `test_validation.py`; final rates `FINAL_calibrated_rates.csv`, paired differences `GLAO_power_comparison.csv`, pointwise checks `FINAL_population_anchor_stress.csv`, posterior predictions `FINAL_posterior_predictive.csv`; all figures in `figures/` PNG/PDF. `false_positive_audit.md`, `redshift_bandpass_limitations.md`, `instrument_provenance.md`, `FINAL_PROTOCOL.md` give the scientific contract. `validation.json` records execution and preservation checks.
'''
 (O/'scientific_report.md').write_text(text)
 (O/'workshop_statement.md').write_text('''# Workshop statement
Colour structure survives the simulated degradation, but it is not uniquely dust structure. We calibrated matched DR1 foreground-screen controls with spatial population uncertainty and independent noise. Controlled screen recovery can be high; realistic SKIRT interpretations still fail model and population stress tests. GLAO offers conditional numerical gains in selected cases, not a validated general dust-discrimination improvement. Actual observer passbands and independent galaxies remain necessary for that claim.
''')
 return text

def build():
 paired_comparison();primary_truth_table();paths=figures();reports();return paths
if __name__=='__main__':build()
