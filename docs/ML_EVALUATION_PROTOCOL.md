# Frozen ML evaluation protocol

Verified from saved protocols/receipts on 2026-10-29. **The final20 has been evaluated once and is spent. Never reuse it as an untouched sample, tune on it, or execute supplementary final-stage scripts.** This document does not authorize fitting or inference.

## Frozen selection and exact IDs

[Original freeze](../analysis_results/ml_feasibility_20261027/expansion/partitions_frozen.json), [partition table](../analysis_results/ml_feasibility_20261027/expansion/galaxy_partitions.csv). Selection froze at 2026-10-27T03:47:20.721476Z, seed 20261027. Previously inspected 26 objects all became development; 94 new metadata-stratified galaxies were assigned 60 development, 14 validation, 20 final. Old 26-object test labels are historical, not fresh test status. Selected mass/activity strata are not a representative volume sample.
**development (86)**: 13, 63883, 117272, 167418, 184937, 294866, 324124, 355724, 394621, 424289, 486919, 502995, 507292, 535051, 546870, 553837, 558410, 594731, 596866, 604516, 613006, 613192, 616014, 626287, 630975, 638950, 571633, 578834, 319734, 208821, 184946, 599865, 565537, 586836, 539667, 289386, 460726, 96763, 474008, 461785, 324129, 527309, 319732, 516760, 612825, 556699, 348901, 220597, 610988, 455291, 602820, 117296, 521429, 628555, 448830, 576516, 545437, 96767, 626408, 610668, 342447, 595100, 429473, 220598, 533999, 289389, 96775, 220607, 242794, 63884, 522983, 184945, 184931, 253865, 475619, 630760, 366407, 383975, 618318, 167415, 184949, 571072, 275546, 589873, 513106, 338448.

**validation (14)**: 584286, 117253, 585080, 35, 584511, 96783, 536147, 583256, 459557, 441709, 220603, 499704, 379804, 564268.

**final_test (20)**: 333424, 63868, 14, 294867, 440408, 588986, 612699, 625281, 414918, 648822, 625800, 184951, 388545, 143899, 96780, 39, 578294, 167407, 63875, 590926.

Historical partition-file SHA-256 values (receipt values; originals preserved):

- `galaxy_partitions.csv`: `32779aeadf1e7ff2ed8c9ce93268fd112a5a2d2d3e25e4b3cbf3e9f4c12b20c1`
- `validation_galaxies.csv`: `d602203fecc84628782b3ec1608ac7f5b4bca2b988c3e20dd908da4271408ba5`
- `strata.csv`: `830ea0140316b3347ec8bd9d1d06d3f0ec5774cd7285d6a5d0d2136fecc61f3e`
- `development_galaxies.csv`: `87034165bc1b4630f4ae682bbd58898b88998c065c522b138507b6b301227121`
- `final_test_galaxies.csv`: `01a82f29f8b7b4e04d05b46ffa5388dbf8bff2f5cc5149e2c565441e59fbfd34`


## Grouping and leakage precautions

Galaxy is the independent sampling unit. Five orientations, four canonical noise draws (eight in preliminary work), bands and repeated targets are correlated records within a galaxy. Keep every view/draw together through folds, intervals, comparisons and bootstraps. No random row split is valid. Equal-galaxy aggregation prevents row count from determining scientific weight.

Source controls: development 13, 167418, 184937, 613192, 319734, 208821, 184946, 117296, 96767, 63884, 184945, 338448; validation 35; final 14, 96780, 39, 63875. Exact-zero projected dust does not imply zero source-product residual. Canonical fits use 74 positive-dust development objects, 13 validation interval calibrators and 16 primary final objects; all controls/predictions are preserved separately, without forcing labels to zero.

Features are observable dusty-image photometry/morphology. Clear counterparts, true attenuation/dust maps, galaxy IDs, mass/SFR and true inclination are excluded from X. Scaling, median imputation, spatial PCA8 and target scaling fit inside the training fold. Known distance/center, absolute apparent-flux luminosity priors and adaptive NIR reference apertures remain transfer limitations, not hidden truth features.

## Model selection and estimands

[Development protocol](../analysis_results/ml_expanded_20261028/DEVELOPMENT_PROTOCOL.md), [group folds](../analysis_results/ml_expanded_20261028/development_group_folds.csv), [family settings](../analysis_results/ml_expanded_20261028/chosen_family_settings.csv), [recommended settings](../analysis_results/ml_expanded_20261028/recommended_settings.csv).

