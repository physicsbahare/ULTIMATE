# Scientific decisions and status ledger

Verified from existing artifacts on 2026-10-29. Status vocabulary: **COMPLETED**, **RESOLVED**, **NEGATIVE_RESULT**, **LIMITATION_ACCEPTED**, **BLOCKED**, **OPEN**, **SUPERSEDED**. Experiments can be completed while their hypotheses receive negative results. Preserve both.

The linked source/report and exhaustive [artifact indexes](COMPLETED_ANALYSES.md) provide supporting code, tables and figures; detailed context is in the [science](evidence/SCIENCE_ARCHIVE_REVIEW.md), [ML](evidence/ML_ARCHIVE_REVIEW.md) and [instrument](evidence/INSTRUMENT_ARCHIVE_REVIEW.md) reviews. Historical proposals are superseded where later work answered them.

## D01: Can the original pilot be reproduced and generalized across views?

**Decision status:** COMPLETED.

**Question investigated:** Can the original pilot be reproduced and generalized across views?

**Experiments performed:** Reproduced O1, five orientations and 27-choice mask/aperture sensitivity.

**Relevant source code and report:** Root inspect_inputs.py/build_notebooks.py; scientific_summary.md and tng_orientation_summary.csv. [Supporting record](../analysis_results/scientific_summary.md).

**Numerical evidence:** O1: A_g = .334442 mag, A_Ks = .020562 mag, rho_g = .924164 and rho_Ks = .548340. O2 Ks correlations are sensitive to masks.

**Scientific conclusion:** Ideal paired-image diagnostics reproduce; views are correlated and negative attenuation is retained.

**Remaining uncertainty:** No observer-accessible clear truth, component separation or population generalization.

## D02: Does positive screen evidence identify physical dust geometry?

**Decision status:** NEGATIVE_RESULT.

**Question investigated:** Does positive screen evidence identify physical dust geometry?

**Experiments performed:** Eight-band observer proxies, uniform/variable controls, priors, interpolation and discrepancy robustness.

**Relevant source code and report:** screen_test: run_experiment.py, screen_inference.py, run_robustness.py; scientific_report.md. [Supporting record](../analysis_results/screen_test_20261026/scientific_report.md).

**Numerical evidence:** Known uniform controls yield ln B ≈ +7.318 at z = .6 and +20.161 at z = 1 with restricted priors.

**Scientific conclusion:** Screen classification/color structure is not reliable physical geometry inference.

**Remaining uncertainty:** Broadband stellar-population/dust ambiguity and synthetic photometry approximation.

## D03: Does conditional ensemble calibration protect physical nulls?

**Decision status:** NEGATIVE_RESULT.

**Question investigated:** Does conditional ensemble calibration protect physical nulls?

**Experiments performed:** Final independent 500-draw calibration/evaluation, population-anchor stress.

**Relevant source code and report:** dr1_calibrated_screen: experiment.py, final_ensemble.py, final_stress.py; false_positive_audit.md. [Supporting record](../analysis_results/dr1_calibrated_screen_20261026/false_positive_audit.md).

**Numerical evidence:** Worst generator-null rate: 5.4%. Matched patchy-screen gain: 8 percentage points [2.8, 14.4]. Fixed anchor: 492/500 = 98.4% false positives.

**Scientific conclusion:** Conditional generator calibration succeeds only in its declared ensemble; general physical-null guarantee fails.

**Remaining uncertainty:** Unmodeled fixed-population distribution/covariance; no unique physical geometry.

## D04: What caused the anchor failure and did a positive model fix it?

**Decision status:** NEGATIVE_RESULT.

**Question investigated:** What caused the anchor failure and did a positive model fix it?

**Experiments performed:** Reproduced failing anchor; rank/color/push-forward checks; positive population-mixture × screen model; bounded adequacy gate.

**Relevant source code and report:** multiplicative: diagnose.py, physical_model.py, pilot.py, absolute_failure.py; scientific_report.md/development_gate.json. [Supporting record](../analysis_results/multiplicative_diagnosis_20261026/scientific_report.md).

**Numerical evidence:** Norm outside the first two PCs ≈ 2.97e-16. The old score, 85.45, exceeds the 69.59 cutoff. Physical-null chi² ≈ 436/812. Among 68 fit pairs, 42 null fits and 33 alternative fits failed.

**Scientific conclusion:** Covariance/probability push-forward is dominant; positivity tests do not solve adequacy. The failed gate prohibited a large evaluation.

