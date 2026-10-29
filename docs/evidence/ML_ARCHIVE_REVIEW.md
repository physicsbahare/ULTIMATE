# Read-only ML archive review

Review date: 2026-10-29. Scope: `analysis_results/ml_feasibility_20261027`, `ml_expanded_20261028`, `ml_validation_20261028`. This review read existing reports, protocols, JSON receipts and CSV tables. No scientific program, training, rendering, inference, extraction, download or result regeneration was executed. Only this `/tmp` review was written. Saved audits are described as saved evidence; this review did not independently rehash all large archives or reproduce their statistical results.

## Authoritative current status

The canonical expanded experiment is `ml_expanded_20261028`. It completed the project's one frozen final20 evaluation. The supplementary experiment in `ml_validation_20261028` is validation-only, with **zero** additional final inference. Its `project_continuation_report.md` is the clearest combined handoff, and its README explicitly reconciles overlapping execution. Do not promote supplementary validation scores to final scores or treat the spent final20 as a fresh holdout. Pilot acquisition reports and pre-unseal READMEs are historical snapshots, not current dataset status.

Completed: 120 galaxies/600 views verified; frozen 86/14/20 assignments preserved; source controls retained; development model selection and validation calibration; one canonical final evaluation; executed notebooks, fitted estimators, per-view/draw predictions, conditional bootstrap metrics, learning curves, OOD/source-control cases, aperture/center/instrument stresses, figures, delivery and preservation checks. Unresolved: physical source-label calibration, observer-frame/instrument transfer, broader selection/domain generalization, and fully realistic centering/segmentation/background/PSF covariance uncertainty. These prevent claims of precise physical dust attenuation, unique 3D geometry or a validated ULTIMATE forecast.

## 1. Chronological experiment record

### 2026-10-27 pilot: grouped feasibility on the already inspected26

Evidence: `ml_feasibility_20261027/{PROTOCOL.md,README.md,scientific_report.md,workshop_results.md,ml_review_notes.md,train_test_provenance.json,preliminary_cv_splits.csv}`.

All26 were development-only. Four zero-projected-dust controls (13,167418,184937,613192) were excluded from fits and interval calibration, leaving22 independent fitting-eligible galaxies, five views each. Seven targets: integrated signed `A_g`, `A_Ks`, smoothed1-kpc g median attenuation, native dusty-minus-clear g/Ks R50 and concentration differences. R12 fixed-origin aperture; known distance/center. 130 label records,6240 feature rows; noiseless rows repeated identically eight times preserve weighting, not independent draws. Features measured solely on dusty observed-image photometry/morphology; IDs, clear images, physical maps, mass/SFR and true inclination excluded from X. Photometry includes absolute apparent g flux, so fixed-distance luminosity prior remains a transfer limitation.

Five galaxy folds (seed20261027), with4/5 outer-test objects, five independent calibration galaxies and12/13 fitting galaxies per fold. Whole views/draws stay with galaxy. Fixed training median, photometric ridge, morphology ridge, full ridge(alpha10), shallow80-tree forest(depth4/minleaf20), without outcome-based tuning. Calibration score is each galaxy's maximum residual over all views/draws; nominal80% uses rankceil(6*.8)=5, the maximum of five scores. Per-target coverage is not joint coverage across targets. Original exact-moment noise, noiseless and equal-added-variance paired mocks distinguish added bands, resolution and noise.

Original-noise GLAO g/J/Ks equal-galaxy MAEs:

| target | constant | photometry | full ridge | forest |
|---|---:|---:|---:|---:|
| Ag | .22122 | .08877 | .09720 | .15304 |
| AKs | .03950 | .01182 | .01038 | .02643 |
| Ag_p50_1kpc | .09999 | .10846 | .12155 | .10267 |
| dR50g | .40651 | .32630 | .28420 | .34951 |
| dR50Ks | .09961 | .06881 | .04928 | .07779 |
| dCg | .43797 | .33929 | .23454 | .36960 |
| dCKs | .11742 | .09664 | .06999 | .10328 |

Pilot conclusion: worthwhile conditional surrogate study; **no robust GLAO ML benefit**. Every full-ridge and forest primary seven-target GLAO interval includes zero. Ridge Ks R50 gain .00018094kpc,95%[-.00094969,.00156720]. Extra NIR information dominates the PSF change, but g-only versus three bands is1h versus3h, not equal total time. Spatial attenuation median fails to beat constant. Native-clear corrected Ks R50 error decreases .17648(raw)→.09768(constant)→.08015(photometry)→.06485(ridge), retaining PSF/noise residuals. g R50 whole-galaxy coverage15/22 and Ag16/22 fall below nominal80%; broad intervals exclude unknown physical-label systematics. High-mass-quartile holdout6/fitting16 gives full-ridge dCg MAE .7675 versus .2345 in CV. Source-null Ks R50 challenge .1672 versus .0493. R12→R30 label changes median .2436kpc(g R50),.0494kpc(Ks), comparable to prediction errors and much larger than GLAO gains.

