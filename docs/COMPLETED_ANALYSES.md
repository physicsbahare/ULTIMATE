# Completed analyses and full artifact index

Verified 2026-10-29 from reports, protocols, receipts, code and result tables. **Do not rerun these analyses to document them.** All 13 top-level result directories and their nested studies are covered. “Completed” means the investigation delivered its result, including negative findings; it does not imply every physical question was solved.

Older next_experiments.md, PLAN.md and pre-unseal reports are historical. Read current state and supersession decisions first. A per-directory index lists every artifact and its Git/server disposition, including figures, tables, logs, configurations, models and arrays.

## Root pilot and five-view reproduction

**Directory:** `analysis_results/.`. **Status:** COMPLETED.

**Purpose:** Reproduce the original galaxy 294866 pilot and assess mask, aperture and viewing dependence.

**Data/sample:** One galaxy, five correlated views and 25 input images.

**Code entry points:** [inspect_inputs.py](../analysis_results/inspect_inputs.py), [build_notebooks.py](../analysis_results/build_notebooks.py), [write_reports.py](../analysis_results/write_reports.py), [validate_outputs.py](../analysis_results/validate_outputs.py).

**Report:** [scientific_summary.md](../analysis_results/scientific_summary.md).

**Scientific result:** O1 integrated A_g = .334442 mag and A_Ks = .020562 mag; rho_g = .924164 and rho_Ks = .548340. Other views show strong Ks sign/selection dependence. Negative attenuation is retained.

**Output evidence:** [tng_orientation_summary.csv](../analysis_results/tng_orientation_summary.csv), [tng_mask_aperture_sensitivity.csv](../analysis_results/tng_mask_aperture_sensitivity.csv), [tng_input_validation.csv](../analysis_results/tng_input_validation.csv), [figures/five_orientation_maps.png](../analysis_results/figures/five_orientation_maps.png).

**Completion / why repetition is unnecessary:** Original and five-view notebooks executed; input/mask sensitivity and HAWK-I initial audit already delivered. Do not treat early next_experiments.md as current work.

## Initial observer-band screen controls

**Directory:** `analysis_results/screen_test_20261026`. **Status:** COMPLETED / NEGATIVE_RESULT.

**Purpose:** Test whether observable colors identify uniform versus variable foreground screens.

**Data/sample:** Actual structured DR1 scenes of galaxy 294866. O1: z = .1/.3/.6/1 and .25/1/4 h per band; other views: z = .3.

**Code entry points:** [run_experiment.py](../analysis_results/screen_test_20261026/run_experiment.py), [run_robustness.py](../analysis_results/screen_test_20261026/run_robustness.py), [screen_inference.py](../analysis_results/screen_test_20261026/screen_inference.py), [instrument.py](../analysis_results/screen_test_20261026/instrument.py), [validate_delivery.py](../analysis_results/screen_test_20261026/validate_delivery.py).

**Report:** [scientific_report.md](../analysis_results/screen_test_20261026/scientific_report.md). **Notebook:** [ULTIMATE_static_screen_test.ipynb](../analysis_results/screen_test_20261026/ULTIMATE_static_screen_test.ipynb).

**Scientific result:** 574 marginalized fits, 200 robustness fits and 20 oracle cases. Known uniform controls yield strong false-positive evidence. Interpolation and model discrepancy affect conclusions; geometry classification is unreliable.

**Output evidence:** [screen_model_summary.csv](../analysis_results/screen_test_20261026/screen_model_summary.csv), [robustness_results.csv](../analysis_results/screen_test_20261026/robustness_results.csv), [observable_uniform_screen_residuals.csv](../analysis_results/screen_test_20261026/observable_uniform_screen_residuals.csv), [spectral_interpolation_sensitivity.csv](../analysis_results/screen_test_20261026/spectral_interpolation_sensitivity.csv).

**Completion / why repetition is unnecessary:** Original screen/noise/calculator/oracle/grid robustness already tested; no physical-null gate passed.

**All outputs, including figures/tables:** [artifact inventory](inventories/screen_test_20261026.md).

## DR1 calibrated screen ensemble and anchor stress

**Directory:** `analysis_results/dr1_calibrated_screen_20261026`. **Status:** COMPLETED / NEGATIVE_RESULT.

**Purpose:** Calibrate observable contrast statistics against independent population/null draws.

**Data/sample:** Galaxy 294866 rest-frame griz/JHKs and a declared empirical population generator; final protocol uses 500 calibration and 500 evaluation draws per scene.