Canonical primary uses common adaptive R=clip(1.5 R80,8,30) kpc from a deep dusty-Ks seeing reference, R80 within R35; fixed R12 is sensitivity. Same radius applies across bands/strategies/clear/dusty. Eight signed targets include integrated A_g/A_Ks, 1-kpc-smoothed g median/IQR, g/Ks R50 and concentration differences. Delta morphology means native dusty minus clear; correction subtracts predicted delta from observed dusty morphology while retaining instrumental transfer error.

Seventeen candidate settings × three scenarios × five grouped folds = 255 development CV fits. Per-family/target settings are shared between seeing/GLAO, selected from development mean MAE. Nominal and sensitivity estimators total 108 saved canonical artifacts. Approximate screen, median, photometric/summary/spatial ridge, forest and spatial boosting baselines are retained. Recommended families/hyperparameters were frozen before final, not selected from final scores. Validation calibrated intervals rather than tuning canonical hyperparameters.

## Metrics and uncertainties

MAE/RMSE and signed bias are aggregated with equal galaxy weighting; per-view/draw and per-galaxy tables retain tails and controls. Paired GLAO gain is seeing error minus GLAO error: positive favors GLAO. Bootstrap resamples galaxies (5,000 draws), conditions on fitted models and does not include retraining, source-label, selection or instrument-systematic uncertainty. Multiple comparisons remain exploratory unless explicitly predeclared.

Canonical nominal 80% per-target whole-galaxy intervals use calibration scores equal to each galaxy's maximum residual over all views/draws. With 13 calibration galaxies the order statistic rank is ceil(14×0.8)=12. They are not joint coverage over eight targets. Final A_g whole-galaxy coverage is 12/16; A_Ks 16/16, Ks R50 15/16, Ks concentration 14/16; small conditional counts are not universal coverage guarantees.

## Exact single-final provenance

[FINAL_PROTOCOL_FROZEN.json](../analysis_results/ml_expanded_20261028/FINAL_PROTOCOL_FROZEN.json): 2026-10-28T02:37:19.833340Z; 136 frozen artifacts; SHA-256 `587aab56d39e6b29ad47f381c4b1440c8dd28eb52811ebc4ae3842b6fc220ce4`. The final unseal receipt completed 02:42:13.589295Z, with checks before/during/after extraction and concurrent-run lock. [Completion receipt](../analysis_results/ml_expanded_20261028/FINAL_EVALUATION_COMPLETED.json) records 153,600 prediction rows, 20 total/16 primary/4 controls, `models_retuned=false`, `final_evaluation_count=1`. [Final unseal README](../analysis_results/ml_expanded_20261028/data_audit/FINAL_UNSEAL_README.md) explains historical sealed metadata versus opened final-only records.

[Canonical provenance check](../analysis_results/ml_validation_20261028/canonical_final_provenance_check.json) binds the same receipt. [Independent score audit](../analysis_results/ml_validation_20261028/canonical_final_score_audit.json) checks the saved 153,600 rows and 384 metric rows without calling model.predict. It is not a second evaluation.

## Supplementary validation-only work

[Continuation report](../analysis_results/ml_validation_20261028/project_continuation_report.md) reconciles concurrent work. A changed canonical-source freeze check blocked supplementary final access. [FINAL_EVALUATION_NOT_REPEATED.json](../analysis_results/ml_validation_20261028/FINAL_EVALUATION_NOT_REPEATED.json) records **zero supplementary final inference**; final scripts reject the spent project set.

Supplementary models use development-only grouped tuning separately per strategy; 252 configurations (210 main +42 integrated Ks), 210 physical joblib artifacts (180 main +30 integrated Ks). Validation scores include all 14 objects and are not interchangeable with canonical 13-positive-dust calibration or 16-final metrics. Its [interval split](../analysis_results/ml_validation_20261028/validation_interval_split.json) freezes seven calibration and seven assessment galaxies. These are descriptive validation findings, not a new final-selected winner. Learning curves/OOD and empirical/aperture sensitivities were completed without reopening final.

Any scientifically revised confirmatory model requires a **new independent holdout** and a new preregistered protocol. A saved artifact may be inspected or audited arithmetically without new inference; do not refit or rescore final merely to refresh documentation. Full audit details and historical pilot folds: [ML archival review](evidence/ML_ARCHIVE_REVIEW.md).