Saved independent pilot review checks369600 heldout records, exact key grouping, error/summary agreement<=1.7e-16, gains<=3.2e-16, all g-only gains exactly0, correction sign/joins<1e-15, coverage and bootstrap reproduction;49280 stress predictions finite/unique. This review did not rerun those checks.

### 2026-10-27 metadata-only expansion and HAWK-I branch

Selection freeze at2026-10-27T03:47:20.721476+00:00, seed20261027. Official catalogue1154;26 historical objects fixed to development;1128 new eligible. Five mass×five activity strata(zeroSFR+four positive-sSFR groups);19 strata quota4 and6 quota3 gives94 new objects. Uniform without replacement per stratum. Frozen selected94 randomly assigned60development/14validation/20final. Conditional quota inclusion n_h/N_h and marginal(94/25)/N_h are distinguished; old26 have no claimed population sampling probability. Gas-fraction/surface-density proxies do not establish dust mass or morphology classes; no true morphology/inclination/dust selection metadata available. Balanced selected sample is not volume representative.

Pilot acquisition report timestamp04:07:58UTC records12/94 new verified,38/120 total, backgroundPID27948; this is superseded by next-day120 verification. All94 preflight60,164,124,583bytes(56.032GiB). Secure downloader used CRC/tar/SHA checks without final science inspection, resumable chunks,100GiB floor+256MiB headroom; no full snapshot/DR2 download.

HAWK-I branch (`ml_feasibility_20261027/hawki`): ESO reduced NGC3256 programme60.A-9475(A) products available; existing22 local raw science exposures complete. Three certified complete raw-to-master associations, but local master files/EsoRex absent, so no incomplete custom raw reduction claimed. Target-centered Jan6 science/variance/confidence cutouts2364² retain64.18MiB; initial corrected cutout transfer included128.36MiB total. FITS checksums/WCS checked. ScienceADU; VARMAP semantics squared units despite inheritedADU header; confidence is not inverse variance.

103/109 accepted compact candidates: median FWHM .3166arcsec,beta4.753,q.8199,D50.3533arcsec. They are not all confirmed stars; field/sample scatter and analytic wing extrapolation matter. Nine quality2MASS associations: FWHM.29352,beta3.74148; radial separation median.1210arcsec/RMS.1688. HAWKI−transformed2MASS median−.05576mag,robust scatter.13902,RMS.24292,outlier retained. Actual associated PHOTCAL uses .03J+.97Ks, differing from release document's H formula; both retained. 2MASS is pipeline reference too, so this is consistency rather than independent calibration. Background adjacentrho .2753/.2932; R32 noise3.4213×pixel prediction and2.0121×diagonal variance. Local-correlation stresses do not reproduce full aperture noise. Original pilot post-protocol stress deliberately preserves full103 beta4.753; later branches use nine-star beta3.7415 rather than silently retuning the original result. HAWK-I supplies nuisance information, neither dust truth nor ULTIMATE resolution.

### 2026-10-28 canonical expanded protocol and preparation

Evidence: `ml_expanded_20261028/{DEVELOPMENT_PROTOCOL.md,README.md,scientific_report.md,data_audit/README.md,data_audit/final_inventory_audit.md}`.

94/94 acquisition completed. Initial gate checked old294866 and new development571633,578834,319734 before processing other science. Old26 raw hashes6240 match;294866 R12 morphology reproduces to machine precision, attenuation3.5e-16.100 nonfinal archives streamed; only seven central800² arrays/view cached from native1600²/100pc images: g/J/Ks dusty+clear and projected dust. NativeMJy/sr andMsun/pc² units/grids verified;22 band pairs have member/hash/header checks, whereas only selectedg/J/Ks+dust arrays have full numerical checks. Header filter keywords absent: basename identifies bands but does not prove historical spectral-operator equivalence.

New primary aperture: common dusty-Ks seeing-reference R=clip(1.5R80 measured withinR35,8,30)kpc; fixedR12 retained sensitivity. Same aperture for all strategies/bands/noise/clear/dusty. Reference is deep with known center/distance and no fully propagated segmentation/radius noise; not total light. Adaptive optical feature models already condition on NIR aperture; fixed12 is cleaner g-only comparison. Eight targets add smoothedg attenuation IQR to pilot seven; signed valid negative attenuation retained. Spatial stats use1kpcFWHM and clear>1e-4 peak. Source-null flags follow exact projected dust, not zeroSFR.

12 development controls→74 fit;1 validation control→13 interval calibrators. Both apertures, optical/seeingNIR/GLAONIR, four paired noise draws×five views.17 candidate settings×3scenarios×5groupedfolds=255CV fits/checkpoints. Development-only common per-family/target settings selected by mean seeing/GLAO CV MAE. Families: median, approximate screen-color, photometric/summary/spatial ridge, summary/spatial forest, spatialboost; training-only scaling/imputation/PCA8.84 nominal estimator artifacts and24 noise-sensitivity artifacts=108. Validation not used for hyperparameters.13 calibration-galaxy maximum scores give80% rankceil(14*.8)=12; intervals per target, not eight-target simultaneous.5000 paired galaxy bootstrap draws condition on fitted models, omit retraining/source/selection uncertainty.