**Code entry points:** [experiment.py](../analysis_results/dr1_calibrated_screen_20261026/experiment.py), [final_ensemble.py](../analysis_results/dr1_calibrated_screen_20261026/final_ensemble.py), [final_stress.py](../analysis_results/dr1_calibrated_screen_20261026/final_stress.py), [residual_diagnostics.py](../analysis_results/dr1_calibrated_screen_20261026/residual_diagnostics.py), [validate_delivery.py](../analysis_results/dr1_calibrated_screen_20261026/validate_delivery.py).

**Report:** [scientific_report.md](../analysis_results/dr1_calibrated_screen_20261026/scientific_report.md). **Notebook:** [Calibrated_DR1_screen_experiment.ipynb](../analysis_results/dr1_calibrated_screen_20261026/Calibrated_DR1_screen_experiment.ipynb).

**Scientific result:** Conditional matched-PSF patchy-screen power at z = .3 is 78% seeing / 86% GLAO, a gain of 8 percentage points [2.8, 14.4]. A new fixed population anchor yields 492/500 = 98.4% false positives, defeating general classification.

**Output evidence:** [FINAL_calibrated_rates.csv](../analysis_results/dr1_calibrated_screen_20261026/FINAL_calibrated_rates.csv), [FINAL_population_anchor_stress.csv](../analysis_results/dr1_calibrated_screen_20261026/FINAL_population_anchor_stress.csv), [FINAL_posterior_predictive.csv](../analysis_results/dr1_calibrated_screen_20261026/FINAL_posterior_predictive.csv), [GLAO_power_comparison.csv](../analysis_results/dr1_calibrated_screen_20261026/GLAO_power_comparison.csv), [false_positive_audit.md](../analysis_results/dr1_calibrated_screen_20261026/false_positive_audit.md).

**Completion / why repetition is unnecessary:** Final conditional ensemble and decisive stress completed. FINAL_ tables supersede development rates; failure is a scientific result.

**All outputs, including figures/tables:** [artifact inventory](inventories/dr1_calibrated_screen_20261026.md).

## Positive multiplicative model and failure diagnosis

**Directory:** `analysis_results/multiplicative_diagnosis_20261026`. **Status:** COMPLETED / NEGATIVE_RESULT.

**Purpose:** Explain the catastrophic anchor failure and test a positive population × attenuation model.

**Data/sample:** Frozen prior anchor, training-region empirical SEDs, 17 bounded pilot scenes, and sparse-aperture/full-pixel comparisons.

**Code entry points:** [run_focused.py](../analysis_results/multiplicative_diagnosis_20261026/run_focused.py), [diagnose.py](../analysis_results/multiplicative_diagnosis_20261026/diagnose.py), [physical_model.py](../analysis_results/multiplicative_diagnosis_20261026/physical_model.py), [pilot.py](../analysis_results/multiplicative_diagnosis_20261026/pilot.py), [absolute_failure.py](../analysis_results/multiplicative_diagnosis_20261026/absolute_failure.py), [degeneracy_bound.py](../analysis_results/multiplicative_diagnosis_20261026/degeneracy_bound.py), [validate_results.py](../analysis_results/multiplicative_diagnosis_20261026/validate_results.py).

**Report:** [scientific_report.md](../analysis_results/multiplicative_diagnosis_20261026/scientific_report.md). **Notebook:** [ULTIMATE_targeted_positive_model.ipynb](../analysis_results/multiplicative_diagnosis_20261026/ULTIMATE_targeted_positive_model.ipynb).

**Scientific result:** The anchor reproduces. Incorrect covariance/probability propagation dominates, rather than missing PC rank. Physical-null chi² ≈ 436/812; the positive model fails its gate. Among 68 fit pairs, 42 null fits and 33 alternative fits failed. Sparse known-pair power is 9.29%/8.69%, but nearly 100% with pixels retained.

**Output evidence:** [mechanism.json](../analysis_results/multiplicative_diagnosis_20261026/mechanism.json), [development_gate.json](../analysis_results/multiplicative_diagnosis_20261026/development_gate.json), [absolute_failure_isolation.csv](../analysis_results/multiplicative_diagnosis_20261026/absolute_failure_isolation.csv), [conditional_identifiability_bound.csv](../analysis_results/multiplicative_diagnosis_20261026/conditional_identifiability_bound.csv).

**Completion / why repetition is unnecessary:** Mechanism, positive-model adequacy, absolute-color, convergence, u-band and pixel/aperture checks are complete. The failed gate explicitly prohibited a large evaluation.

**All outputs, including figures/tables:** [artifact inventory](inventories/multiplicative_diagnosis_20261026.md).

## Spatial structure and resolution pilot

**Directory:** `analysis_results/spatial_structure_pilot_20261026`. **Status:** COMPLETED.

**Purpose:** Separate spatial/morphology transfer from dust-specific attribution.

**Data/sample:** Five views of galaxy 294866; clear, uniform-screen, patchy population-shift and mixed controls; conditional redshifts, PSFs and depths; 40 noise draws per primary test.

