"""Create figures and a report strictly from saved executed results."""
import pilot as p
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
O=p.O
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
COLORS={'seeing':'#286b9a','glao':'#c85d23'}

def save(fig,name):
 for ext in ['png','pdf']:fig.savefig(O/f'figures/{name}.{ext}',dpi=190,bbox_inches='tight')
 plt.close(fig)
def figures():
 refs=pd.read_csv(O/'reference_summary.csv');fig,axes=plt.subplots(3,5,figsize=(15,9),layout='constrained')
 for col,v in enumerate(['O1','O2','O3','O4','O5']):
  a=np.load(O/f'references/{v}_effective_attenuation.npz')
  for row,j,lo,hi,label in [(0,0,-.1,1.,'g effective attenuation [mag]'),(1,2,-.025,.15,'Ks effective attenuation [mag]')]:
   im=axes[row,col].imshow(a['A_eff'][j],origin='lower',extent=[-20,20,-20,20],cmap='RdBu_r',norm=TwoSlopeNorm(vmin=lo,vcenter=0,vmax=hi));axes[row,col].set(xlim=(-12,12),ylim=(-12,12),title=v if row==0 else None,xlabel='x [kpc]');
   if col==0:axes[row,col].set_ylabel('y [kpc]')
  im2=axes[2,col].imshow(np.log10(np.maximum(a['dust_surface_density'],1e-5)),origin='lower',extent=[-20,20,-20,20],vmin=-2,vmax=1,cmap='magma');axes[2,col].set(xlim=(-12,12),ylim=(-12,12),xlabel='x [kpc]')
 # Separate colorbars from repeated grids.
 fig.colorbar(axes[0,-1].images[0],ax=axes[0,:],shrink=.8,label='A_eff,g [mag]');fig.colorbar(axes[1,-1].images[0],ax=axes[1,:],shrink=.8,label='A_eff,Ks [mag]');fig.colorbar(im2,ax=axes[2,:],shrink=.8,label='log10 projected dust [M_sun pc⁻²]');fig.suptitle('Five views of one galaxy: effective attenuation and projected mass are different quantities\nNegative attenuation retained; display range clipped, numerical maps unchanged');save(fig,'01_reference_maps')
 fig,axes=plt.subplots(2,3,figsize=(12,8),layout='constrained')
 for row,mode in enumerate(['seeing','glao']):
  a=np.load(O/f'observations/O1_z0.1_{mode}_1.0h_gaussian.npz');r=a['radius_kpc'];extent=[-r.shape[0]/2*float(a['pixel_kpc']),r.shape[0]/2*float(a['pixel_kpc'])]*2
  rate=a['SKIRT_observed_rate'][2];im=axes[row,0].imshow(np.log10(np.maximum(rate,.03)),origin='lower',extent=extent,vmin=-1.2,vmax=2.4,cmap='gray');fig.colorbar(im,ax=axes[row,0],label='log10 Ks source rate [e⁻ s⁻¹ pix⁻¹]')
  val=np.ma.masked_where(r>=12,a['SKIRT_J_Ks_NIR_value']);im=axes[row,1].imshow(val,origin='lower',extent=extent,vmin=-.12,vmax=.12,cmap='RdBu_r');fig.colorbar(im,ax=axes[row,1],label='J−Ks local colour structure [mag]')
  axes[row,2].imshow(a['SKIRT_J_Ks_NIR_detected'],origin='lower',extent=extent,cmap='Greys',vmin=0,vmax=1);axes[row,2].contour(np.where(a['valid_truth'],a['J_Ks_NIR_reference'],np.nan),levels=[.05],origin='lower',extent=extent,colors=['#c85d23'],linewidths=.7)
  for col in range(3):axes[row,col].set(xlim=(-12,12),ylim=(-12,12),xlabel='x [kpc]',ylabel=f'{mode}: y [kpc]')
  axes[row,0].set_title(f'Native Ks, D50={a["widths_arcsec"][2]:.3f} arcsec',fontsize=9);axes[row,1].set_title('J−Ks, NIR matched; 1 kpc scale',fontsize=9);axes[row,2].set_title('Black: candidates; orange: truth',fontsize=9)
 fig.suptitle('O1, z=0.1 distance degradation, one hour per band; first fixed evaluation draw\nDR1 rest bands and provisional noise proxies, not exact observer-frame photometry');save(fig,'02_seeing_GLAO_images')
 # A second explicitly illustrative view shows more extended reference colour
 # structure. Neither view was used to tune the measurement thresholds.
 fig,axes=plt.subplots(2,3,figsize=(12,8),layout='constrained')
 for row,mode in enumerate(['seeing','glao']):
  a=np.load(O/f'observations/O3_z0.1_{mode}_1.0h_gaussian.npz');r=a['radius_kpc'];extent=[-r.shape[0]/2*float(a['pixel_kpc']),r.shape[0]/2*float(a['pixel_kpc'])]*2
  for col,(scene,method) in enumerate([('SKIRT','J_Ks_NIR'),('clear','g_Ks_matched'),('SKIRT','Ks_native')]):
   value=a[f'{scene}_{method}_value'];det=a[f'{scene}_{method}_detected'];amp=.03 if method=='Ks_native' else .05
   im=axes[row,col].imshow(np.ma.masked_where(r>=12,value),origin='lower',extent=extent,vmin=-.12 if col<2 else -.3,vmax=.12 if col<2 else .3,cmap='RdBu_r');axes[row,col].contour(det.astype(float),levels=[.5],origin='lower',extent=extent,colors=['black'],linewidths=.6)
   if scene=='SKIRT':axes[row,col].contour(np.where(a['valid_truth'],a[f'{method}_reference'],np.nan),levels=[amp],origin='lower',extent=extent,colors=['#e9a600'],linewidths=.8)
   fig.colorbar(im,ax=axes[row,col],shrink=.75,label='Structure [mag]' if col<2 else 'Fractional deficit')
   axes[row,col].set(xlim=(-12,12),ylim=(-12,12),xlabel='x [kpc]',ylabel=f'{mode}: y [kpc]',title=['SKIRT J−Ks: partial correspondence','Clear g−Ks: stellar-only candidates','SKIRT Ks: poor dust attribution'][col]);axes[row,col].title.set_fontsize(9)
 fig.suptitle('Illustrative O3 first fixed draw: success, stellar contamination, and failure together\nz=0.1 degradation, 1h/band, 1kpc scale; black=candidates, gold=dust-induced reference');save(fig,'09_success_failure_examples')
 f=pd.read_csv(O/'feature_summary.csv');primary=f.query('view=="O1" and z==0.1 and hours==1 and kind=="gaussian" and scene=="SKIRT"');fig,axes=plt.subplots(2,3,figsize=(13,7),layout='constrained')
 for col,method in enumerate(p.METHODS):
  for mode,color in COLORS.items():
   d=primary[(primary.method==method)&(primary['mode']==mode)].sort_values('scale_kpc')
   for row,metric in enumerate(['completeness','contamination']):axes[row,col].errorbar(d.scale_kpc,d[metric],yerr=[d[metric]-d[metric+'_lo'],d[metric+'_hi']-d[metric]],color=color,marker='o',label=mode,capsize=3)
  axes[0,col].set(title=method,ylabel='Reference-feature area recovered',ylim=(-.05,1.05));axes[1,col].set(xlabel='Analysis kernel FWHM [kpc]',ylabel='Candidate area outside reference',ylim=(-.05,1.05));axes[0,col].legend()
 fig.suptitle('Observable candidates versus known dust-induced changes: successful and failed attribution\nO1 z=0.1, 1h/band; 95% Monte Carlo mean intervals over 40 independent noise draws');save(fig,'03_feature_recoverability')
 fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained');scenes=['clear','uniform','population_shift','SKIRT'];labels=['Clear','Uniform','Population\nshift','SKIRT']
 for ax,method in zip(axes,p.METHODS):
  for mode,color,off in [('seeing',COLORS['seeing'],-.12),('glao',COLORS['glao'],.12)]:
   d=f.query('view=="O1" and z==0.1 and hours==1 and kind=="gaussian" and scale_kpc==1');d=d[(d.method==method)&(d['mode']==mode)].set_index('scene').loc[scenes];ax.bar(np.arange(4)+off,d.candidate_area_fraction,width=.24,color=color,label=mode)
  ax.set(xticks=np.arange(4),xticklabels=labels,title=method,ylabel='Candidate fraction of evaluated disk area');ax.legend(fontsize=8)
 fig.suptitle('Significant image structure does not imply dust: controls retain stellar/morphological structure\nSame fixed thresholds; O1 z=0.1, 1h/band, 1kpc analysis scale');save(fig,'04_control_contamination')
 m=pd.read_csv(O/'dust_morphology_bias_summary.csv');raw=pd.read_csv(O/'dust_morphology_paired_draws.csv');fig,axes=plt.subplots(2,3,figsize=(13,7),layout='constrained')
 for row,band in enumerate(['g','Ks']):
  for col,metric in enumerate(['C','A','R50']):
   ax=axes[row,col]
   for mode,color,off in [('seeing',COLORS['seeing'],-.08),('glao',COLORS['glao'],.08)]:
    d=m.query('z==0.1 and hours==1 and kind=="gaussian"');d=d[(d.band==band)&(d['mode']==mode)].set_index('view').loc[['O1','O2','O3','O4','O5']];ax.errorbar(np.arange(5)+off,d[metric],yerr=[d[metric]-d[metric+'_lo'],d[metric+'_hi']-d[metric]],fmt='o',capsize=3,color=color,label=mode)
   intrinsic=raw.query('z==0.1 and hours==1 and kind=="gaussian" and draw==-1 and mode=="seeing"');intrinsic=intrinsic[intrinsic.band==band].set_index('view').loc[['O1','O2','O3','O4','O5']];ax.scatter(np.arange(5),intrinsic[metric],marker='x',color='black',label='No observing PSF')
   ax.axhline(0,color='gray',ls=':');ax.set(xticks=np.arange(5),xticklabels=['O1','O2','O3','O4','O5'],ylabel=f'{band}: dusty − clear {metric}'+(' [kpc]' if metric=='R50' else ''))
   if row==0 and col==0:ax.legend(fontsize=8)
 fig.suptitle('Paired dust-induced morphology changes; five correlated views of galaxy 294866\nz=0.1 degradation, 1h/band; error bars describe noise only; centre and R<12kpc aperture fixed');save(fig,'05_morphology_bias')
 tr=pd.read_csv(O/'scale_transfer.csv');fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
 for ax,method in zip(axes,p.METHODS):
  for mode,color in COLORS.items():
   for z,style in [(.05,'--'),(.1,'-')]:
    d=tr[(tr.view=='O1')&(tr.z==z)&(tr['mode']==mode)&(tr.method==method)&(tr.kind=='gaussian')].sort_values('scale_kpc');ax.plot(d.scale_kpc,d.RMS_retention,style,marker='o',color=color,label=f'{mode}, z={z}')
  ax.set(xlabel='Analysis kernel FWHM [kpc]',ylabel='RMS of dust imprint retained / intrinsic',title=method)
 axes[0].legend(fontsize=8);fig.suptitle('Truth-only spatial transfer diagnostic: GLAO preserves NIR dust-induced structure\nThis is counterfactual evaluation, not an observational dust template or detection probability');save(fig,'06_spatial_transfer')
 fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
 for col,method in enumerate(p.METHODS):
  for mode,color in COLORS.items():
   d=f.query('view=="O1" and z==0.1 and kind=="gaussian" and scene=="SKIRT" and scale_kpc==1');d=d[(d.method==method)&(d['mode']==mode)].sort_values('hours');axes[col].errorbar(d.hours,d.completeness,yerr=[d.completeness-d.completeness_lo,d.completeness_hi-d.completeness],fmt='o-',color=color,label=mode,capsize=3)
  axes[col].set(xlabel='Exposure [hours per band]',ylabel='Reference area completeness',title=method,xscale='log',ylim=(-.05,1.05));axes[col].set_xticks([.25,1.,4.],labels=['0.25','1','4']);axes[col].minorticks_off();axes[col].legend()
 fig.suptitle('Exposure-depth sensitivity at fixed 1kpc analysis scale; O1 z=0.1\nNIR threshold crossings can be noise-assisted; lower depth is not intrinsically better recovery');save(fig,'07_depth_sensitivity')
 # Surface brightness and PSF-wing sensitivity retain separate scenarios.
 fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
 for mode,color in COLORS.items():
  for method,style in [('g_Ks_matched','-'),('J_Ks_NIR','--')]:
   d=primary[(primary.method==method)&(primary['mode']==mode)&(primary.scale_kpc==1)].iloc[0];axes[0].plot([0,1,2],[d[f'completeness_SB{x}'] for x in range(3)],style,marker='o',color=color,label=f'{mode}, {method}')
  for kind,style in [('gaussian','-'),('moffat',':')]:
   d=tr[(tr.view=='O1')&(tr.z==.1)&(tr['mode']==mode)&(tr.method=='Ks_native')&(tr.kind==kind)].sort_values('scale_kpc');axes[1].plot(d.scale_kpc,d.RMS_retention,style,marker='o',color=color,label=f'{mode}, {kind}')
 axes[0].set(xticks=[0,1,2],xticklabels=['Low','Middle','High'],xlabel='Intrinsic Ks SB tercile (evaluation only)',ylabel='Reference area completeness',ylim=(-.05,1.05));axes[1].set(xlabel='Analysis kernel FWHM [kpc]',ylabel='Ks dust-imprint RMS retention',title='PSF wings: equal-D50 Moffat β=2.5');axes[0].legend(fontsize=7);axes[1].legend(fontsize=8);fig.suptitle('Surface brightness and PSF sensitivity; conditional one-galaxy results');save(fig,'08_SB_and_PSF_sensitivity')