Recommended frozen settings: Ag summary_ridge_1; AKs summary_ridge_10; Ag_p50 spatial_forest_8; Ag_IQR spatial_boost_3; dR50Ks summary_ridge_1; dCKs spatial_ridge_1; dR50g spatial_ridge_1; dCg spatial_boost_2. These choices precede final and must not be replaced by whichever family happens to score best after final.

### Canonical freeze, final unseal and one evaluation

`FINAL_PROTOCOL_FROZEN.json`:2026-10-28T02:37:19.833340+00:00;136 code/model/calibration/protocol/sensitivity artifacts; SHA256 **587aab56d39e6b29ad47f381c4b1440c8dd28eb52811ebc4ae3842b6fc220ce4**. Scope operational-product contrast only; exact-zero final controls separately retained. Its exact20IDs equal original selection freeze. `PREFINAL_VALIDATION.json`02:36:28 passes disjoint folds, allowlist, finite labels, optical identity,13/rank12calibration and sealed final. Unsealer checks hashes before, during and after extraction, locks concurrent run, binds resume to same receipt. `final_unseal/receipt.json` completed02:42:13.589295UTC:20galaxies/100views/4800headers/700arrays, old100 audit snapshots unchanged. Original audit CSV final rows intentionally retain historical sealed flags; final-only stage rows correctly mark opened status.

`FINAL_EVALUATION_COMPLETED.json`:20galaxies,16primary,4controls,153600predictionrows,`models_retuned=false`,`final_evaluation_count=1`, same freezeSHA. Final source controls14,39,63875,96780. `POSTFINAL_VALIDATION.json`02:58:21 passes. Independent `data_audit/final_inventory_audit.json` rehashes120compressed archives and600cachefiles;28800headers/4200arrays/600physical rows;136frozen artifacts match; no re-extraction/prediction performed. Earlier manifests preserve242pilot+795morphology+19continuation files=1056. Saved audit disk284.6GiB and downloaderPID absence describe audit time, not a new current-process measurement.

Final primary adaptive/nominal scores:

| target | constant MAE | recommended seeing | recommended GLAO | GLAO RMSE | seeing−GLAO gain[95%] |
|---|---:|---:|---:|---:|---|
| Ag | .3003 | .0734 | .0741 | .1098 | −.0007[−.0057,.0042] |
| AKs | .0594 | .0124 | .0124 | .0163 | −.0001[−.0003,.0002] |
| Ag_p50 | .0522 | .0441 | .0441 | .1397 | −.0000[−.0005,.0005] |
| Ag_IQR | .1214 | .0745 | .0707 | .1639 | .0038[−.0003,.0079] |
| dR50Ks | .1282 | .0777 | .0799 | .1189 | −.0022[−.0077,.0026] |
| dCKs | .1521 | .0887 | .0887 | .1306 | .0000[−.0121,.0127] |
| dR50g | .4939 | .2044 | .2236 | .3167 | −.0192[−.0341,−.0062] |
| dCg | .4808 | .2339 | .2445 | .3277 | −.0106[−.0225,.0021] |

No recommended GLAO dust-bias interval wholly positive; gR50 worsens. Integratedg incremental gain over photometric baseline spans0; KsR50 versus constant also spans0. Ksconcentration and spatialIQR beat both baselines conditionally. Photometry stays competitive: final GLAOAg .0793 versus spatialboost .0971 andforests~.135; approximate screen .2720. Expanded spatial median revises pilot failure but MAE.0441/RMSE.1397 exposes heavy failure tail. Final p50 maximum1.329mag versus development.977; IQR1.544 versus.815. Tree range limits and degenerate features remain; truth-range observations are post-evaluation explanations, not deployable OOD flags or grounds for excluding cases.

Distinct benefit: native-dusty KsR50 transfer MAE .1238seeing→.0595GLAO; paired gain .0642[.0398,.0890]. Dust-corrected native-clear KsR50 .1210→.0861; gain .0349[.0091,.0633]. GLAO correction rawnative-clear error .2325→.0861. Concentration native-dusty .5439→.3200; correctednative-clear .5544→.3297 approximately. Better morphology transfer coexists with no demonstrated extra information about underlying paired dust bias.

Canonical Ag entire-galaxy coverage12/16=.75; AKs16/16,dR50Ks15/16,dCKs14/16,p50 13/16,IQR14/16,dR50g15/16,dCg13/16. Counts small, no population guarantee. Four final controls predict meanAg .1992 versus atlas .1207, operationalMAE.0789; no forced correction to zero. Learning curves12→74 independent development objects improve validationGLAOAg .1087→.0561,dCKs .1780→.0725,dR50Ks .1408→.0651. Motivates more calibrated data; no proof same-source scaling eliminates systematics.