**Code entry points:** [pilot.py](../analysis_results/spatial_structure_pilot_20261026/pilot.py), [secondary_analysis.py](../analysis_results/spatial_structure_pilot_20261026/secondary_analysis.py), [boundary_sensitivity.py](../analysis_results/spatial_structure_pilot_20261026/boundary_sensitivity.py), [depth_threshold_diagnostic.py](../analysis_results/spatial_structure_pilot_20261026/depth_threshold_diagnostic.py), [validation_checks.py](../analysis_results/spatial_structure_pilot_20261026/validation_checks.py).

**Report:** [scientific_report.md](../analysis_results/spatial_structure_pilot_20261026/scientific_report.md). **Notebook:** [ULTIMATE_spatial_structure_pilot.ipynb](../analysis_results/spatial_structure_pilot_20261026/ULTIMATE_spatial_structure_pilot.ipynb).

**Scientific result:** Conditional morphology/feature transfer is supported; unique dust attribution is not. Thresholded seeing completeness falls .1587 → .03913 → .00652 with depth as noise-assisted crossings vanish. PSF filtering and optical matching bound resolution.

**Output evidence:** [feature_summary.csv](../analysis_results/spatial_structure_pilot_20261026/feature_summary.csv), [paired_GLAO_summary.csv](../analysis_results/spatial_structure_pilot_20261026/paired_GLAO_summary.csv), [scale_transfer.csv](../analysis_results/spatial_structure_pilot_20261026/scale_transfer.csv), [depth_threshold_diagnostic.csv](../analysis_results/spatial_structure_pilot_20261026/depth_threshold_diagnostic.csv), [dust_morphology_bias_summary.csv](../analysis_results/spatial_structure_pilot_20261026/dust_morphology_bias_summary.csv), [PSF_morphology_bias_summary.csv](../analysis_results/spatial_structure_pilot_20261026/PSF_morphology_bias_summary.csv).

**Completion / why repetition is unnecessary:** Resolution, depth, component incidence, boundaries, control contamination and morphology decomposition were investigated. The MaNGA note remains a proposal.

**All outputs, including figures/tables:** [artifact inventory](inventories/spatial_structure_pilot_20261026.md).

## 26-galaxy morphology and observing bias

**Directory:** `analysis_results/multigalaxy_morphology_20261027`. **Status:** COMPLETED.

**Purpose:** Measure dust-pair morphology across sample/views and conditional instrumental transfer.

**Data/sample:** 26 galaxies × 5 views × 22 band pairs = 2860 native comparisons; 5 development / 21 historically held-out galaxies. The g/J/Ks observing scenario uses z = .1 and 8 noise draws.

**Code entry points:** [audit_sample.py](../analysis_results/multigalaxy_morphology_20261027/audit_sample.py), [run_stages.py](../analysis_results/multigalaxy_morphology_20261027/run_stages.py), [observe.py](../analysis_results/multigalaxy_morphology_20261027/observe.py), [statistics_analysis.py](../analysis_results/multigalaxy_morphology_20261027/statistics_analysis.py), [additional_robustness.py](../analysis_results/multigalaxy_morphology_20261027/additional_robustness.py), [null_diagnostics.py](../analysis_results/multigalaxy_morphology_20261027/null_diagnostics.py), [validate_science.py](../analysis_results/multigalaxy_morphology_20261027/validate_science.py).

**Report:** [scientific_report.md](../analysis_results/multigalaxy_morphology_20261027/scientific_report.md). **Notebook:** [ULTIMATE_multigalaxy_morphology.ipynb](../analysis_results/multigalaxy_morphology_20261027/ULTIMATE_multigalaxy_morphology.ipynb).

**Scientific result:** Median native ΔR50 within R < 12 kpc: g +.4003 kpc, Ks +.1239 kpc. Galaxy 294866 is retained as an opposite-sign outlier. Ks dusty-radius error changes .08055 → .03942 kpc and concentration error .36702 → .19016. Dust-difference, shape and asymmetry gains are weaker or estimator-sensitive.

**Output evidence:** [primary_dust_bias.csv](../analysis_results/multigalaxy_morphology_20261027/primary_dust_bias.csv), [galaxy_bootstrap_summary.csv](../analysis_results/multigalaxy_morphology_20261027/galaxy_bootstrap_summary.csv), [GLAO_bootstrap_summary.csv](../analysis_results/multigalaxy_morphology_20261027/GLAO_bootstrap_summary.csv), [aperture_center_robustness.csv](../analysis_results/multigalaxy_morphology_20261027/aperture_center_robustness.csv), [detector_sampling_robustness.csv](../analysis_results/multigalaxy_morphology_20261027/detector_sampling_robustness.csv), [asymmetry_estimator_sensitivity.csv](../analysis_results/multigalaxy_morphology_20261027/asymmetry_estimator_sensitivity.csv), [zero_projected_dust_summary.csv](../analysis_results/multigalaxy_morphology_20261027/zero_projected_dust_summary.csv).

