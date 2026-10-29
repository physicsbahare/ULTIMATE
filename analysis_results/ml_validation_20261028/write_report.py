from pathlib import Path
import json
import pandas as pd,numpy as np
O=Path(__file__).resolve().parent

def table(d):
 d=d.copy()
 for c in d:
  if pd.api.types.is_float_dtype(d[c]):d[c]=d[c].map(lambda v:f'{v:.5f}')
 return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in d.itertuples(index=False,name=None))

def run():
 val=pd.read_csv(O/'model_comparison.csv');hasfinal=(O/'final_metrics.csv').exists();settings=json.loads((O/'model_settings.json').read_text());targets=['A_g','dR50_Ks','dC_Ks','A_Ks','A_g_p50_1kpc','A_g_IQR_1kpc'];models=['constant_photo_median','constant_photo_mean','ridge_photo','ridge_summary','forest_summary','boost_summary','ridge_spatial']
 if hasfinal:
  lookup=val[['tag','aperture','bands','mode','target','model']].drop_duplicates('tag');m=pd.read_csv(O/'final_metrics.csv').drop(columns='target').merge(lookup,on='tag',validate='one_to_one');stage='Final 20';p=pd.read_csv(O/'final_predictions.csv.gz').merge(lookup,on=['tag','target'],validate='many_to_one');n=20
 else:m=val[val.stage=='validation'];p=pd.read_csv(O/'heldout_predictions.csv.gz');p=p[p.stage=='validation'];stage='Validation 14';n=14
 primary=m[(m.aperture=='fixed12')&(m.bands=='nir')&(m['mode']=='seeing')];pivot=primary.pivot(index='target',columns='model',values='MAE').reindex(targets)[models]
 line=[]
 for target in targets[:3]:
  best=primary[primary.target==target].sort_values('MAE').iloc[0];base=primary[(primary.target==target)&(primary.model=='constant_photo_median')].iloc[0];photo=primary[(primary.target==target)&(primary.model=='ridge_photo')].iloc[0]
  line.append(f'- **{target}:** best numerical MAE {best.MAE:.5f} ({best.model}); photometric ridge {photo.MAE:.5f}; median constant {base.MAE:.5f}. The best row is descriptive across the recorded models, not a new test-driven model selection.')
 ap=pd.read_csv(O/'aperture_target_sensitivity.csv');env=pd.read_csv(O/'source_control_envelopes.csv');cal=pd.read_csv(O/'uncertainty_calibration.csv');ood=pd.read_csv(O/'OOD_summary.csv');corr=pd.read_csv(O/'morphology_correction_accuracy.csv');lc=pd.read_csv(O/'learning_curves.csv');sens=pd.read_csv(O/'sensitivity_summary.csv');data=json.loads((O/'data_verification.json').read_text());y=pd.read_csv(O/'target_table.csv');counts=y.drop_duplicates('subhalo_id').groupby(['partition','zero_projected_dust']).size().reset_index(name='galaxies')
 gains=[]
 for target in targets:
  for model in models:
   a=p[(p.target==target)&(p.aperture=='fixed12')&(p.bands=='nir')&(p['mode']=='seeing')&(p.model==model)].assign(ae=lambda x:abs(x.truth-x.prediction)).groupby('subhalo_id').ae.mean()
   b=p[(p.target==target)&(p.aperture=='fixed12')&(p.bands=='nir')&(p['mode']=='glao')&(p.model==model)].assign(ae=lambda x:abs(x.truth-x.prediction)).groupby('subhalo_id').ae.mean()
   d=(a-b).to_numpy();rng=np.random.default_rng(20261028);boot=d[rng.integers(len(d),size=(5000,len(d)))].mean(axis=1);gains.append(dict(target=target,model=model,gain=float(d.mean()),lo=float(np.quantile(boot,.025)),hi=float(np.quantile(boot,.975))))
 gains=pd.DataFrame(gains);gains.to_csv(O/('final_GLAO_comparison.csv' if hasfinal else 'validation_GLAO_comparison.csv'),index=False)
 gp=gains[gains.target.isin(targets[:3])&gains.model.isin(['ridge_photo','ridge_summary','ridge_spatial'])]
 positive=gp[gp.lo>0];negative=gp[gp.hi<0];zero=len(gp)-len(positive)-len(negative)
 finalnote='The final 20 were opened once, only after the immutable method/model/settings bundle was recorded. No final-driven tuning, feature revision, model refit or second evaluation was performed. See `FINAL_PROTOCOL_FROZEN.json` and `final_evaluation_started.json`.' if hasfinal else 'The pre-existing pipeline completed the project’s single frozen final evaluation in ../ml_expanded_20261028/. These supplementary models remain validation-only and were never evaluated on the final galaxies. Consult project_continuation_report.md for the verified canonical final results; no second final scoring is performed here.'
 text=f'''# Supplementary grouped validation: ULTIMATE–Subaru ML feasibility

Executed continuation, 2026-10-28, existing phd environment. Earlier analyses are preserved. Scope: useful attenuation statistics and morphology-bias prediction from conditional optical/NIR mocks, with explicit failure cases.

## Scientific decision

The expanded experiment tests prediction of **signed DR1 dusty/clear paired-image differences**. It does not resolve their physical calibration: zero-projected-dust galaxies retain systematic spectral and spatial residuals. Model MAE cannot be interpreted as equivalent physical dust precision. A paper on a carefully qualified benchmark is feasible; a validated observer-frame ULTIMATE dust-geometry forecast or unique three-dimensional reconstruction is not established.

{chr(10).join(line)}

{finalnote}

## Sample and provenance

All 120 archives are present. Independently recomputed compressed SHA256 and byte lengths match the downloader's CRC/tar-validated records; no duplicate download was started. Frozen assignments remain 86 development, 14 validation, 20 final. Nonfinal audit independently checks 500 views/3500 cache arrays and 24000 FITS headers; 6240 original26 member hashes match previous inventories. Units: MJy/sr for images, Msun/pc² for projected dust. Band identity is supplied by archive basenames because the analytic FITS headers have no filter keyword; names alone do not prove historical filter-response equivalence. g/J/Ks and dust full arrays are validated; other bands have header/member-hash checks. Failed source preparations:0.

Nonfinal zero-field controls: 13, including the original four. All remain in their frozen galaxy partition; source-null status excludes development controls from fits, never reassigns them to the final set. No SFR-based dust-free classification is used.

{table(counts)}

Equal-galaxy metrics describe this deliberately selected mass/activity sample. They are not volume-weighted population estimates. Five views include antipodal directions; neither views nor noise draws are independent galaxies. Physical stellar mass, SFR and dust are diagnostic columns only, absent from predictor allowlists.

## Target reliability and aperture definition

A_g=−2.5log10(sum dusty/sum clear). ΔR50 and ΔC are native dusty minus clear within the same aperture; C=5log10(R80/R20), first signed cumulative-flux crossings. Smoothed spatial median/IQR use1-kpc Gaussian FWHM, positive finite pixels and clear>1e−4 of peak; valid negative attenuation remains. These are area-weighted effective statistics, not dust mass, optical depth or unique 3D geometry.

Fixed12 is a circular R<12kpc aperture at the known origin. Adaptive R=clip(1.5 R80 measured within R35 in the deep dusty-Ks seeing reference,8,30)kpc. This reduces some truncation but uses a finite reference and idealized deep Ks segmentation. It is not a validated total-light aperture, especially when capped; flags retain capped/minimum-limited and <90% R35-flux cases. Because adaptive selection uses NIR, the strict optical-only information comparison uses fixed12 as primary. Alternative aperture results change the estimand rather than supplying random label-error draws.

{table(ap)}

Old-four matched-operator control envelopes, defined from the original controls only; the integrated-Ks extension follows the same policy before final freezing:

{table(env[['aperture','target','max_abs']])}

No envelope is subtracted, treated as sigma, or used to force targets to zero. The large adaptive concentration residual is retained. Direct raw/cache matches and common units/WCS disfavor local processing as the primary integrated-offset cause. Full160-kpc g control offsets persist near0.121mag, with alternating signs across filters. Smoothing reduces normalized spatial residuals, compatible with a Monte Carlo contribution; it cannot explain the coherent integrated band pattern alone. Different analytic-probe versus Monte Carlo spectral/filter operators are a leading candidate, not a demonstrated historical configuration error. Source-owner NoMedium runs with frozen particle SEDs/filters, convolve=false/true and repeated photon seeds are required to settle this. See the existing source audit in `../ml_expanded_20261028/label_audit/source_label_report.md`.

## Training and {stage} predictions

Only observed dusty-image fluxes, colours, radii, concentration, q, asymmetry, radial fractions, colour gradients, angular harmonics, texture and normalized8×8 cells enter X. Metadata, clear images, target columns, true dust/stellar maps and galaxy IDs never enter X. Constant median/mean, photometric ridge, summary ridge, random forest, gradient boosting and spatial ridge are all retained. A photometric regression is a simple empirical colour/luminosity baseline; the fixed-distance luminosity prior limits transfer.

Five-fold galaxy-grouped development CV chooses settings. Median imputation and scaling fit inside each fold. Ridge alpha1/10/100/1000; forest120trees with leaf8/24 and max_features0.75; boosting100depth2trees, learning_rate0.04, Huber loss, leaf12/32. Validation never selects hyperparameters. The development tuning scores are not unbiased out-of-sample performance. Independent validation/final metrics average absolute/squared error within galaxy, then equally across galaxies. RMSE=sqrt(mean galaxy MSE). MAE95% intervals resample galaxies conditional on the fitted models; they do not include retraining or unknown source-product systematics.

{stage} fixed12, nominal seeing g/J/Ks MAE (mag for attenuation, kpc for ΔR50, dimensionless ΔC):

{table(pivot.reset_index())}

The median-attenuation and IQR targets remain exploratory, with every unsuccessful model in the table. An improvement would concern an effective projected statistic; it does not uniquely identify geometry. Full per-view/draw predictions, signed residuals, MAE/RMSE/bias and empirical baseline comparisons are saved.

![Validation model comparison](figures/model_comparison.png)
![Validation predictions and residuals](figures/predictions_residuals.png)

## Does GLAO add information?

The comparison fixes galaxies, bands, sampling and1h per band. Optical g stays0.700arcsec in both modes. Nominal Gaussian J widths0.658/0.508arcsec and Ks0.588/0.390arcsec are inherited provisional scenarios; this is not a new claim of a measured0.2arcsec ULTIMATE PSF. Optical-only g versus g/J/Ks separates extra bands from seeing/GLAO resolution, but1versus3hours total is an information ablation, not equal-total-time efficiency.

{stage} seeing MAE minus GLAO MAE, positive denotes improvement:

{table(gp)}

Among these nine prelisted ridge/primary-target comparisons, {len(positive)} intervals are wholly positive, {len(negative)} wholly negative and {zero} cross zero. These are marginal conditional intervals across a larger family of comparisons, with no multiplicity-adjusted detection claim. A robust physical-inference benefit cannot be inferred from a single favorable cell. `paired_galaxy_comparisons.csv` separately records the extra-NIR-band contribution on validation14. Equal-noise/noiseless scoring uses nominal-trained frozen models and therefore diagnoses sensitivity; it does not claim matched-condition retraining.

![Validation GLAO increment](figures/GLAO_increment.png)

A smaller PSF can preserve dusty morphology while failing to improve prediction of a subtle paired dust difference. Compression, finite independent sample size, source-label residuals and population–dust degeneracy remain competing limits. Earlier full-pixel known-pair separation showed that aperture compression can discard information; the present8×8-cell ridge experiment is a bounded spatial-feature test, not a validated full-image generative inference.

## Morphology correction

`morphology_correction_accuracy.csv` compares observed dusty morphology before/after subtracting the predicted native pair bias with the native clear reference. A separate native correction isolates pair-bias prediction from PSF/noise effects. Predicting the pair bias well does not automatically eliminate the PSF contribution. Constant and photometric corrections remain explicit comparators, including adverse galaxies and viewing directions.

![Validation corrected morphology](figures/morphology_correction.png)

## Calibration, OOD and learning curves

Seven validation galaxies calibrate each80% simultaneous galaxy interval via maximum absolute residual across all views/draws; seven different validation galaxies assess coverage. With seven calibrators rankceil(8×0.8)=7 uses the maximum; widths may be broad. The validation selection, small counts and source-label systematics preclude an unqualified population coverage guarantee. `uncertainty_calibration.csv` retains entire-galaxy and row coverage separately. If final scores exist, final 20 assess the same frozen widths independently.

![Validation interval assessment](figures/interval_assessment.png)

The deliberate OOD challenge holds out the development upper stellar-mass quartile and retunes on lower-mass training galaxies only. It is a same-simulation covariate shift, not simulation-to-real validation. `OOD_summary.csv` and per-orientation predictions retain failures. Source-null predictions remain a separate challenge. Mass/SFR/dust, apparent q, flux and view diagnostics are saved; apparent q is not known physical inclination and fixed directions are not an isotropic population.

Development learning curves use12/24/48/all available training galaxies per outer fold, with tuning repeated within each subset. Fold scatter is descriptive, not an independent-galaxy confidence interval. These curves assess whether model variance still changes with sample size; they cannot establish that more same-source data remove systematic label or simulation-domain error.

![Development learning curves](figures/learning_curves.png)

## Empirical HAWK-I-informed sensitivity

Existing ESO reduced NGC3256 products supply PSF/noise information only. Candidate median FWHM0.3166arcsec differs from the nine quality-selected2MASS associations'0.2935arcsec; beta and q are selection-dependent. Sensitivity uses beta3.7415/q0.8199 for elliptical NIR wings at nominal D50; a separately named HAWK-I-shape condition uses actual0.2935arcsec Ks FWHM in the assisted branch. Optical g remains unchanged. This is not evidence for a real0.2arcsec ULTIMATE PSF.

O1/two-draw sensitivity includes nominal, local covariance, an explicit added long-scale component, wings, HAWK-I shape,0.2arcsec sampling and quarter surface brightness. Coarser pixels scale sky variance by pixel area while retaining per-pixel read/dark terms. Local covariance reproduces adjacent rho≈0.28–0.29, but gives R32 aperture excess≈1.59 rather than measured3.42; the long-component stress gives≈2.72 and is deliberately not described as a calibrated ESO covariance model. No ADU noise amplitude is transplanted into simulation electrons. Field PSF variation, anisotropic sky, real masks/centering and full covariance remain unvalidated.

Frozen models score these inputs without retuning. O1 sensitivity is not the full-five-view primary benchmark. `sensitivity_summary.csv` retains all outcomes; `hawki_collaborator_manifest.md` and two small CSV manifests list relevant existing reduced products/calibration references without packaging or transfer. The collaborator's independent raw reduction is not duplicated. HAWK-I supplies neither dust truth nor independent validation of ML attenuation.

![Validation HAWK-I-informed stress](figures/empirical_stress.png)

## Literature and publication assessment

[Fu et al.2025](https://academic.oup.com/mnras/article/540/3/2081/8140852) provides a direct image-based attenuation-ML precedent using high-redshift IllustrisTNG/JWST mocks and CNNs. Its epoch, bands and parametrized dust targets differ from these low-redshift paired morphology labels; agreement with an SED-fitting estimator is model-dependent. Our added value must be controlled instrumental information tests, interpretable baselines and grouped generalization, rather than the first use of ML for attenuation.

The closest verified Dobbels reference is [Dobbels & Baes2021, A&A655A34](https://arxiv.org/abs/2110.01704), which predicts resolved dust luminosity/mass/temperature maps from UV–MIR images. The requested “Dobbels et al.2022” was not uniquely identified and is not silently relabelled. Their galaxy-to-galaxy bias motivates group-held-out tests; emission/SED-derived targets are distinct from paired attenuation truth.

[Bokona Tulu et al.2026](https://arxiv.org/abs/2605.20886) already studies wavelength and dust dependence of nonparametric morphology in the1154-galaxy TSA. Their StatMorph operator differs from ours. Rediscovering dust-dependent morphology is insufficient novelty. [DeepMerge II](https://arxiv.org/abs/2103.01373) shows that simulation/observation domain shifts can degrade astronomical ML and that domain adaptation can help classification; this does not validate calibration of a continuous dust target here.

A publishable contribution is a transparent **conditional surrogate benchmark** establishing which effective pair statistics beat empirical baselines, which corrections survive aperture/systematic tests and whether NIR resolution contributes beyond photometry. Required before a physical ULTIMATE forecast: historical source/filter operator reconciliation; packet uncertainty/convergence; observer-frame spectral/instrument synthesis; independent stellar-population prescriptions and cross-simulation tests; calibrated field-dependent PSFs, sky/covariance, depth and segmentation; external attenuation constraints with their own model uncertainty. Large CNN/U-Net training would not remove these prerequisites.

The earlier98.4% screen false-positive failure, failed forward-model predictive adequacy, unsuccessful spatial median and weak GLAO results remain evidence. This continuation does not replace them with an unsupported3D-geometry success claim.
'''
 (O/'scientific_report.md').write_text(text)
 workshop=f'''# Workshop summary — actual expanded results

**Beyond the Foreground Screen: Machine-Learning Dust Geometry with ULTIMATE-Subaru**

A120-galaxy DR1 inventory is verified, preserving86/14/20 galaxy partitions. Models use observable g/J/Ks photometry and bounded spatial features; dust-free images and simulation physics enter labels/scoring only. All five views and noise draws remain grouped by galaxy.

{stage} numerical results, nominal seeing fixed12:

{chr(10).join(line)}

The comparison distinguishes additional NIR bands from narrower NIR PSFs. All favorable and adverse resolution outcomes are retained; multiple comparisons and conditional observing assumptions limit instrument claims. Signed source-control residuals and aperture-dependent labels prevent equating predictive accuracy with physical dust precision.

The strongest defensible message is learning selected effective attenuation statistics and morphology-bias corrections relative to simple baselines. This is neither unique3D dust-geometry recovery nor a validated observer-frame ULTIMATE forecast. Empirical HAWK-I PSF/covariance tests improve realism but supply no dust truth. Source/filter calibration and simulation-to-observation transfer remain the publication-critical next evidence.

{finalnote}
'''
 (O/'workshop_summary.md').write_text(workshop)
 print(stage,'report written')
if __name__=='__main__':run()