### Concurrent supplementary validation-only work

`ml_validation_20261028` reuses canonical100 nonfinal products read-only, without duplicate downloads/preparation. Main five-target design210configurations plus integratedKs42=252 (six targets×seven models×three scenarios×two apertures). Main estimator files180; integratedKs subtree30joblib files. Settings/receipts can count constant configurations without a persisted estimator: distinguish configuration count from artifact count. `execution_complete.json` main saysmodels210 and integratedsays42; current physical joblib counts180+30=210. Combined handoff's “252 configurations and180 fitted artifacts” omits integratedKs estimator subtree; preserve this granularity if documenting counts.

Constantsmedian/mean, photometricridge, summaryridge/forest/boost, spatialridge. Per-scenario development tuning differs from canonical's common settings; ridge1/10/100/1000,forest120trees leaf8/24,max_features.75,boost100depth2 learningrate.04Huber leaf12/32. Five-fold groupeddevelopment, training-fold preprocessing. Learning curves nested tuning per subset, development-only; OOD high-mass refits retune lower-mass subset. Validationpoint metrics use all14, including1sourcecontrol; do not compare directly to canonical13positive-dust validation or16final as equivalent samples.7calibration/7assessment split frozen before labels; rank7maxscore, separate assessment intervals.

Saved `model_verification.json`:252configurations,131040predictions,504 independently recomputed score rows, uniquekeys, truth-perturbation/allowlist checks pass. `analysis_invariants.json`:24000features/1000targets/100nonfinal; identical optical controls/equal-galaxy tests. Fixed12seeingNIR validation MAE(summaryridge/photometric/constantmedian):Ag .06274/.07273/.23784;dR50Ks .04335/.05112/.11218;dCKs .07939/.10259/.13963. AKs .01463ridge versusforest .01363; p50boost .04742 versusconstant .06615; IQRboost .06201 versusconstant .11806. SpatialridgeAg .08124 loses tophotometric. No9prelistedridge/primarytargetGLAOinterval wholly positive or negative. These are descriptive validation outcomes, not a final-selected winner.

Its attempted exact-file freeze check detected changed canonical source before any supplementary final access. AST-consistency audit finds geometry/aperture_policy/labels_for/FeaturePlan/process identical; changes are final-driver isolation/guards. Canonical had independently frozen and completed final while supplementary models ran. Supplementary final scripts now reject spenttestset. `FINAL_EVALUATION_NOT_REPEATED.json` statesownfreezeaborted=true,supplementarycount0. `canonical_final_provenance_check.json` binds samefreezeSHA, canonicalcount1, supplementary0. `canonical_final_score_audit.json` independently verifies153600storedrows/384metricrows/uniqueorientationdrawkeys/finitepredictions explicitly withoutmodel.predict. `completion_verification.json`:9notebookcodecells,0errors,guardrejectsrepeat,truecanonicalhashes,7PDFfigures. Confirmatory revisions require a new independent holdout.

## 2. Source-label audit and publication limits

`ml_expanded_20261028/label_audit/source_label_report.md` only opens four historical controls, not new expanded/validation/final science. Independent minimal FITS decoding checks 24 O1 g/J/Ks images exactly equal old 400² cache crops; pair units/WCS agree; four dust maps are exactly zero; full-field sums agree within 3.64e-12. Full 160-kpc g median offset is +0.120994 mag (range +0.117605 to +0.123231), Ks +0.019342. Each of 22 bands retains its individual sign across 20 correlated views, but signs alternate across filters (FUV −0.152646, r −0.023176, z −0.052064; g positive). A local crop/unit/precision conversion cause is disfavored. Flux-normalized spatial RMS decreases after 1-kpc smoothing: g .01806→.00564, J .01839→.00477, Ks .02030→.00694. A Monte Carlo spatial component is plausible but insufficient to explain the coherent integrated spectral offset.

An analytic clear-probe versus Monte Carlo dusty-instrument spectral/filter operator difference is a leading hypothesis, not an established historical SKIRT error. Current documentation exposes monochromatic sampling at convolve=false versus filter integration at true; original .ski files, source SEDs, filter checksums and packet statistics are unavailable. Birth-cloud/source-SED differences or unrepresented transfer components are not excluded by a zero projected diffuse field. No global offset is subtracted; negative valid labels are retained. Old control envelopes are descriptive, not sigma values, detection thresholds or validated physical error bounds. Adaptive old-control maxima are Ag .124333, AKs .022591, dR50Ks .037487, dCKs .239817 (fixed12 dCKs .045964). Positive-dust physical labels remain uncertain too.

The minimal proposed source-owner reproduction is specified in `ml_validation_20261028/source_owner_reproduction_request.md`: use the same historical particle SEDs, filters and configuration; compare analytic convolve=false/true; run NoMedium instruments with at least three seeds and two packet counts including 1e9; compare full-field, R12 and adaptive fluxes/morphology; separately test birth-cloud source construction and projection. This is a specification only; no message or transfer was performed. Equivalent source calibration evidence is needed before physical precision claims.