**Completion / why repetition is unnecessary:** Sample/selection audits, native wavelength dependence, observational bias, spatial filtering, aperture/center/four-view/PSF/depth/sampling and source-null sensitivities are complete. These 26 galaxies later became development data.

**All outputs, including figures/tables:** [artifact inventory](inventories/multigalaxy_morphology_20261027.md).

## Independent morphology continuation verification

**Directory:** `analysis_results/multigalaxy_morphology_20261027/continuation_verification`. **Status:** COMPLETED.

**Purpose:** Independently verify existing study without altering its primary outputs.

**Data/sample:** 26 archive hashes, 795 study files and 289 earlier files; a five-galaxy replay, 20 radial checks and two FITS spot checks.

**Code entry points:** [verify_existing_study.py](../analysis_results/multigalaxy_morphology_20261027/continuation_verification/verify_existing_study.py), [check_noise_moments.py](../analysis_results/multigalaxy_morphology_20261027/continuation_verification/check_noise_moments.py), [finalize_verification.py](../analysis_results/multigalaxy_morphology_20261027/continuation_verification/finalize_verification.py).

**Report:** [README.md](../analysis_results/multigalaxy_morphology_20261027/continuation_verification/README.md). **Notebook:** [independent_verification.ipynb](../analysis_results/multigalaxy_morphology_20261027/continuation_verification/independent_verification.ipynb).

**Scientific result:** 10 unit tests pass; 840 replayed morphology rows agree, with gain agreement ≈ 9.98e-17. Aggregate Poisson/read variance ratios are ≈ .99603/.99921/1.00030. Zero-control exclusion is descriptive and does not repair the primary sample.

**Output evidence:** [verification_receipt.json](../analysis_results/multigalaxy_morphology_20261027/continuation_verification/verification_receipt.json), [independently_recomputed_galaxy_gains.csv](../analysis_results/multigalaxy_morphology_20261027/continuation_verification/independently_recomputed_galaxy_gains.csv), [independent_native_and_null_sensitivity.csv](../analysis_results/multigalaxy_morphology_20261027/continuation_verification/independent_native_and_null_sensitivity.csv), [five_galaxy_fresh_replay.csv](../analysis_results/multigalaxy_morphology_20261027/continuation_verification/five_galaxy_fresh_replay.csv).

**Completion / why repetition is unnecessary:** Existing independent verification and notebook are delivered. No need to rerun this expensive replay for archive validation.

**All outputs, including figures/tables:** [artifact inventory](inventories/multigalaxy_morphology_20261027.md).

## Preliminary grouped ML feasibility

**Directory:** `analysis_results/ml_feasibility_20261027`. **Status:** COMPLETED.

**Purpose:** Predict operational attenuation and dust-bias targets with observable-only baselines.

**Data/sample:** 26 development galaxies: 4 source controls and 22 fit-eligible objects. Fivefold grouped CV uses 5 independent galaxies for interval calibration per fold.

**Code entry points:** [ml_data.py](../analysis_results/ml_feasibility_20261027/ml_data.py), [ml_benchmark.py](../analysis_results/ml_feasibility_20261027/ml_benchmark.py), [ml_postprocess.py](../analysis_results/ml_feasibility_20261027/ml_postprocess.py), [label_quality_audit.py](../analysis_results/ml_feasibility_20261027/label_quality_audit.py), [empirical_stress.py](../analysis_results/ml_feasibility_20261027/empirical_stress.py), [validate_ml_delivery.py](../analysis_results/ml_feasibility_20261027/validate_ml_delivery.py).

**Report:** [scientific_report.md](../analysis_results/ml_feasibility_20261027/scientific_report.md). **Notebook:** [ULTIMATE_preliminary_ML.ipynb](../analysis_results/ml_feasibility_20261027/ULTIMATE_preliminary_ML.ipynb).

**Scientific result:** GLAO A_g errors: constant .22122, photometry .08877, full ridge .09720. Ks R50 errors: constant .09961, ridge .04928 kpc. Spatial-median ridge (.12155) loses to the constant (.09999). No robust extra GLAO ML gain; out-of-domain and undercoverage failures are retained.