**Remaining uncertainty:** Historical stellar/source likelihood and convergence remain inadequate.

## D05: Is sparse-band degeneracy a full-image impossibility result?

**Decision status:** RESOLVED.

**Question investigated:** Is sparse-band degeneracy a full-image impossibility result?

**Experiments performed:** Sparse-aperture counterexample versus retained-pixel fixed-pair information; u-band direction check.

**Relevant source code and report:** multiplicative: degeneracy.py, degeneracy_bound.py, aperture_information.py, existing_band_check.py. [Supporting record](../analysis_results/multiplicative_diagnosis_20261026/scientific_report.md).

**Numerical evidence:** At 5% false-positive rate, sparse fixed-pair power is 9.29%/8.69%; retaining pixels gives nearly 100%. The ≈ .021 mag coherent intrinsic-color bound is conditional.

**Scientific conclusion:** Compression can lose available distinguishing information; no universal broadband-image impossibility theorem follows.

**Remaining uncertainty:** Known-pair information does not establish feasible population-marginalized inference or spectroscopy exposure.

## D06: Can GLAO transfer structure without proving dust specificity?

**Decision status:** COMPLETED.

**Question investigated:** Can GLAO transfer structure without proving dust specificity?

**Experiments performed:** Spatial pilot, clear/uniform/patchy/mixed controls, component, depth, boundary and morphology checks.

**Relevant source code and report:** spatial: pilot.py, secondary_analysis.py, boundary_sensitivity.py; scientific_report.md. [Supporting record](../analysis_results/spatial_structure_pilot_20261026/scientific_report.md).

**Numerical evidence:** Dusty Ks concentration PSF bias changes −.291 → −.126. Effective widths after 1-kpc smoothing are ≈ 1.572/1.370 kpc.

**Scientific conclusion:** Conditional morphology/feature transfer is supported; color structure is not uniquely dust.

**Remaining uncertainty:** Population contamination, band matching, PSF-erased frequencies and rest-band proxies.

## D07: Why does threshold completeness decrease with deeper exposure?

**Decision status:** RESOLVED.

**Question investigated:** Why does threshold completeness decrease with deeper exposure?

**Experiments performed:** Noiseless threshold comparison and noise-crossing prediction.

**Relevant source code and report:** spatial: depth_threshold_diagnostic.py; depth_threshold_diagnostic.csv. [Supporting record](../analysis_results/spatial_structure_pilot_20261026/depth_threshold_diagnostic.csv).

**Numerical evidence:** Seeing completeness falls .1587 → .03913 → .00652 at .25/1/4 h. All 46 seeing reference pixels lie below the .05 mag cut.

**Scientific conclusion:** Noise-assisted crossings explain the trend; thresholded area is not physical recovery.

**Remaining uncertainty:** Threshold-dependent metric; depth cannot restore erased spatial modes.

## D08: Are single-galaxy dust-morphology signs general?

**Decision status:** COMPLETED.

**Question investigated:** Are single-galaxy dust-morphology signs general?

**Experiments performed:** 26 galaxies × five views × 22 bands; selection and viewing audits; 21 historically held-out galaxies.

**Relevant source code and report:** multigalaxy: audit_sample.py, statistics_analysis.py, morphology.py; scientific_report.md. [Supporting record](../analysis_results/multigalaxy_morphology_20261027/scientific_report.md).

**Numerical evidence:** Median ΔR50: g +.4003 kpc, Ks +.1239 kpc. Original galaxy 294866 is an opposite-sign outlier. Between-galaxy variation exceeds typical within-galaxy viewing SD.

**Scientific conclusion:** Report chosen-sample distribution and retain outlier; no universal sign or representative population claim.

**Remaining uncertainty:** Balanced/nonrepresentative sample, aperture and source-product systematics.

## D09: Which morphology/observing gains survived existing sensitivity checks?

**Decision status:** COMPLETED.

**Question investigated:** Which morphology/observing gains survived existing sensitivity checks?

**Experiments performed:** PSF/noise, detector, aperture/center, four-view, asymmetry and depth checks plus independent continuation.

**Relevant source code and report:** multigalaxy: observe.py, additional_robustness.py, null_diagnostics.py; continuation_verification/README.md. [Supporting record](../analysis_results/multigalaxy_morphology_20261027/continuation_verification/README.md).

**Numerical evidence:** Ks dusty-morphology R50 error: .08055 → .03942 kpc; concentration error: .36702 → .19016. The dust-concentration gain CI crosses zero, q can worsen, and the asymmetry gain changes sign with the estimator.