`label_audit/literature_context.md` documents Fu2025 attenuation ML, Dobbels & Baes2021 resolved dust (the requested 2022 reference remains unidentified), same-atlas Bokona Tulu2026 morphology, Baes radii studies and DeepMergeII domain shift. These preclude broad claims of first dust ML, first atlas dust morphology, unique geometry or demonstrated sim-to-real validation. This archival review did not re-browse external literature.

## 3. Executed sensitivity substudies

Canonical `instrument_sensitivity/` uses the first six development IDs (13,63883,117272,167418,184937,294866) plus all 14 validation objects, O1 only, four draws and paired modes. Verification records 640 rows, 20 galaxies, 180 observable features, zero nonfinite cells and zero final rows. Cases are A Gaussian baseline; B Ks-only circular Moffat wings, beta3.7414837, at the nominal mode-specific D50; C B plus local correlation rho .2752555/.29317406 preserving marginal variance; D exact 2×2 software sums of A with summed variance and the same physical footprint. Independent baseline checks on six objects give maximum difference zero; padded flux loss 5.07e-9; binned total flux/variance errors 4.44e-16; a million-pixel test gives variance1.000620 and rho .276081/.293047.

No selection or retraining occurs in this feature run. Frozen canonical models score the 13 positive-dust validation objects. `instrument_stress_predictions_summary.csv` has 64 rows, gains has 32. Mixed results remain, including exploratory positive dCg wing/covariance intervals; they do not override the final no-gain finding. Software binning is not a new detector design. Circular kernels omit ellipticity and field variation; the short covariance filter omits long-scale structure and does not transfer real ADU amplitudes. The six-file HAWK-I sharing manifest has checked hashes but no copied or transferred products.

`center_aperture_report.md` uses the same 20 nonfinal O1 scenes, seven native-label cases: baseline; radius×.8; radius×1.2 capped at35 kpc; ±.5-kpc x/y shifts (five native pixels), separately applied. It retains 1120 target rows, 140 wide galaxy/case rows and eight targets. Saved baselines agree within 2.22e-16, direct geometry within 1.78e-15, aperture-flux relative error zero; smoothing edge margin is at least7.24 kpc and no radius cap triggers. Validation median absolute radius×.8/×1.2 changes are Ag .01904/.01193 mag, dR50Ks .02286/.01203 kpc, dCKs .03214/.02374. Center shifts change dCKs by median .04738–.07920, maximum .44709. Radius×.8 changes spatial median attenuation by up to .13139 mag and dR50Ks by .12489 kpc. Changing radius changes the estimand; a fixed center displacement is not an estimated centering-error distribution. Only O1 and separate perturbations are tested, without recomputing observed noisy features or predictions. Concentration correction is materially center sensitive.

Supplementary `empirical_sensitivity.py` and `sensitivity_*.csv` use O1/two draws and frozen nominal models, testing nominal, local covariance, an added long-scale component, elliptical wings, actual HAWK-I shape, .2-arcsec sampling and quarter surface brightness. Nominal D50 wing parameters beta3.7415/q.8199 are distinct from the actual HAWK-I .2935-arcsec Ks FWHM case. Coarse pixels scale sky variance with pixel area and retain per-pixel read/dark terms: this differs from canonical software binning. `sensitivity_noise_response.csv` shows local rho .274921/.293355 but R32 aperture excess1.58537 versus measured3.4213. The long component gives rho .289495/.307558 and excess2.72148. This deliberate long-scale stress remains uncalibrated. No raw reduction, download, packaging or transfer occurred in this continuation. HAWK-I provides neither dust truth nor a measured ULTIMATE PSF.

## 4. Artifact and entrypoint map

### Pilot

Read `ml_feasibility_20261027/scientific_report.md`, `workshop_results.md`, `PROTOCOL.md`, `ml_review_notes.md`, and `ULTIMATE_preliminary_ML.ipynb` (+HTML). Primary definitions/entrypoints are `ml_data.py`, `ml_benchmark.py`, `ml_postprocess.py`, `label_quality_audit.py`, `empirical_stress.py`, `write_ml_report.py`, `execute_ml_notebook.py`, `validate_ml_delivery.py`. Key tables are `operational_labels.csv`, `observable_features.csv`, `heldout_predictions.csv.gz`, `heldout_summary.csv`, `galaxy_heldout_errors.csv`, `GLAO_ML_gain_summary.csv`, `paired_model_comparisons.csv`, `correction_summary.csv`, `OOD_summary.csv`, `label_policy_uncertainty_summary.csv`, `empirical_stress_summary.csv`. Provenance: `feature_provenance.json`, `execution_provenance.json`, `output_manifest.sha256`.

PNG/PDF figures in `figures/`: `01_grouped_ML_errors`, `02_GLAO_ML_ablation`, `03_extra_bands_vs_resolution`, `04_heldout_predictions`, `05_uncertainty_and_OOD`, `06_morphology_correction`. HAWK-I report/addendum, `empirical_model_inputs.json`, `catalogue_validation_summary.json`, source fits, crossmatches, noise tables and `reduced_noise.png` remain under `hawki/`. Expansion selection/probability/acquisition evidence is under `expansion/`.