**Output evidence:** [heldout_summary.csv](../analysis_results/ml_feasibility_20261027/heldout_summary.csv), [GLAO_ML_gain_summary.csv](../analysis_results/ml_feasibility_20261027/GLAO_ML_gain_summary.csv), [correction_summary.csv](../analysis_results/ml_feasibility_20261027/correction_summary.csv), [OOD_summary.csv](../analysis_results/ml_feasibility_20261027/OOD_summary.csv), [label_policy_uncertainty_summary.csv](../analysis_results/ml_feasibility_20261027/label_policy_uncertainty_summary.csv), [empirical_stress_summary.csv](../analysis_results/ml_feasibility_20261027/empirical_stress_summary.csv).

**Completion / why repetition is unnecessary:** Grouped leakage controls, intervals, out-of-domain tests, aperture/label stress and empirical PSF/covariance tests are complete. The expanded study extends the pilot without erasing its failures.

**All outputs, including figures/tables:** [artifact inventory](inventories/ml_feasibility_20261027.md).

## Frozen metadata expansion and acquisition

**Directory:** `analysis_results/ml_feasibility_20261027/expansion`. **Status:** COMPLETED.

**Purpose:** Freeze partitions before new science-image access and acquire bounded official DR1 sources.

**Data/sample:** 1154 catalogue entries, 1128 newly eligible galaxies; 94 new + 26 original = 120, frozen into 86/14/20 partitions.

**Code entry points:** [freeze_selection.py](../analysis_results/ml_feasibility_20261027/expansion/freeze_selection.py), [update_acquisition_status.py](../analysis_results/ml_feasibility_20261027/expansion/update_acquisition_status.py), [verify_expansion.py](../analysis_results/ml_feasibility_20261027/expansion/verify_expansion.py), [../../../data/TNG50_SKIRT_DR1_ml_expansion/download_expansion.py](../analysis_results/ml_feasibility_20261027/expansion/../../../data/TNG50_SKIRT_DR1_ml_expansion/download_expansion.py).

**Report:** [README.md](../analysis_results/ml_feasibility_20261027/expansion/README.md).

**Scientific result:** Seed 20261027; 25 mass/activity cells. All 94 new datasets were later verified in the canonical audit. The early 12/94 download report is superseded by the completed inventory.

**Output evidence:** [partitions_frozen.json](../analysis_results/ml_feasibility_20261027/expansion/partitions_frozen.json), [galaxy_partitions.csv](../analysis_results/ml_feasibility_20261027/expansion/galaxy_partitions.csv), [development_galaxies.csv](../analysis_results/ml_feasibility_20261027/expansion/development_galaxies.csv), [validation_galaxies.csv](../analysis_results/ml_feasibility_20261027/expansion/validation_galaxies.csv), [final_test_galaxies.csv](../analysis_results/ml_feasibility_20261027/expansion/final_test_galaxies.csv), [acquisition_report.md](../analysis_results/ml_feasibility_20261027/expansion/acquisition_report.md).

**Completion / why repetition is unnecessary:** The freeze and provenance are permanent. No reselection, duplicate download or final-partition reclassification is needed.

**All outputs, including figures/tables:** [artifact inventory](inventories/ml_feasibility_20261027.md).

## NGC 3256 empirical calibration branch

**Directory:** `analysis_results/ml_feasibility_20261027/hawki`. **Status:** COMPLETED.

**Purpose:** Use official reduced products and star/catalogue/background evidence as sensitivity inputs.

**Data/sample:** 22 local raw exposures; January 6 science/variance/confidence cutouts; 103 compact candidates and nine quality 2MASS matches.

**Code entry points:** [query_archive.py](../analysis_results/ml_feasibility_20261027/hawki/query_archive.py), [query_calibrations.py](../analysis_results/ml_feasibility_20261027/hawki/query_calibrations.py), [diagnose_reduced.py](../analysis_results/ml_feasibility_20261027/hawki/diagnose_reduced.py), [diagnose_raw.py](../analysis_results/ml_feasibility_20261027/hawki/diagnose_raw.py), [validate_catalogue.py](../analysis_results/ml_feasibility_20261027/hawki/validate_catalogue.py), [export_empirical_model.py](../analysis_results/ml_feasibility_20261027/hawki/export_empirical_model.py).

**Report:** [hawki_empirical_calibration_report.md](../analysis_results/ml_feasibility_20261027/hawki/hawki_empirical_calibration_report.md).

**Scientific result:** Three certified complete calibration associations. Reduced candidate FWHM is .3166 arcsec; the nine-star value is .29352 arcsec. Adjacent covariance ≈ .2753/.2932; large-aperture noise exceeds the local-filter model. No new local raw reduction was performed.

**Output evidence:** [reduced_psf_spatial_bins.csv](../analysis_results/ml_feasibility_20261027/hawki/reduced_psf_spatial_bins.csv), [empirical_model_inputs.json](../analysis_results/ml_feasibility_20261027/hawki/empirical_model_inputs.json), [catalogue_validation_summary.json](../analysis_results/ml_feasibility_20261027/hawki/catalogue_validation_summary.json), [reduced_download_log.json](../analysis_results/ml_feasibility_20261027/hawki/reduced_download_log.json), [calibration_association_manifest.csv](../analysis_results/ml_feasibility_20261027/hawki/calibration_association_manifest.csv).