**Scientific conclusion:** Strong conditional size/concentration preservation; weaker dust-difference recovery; no universal morphology advantage.

**Remaining uncertainty:** Known center/sky, finite aperture, real backgrounds and independent physical truth.

## D10: Do zero projected-dust maps guarantee zero attenuation/bias labels?

**Decision status:** LIMITATION_ACCEPTED.

**Question investigated:** Do zero projected-dust maps guarantee zero attenuation/bias labels?

**Experiments performed:** Historical controls, independent minimal FITS decoder, full-field/crop/unit/precision/spectral-sign/smoothing audits.

**Relevant source code and report:** ml_expanded/label_audit: audit_old_controls.py, make_old_quality_masks.py; source_label_report.md. [Supporting record](../analysis_results/ml_expanded_20261028/label_audit/source_label_report.md).

**Numerical evidence:** Full-field median attenuation: g +.120994 mag, Ks +.019342 mag. All 24 raw O1 images exactly match the cache; the band-sign pattern persists across 20 views.

**Scientific conclusion:** Operational labels retain source residuals; no universal offset subtraction or calibrated physical precision.

**Remaining uncertainty:** Source/filter operator mismatch is a leading hypothesis, not demonstrated; historical configurations/RT statistics missing.

## D11: Should the project expand beyond preliminary ML?

**Decision status:** RESOLVED.

**Question investigated:** Should the project expand beyond preliminary ML?

**Experiments performed:** Grouped 26-galaxy pilot, baselines, OOD, intervals, aperture/label and empirical stress.

**Relevant source code and report:** ml_feasibility: ml_data.py, ml_benchmark.py, ml_postprocess.py; scientific_report.md. [Supporting record](../analysis_results/ml_feasibility_20261027/scientific_report.md).

**Numerical evidence:** A_g error: constant .22122 versus photometry .08877. Ks R50 error: constant .09961 versus ridge .04928. Spatial-median ridge fails to beat the constant baseline; no extra GLAO gain.

**Scientific conclusion:** Conditional surrogate feasibility justified a frozen larger benchmark; pilot failures remain preserved.

**Remaining uncertainty:** Small sample, undercoverage and OOD transfer; no physical precision.

## D12: What partitions and sampling units are permissible?

**Decision status:** RESOLVED.

**Question investigated:** What partitions and sampling units are permissible?

**Experiments performed:** Metadata-only 120 selection freeze, grouped development CV and before-image access partition assignment.

**Relevant source code and report:** ml_feasibility/expansion: freeze_selection.py; partitions_frozen.json, galaxy_partitions.csv. [Supporting record](ML_EVALUATION_PROTOCOL.md).

**Numerical evidence:** 86 development / 14 validation / 20 final galaxies. All original 26 are development objects; 74 are eligible for canonical training and 13 for calibration.

**Scientific conclusion:** Galaxy-level splits; all views/draws stay together; frozen IDs/hashes are permanent.

**Remaining uncertainty:** Deliberately stratified sample and nonrandom original 26 limit population inference.

## D13: What did the canonical final benchmark establish?

**Decision status:** COMPLETED.

**Question investigated:** What did the canonical final benchmark establish?

**Experiments performed:** Development-only selection, pre-final freeze, single unseal/evaluation; controls, OOD, intervals and tails retained.

**Relevant source code and report:** ml_expanded: expanded_models.py, expanded_features.py, summarize.py; scientific_report.md. [Supporting record](../analysis_results/ml_expanded_20261028/scientific_report.md).

**Numerical evidence:** GLAO errors: A_g .3003 → .0741 mag; A_Ks .0594 → .0124 mag; Ks ΔR50 .1282 → .0799 kpc; ΔC .1521 → .0887.

**Scientific conclusion:** Recommended ML predicts operational paired DR1 targets. These metrics do not measure physical dust accuracy.

**Remaining uncertainty:** Physical source calibration, reference aperture, selected domain and conditional uncertainty.

## D14: Did GLAO add robust ML information about dust bias?

**Decision status:** NEGATIVE_RESULT.

**Question investigated:** Did GLAO add robust ML information about dust bias?

**Experiments performed:** Preliminary, canonical expanded and supplementary paired-galaxy comparisons.

**Relevant source code and report:** ml_expanded: diagnostics.py/summarize.py; recommended_gains.csv; ml_validation: model_study.py. [Supporting record](../analysis_results/ml_expanded_20261028/recommended_gains.csv).