### Canonical expanded study

Read `ml_expanded_20261028/scientific_report.md`, `workshop_summary.md`, `README.md`, `DEVELOPMENT_PROTOCOL.md`, and executed `expanded_ml_executed.ipynb`/HTML. Definitions: `data_audit/prepare_data.py`, `data_audit/unseal_final.py`, `expanded_features.py`, `expanded_models.py`, `diagnostics.py`, `summarize.py`, `correction_analysis.py`, `domain_diagnostics.py`, `figures.py`, `write_reports.py`, `execute_notebook.py`, `verify_results.py`. The model main entrypoint can rewrite protected development artifacts; the final evaluator refuses repeat use. The notebook reads saved final predictions and demonstrates a real 74-object development refit, reproducing 13-object validation predictions within1e-10. Eight code cells executed, zero errors. No such entrypoint ran during this archival review.

Key tables/artifact locations:

- `expanded_galaxy_inventory.csv`, `sample_quality_counts.csv`: sample/control/quality accounting.
- `target_table.csv`, `final_target_table.csv`, `feature_table.csv.gz`, `final_feature_table.csv.gz`, `derived/<ID>/`: paired labels, observables and aperture/render provenance.
- `development_group_folds.csv`, `chosen_family_settings.csv`, `recommended_settings.csv`, `models/`, `cv_checkpoints/`: exact grouped development selection and estimators.
- `validation_and_control_predictions.csv.gz`, `final_predictions.csv.gz`, `performance_summary.csv`, `recommended_performance.csv`, `galaxy_metrics.csv`: predictions and equal-galaxy metrics.
- `paired_galaxy_gains.csv`, `recommended_gains.csv`, `final_native_dusty_morphology_transfer*`, `final_morphology_correction_gains.csv`: incremental model/band/resolution effects and morphology transfer/correction.
- `learning_curves.csv`, `shift_and_noise_predictions*`, `observable_OOD*`, `source_control_recommended*`, `within_view_noise_and_orientation_residuals.csv`, `property_stratified_errors.csv`, `target_range_diagnostics.csv`: learning, shift, controls, repeated-measurement and tail diagnostics.
- `label_audit/`, `instrument_sensitivity/`, `data_audit/` and `data_audit/final_unseal/`: specialized source/instrument/input audits and stage receipts.

Eight PNG/PDF figure pairs: `model_and_observing_strategy_comparison`, `paired_GLAO_gains`, `prediction_vs_atlas_target`, `residuals_and_galaxy_properties`, `learning_curves`, `aperture_target_sensitivity`, `representative_success_and_failure_images`, `spatial_attenuation_statistics`.

### Supplementary study

Read `ml_validation_20261028/project_continuation_report.md`, `scientific_report.md`, `workshop_final_summary.md`, `workshop_summary.md`, `protocol.md`, and `expanded_training_evaluation.ipynb`. Definitions: `model_study.py`, `integrated_Ks_study.py`, `merge_integrated_Ks.py`, `empirical_sensitivity.py`, `model_interpretation.py`, `audit_canonical_final.py`, `verify_inventory.py`, `verify_results.py`, `verify_tables.py`, `write_report.py`. Final-stage/evaluation entrypoints are disabled. Historical protocol language about sealed final data is reconciled by explicit final-status paragraphs and dedicated no-repeat receipts.

Tables/artifacts: `model_comparison.csv`, `heldout_predictions.csv.gz`, `galaxy_residuals.csv`, `paired_galaxy_comparisons.csv`, `uncertainty_calibration.csv`, `validation_interval_split.json`, `learning_curves.csv`, `OOD_summary.csv`, `OOD_per_orientation_predictions.csv.gz`, `aperture_target_sensitivity.csv`, `source_control_envelopes.csv`, `label_quality_flags.csv`, `observational_quality_flags.csv.gz`, `model_feature_interpretation.csv` (9108 rows), `sensitivity_summary.csv`, `sensitivity_noise_response.csv`, `canonical_final_metric_recomputation.csv`. Original integrated-Ks tables and estimators remain under `integrated_Ks/`.

Seven PNG/PDF figure pairs: `model_comparison`, `predictions_residuals`, `GLAO_increment`, `morphology_correction`, `interval_assessment`, `learning_curves`, `empirical_stress`.

## 5. Practical archival cautions and unresolved evidence

The completed evidence supports a workshop and bounded benchmark paper. Preserve the failed pilot spatial target, undercoverage, OOD/source-control errors, expanded spatial tails and adverse GLAO cases beside successful photometry/correction. No universal source-control subtraction is justified. Fixed-rest-band z=.1 g/J/Ks mocks are not observer-frame ULTIMATE passbands. Nominal Ks FWHM is approximately .588/.390 arcsec, not an actual .2-arcsec instrument; g stays .7 arcsec. Four draws×five views are repeated observations, not 100 independent test galaxies. A single simulation volume and selected subhalo sample limit universality; conditional bootstrap does not retrain models and comparisons are numerous. Deep-Ks selection, known centers/distances, finite apertures, fixed-luminosity priors and unmodeled background/segmentation/field-PSF covariance limit transfer.