def table(df):
 return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(str(x) for x in r)+' |' for r in df.itertuples(index=False,name=None))
def report():
 f=pd.read_csv(O/'feature_summary.csv');tr=pd.read_csv(O/'scale_transfer.csv');m=pd.read_csv(O/'dust_morphology_bias_summary.csv');refs=pd.read_csv(O/'reference_summary.csv');pair=pd.read_csv(O/'paired_GLAO_summary.csv')
 d=f.query('view=="O1" and z==0.1 and hours==1 and kind=="gaussian" and scene=="SKIRT"');tab=d[['mode','method','scale_kpc','completeness','contamination','correlation']].copy()
 for c in ['completeness','contamination','correlation']:tab[c]=tab[c].map(lambda v:f'{v:.3f}')
 def get(method,mode,scale=1):return d[(d.method==method)&(d['mode']==mode)&(d.scale_kpc==scale)].iloc[0]
 s=get('J_Ks_NIR','seeing');g=get('J_Ks_NIR','glao');gain=pair.query('view=="O1" and z==0.1 and hours==1 and kind=="gaussian" and scene=="SKIRT" and method=="J_Ks_NIR" and scale_kpc==1').iloc[0]
 mor=m.query('view=="O1" and z==0.1 and hours==1 and kind=="gaussian" and mode=="seeing" and band=="g"').iloc[0]
 comp=pd.read_csv(O/'component_incidence.csv').query('view=="O1" and z==0.1 and hours==1 and kind=="gaussian" and scene=="SKIRT" and method=="J_Ks_NIR" and scale_kpc==1').set_index('mode')
 psfb=pd.read_csv(O/'PSF_morphology_bias_summary.csv').query('view=="O1" and z==0.1 and hours==1 and kind=="gaussian" and scene=="SKIRT" and band=="Ks"').set_index('mode')
 controls=f.query('view=="O1" and z==0.1 and hours==1 and kind=="gaussian" and mode=="glao" and scale_kpc==1 and scene!="SKIRT"')[['scene','method','candidate_area_fraction']].copy();controls.candidate_area_fraction=controls.candidate_area_fraction.map(lambda x:f'{100*x:.2f}%')
 views=f.query('hours==1 and kind=="gaussian" and scene=="SKIRT" and method=="J_Ks_NIR" and scale_kpc==1')[['view','z','mode','completeness','contamination']].copy()
 views.to_csv(O/'NIR_orientation_distance_comparison.csv',index=False)
 for c in ['completeness','contamination']:views[c]=views[c].map(lambda v:f'{v:.3f}' if np.isfinite(v) else 'undefined: no reference/candidate')
 text=f'''# ULTIMATE-like imaging: spatial structure and morphology feasibility

## Decision

**GO for a conditional dust-induced morphology and spatial-transfer result; NO-GO for interpreting generic red/dark structures as unique dust detections.** This executed pilot addresses image structure, not 3D dust geometry or absolute dust mass. The earlier catastrophic false positives and inadequate physical SED fits remain valid and are not superseded.

For O1 at illustrative z=0.1 and one hour per band, NIR-only J−Ks candidates at the 1kpc analysis scale recover {100*s.completeness:.1f}% (seeing) / {100*g.completeness:.1f}% (GLAO) of the positive reference area, with {100*s.contamination:.1f}% / {100*g.contamination:.1f}% contamination relative to that reference. The paired completeness change is {100*gain.completeness:.2f} percentage points [95% Monte Carlo mean interval {100*gain.completeness_lo:.2f}, {100*gain.completeness_hi:.2f}]. This is an actual conditional result for one view, fixed coefficients/PSFs and a thresholded truth definition, **not a generic ULTIMATE dust-recovery forecast**. The NIR reference covers only a small fraction of the disk; its area is reported in `scale_transfer.csv`. Inspect all orientations and scales rather than promoting this single result as population performance.

The area gain must not be confused with a reliably detected individual object. In this O1 NIR example there is one scale-sized reference feature, but a scale-sized candidate component appears in only {int(comp.loc['glao'].draws_with_scale_sized_component)}/40 GLAO draws ({100*comp.loc['glao'].incidence:.1f}%; exact 95% interval {100*comp.loc['glao'].ci_low:.1f}–{100*comp.loc['glao'].ci_high:.1f}%) versus 0/40 seeing draws (upper95% limit {100*comp.loc['seeing'].ci_high:.1f}%). The five paired discordances give a two-sided exact McNemar p=0.0625: this small experiment does **not** establish a 5%-level component-incidence advantage, even though the paired area gain is clear under its noise model. No multiple-test-adjusted significance is claimed.

The straightforward native Ks unsharp-deficit detector often identifies stellar morphology instead of the dust imprint. Optical–NIR structure can overlap dust-induced colour changes but is also present without spatially varying dust. Those unsuccessful cases are retained, not re-thresholded. The primary workshop outcome should therefore combine measured dust-induced morphology changes with conditional NIR spatial-transfer improvement.

## What ran

Five correlated views of **one** DR1 galaxy 294866, using actual LSST g and 2MASS J/Ks images and projected dust maps. O1: z=0.05/0.1, 0.25/1/4h per band, seeing/GLAO. O2–O5: z=0.1, 1h per band, both modes. Additional O1 z=0.1, 1h equal-D50 Moffat sensitivity. Each of 22 conditions has four scenes and **40 independent final noise draws**: clear, uniform screen, stellar-only positive colour shifts, original SKIRT. This is 3,520 paired-scene observations, with three bands each. Gaussian baseline has three methods at three analysis scales; Moffat sensitivity uses native Ks only, not an invalid Gaussian colour-matching prescription. All criteria were fixed in `PROTOCOL.md` before evaluation; no Bayesian classification grid, ML, installations or science downloads were performed.

Forty separate calibration draws per method/noise prescription check analytic variance, including exact aggregate Poisson counts plus independent summed read noise. Variance agreement is documented in `noise_covariance_validation.csv`; calibration did not select thresholds. Exposure depth is **per band**, so 1h means 3h on source over these three bands, before overheads. At 60s DIT this is 60 reads per band, not a single long exposure.

## Reference attenuation and interpretation

A_eff,b(x)=−2.5 log10[I_SKIRT,b(x)/I_clear,b(x)], with finite positive intensities, I_clear>10⁻⁴ of the band peak and R<12kpc. Source pixels are 100pc; this sampling does not establish independently resolved physical structure at 100pc. Negative A_eff is retained: scattering and/or SKIRT Monte Carlo fluctuations can enhance local flux; no component/error maps allow a decomposition. No conversion to optical depth, dust mass or a unique 3D arrangement is made.

`reference_summary.csv` gives the aperture-integrated attenuation, negative fractions and projected-mass rank associations separately by band and view. Their viewing-angle dependence is retained; projected dust is a post-measurement check, never an observational template. `projected_dust_checks.csv` and `scale_transfer.csv` also compare detector-grid attenuation/structure with projected mass. Smoothing, stellar weighting, scattering and line-of-sight projection prevent a unique attenuation–mass relationship.

Truth-only structure references are the difference between the same observable computed on SKIRT and clear images, with area-integrated sampling but no observational PSF, and analysis smoothing FWHM 0.5/1/2kpc. PSF-limited references are saved separately. A kernel FWHM is **not an inferred feature diameter**; the effective width combines analysis smoothing and instrumental PSF. The reference excludes positive dust effects below 0.05mag (colours) or 0.03 fractional deficit. Features outside those operational cuts are not necessarily dust-free.

## Observable methods and results

The measurement function receives observed band images, variance, pixel scale and PSFs only. Counterparts and physical maps enter rendering/scoring, never feature selection. Positive candidates must exceed both 3 propagated noise SD and the fixed amplitude cut; fine and broad fluxes require S/N>10. This is a local significance requirement, not an image-wide false-alarm or false-discovery calibration.

- g−Ks fine-minus-broad colour, matched to 0.8arcsec in both modes; g always has its seeing-limited 0.7arcsec PSF.
- J−Ks colour, matched within NIR to each strategy's J width, preserving finer GLAO information relative to optical matching.
- Native Ks brightness deficit, 1−I_fine/I_broad, without smoothing to g resolution.
- Concentration C=5log10(R80/R20), circular R50, second-moment axis ratio, and noise-corrected 180° asymmetry, measured in R<12kpc about the fixed simulation centre. Signed sky-subtracted pixels are retained. These are defined pilot measurements, not optimized survey morphology estimates.

O1, z=0.1, 1h/band (pixel-area measures; all independent noise draws retained):

{table(tab)}

Distance/view sensitivity at 1kpc in J−Ks, one hour per band:

{table(views)}

At O1/z=0.1 the 0.5kpc analysis-scale NIR reference is not recovered by the fixed selector in either mode; the 2kpc area recovery is about74%/82% seeing/GLAO. This is evidence for recoverable structures after kpc-scale smoothing in these particular scenes, not a universal minimum dust-cloud size. At z=0.1 the native Ks Gaussian width is1.085kpc seeing/0.718kpc GLAO, and within-NIR matching gives1.213/0.936kpc before analysis smoothing. At1kpc smoothing the J−Ks effective widths are therefore about1.572/1.370kpc. The actual candidate feature shapes, brightness, amplitude cut and stellar structure matter as much as this nominal width. O2 has no positive J−Ks reference above the chosen cut, so its undefined completeness is not a failed recovery estimate.

Completeness is reference area recovered; contamination is candidate area outside the positive reference. It includes stellar structures and dust effects not captured by the operational reference cut, so it is **not a universal astrophysical false-discovery probability**. Reference-component area recovery uses overlap with the union of thresholded pixels (30% area), while candidate-component counts require the separate minimum scale-related area. Thus reference-component area recovery alone does not certify detection of a connected object. Both are recorded; `component_incidence.csv` provides component counts and exact noise-realization intervals. No independent-pixel error bars are used. The 95% mean intervals describe uncertainty in the repeated-noise mean for a fixed scene; they exclude instrument, SPS, simulation and galaxy-to-galaxy uncertainty. Pixelized radii have finite sampling precision.

## Controls: dust attribution remains limited

Candidate area for O1 z=0.1, 1h, 1kpc, GLAO:

{table(controls)}

The clear and uniform-screen scenes share the actual structured stellar populations. The shifted control adds a fixed smooth-plus-patchy, positive non-screen spectral perturbation. Its NIR colour variation is deliberately limited by the stated generator; low contamination on this control does **not** establish robustness to arbitrary NIR population shifts. In the controls every varying-dust attribution is false, even though the measured structure itself can be real. `control_structure_incidence.csv` gives per-scene incidence and exact binomial intervals across noise draws. Null controls have no varying-dust reference, so completeness is undefined; NaN is retained rather than converted to zero.

There is no credible single dust-feature resolution limit. `conditional_scale_recoverability.csv` gives a descriptive completeness≥50%, contamination≤50% summary separately for every view, PSF, depth and scale, not a preregistered acceptance test or a universal resolution limit. Passing that truth-overlap criterion is not sufficient for dust specificity when control scenes generate similar candidates. No measurement thresholds were changed after seeing these failures.

## Morphology, GLAO and observing conditions

For O1 g at z=0.1, 1h, seeing, dust changes C by {mor.C:.3f}, asymmetry by {mor.A:.3f}, and R50 by {mor.R50:.3f}kpc. This is a **paired simulation counterfactual**, not something directly measurable for one real galaxy lacking its dust-free counterpart. The five-view paired table and figure show the full viewing dependence, including sign changes where present. Morphological noise bias, dust-induced bias and PSF changes are separate outputs. Orientation second-moment axis ratios characterize apparent flattening; exact inclinations are not inferred.

`scale_transfer.csv` measures how much of each truth-isolated dust imprint survives the PSF; `paired_GLAO_summary.csv` gives paired changes in actual candidate overlap and contamination. Narrower NIR PSFs can preserve more structure without making it uniquely attributable to dust. For the O1 dusty Ks image, the measured-minus-no-observational-PSF concentration bias changes from {psfb.loc['seeing'].C:.3f} (seeing) to {psfb.loc['glao'].C:.3f} (GLAO); this is conditional morphology preservation, not a dust-specific statistic. `PSF_morphology_bias_summary.csv` retains all corresponding cases. g−Ks colour resolution is intentionally capped by optical matching; its near-equality between modes is a design consequence. Native NIR structure, PSF wings, depth and surface-brightness terciles are evaluated separately. Longer exposures cannot recover spatial frequencies removed by the PSF. Some metrics may worsen when resolution reveals more non-dust stellar structure; no guaranteed GLAO advantage is asserted for every metric/view.

**An important unsuccessful depth trend:** O1 1kpc J−Ks completeness decreases as depth increases in some cases. This is not improved physical recovery at lower depth. `depth_threshold_diagnostic.csv` shows that none of the46 reference pixels has a noiseless seeing observable above0.05mag (median0.0429mag), while12 do for GLAO (median0.0474mag). PSF dilution and stellar colour change the observable relative to the known dust-only imprint. Noise scatters pixels across the amplitude threshold: first-order expected seeing completeness0.137/0.037/0.003 at0.25/1/4h agrees with measured0.159/0.039/0.007 within Monte Carlo intervals. Thus an area-overlap increase can itself be noise-assisted; do not turn the quoted GLAO area gain into a robust feature-detection forecast.

Finite-field sensitivity is explicit in `boundary_sensitivity.csv`: a 32kpc versus48kpc measurement field changes 1kpc structures by at most0.00023mag in g−Ks and0.00033 in Ks fractional deficit for checked O1 cases. At the largest2kpc analysis scale, boundary differences reach0.0133mag/0.0258 fractional deficit near the edge, material relative to the cuts; those largest-scale edge classifications deserve caution. This check does not validate every orientation's boundary effects.

## Bandpass, distance and noise limitations

This is **matched-rest-band distance degradation**, not exact observer-frame ULTIMATE synthetic photometry. Physical size/luminosity/populations/dust are fixed. Flat ΛCDM H0=70, Ωm=0.3 supplies D_A; MJy/sr is frequency-specific, hence I_nu/(1+z)^3 and source pixel solid angle, with flux-conserving area overlap. No extra bolometric (1+z)^−4 factor, intrinsic size evolution, or interpolation into unsupported observer bands is used. Even at z=0.1, rest Ks shifts to ~2.375µm, so its nominal Ks electron/noise conversion is a conditional proxy. z=0.3 rest-Ks is deliberately not used as a realizable observer-Ks forecast.

Gaussian design widths are g=0.700arcsec both modes; J=0.658/0.508 and Ks=0.588/0.390arcsec seeing/GLAO. The calculator D50 is equated to Gaussian FWHM only in the Gaussian baseline. Equal-D50 Moffat β=2.5 is a wings sensitivity case, not another measured instrument PSF. There is no guaranteed 0.2arcsec resolution. Detector 0.1arcsec pixels and existing sky/thermal/throughput/read/dark parameters are provisional; actual DR1 bands are not exact ULTIMATE passbands. Source electrons are derived through the stored photon-per-Jy coefficient. Noise includes source, sky, thermal, dark and split-read terms; sky subtraction is assumed known, with no flat-field, sky-residual, PSF-estimation or registration errors. Smoothing-induced noise covariance is propagated through combined kernels, including fine–broad covariance and first-order nonlinear derivatives. The mocks assume independent native detector pixels, so realistic reduced-image resampling covariance remains a future requirement.

## Workshop and future paper

**Strongest workshop claim:** for one structured galaxy, dust measurably changes spatial light distribution and morphology; GLAO-like NIR PSFs conditionally retain more small-scale information, while straightforward red/dark-feature selection has population/morphology contamination. Present paired morphology plots plus observed images, spatial-transfer curves and explicit successful/unsuccessful overlap examples. Retain the previous negative geometry result as motivation, not as a claim disproving all broadband information.

**Plausible future paper:** a multi-galaxy study of dust-induced morphology bias and spatial information transfer, with actual passbands/PSFs/sky systematics and independent observational validation. Feature attribution would need additional stellar-population constraints and a diverse independent galaxy sample. The present five views cannot provide that generalization. A focused [MaNGA proposal](MaNGA_validation_note.md) is supplied; no acquisition or request to Anil was made, and its connection to GECKOS remains unresolved.
'''
 (O/'scientific_report.md').write_text(text)
 summary=f'''# Workshop feasibility summary

**Present dust-induced morphology bias and conditional NIR spatial information, not unique dust geometry.** The previous false-positive/SED-fit failures remain valid.

Executed: galaxy294866, five correlated views, actual DR1 g/J/Ks, matched-rest-band distance degradation z=0.05/0.1, provisional seeing/GLAO PSFs. Forty independent evaluation draws per scene/condition; 22 conditions, 3,520 three-band mock observations. No new science downloads, installations, ML or old Bayesian-grid reruns.

- At z=0.1,1h/band, dust reduces the measured g half-light radius by0.65–1.31kpc across these views. These are paired dusty/clear simulation changes, not a directly observed correction for real galaxies.
- In O1, GLAO increases the 1kpc-analysis J−Ks dust-reference area recovered from{100*s.completeness:.1f}% to{100*g.completeness:.1f}%; paired gain{100*gain.completeness:.1f} percentage points (95% Monte Carlo mean interval{100*gain.completeness_lo:.1f}–{100*gain.completeness_hi:.1f}). The reference covers only1.56kpc². This is conditional area overlap, not a generic dust-detection forecast.
- Individual scale-sized NIR components appear in5/40 GLAO versus0/40 seeing O1 draws. Exact paired two-sided p=0.0625; robust component-incidence improvement is not established. Other views differ and O2 has no above-cut NIR reference.
- Native Ks dark-feature selection has severe stellar-morphology contamination. g−Ks structures also occur in dust-free/uniform controls. Low contamination in selected J−Ks cases is not proof of robustness to arbitrary stellar-population variation.
- For the O1 dusty Ks image, concentration bias relative to no-observational-PSF sampling changes from{psfb.loc['seeing'].C:.3f} to{psfb.loc['glao'].C:.3f}. GLAO can preserve morphology without providing unique dust attribution.

**Workshop recommendation:** show the paired morphology figure, spatial-transfer curves, and explicit successes/failures. **Future-paper direction:** multi-galaxy dust-induced morphology and spatial-transfer study, validated instrument/filter/noise assumptions, plus a small independently selected MaNGA comparison. This pilot alone does not establish galaxy generalization or exact observer-frame ULTIMATE sensitivity. Rest Ks at z=0.1 is not ordinary observer Ks. Largest2kpc-scale edge classifications have finite-field sensitivity; simulation Monte Carlo errors are unavailable.
'''
 (O/'workshop_summary.md').write_text(summary)
 return text

def run():figures();return report()
if __name__=='__main__':run()