**Numerical evidence:** Canonical A_g error: seeing .0734 / GLAO .0741; Ks ΔR50 error: .0777 / .0799. No recommended GLAO-gain interval is wholly positive; g R50 worsens.

**Scientific conclusion:** No robust additional GLAO benefit established under tested conditions.

**Remaining uncertainty:** Limited sample/conditions; does not rule out future physical information gains.

## D15: Does direct/corrected morphology still benefit?

**Decision status:** COMPLETED.

**Question investigated:** Does direct/corrected morphology still benefit?

**Experiments performed:** Transfer errors relative to native dusty morphology and correction errors relative to native clear morphology, distinct from bias prediction.

**Relevant source code and report:** ml_expanded: correction_analysis.py; final_morphology_correction_gains.csv. [Supporting record](../analysis_results/ml_expanded_20261028/final_morphology_correction_gains.csv).

**Numerical evidence:** Native-dusty Ks R50 error: .1238 → .0595 kpc. Corrected native-clear error: .1210 → .0861 kpc; gain .0349 [.0091, .0633].

**Scientific conclusion:** Positive conditional direct/corrected-radius result coexists with the negative result for extra ML information about dust bias.

**Remaining uncertainty:** Known center/aperture, rest band, noisy observing model and operational clear truth.

## D16: May supplementary/revised models use the final 20 as untouched data?

**Decision status:** RESOLVED.

**Question investigated:** May supplementary/revised models use the final 20 as untouched data?

**Experiments performed:** Canonical freeze/unseal receipts; changed-source freeze abort; saved prediction arithmetic/provenance audit.

**Relevant source code and report:** ml_validation: audit_canonical_final.py, final_evaluation.py; FINAL_EVALUATION_NOT_REPEATED.json. [Supporting record](../analysis_results/ml_validation_20261028/project_continuation_report.md).

**Numerical evidence:** Canonical predictions: 153600 rows; evaluation_count = 1. Supplementary final-evaluation count = 0. Freeze SHA: 587aab56…fc220ce4.

**Scientific conclusion:** The final 20 are permanently spent. Supplementary results are validation-only; a revised confirmatory model needs a new independent holdout.

**Remaining uncertainty:** No statistical reset by renaming splits or inspecting outcomes again.

## D17: Are aperture/center/instrument sensitivities absent?

**Decision status:** RESOLVED.

**Question investigated:** Are aperture/center/instrument sensitivities absent?

**Experiments performed:** Canonical nonfinal PSF/covariance/software-binning tests, center/radius and supplementary empirical sensitivities.

**Relevant source code and report:** ml_expanded/instrument_sensitivity: run_stress.py, center_aperture_stress.py; ml_validation: empirical_sensitivity.py. [Supporting record](../analysis_results/ml_expanded_20261028/instrument_sensitivity/center_aperture_report.md).

**Numerical evidence:** 640 instrument cases and 1120 center-target rows. Center shifts change dC_Ks by median .047–.079, maximum .447.

**Scientific conclusion:** Existing bounded tests are complete; concentration definition and centering matter. Do not recommend them as new work.

**Remaining uncertainty:** No fully propagated deployed segmentation/centering distribution or joint perturbation calibration.

## D18: Are required DR2 replacement products available for this plan?

**Decision status:** BLOCKED.

**Question investigated:** Are required DR2 replacement products available for this plan?

**Experiments performed:** Authenticated metadata/catalogue/file-category/specification inspection; local DR1 identity check.

**Relevant source code and report:** screen_test: probe_tng.py, inspect_catalogue.py; catalogue_status.md, tng_catalogue_probe.json. [Supporting record](../analysis_results/screen_test_20261026/catalogue_status.md).

**Numerical evidence:** The legacy atlas lists 1154 URLs. No applicable DR2-specific replacement route or local products were verified.

**Scientific conclusion:** Suitability and availability were already checked; required data are unavailable for the planned use. Reopen only with new release-specific evidence.

**Remaining uncertainty:** Existing records do not prove 294866 affected by the reported DR1 allocation issue; exact applicable release access is not established.

## D19: Are NGC 3256 products/calibration associations still missing?

**Decision status:** SUPERSEDED.

**Question investigated:** Are NGC 3256 products/calibration associations still missing?

**Experiments performed:** Initial raw inventory followed by official reduced-product, Cal Selector and catalogue characterization.