Existing receipts and hashes support archive verification without training. New source calibration needs historical configuration/SED/filter evidence or corrected matched products. Packet convergence, observer-frame instrument synthesis, independent domain tests and realistic population/redshift selection remain required. Confirmatory model revisions require a new holdout. Source-owner requests and collaborator manifests are prepared specifications, not completed communications. Preserve historical acquisition/sealing snapshots as dated stage history and distinguish configuration counts from saved-estimator counts.

## Exact frozen IDs, splits and receipt hash appendix

**development (86)**: 13, 63883, 117272, 167418, 184937, 294866, 324124, 355724, 394621, 424289, 486919, 502995, 507292, 535051, 546870, 553837, 558410, 594731, 596866, 604516, 613006, 613192, 616014, 626287, 630975, 638950, 571633, 578834, 319734, 208821, 184946, 599865, 565537, 586836, 539667, 289386, 460726, 96763, 474008, 461785, 324129, 527309, 319732, 516760, 612825, 556699, 348901, 220597, 610988, 455291, 602820, 117296, 521429, 628555, 448830, 576516, 545437, 96767, 626408, 610668, 342447, 595100, 429473, 220598, 533999, 289389, 96775, 220607, 242794, 63884, 522983, 184945, 184931, 253865, 475619, 630760, 366407, 383975, 618318, 167415, 184949, 571072, 275546, 589873, 513106, 338448

**validation (14)**: 584286, 117253, 585080, 35, 584511, 96783, 536147, 583256, 459557, 441709, 220603, 499704, 379804, 564268

**final_test (20)**: 333424, 63868, 14, 294867, 440408, 588986, 612699, 625281, 414918, 648822, 625800, 184951, 388545, 143899, 96780, 39, 578294, 167407, 63875, 590926

Frozen partition file SHA256 values:

- `galaxy_partitions.csv`: `32779aeadf1e7ff2ed8c9ce93268fd112a5a2d2d3e25e4b3cbf3e9f4c12b20c1`
- `validation_galaxies.csv`: `d602203fecc84628782b3ec1608ac7f5b4bca2b988c3e20dd908da4271408ba5`
- `strata.csv`: `830ea0140316b3347ec8bd9d1d06d3f0ec5774cd7285d6a5d0d2136fecc61f3e`
- `development_galaxies.csv`: `87034165bc1b4630f4ae682bbd58898b88998c065c522b138507b6b301227121`
- `final_test_galaxies.csv`: `01a82f29f8b7b4e04d05b46ffa5388dbf8bff2f5cc5149e2c565441e59fbfd34`
- `partitions_frozen.json`: `b5bd5d8391221a580bde6742dee6d088e18cd5e7928a2dbc90bd642da4e0fe86`

### analysis_results/ml_feasibility_20261027/preliminary_cv_splits.csv

- Fold0 calibration: 630975, 424289, 613006, 558410, 553837
- Fold0 fit: 63883, 294866, 394621, 486919, 502995, 507292, 535051, 546870, 594731, 596866, 626287, 638950
- Fold0 outer_test: 117272, 324124, 355724, 604516, 616014
- Fold1 calibration: 63883, 117272, 324124, 546870, 616014
- Fold1 fit: 355724, 424289, 486919, 502995, 507292, 553837, 558410, 594731, 596866, 604516, 613006, 630975
- Fold1 outer_test: 294866, 394621, 535051, 626287, 638950
- Fold2 calibration: 626287, 486919, 616014, 294866, 546870
- Fold2 fit: 63883, 117272, 324124, 355724, 394621, 502995, 507292, 535051, 558410, 594731, 604516, 613006, 638950
- Fold2 outer_test: 424289, 553837, 596866, 630975
- Fold3 calibration: 355724, 117272, 630975, 486919, 594731
- Fold3 fit: 294866, 324124, 394621, 424289, 507292, 535051, 553837, 596866, 604516, 613006, 616014, 626287, 638950
- Fold3 outer_test: 63883, 502995, 546870, 558410
- Fold4 calibration: 394621, 546870, 626287, 638950, 596866
- Fold4 fit: 63883, 117272, 294866, 324124, 355724, 424289, 502995, 535051, 553837, 558410, 604516, 616014, 630975
- Fold4 outer_test: 486919, 507292, 594731, 613006

### analysis_results/ml_expanded_20261028/development_group_folds.csv