**Completion / why repetition is unnecessary:** Discovery, certified associations, official cutout diagnostics, catalogue matching and local-noise analysis are complete. The early missing-local-calibration statement is superseded.

**All outputs, including figures/tables:** [artifact inventory](inventories/ml_feasibility_20261027.md).

## Canonical expanded single-final ML

**Directory:** `analysis_results/ml_expanded_20261028`. **Status:** COMPLETED.

**Purpose:** Frozen operational attenuation/morphology benchmark and observing-strategy comparison.

**Data/sample:** 120 galaxies / 600 views; 74 fit, 13 calibration, 16 primary-final objects plus 4 final controls; four draws, two apertures and three scenarios.

**Code entry points:** [data_audit/prepare_data.py](../analysis_results/ml_expanded_20261028/data_audit/prepare_data.py), [expanded_features.py](../analysis_results/ml_expanded_20261028/expanded_features.py), [expanded_models.py](../analysis_results/ml_expanded_20261028/expanded_models.py), [diagnostics.py](../analysis_results/ml_expanded_20261028/diagnostics.py), [correction_analysis.py](../analysis_results/ml_expanded_20261028/correction_analysis.py), [domain_diagnostics.py](../analysis_results/ml_expanded_20261028/domain_diagnostics.py), [verify_results.py](../analysis_results/ml_expanded_20261028/verify_results.py).

**Report:** [scientific_report.md](../analysis_results/ml_expanded_20261028/scientific_report.md). **Notebook:** [expanded_ml_executed.ipynb](../analysis_results/ml_expanded_20261028/expanded_ml_executed.ipynb).

**Scientific result:** Canonical GLAO constant → ML errors: A_g .3003 → .0741 mag, A_Ks .0594 → .0124 mag, dR50_Ks .1282 → .0799 kpc and dC_Ks .1521 → .0887. No robust added GLAO dust-bias ML gain. Corrected Ks radius error is .1210 → .0861 kpc. Final evaluation count = 1.

**Output evidence:** [recommended_performance.csv](../analysis_results/ml_expanded_20261028/recommended_performance.csv), [recommended_gains.csv](../analysis_results/ml_expanded_20261028/recommended_gains.csv), [final_predictions.csv.gz](../analysis_results/ml_expanded_20261028/final_predictions.csv.gz), [final_morphology_correction_gains.csv](../analysis_results/ml_expanded_20261028/final_morphology_correction_gains.csv), [FINAL_PROTOCOL_FROZEN.json](../analysis_results/ml_expanded_20261028/FINAL_PROTOCOL_FROZEN.json), [FINAL_EVALUATION_COMPLETED.json](../analysis_results/ml_expanded_20261028/FINAL_EVALUATION_COMPLETED.json).

**Completion / why repetition is unnecessary:** Development selection, one final evaluation, prediction tables, source controls, uncertainty, learning curves, out-of-domain tests, instrument/center/aperture sensitivity, notebook execution and post-final preservation are complete. Do not repeat inference.

**All outputs, including figures/tables:** [artifact inventory](inventories/ml_expanded_20261028.md).

## Completed historical source-label audit

**Directory:** `analysis_results/ml_expanded_20261028/label_audit`. **Status:** COMPLETED / LIMITATION_ACCEPTED.

**Purpose:** Test local explanations for nonzero pair residuals at zero projected dust.

**Data/sample:** Four historical controls; 24 raw O1 g/J/Ks images; full-field signs in 22 bands across 20 correlated views.

**Code entry points:** [audit_old_controls.py](../analysis_results/ml_expanded_20261028/label_audit/audit_old_controls.py), [make_old_quality_masks.py](../analysis_results/ml_expanded_20261028/label_audit/make_old_quality_masks.py), [verify_audit.py](../analysis_results/ml_expanded_20261028/label_audit/verify_audit.py).

**Report:** [source_label_report.md](../analysis_results/ml_expanded_20261028/label_audit/source_label_report.md).

**Scientific result:** An independent FITS decoder exactly agrees with the cache. Crop, unit and precision errors are disfavored as local causes. Full-field attenuation: g ≈ .120994 mag, Ks ≈ .019342 mag. The source-operator hypothesis is unproved; an unmapped source/radiative-transfer component is not excluded.

**Output evidence:** [report_inclusion_brief.md](../analysis_results/ml_expanded_20261028/label_audit/report_inclusion_brief.md), [literature_context.md](../analysis_results/ml_expanded_20261028/label_audit/literature_context.md).

