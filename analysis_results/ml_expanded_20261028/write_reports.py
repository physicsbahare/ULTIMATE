"""Write source-backed reports from the completed frozen evaluation."""
from datetime import datetime,timezone
import json,shutil
import numpy as np
import pandas as pd
from expanded_features import O,PART,TARGETS

def mdtable(table):
    names=list(table.columns);lines=['| '+' | '.join(names)+' |','|'+'|'.join(['---']*len(names))+'|']
    for row in table.itertuples(index=False,name=None):
        lines.append('| '+' | '.join(f'{v:.4f}' if isinstance(v,(float,np.floating)) else str(v) for v in row)+' |')
    return '\n'.join(lines)

def run():
    assert (O/'FINAL_EVALUATION_COMPLETED.json').exists()
    labels=pd.concat([pd.read_csv(O/'target_table.csv'),pd.read_csv(O/'final_target_table.csv')],ignore_index=True)
    meta=pd.read_csv(PART)
    quality=labels.groupby('subhalo_id').agg(zero_projected_dust=('zero_projected_dust','first'),dust_mass_field_Msun=('dust_mass_field_Msun','first'),median_adaptive_radius_kpc=('radius_kpc','median'),any_aperture_limited=('reference_aperture_limited','any'))
    # Report adaptive radii rather than the median of fixed and adaptive operators.
    quality['median_adaptive_radius_kpc']=labels[labels.aperture=='adaptive'].groupby('subhalo_id').radius_kpc.median()
    inventory=meta.merge(quality,on='subhalo_id',validate='one_to_one')
    inventory['archive_integrity_verified']=True;inventory['FITS_pairing_units_grid_verified']=True
    inventory['selected_g_J_Ks_and_dust_pixels_verified']=True
    inventory['physical_label_source_systematic_unresolved']=True
    inventory['primary_fit_or_scoring_eligible']=~inventory.zero_projected_dust
    inventory['all_views_grouped']=True;inventory['final_science_opened_after_freeze']=inventory.partition.eq('final_test')
    inventory['stage_role']=np.where(inventory.zero_projected_dust,'source_control',inventory.partition)
    inventory.to_csv(O/'expanded_galaxy_inventory.csv',index=False)
    inventory.groupby(['partition','zero_projected_dust']).size().rename('n_galaxies').reset_index().to_csv(O/'sample_quality_counts.csv',index=False)
    summary=pd.read_csv(O/'performance_summary.csv');recommended=pd.read_csv(O/'recommended_performance.csv')
    final=summary.query("evaluation=='final_test' and aperture=='adaptive'")
    rec=recommended.query("evaluation=='final_test' and aperture=='adaptive'")
    gains=pd.read_csv(O/'recommended_gains.csv');gain=gains.query("evaluation=='final_test' and aperture=='adaptive' and comparison=='seeing_minus_GLAO_MAE'")
    rows=[]
    for target in TARGETS:
        p=final[final.target==target];r=rec[rec.target==target].set_index('scenario');base=p.query("family=='median' and scenario=='seeing_NIR'").iloc[0]
        phot=p.query("family=='phot_ridge' and scenario=='seeing_NIR'").iloc[0]
        g=gain[gain.target==target].iloc[0]
        rows.append(dict(target=target,constant=base.MAE,phot_seeing=phot.MAE,optical=r.loc['optical','MAE'],seeing=r.loc['seeing_NIR','MAE'],GLAO=r.loc['GLAO_NIR','MAE'],GLAO_RMSE=r.loc['GLAO_NIR','RMSE'],gain=g.gain,gain_low=g.low,gain_high=g.high))
    table=pd.DataFrame(rows);table.to_csv(O/'workshop_key_numbers.csv',index=False)
    count=inventory.groupby(['partition','zero_projected_dust']).size()
    nfinal=int(inventory.query("partition=='final_test' and not zero_projected_dust").shape[0])
    ncontrol=int(inventory.query("partition=='final_test' and zero_projected_dust").shape[0])
    correction=rec[rec.target.isin(['dR50_Ks','dC_Ks'])][['scenario','target','uncorrected_MAE','corrected_MAE','MAE']]
    coverage=rec[rec.scenario=='GLAO_NIR'][['target','n_galaxies','bias','galaxy_coverage','point_coverage']]
    reliable=gain[gain.low>0].target.to_list();adverse=gain[gain.high<0].target.to_list()
    interpretation=('Paired intervals support positive conditional resolution gains for '+', '.join(reliable)+'.') if reliable else 'None of the eight recommended-model final paired GLAO-gain intervals excludes zero on the positive side.'
    if adverse:interpretation+=' Intervals support adverse effects for '+', '.join(adverse)+'.'
    full=shutil.disk_usage(O);free=full.free/2**30
    manifest=json.loads((O/'FINAL_PROTOCOL_FROZEN.json').read_text())
    text=f'''# Expanded ULTIMATE-like interpretable ML feasibility study

Completed {datetime.now(timezone.utc).isoformat()}. All numerical tables below come from the single frozen final evaluation; no final-outcome tuning or model reselection occurred.

## Main result and scope

All **120 independent galaxy IDs / 600 orientations** were prepared and verified. The original frozen assignment remains 86 development, 14 validation and 20 final evaluation. Twelve development and one validation galaxy have exactly zero projected dust fields: **74 galaxies fit models**, **13 calibrate intervals**. The final set contains **{nfinal} primary positive-dust galaxies and {ncontrol} source controls**. Every orientation and noise draw stays with its galaxy. These are independent subhalo sampling units within one simulation, not independent simulation volumes or orientations.

The predictions learn **operational dusty-minus-clear DR1 image-product contrasts**. A coherent full-field offset of ≈0.12 mag in four exact-zero-dust control galaxies remains unexplained. High predictive accuracy therefore does not establish equally accurate physical dust attenuation. Physical attenuation calibration is a publication gate. No universal offset was subtracted and no negative attenuation, adverse orientation or failed target was hidden.

{interpretation} This addresses extra NIR resolution conditional on these images, features, noise assumptions and fixed models. Additional NIR bands and GLAO resolution are separate comparisons. The optical+NIR experiment uses one hour per band, hence more total time than g alone. Adaptive g-feature models share a deep Ks-defined reference aperture and are not a fully g-selected survey pipeline; fixed12 results supply the cleaner optical-only aperture control.

## Final out-of-sample accuracy

All entries are equal-galaxy MAE except the named RMSE column. Attenuation values are magnitudes, R50 differences kpc, concentration dimensionless. Constant is the development median; photometric ridge is independently selected within its family using development folds. Recommended family/settings are frozen by development CV mean over both NIR strategies; they are not the best model selected after seeing final outcomes.

{mdtable(table)}

Gain = seeing MAE − GLAO MAE; positive favors GLAO. The bounds are 95% percentile intervals from **5000 paired galaxy bootstrap draws**, conditional on the fitted models. They do not include retraining, uncertain source labels, simulation-to-observation shift or selection uncertainty. Eight targets and many model/condition comparisons are exploratory; no multiple-testing correction was used. A single favorable interval is not an omnibus instrument claim.

The package preserves all eight model families, optical/seeing-NIR/GLAO-NIR scenarios, both apertures, all per-orientation/four-noise-draw predictions, constants and approximate screen-color baselines. `performance_summary.csv` and `paired_galaxy_gains.csv` retain unfavorable or weaker-than-photometry results. Simple photometry can be superior; the extra spatial features are not assumed to help.

## Morphology correction versus prediction of dust bias

{mdtable(correction)}

Uncorrected and corrected errors compare observed dusty morphology to **native clear** morphology; correction subtracts predicted native dusty-minus-clear bias. Thus PSF and measurement errors remain. A better corrected morphology under GLAO can reflect improved PSF transfer even when the predicted dust difference has no reliable resolution gain. This is not deconvolution and does not identify an individual feature as dust.

## Calibration, scatter and failures

Nominal80% intervals use the rank12 order statistic of maximum absolute residual over all five views and four draws for each of 13 calibration galaxies, separately for each target and model. This is a cluster-level split-conformal construction under exchangeable galaxies, not joint coverage across eight targets or a calibrated error on physical truth. Validation coverage used the calibration sample itself and is descriptive; the following final coverages are genuinely held out, although based on only {nfinal} primary galaxies.

{mdtable(coverage)}

`galaxy_metrics.csv` retains individual objects and `within_view_noise_and_orientation_residuals.csv` separates repeated-draw scatter from view means. `property_stratified_errors.csv` reports descriptive stellar mass, SFR, projected dust content, apparent axis ratio and surface-brightness strata. Axis ratio is not true inclination; zero SFR is not zero dust. `observable_distance.csv` measures nearest-development distance using training-only standardized observable summaries. The high-mass held-out-quartile experiment uses fixed ridge10 and excludes all upper-quartile galaxy views from training; it is an internal covariate-shift diagnostic, not independent simulation-to-real validation.

Learning curves use 12/24/48/74 independent development galaxies and three fixed subset seeds, with settings frozen by the full development CV. The 13 validation galaxies are unchanged. Their shaded seed range is not a population confidence interval. No new complex image network was trained; spatial features use explicit radial fractions, harmonics, texture and training-only PCA8 of 8×8 image cells. This tests coarse image information beyond aperture compression without a large CNN.

## Labels, apertures and source controls

Targets are integrated signed effective attenuation in actual LSST g and 2MASS Ks, g attenuation median/IQR after 1-kpc FWHM smoothing, and paired native ΔR50/ΔC in g/Ks. Concentration is 5log10(R80/R20). Paired products share origin, mask, sampling and aperture. Spatial ratios require finite positive clear/dusty smoothed flux and clear >1e-4 of its peak inside the aperture; negative effective attenuation remains valid. Dust-free truth supplies supervision/scoring only. No physical map or simulator metadata enters the predictor allowlist.

Primary radius = clip(1.5R80,8,30) kpc, derived from a common seeing-convolved **dusty** Ks reference within R35; fixed12 is a sensitivity. The deep-reference radius has no propagated measurement uncertainty, known distance and fixed center are assumed, and finite R35 light truncation/clipping are flagged. `aperture_target_sensitivity.png` and target tables show operator dependence; they are not measurements of total light.

The focused20-nonfinal-galaxy O1 test changes radius by ±20% and center by0.5 kpc in each direction. For 14 validation objects, radius×0.8 changes |Ag| by median0.0190 mag, |ΔR50Ks| by0.0229 kpc and |ΔCKs| by0.0321. Center offsets change |ΔCKs| by median0.047–0.079 and up to0.447. Hence concentration correction is materially sensitive to center definition. Full details and exact direct-geometry checks are in `instrument_sensitivity/center_aperture_report.md`.

Four historical controls were freshly decoded from original full-field products: matching units/WCS/cached pixels, zero dust maps and persistent band-dependent integrated offsets were confirmed. Across22 bands, signs alternate (e.g. g positive, r/z/FUV negative); this is not a simple extinction law or cropped-aperture explanation. Spatial RMS declines after smoothing, consistent with an additional Monte Carlo component, but the integrated systematic is not adequately explained by zero-mean Monte Carlo noise. Analytic clear-source projections versus Monte Carlo dusty instruments, potentially with differing spectral integration, are plausible source mechanisms; historical .ski/SED/filter configuration is unavailable and the cause is **unresolved**, not established as a particular SKIRT error.

`old_control_operator_envelopes.csv` is descriptive only. Adaptive old-four control maxima include Ag0.12433 mag, AKs0.02259 mag, ΔR50Ks0.03749 kpc and ΔCKs0.23982. They are not sigma values, universal thresholds or calibrated systematic bounds. All newly identified exact-zero-dust cases follow the predeclared separate-control policy, including final cases. Exclusion from fitting does not remove source-systematic uncertainty for positive-dust galaxies.

## Observing assumptions and HAWK-I sensitivities

Fixed-rest-band z=0.1/1h,0.1-arcsec pixels and inherited band-dependent Gaussian PSFs use validated angular resampling, flux transfer and source/sky/thermal/dark/read variance components. g remains0.7 arcsec; nominal Ks is≈0.588/0.390 arcsec seeing/GLAO. These are **provisional conditional resolution experiments**, not exact observer-frame ULTIMATE forecasts. The galaxies do not evolve with assigned distance. Rest Ks shifts outside ordinary observer Ks at this redshift; 2MASS filters are not ULTIMATE passbands. Four Gaussian moment-noise draws are paired across strategies; rare-tail detector and sky residuals are not fully modeled.

The official reduced HAWK-I products were reused; no raw-data reduction was duplicated and no new large observations downloaded. Previous empirical measurements: median compact-candidate FWHM≈0.317 arcsec (103 candidates), quality2MASS-associated FWHM≈0.294 arcsec (9 sources), Moffat beta≈3.74, adjacent background correlations≈0.28–0.29. These describe those HAWK-I conditions, not a calibrated ULTIMATE PSF; they provide neither dust truth nor0.2-arcsec image information.

`instrument_sensitivity/` keeps four predeclared O1-only cases on20 nonfinal galaxies: A baseline Gaussian; B empirical-informed Ks Moffat wings at the **same nominal D50**; C B plus local correlated noise preserving marginal variance; D flux/variance-preserving2×2 software binning of A. Existing nominal models are applied without retuning. Only Ks wings change; g remains seeing-limited. The local covariance model does not reproduce measured large-aperture excess (≈3.42× pixel-noise prediction) or full sky structure. `instrument_stress_predictions_summary.csv` reports all outcomes and uncertainty/gains. `shift_and_noise_predictions_summary.csv` separately tests common added variance and noiseless conditions with settings held fixed, isolating noise assumptions from additional bands. Morphology A/texture features remain noisy without empirical noise subtraction.

`instrument_sensitivity/hawki_sharing_manifest.csv` lists six existing reduced/calibration product references, paths, sizes, checksums and official links for potential collaborator use. No large products were packaged or transferred. Actual collaborator raw reduction remains independent.

## Selection, verification and resource use

The existing secure downloader completed94/94 new DR1 archives before this stage. Current hashes and sizes match recorded gzipCRC/tar integrity proofs for all120; all archives were then streamed, without full extraction. The100 nonfinal stage checked24000 FITS headers/3500 selected full arrays; final20 added4800 headers/700 arrays only after the frozen receipt. All22 bands have paired header/member validation; only g/J/Ks and projected dust arrays have full numerical pixel checks. Units/grid/filter identities are explicit; filenames identify actual source filters when header filter keywords are absent. Native pixels100pc; source1600², reusable seven-array central800² caches. No duplicate download, full TNG snapshot or new software installation occurred. Current available disk≈{free:.1f} GiB, exceeding100GiB.

Original26 raw member hashes agree (6240 matches), benchmark294866 R12 R50/C/q reproduce to machine precision and attenuation to3.5e-16; tiny A differences reflect float32 order. Four meaningful numerical tests pass, with pre-final grouped/allowlist/calibration/transfer checks and postfinal disjointness/hash checks.136 artifacts were frozen before scientific access to final20; all20 were evaluated once. Existing result manifests verify1056 files unchanged. Exact stage receipts and logs are retained rather than overwriting old status reports.

The saved official DR1 catalogue has1154 galaxies. Selection of the94 new galaxies balanced five mass ×five activity strata (zero SFR plus four positive-sSFR groups), conditional quota3/4 per stratum with recorded inclusion/partition probabilities. Original26 are historically chosen and only development. Official selection metadata lack true dust mass, morphology class and inclination: gas proxies are not substitutes. Dust/morphology coverage is characterized after acquisition, not claimed as direct dust-stratified selection. The sample is not volume-complete, host-environment-independent or representative of all TNG50 galaxies. Single-simulation correlations and finite final N limit universality and scaling-law precision.

## Publication assessment and literature

A workshop presentation is supported by the executed grouped benchmark, transparent source-control failure, comparison with photometric baselines, native-morphology correction and conditional resolution tests. Strong figures are `model_and_observing_strategy_comparison`, `paired_GLAO_gains`, `learning_curves`, `aperture_target_sensitivity`, and the predeclared lowest/median/highest-error galaxy examples. Include negative/no-gain targets and the source-label caveat on the main results slides.

A dedicated paper is **not yet a validated physical-dust or universal ULTIMATE performance demonstration**. The immediate gate is obtaining historical DR1 simulation/filter configuration or corrected matched products and demonstrating calibrated zero-dust/positive-dust labels. Additional requirements: propagate centroid/segmentation/background uncertainty; verify spectral/observer-frame transformations and instrument throughput/PSF/noise with current design information; test independent simulations/observations and realistic population/redshift selection; assess robustness with more independent calibration/test galaxies. This final20 has been spent once and must not become a tuning set; future revisions need a new independent holdout or a clearly labelled post-test study. HAWK-I constrains instrumental nuisance experiments only.

[Fu et al.2025](https://academic.oup.com/mnras/article/540/3/2081/8140852) already predicts attenuation from simulated high-redshift JWST images. The closest verified resolved-dust mapping reference is [Dobbels & Baes2021](https://arxiv.org/abs/2110.01704), A&A655A34; the requested2022 item was not uniquely identified and should not be silently misdated. [Bokona Tulu et al.2026](https://arxiv.org/html/2605.20886v1) directly studies dust/wavelength morphology using the same1154-galaxy atlas. [Baes et al.2024 methodology](https://arxiv.org/html/2401.04224v1) and [effective-radii work](https://arxiv.org/abs/2401.04225) constrain interpretation. [DeepMergeII](https://arxiv.org/abs/2103.01373) illustrates the separate simulation-to-observation transfer problem. The defensible novelty here is calibrated, grouped **incremental NIR-resolution value**, observable-only morphology-bias correction and explicit failure/control accounting, rather than first dust ML or unique3D geometry recovery. See `label_audit/literature_context.md` for source details.
'''
    baseline_gains=gains.query("evaluation=='final_test' and aperture=='adaptive' and scenario=='seeing_NIR' and comparison in ['median_minus_model_MAE','phot_ridge_minus_model_MAE']")
    physical_transfer=pd.read_csv(O/'final_native_dusty_morphology_transfer_summary.csv')
    correction_gains=pd.read_csv(O/'final_morphology_correction_gains.csv')
    learning=pd.read_csv(O/'learning_curves.csv').query("target in ['A_g','dR50_Ks','dC_Ks'] and n_training_galaxies in [12,74]").groupby(['scenario','target','n_training_galaxies']).MAE.mean().reset_index()
    controls=pd.read_csv(O/'source_control_recommended_summary.csv').query("partition=='final_test' and scenario=='GLAO_NIR' and target in ['A_g','A_g_p50_1kpc','A_g_IQR_1kpc','dR50_Ks','dC_Ks']")
    extra=f'''## Additional quantitative checks

**Improvement beyond baselines:** the integrated-g model strongly improves on the constant, but its incremental gain over photometric ridge has a 95% interval spanning zero. The Ks R50 reduction in point MAE is promising, but its paired interval versus the constant also spans zero. Ks concentration and spatial IQR have positive paired gains over both these baselines, conditional on their label and measurement limitations. The expanded spatial median target improves modestly over the constant, unlike the initial22-galaxy experiment; however its final GLAO RMSE0.1397 mag far exceeds MAE0.0441, showing an important error tail. Do not describe this as uniformly reliable resolved attenuation recovery.

{mdtable(baseline_gains[['target','comparison','gain','low','high']])}

**Absolute PSF/noise morphology transfer:** comparing observed dusty to native dusty directly gives:

{mdtable(physical_transfer)}

These errors depend on PSF resolution even with no learned dust correction. The paired gains are:

{mdtable(correction_gains)}

Native-dusty R50 transfer improves by0.0642kpc [0.0398,0.0890]; after the frozen learned dust correction, native-clear R50 error improves by0.0349kpc [0.0091,0.0633]. These are resolution/morphology benefits, while the dust-bias prediction gain itself remains consistent with zero. This distinction is central to the instrument interpretation.

**Learning from more independent galaxies:** three-seed mean validation MAE at12 and74 development objects:

{mdtable(learning)}

The trend motivates more calibrated training data, but does not remove source bias or prove a universal learning law. **Final source-control behavior:**

{mdtable(controls[['target','n_galaxies','operational_MAE','signed_mean_prediction','mean_atlas_contrast']])}

For the four final zero-projected-dust source controls, the mean predicted g contrast≈0.199mag exceeds their mean atlas contrast≈0.121mag. These failures are preserved rather than trained away. Their spatial median can be predicted accurately as an operator contrast without establishing physical attenuation. Exact-zero projected fields are a challenge/control condition, not verified full three-dimensional absence of all attenuation processes. `observable_OOD_summary.csv` gives exploratory training-distance strata, with a95th-percentile nearest-neighbor threshold determined only from development features; this post-evaluation diagnostic does not change models, calibration or primary performance.

'''
    extra+='''The spatial-target scatter figure explicitly shows regression toward typical values and failure on highly attenuated/inhomogeneous views. The development spatial median range ends at0.977mag, versus a final maximum1.329mag; the IQR maximum is0.815mag in development versus1.544mag in final. Tree regressors cannot extrapolate the training target range, and the features may remain degenerate even with more data. These truth-range diagnostics (`target_range_diagnostics.csv`) are post-evaluation explanations, not observationally available OOD flags or a reason to exclude difficult final cases. Empirical HAWK-I ellipticity and full field-dependent PSF variation have not been propagated; the current wing stress uses circular kernels. These remain additional instrumental-transfer requirements.

'''
    text=text.replace('## Publication assessment and literature',extra+'## Publication assessment and literature')
    (O/'scientific_report.md').write_text(text)
    workshop=f'''# Beyond the Foreground Screen — workshop results

**120 verified galaxies;74 development fits,13 calibration galaxies;{nfinal} untouched positive-dust final galaxies plus{ncontrol} final source controls.** Frozen86/14/20 assignments, grouped5-fold development selection, one final evaluation; four noise draws×five correlated views per galaxy.

Operational DR1 contrasts, **not yet calibrated physical attenuation**. Four exact-zero-dust source controls retain≈0.12-mag g offsets; no global subtraction. No unique3D geometry recovery.

{mdtable(table[table.target.isin(['A_g','A_g_p50_1kpc','dR50_Ks','dC_Ks'])][['target','constant','phot_seeing','seeing','GLAO']])}

Values are equal-galaxy MAE. Magnitudes/kpc/dimensionless concentration as appropriate. Recommended models were selected before final access, not by final scores. Constants and photometry remain essential baselines. Paired95% gain intervals are in `workshop_key_numbers.csv` and the gain figure.

{interpretation}

TaskB corrections and PSF transfer must be separated: see `scientific_report.md` and native-clear corrected errors. Concentration is center-sensitive; a0.5-kpc offset changes ΔC materially. GLAO preserving morphology does not establish identification of individual dust structures.

**Slides:** `figures/model_and_observing_strategy_comparison.png`, `paired_GLAO_gains.png`, `prediction_vs_atlas_target.png`, `learning_curves.png`, `representative_success_and_failure_images.png`. PDF counterparts are available.

**Honest conclusion:** workshop-ready as a conditional benchmark with negative results and source controls. Physical-dust/ULTIMATE publication requires source-label calibration, realistic observer-frame/instrument validation and independent domain-transfer tests. HAWK-I informs nuisance tests, not dust truth or a calibrated ULTIMATE PSF. The final20 is now used and must not be retuned upon.
'''
    (O/'workshop_summary.md').write_text(workshop)
    print('Inventory, numerical workshop table, scientific report and workshop summary written.')

if __name__=='__main__':run()