- Fold0 test: 167415, 220607, 253865, 366407, 474008, 486919, 513106, 516760, 586836, 595100, 599865, 602820, 610988, 630760, 630975
- Fold1 test: 220597, 294866, 429473, 455291, 460726, 461785, 521429, 522983, 533999, 553837, 558410, 571633, 594731, 604516, 612825
- Fold2 test: 117272, 220598, 242794, 289389, 475619, 502995, 507292, 527309, 556699, 565537, 589873, 613006, 616014, 626408, 638950
- Fold3 test: 96763, 96775, 184949, 275546, 324129, 355724, 383975, 424289, 448830, 546870, 571072, 596866, 610668, 618318, 626287
- Fold4 test: 63883, 184931, 289386, 319732, 324124, 342447, 348901, 394621, 535051, 539667, 545437, 576516, 578834, 628555

Each fit set is the complement within the74 eligible development IDs; exact full59/60-ID fit lists are retained in the CSV.

Supplementary interval split:

```json
{
  "calibration": [
    536147,
    96783,
    35,
    499704,
    564268,
    379804,
    220603
  ],
  "assessment": [
    459557,
    584511,
    117253,
    441709,
    584286,
    585080,
    583256
  ],
  "final_science_opened": false
}
```

Selected current small-artifact hashes (read-only SHA256 during this review):

- `ml_feasibility_20261027/PROTOCOL.md`: `f90112afc31a64b5c36616a26f70c6640b02bda43da6b3c8efaa28d5d53522c0`
- `ml_expanded_20261028/FINAL_PROTOCOL_FROZEN.json`: `587aab56d39e6b29ad47f381c4b1440c8dd28eb52811ebc4ae3842b6fc220ce4`
- `ml_expanded_20261028/FINAL_EVALUATION_COMPLETED.json`: `230995a78372c0687331315a3d358554ae144b735cdbe10ccbc6fcb5f3577f56`
- `ml_validation_20261028/FINAL_EVALUATION_NOT_REPEATED.json`: `96a6921d50fe10fb9567f9eeea003db1e1f88892464a2dadadf56d5c66856dad`
- `ml_validation_20261028/canonical_final_provenance_check.json`: `1a5dffcb2f81a18392215c11099a951efed8228473fa895ab6a9e6f662cffc16`
- `ml_validation_20261028/canonical_final_score_audit.json`: `aacc18fb4ca58d064d91bce85c64f5a735add1bfa111ed5443bd56ad3ceb1b9b`
- `ml_validation_20261028/validation_interval_split.json`: `c2529115ea1fe428953cee2097b9243f339bd7a3694cacea09ef848805c4ccee`

Control IDs from current canonical inventory:

- development: 13, 167418, 184937, 613192, 319734, 208821, 184946, 117296, 96767, 63884, 184945, 338448
- validation: 35
- final_test: 14, 96780, 39, 63875

All discovered Markdown report/protocol/readme sources in the three scoped archives:

- `analysis_results/ml_feasibility_20261027/PROTOCOL.md`
- `analysis_results/ml_feasibility_20261027/README.md`
- `analysis_results/ml_feasibility_20261027/expansion/README.md`
- `analysis_results/ml_feasibility_20261027/expansion/acquisition_report.md`
- `analysis_results/ml_feasibility_20261027/hawki/catalogue_validation_addendum.md`
- `analysis_results/ml_feasibility_20261027/hawki/hawki_empirical_calibration_report.md`
- `analysis_results/ml_feasibility_20261027/ml_review_notes.md`
- `analysis_results/ml_feasibility_20261027/scientific_report.md`
- `analysis_results/ml_feasibility_20261027/workshop_results.md`
- `analysis_results/ml_expanded_20261028/DEVELOPMENT_PROTOCOL.md`
- `analysis_results/ml_expanded_20261028/README.md`
- `analysis_results/ml_expanded_20261028/data_audit/FINAL_UNSEAL_README.md`
- `analysis_results/ml_expanded_20261028/data_audit/README.md`
- `analysis_results/ml_expanded_20261028/data_audit/final_inventory_audit.md`
- `analysis_results/ml_expanded_20261028/instrument_sensitivity/README.md`
- `analysis_results/ml_expanded_20261028/instrument_sensitivity/center_aperture_report.md`
- `analysis_results/ml_expanded_20261028/label_audit/literature_context.md`
- `analysis_results/ml_expanded_20261028/label_audit/report_inclusion_brief.md`
- `analysis_results/ml_expanded_20261028/label_audit/source_label_report.md`
- `analysis_results/ml_expanded_20261028/scientific_report.md`
- `analysis_results/ml_expanded_20261028/workshop_summary.md`
- `analysis_results/ml_validation_20261028/README.md`
- `analysis_results/ml_validation_20261028/hawki_collaborator_manifest.md`
- `analysis_results/ml_validation_20261028/project_continuation_report.md`
- `analysis_results/ml_validation_20261028/protocol.md`
- `analysis_results/ml_validation_20261028/scientific_report.md`
- `analysis_results/ml_validation_20261028/source_owner_reproduction_request.md`
- `analysis_results/ml_validation_20261028/workshop_final_summary.md`
- `analysis_results/ml_validation_20261028/workshop_summary.md`