**Completion / why repetition is unnecessary:** Local label, spectral/full-field and smoothing checks are complete. Await historical source evidence rather than repeating the local audit.

**All outputs, including figures/tables:** [artifact inventory](inventories/ml_expanded_20261028.md).

## Instrument and aperture/center stresses

**Directory:** `analysis_results/ml_expanded_20261028/instrument_sensitivity`. **Status:** COMPLETED.

**Purpose:** Bound existing model sensitivity without retraining or final access.

**Data/sample:** 20 nonfinal O1 objects: 6 development + 14 validation; 13 positive-dust validation objects for prediction stress.

**Code entry points:** [run_stress.py](../analysis_results/ml_expanded_20261028/instrument_sensitivity/run_stress.py), [center_aperture_stress.py](../analysis_results/ml_expanded_20261028/instrument_sensitivity/center_aperture_stress.py), [verify_outputs.py](../analysis_results/ml_expanded_20261028/instrument_sensitivity/verify_outputs.py).

**Report:** [README.md](../analysis_results/ml_expanded_20261028/instrument_sensitivity/README.md).

**Scientific result:** Moffat, covariance and software 2 × 2 binning produce 640 feature cases. Center/radius tests produce 1120 target rows. Center shifts change concentration by median .047–.079, maximum .447. No final objects, retraining, new winner or validated real covariance.

**Output evidence:** [center_aperture_report.md](../analysis_results/ml_expanded_20261028/instrument_sensitivity/center_aperture_report.md), [observable_feature_shifts.csv](../analysis_results/ml_expanded_20261028/instrument_sensitivity/observable_feature_shifts.csv), [stress_features.csv.gz](../analysis_results/ml_expanded_20261028/instrument_sensitivity/stress_features.csv.gz).

**Completion / why repetition is unnecessary:** PSF/noise/software-binning and native aperture/center stress tests are complete. Changing the aperture changes the estimand; this is not full propagation through noisy segmentation.

**All outputs, including figures/tables:** [artifact inventory](inventories/ml_expanded_20261028.md).

## Supplementary validation-only ML and reconciliation

**Directory:** `analysis_results/ml_validation_20261028`. **Status:** COMPLETED; final repeat BLOCKED.

**Purpose:** Extend development tuning and interval assessment, and independently audit canonical provenance.

**Data/sample:** 100 nonfinal galaxies; all 14 validation galaxies including the control; 7 calibration / 7 assessment objects.

**Code entry points:** [model_study.py](../analysis_results/ml_validation_20261028/model_study.py), [integrated_Ks_study.py](../analysis_results/ml_validation_20261028/integrated_Ks_study.py), [empirical_sensitivity.py](../analysis_results/ml_validation_20261028/empirical_sensitivity.py), [audit_canonical_final.py](../analysis_results/ml_validation_20261028/audit_canonical_final.py), [verify_results.py](../analysis_results/ml_validation_20261028/verify_results.py), [verify_tables.py](../analysis_results/ml_validation_20261028/verify_tables.py).

**Report:** [project_continuation_report.md](../analysis_results/ml_validation_20261028/project_continuation_report.md). **Notebook:** [expanded_training_evaluation.ipynb](../analysis_results/ml_validation_20261028/expanded_training_evaluation.ipynb).

**Scientific result:** 252 configurations, 210 physical joblib artifacts, and 131040 predictions / 504 score rows verified. Supplementary final-evaluation count = 0; canonical count = 1. Validation results are not new final scores.

**Output evidence:** [scientific_report.md](../analysis_results/ml_validation_20261028/scientific_report.md), [model_comparison.csv](../analysis_results/ml_validation_20261028/model_comparison.csv), [validation_interval_split.json](../analysis_results/ml_validation_20261028/validation_interval_split.json), [canonical_final_metric_recomputation.csv](../analysis_results/ml_validation_20261028/canonical_final_metric_recomputation.csv), [FINAL_EVALUATION_NOT_REPEATED.json](../analysis_results/ml_validation_20261028/FINAL_EVALUATION_NOT_REPEATED.json).

**Completion / why repetition is unnecessary:** Models, learning curves, out-of-domain tests, interpretation, empirical stress tests, notebook execution and saved canonical-score audit are complete. Final drivers are disabled under permanent policy.

**All outputs, including figures/tables:** [artifact inventory](inventories/ml_validation_20261028.md).

## M4-offset empirical HAWK-I/GRAAL calibration

**Directory:** `analysis_results/hawki_m4off_20261028`. **Status:** COMPLETED.

**Purpose:** Measure spatial PSF variation, matched stars, finite growth and background-sensitivity inputs.

**Data/sample:** Reduced pawprint and tile from the same 28 raw IDs; 965 primary measurements; 276 pairs / 244 Gaia identities.