**Relevant source code and report:** inspect_hawki.py; ml_feasibility/hawki: query_calibrations.py, diagnose_reduced.py; empirical report. [Supporting record](../analysis_results/ml_feasibility_20261027/hawki/hawki_empirical_calibration_report.md).

**Numerical evidence:** 22 raw exposures / 88 image planes. All 132/132 raw-byte checksum and DATASUM checks pass; three certified complete Raw2Master associations.

**Scientific conclusion:** The earlier missing-local-products statement is historical; empirical reduced-product calibration is complete. No fresh local raw reduction is claimed.

**Remaining uncertainty:** Independent absolute calibration, raw linearity and local calibration masters remain limited.

## D20: What has M4-offset calibrated?

**Decision status:** COMPLETED.

**Question investigated:** What has M4-offset calibrated?

**Experiments performed:** Gaia/ESO star validation, paired planes, spatial PSF/finite-growth measurements, quadrature, window, brightness and noise-confusion checks.

**Relevant source code and report:** hawki_m4off: measure_psf.py, measure_noise.py, build_models_and_figures.py, quadrature_check.py; scientific_report.md. [Supporting record](../analysis_results/hawki_m4off_20261028/scientific_report.md).

**Numerical evidence:** Tile: 356 primary measurements; FWHM .3032 arcsec [.3005, .3070]. There are 276 pairs / 244 IDs; the global paired CI crosses zero.

**Scientific conclusion:** Empirical PSF/background sensitivity inputs are complete; they do not measure ULTIMATE .2 arcsec performance.

**Remaining uncertainty:** Finite PSF wings, spatial conditioning, fit floors, nonlinearity and independent absolute calibration.

## D21: Can large-aperture noise be treated as a calibrated instrument law?

**Decision status:** NEGATIVE_RESULT.

**Question investigated:** Can large-aperture noise be treated as a calibrated instrument law?

**Experiments performed:** Matched-operator NGC/M4 apertures, mask/confusion stress, local covariance and broader background-model responses.

**Relevant source code and report:** hawki_m4off: confusion_stress.py, noise_model_validation.py; sensitivity_models/README.md. [Supporting record](../analysis_results/hawki_m4off_20261028/sensitivity_models/README.md).

**Numerical evidence:** M4 excess noise at R2/R4/R8/R16 ≈ 1.73/2.64/4.60/6.53. R32 has only 11–23 nonoverlapping apertures per plane; broad-response mismatch is 13–37%.

**Scientific conclusion:** Reject R32 calibration; separate local covariance from population/sky confusion; models are stress scenarios, not a unique normalized noise law.

**Remaining uncertainty:** Unconfused galaxy-scale covariance and coverage/depth transfer are not established.

## D22: Does this evidence establish physical/instrument forecast precision?

**Decision status:** LIMITATION_ACCEPTED.

**Question investigated:** Does this evidence establish physical/instrument forecast precision?

**Experiments performed:** Rest-band, broadband-source, selection/control, empirical instrument and uncertainty limitations documented across completed studies.

**Relevant source code and report:** All scientific reports; instrument_audit.md; redshift_bandpass_limitations.md; source_label_report.md. [Supporting record](PROJECT_STATE.md).

**Numerical evidence:** Rest Ks at z = .3 corresponds to 2.807 µm. M4 FWHM ≈ .3032 arcsec does not measure ULTIMATE .2 arcsec performance. Canonical A_g interval coverage is 12/16.

**Scientific conclusion:** Use bounded operational-feasibility framing; do not combine physical, ML bias, direct morphology and instrument claims.

**Remaining uncertainty:** Stronger claims need new source evidence, external calibration and independent validation.

## D23: What remains for publication and future inference?

**Decision status:** OPEN.

**Question investigated:** What remains for publication and future inference?

**Experiments performed:** Reviewed existing reports, literature context, source-owner reproduction specification and MaNGA proposal.

**Relevant source code and report:** ml_validation/source_owner_reproduction_request.md; spatial/MaNGA_validation_note.md; label_audit/literature_context.md. [Supporting record](OPEN_QUESTIONS.md).

**Numerical evidence:** No external observational dust truth or historical-operator reproduction has been delivered; existing forecasts are conditional.

**Scientific conclusion:** Manuscript synthesis, citations and rights are current priorities. Stronger physics depends on new independent evidence.

**Remaining uncertainty:** Novelty, source-operator cause, external transfer, representativeness and long-term data retention.