**Code entry points:** [provenance_audit.py](../analysis_results/hawki_m4off_20261028/provenance_audit.py), [measure_psf.py](../analysis_results/hawki_m4off_20261028/measure_psf.py), [measure_fainter_sample.py](../analysis_results/hawki_m4off_20261028/measure_fainter_sample.py), [measure_noise.py](../analysis_results/hawki_m4off_20261028/measure_noise.py), [build_models_and_figures.py](../analysis_results/hawki_m4off_20261028/build_models_and_figures.py), [noise_model_validation.py](../analysis_results/hawki_m4off_20261028/noise_model_validation.py), [verify_results.py](../analysis_results/hawki_m4off_20261028/verify_results.py).

**Report:** [scientific_report.md](../analysis_results/hawki_m4off_20261028/scientific_report.md). **Notebook:** [empirical_calibration.ipynb](../analysis_results/hawki_m4off_20261028/empirical_calibration.ipynb).

**Scientific result:** Tile median FWHM is .3032 arcsec; spatial PSF/background variations are measured and R32 calibration is rejected. Joint PSF/core+halo templates, local covariance and broader confusion-background stress models are exported. This is not an ULTIMATE .2 arcsec measurement.

**Output evidence:** [PSF_summary.csv](../analysis_results/hawki_m4off_20261028/PSF_summary.csv), [PSF_spatial_cells.csv](../analysis_results/hawki_m4off_20261028/PSF_spatial_cells.csv), [paired_changes.csv](../analysis_results/hawki_m4off_20261028/paired_changes.csv), [aperture_noise.csv](../analysis_results/hawki_m4off_20261028/aperture_noise.csv), [quadrature_sensitivity.csv](../analysis_results/hawki_m4off_20261028/quadrature_sensitivity.csv), [sensitivity_models/README.md](../analysis_results/hawki_m4off_20261028/sensitivity_models/README.md), [completion_audit.json](../analysis_results/hawki_m4off_20261028/completion_audit.json).

**Completion / why repetition is unnecessary:** Empirical calibration, star identity/quality, sampling/window/brightness sensitivity, noise confusion, model validation and notebook execution are complete. Raw linearity and independent absolute calibration remain limited.

**All outputs, including figures/tables:** [artifact inventory](inventories/hawki_m4off_20261028.md).

## Root supporting output directories (all completed)

| Directory | Purpose / sample / result | Source and all outputs | Why no repetition |
|---|---|---|---|
| `attenuation_maps` | Five-view galaxy 294866 500-pc effective attenuation/projected dust/mask FITS; signed attenuation retained. | Root [build_notebooks.py](../analysis_results/build_notebooks.py), [science summary](../analysis_results/scientific_summary.md), [artifact index](inventories/attenuation_maps.md). | Derived ideal-image maps already produced; raw arrays are manifested server-only. |
| `extracted_294866` | Exactly 20 O2–O5 FITS files selected from the existing atlas; no new download. | [inspect_inputs.py](../analysis_results/inspect_inputs.py), [extraction manifest](../analysis_results/extraction_manifest.json), [artifact index](inventories/extracted_294866.md). | Extraction/provenance completed; do not duplicate raw files. |
| `figures` | Root five-view, orientation, correlation and raw HAWK-I inspection figures (PNG/PDF). | [make_presentation.py](../analysis_results/make_presentation.py), [artifact index](inventories/figures.md). | Existing diagnostic/publication-inspection products uploaded. |
| `pilot_reproduction_figures` | Reproduced original notebook figures. | [pilot_reproduced.ipynb](../analysis_results/pilot_reproduced.ipynb), [artifact index](inventories/pilot_reproduction_figures.md). | Original reproduction already executed; archive retains outputs. |

## Figures, tables, configurations, models and verification records

[Every source/notebook](inventories/SOURCE_AND_NOTEBOOK_INDEX.md) is indexed with static imports, definitions, notebook cells and kernel metadata. [FILE_INVENTORY.csv](manifests/FILE_INVENTORY.csv) covers every original path recursively, including additional data/download trees and the installed environment. [Existing checksum records](manifests/EXISTING_CHECKSUM_RECORDS.md) indexes model freezes, input/source manifests and output receipts. Per-study artifact indexes above provide **every** figure/table/log/model/configuration path, rather than relying on a short illustrative output list.

Detailed artifact-backed interpretations: [science review](evidence/SCIENCE_ARCHIVE_REVIEW.md), [ML review](evidence/ML_ARCHIVE_REVIEW.md), [instrument/provenance review](evidence/INSTRUMENT_ARCHIVE_REVIEW.md). They document tested negative cases, legacy scope, evidence limitations and exact count definitions. No saved pass receipt is described as a new rerun during archiving.
