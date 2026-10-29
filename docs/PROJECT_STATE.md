# Current project state

Archival baseline verified **2026-10-29 (Asia/Taipei)** by read-only inspection; a later owner-authorized targeted continuation is recorded at the end of this document. The scientific archive commit is recorded in [GITHUB_SYNC_REPORT.md](GITHUB_SYNC_REPORT.md); that later receipt references its parent archive commit to avoid a self-referential hash. No scientific experiment was performed during the archival update; the separate targeted continuation below did perform new authorized work.

Research title: **Beyond the Foreground Screen: Machine-Learning Dust Geometry with ULTIMATE-Subaru**. Aim: a publishable, bounded ULTIMATE–Subaru feasibility study.

## Objectives and estimands

**Task A:** predict effective attenuation statistics from optical–NIR photometry and spatial observations. **Task B:** predict and correct dust-induced morphology biases. Keep four claims separate:

| Question | Current evidence / boundary |
|---|---|
| Physical dust inference | Unique geometry and calibrated physical attenuation precision are not established; stellar populations and source-product systematics limit identification. |
| Dust-induced morphology-bias prediction | ML predicts operational native dusty-minus-clear DR1 statistics under fixed definitions. |
| Direct observed morphology measurement/recovery | GLAO improves conditional Ks radius/concentration preservation and corrected radius accuracy. This does not imply improved dust inference. |
| Instrumental and observational biases | PSF, noise, depth, sampling, aperture, centers and source selection were investigated; empirical HAWK-I nuisances do not validate ULTIMATE forecasts. |

## Existing data and completed work

All **120 galaxies / 600 correlated views** are prepared and verified in saved receipts. The partition is frozen: 86 development, 14 validation, **20 spent final**. Twelve development, one validation and four final exact-zero projected-dust controls are retained separately; canonical training uses 74 positive-dust development objects, interval calibration 13 validation objects, final primary metrics 16 final objects. The earlier 26-galaxy held-out labels were retired when those galaxies entered development. [ML protocol](ML_EVALUATION_PROTOCOL.md).

Local inputs include original/expanded TNG50–SKIRT DR1 atlases, 26-galaxy morphology products, raw NGC3256 exposures, official NGC3256 reduced cutouts, M4-offset reduced pawprint/tile and calibration/catalogue references. [Data provenance](DATA_PROVENANCE.md) and the recursive [file manifest](manifests/FILE_INVENTORY.csv) cover all trees, not only named studies.

Completed: original pilot/five views, observer-band screen controls, conditional screen calibration and catastrophic false-positive stress, positive multiplicative model and failed gate, spatial-structure/resolution pilot, 26-galaxy morphology and independent replay, preliminary ML, metadata-frozen expansion, canonical ML single final evaluation, supplementary validation-only models, source-label audits, aperture/center/PSF/noise/sampling sensitivities, HAWK-I/GRAAL NGC3256 and M4 characterization. The [complete index](COMPLETED_ANALYSES.md) includes failure studies and output indexes.

## Validated saved numerical findings

Canonical single-final, adaptive-aperture nominal GLAO, equal-galaxy MAE:

| Target | Constant | Recommended ML | Unit |
|---|---:|---:|---|
| A_g | 0.3003 | 0.0741 | mag |
| A_Ks | 0.0594 | 0.0124 | mag |
| Delta R50_Ks | 0.1282 | 0.0799 | kpc |
| Delta C_Ks | 0.1521 | 0.0887 | dimensionless |

[Canonical scientific report](../analysis_results/ml_expanded_20261028/scientific_report.md), [recommended performance](../analysis_results/ml_expanded_20261028/recommended_performance.csv), [final provenance audit](../analysis_results/ml_validation_20261028/canonical_final_provenance_check.json). These numbers describe DR1 paired-image targets, **not validated physical dust precision**. The frozen recommended models must not be replaced with post-final winners.

No robust additional GLAO benefit for ML dust-bias prediction was established under tested conditions. Direct native-dusty Ks radius transfer MAE improves 0.1238→0.0595 kpc; corrected native-clear radius error improves **0.1210→0.0861 kpc** (seeing→GLAO, paired gain 0.0349 kpc, conditional 95% interval [0.0091,0.0633]). [Correction evidence in report](../analysis_results/ml_expanded_20261028/scientific_report.md), [correction gains](../analysis_results/ml_expanded_20261028/final_morphology_correction_gains.csv).

The 26-galaxy primary fixed-R12 study finds median galaxy-mean dust-pair radius changes +0.4003 kpc in g, +0.1239 kpc in Ks; galaxy 294866 is an opposite-sign outlier retained in the archive. [Morphology report](../analysis_results/multigalaxy_morphology_20261027/scientific_report.md).

M4 tile median FWHM≈**0.3032 arcsec**, spatial interval≈[0.3005,0.3070]; spatial PSF and background covariance/confusion vary. NGC3256 and M4 empirical characterization is **completed**. [M4 report](../analysis_results/hawki_m4off_20261028/scientific_report.md). These are empirical sensitivity inputs, not measured ULTIMATE 0.2-arcsec performance.

## Limitations and publication readiness

Zero-projected-dust source residuals remain unexplained: historical controls retain about 0.121 mag integrated g and 0.019 mag Ks offsets over the full field, with filter-dependent signs. A source spectral-operator mismatch is a hypothesis, not a demonstrated historical cause. No global offset correction is justified. [Completed source audit](../analysis_results/ml_expanded_20261028/label_audit/source_label_report.md).

Foreground-screen geometry classification fails population-null calibration; an anchor produces 98.4% false positives despite ensemble calibration. The positive model failed its adequacy/convergence gate. Negative evidence is retained in [failures](FAILED_EXPERIMENTS.md).

Matched-rest-band z=0.1 mocks are conditional distance-degradation experiments, not exact observer-frame ULTIMATE photometry. Fixed/deep aperture, known center/distance, deliberately selected sample, five correlated orientations, imperfect uncertainty coverage and omitted sky/PSF/segmentation/systematic floors limit transfer. R32 empirical noise is rejected. A new confirmatory model needs a new independent holdout.

DR2 suitability/availability was already checked. Required matched data are **not available for the planned use**; generic catalogue authentication was completed and no verified applicable release-specific replacement exists locally. Do not reopen without genuinely new evidence.

The evidence supports a workshop and a carefully bounded operational feasibility paper; a publication-ready physical dust precision or ULTIMATE performance claim is not supported. Current priorities are claim scoping, artifact/citation traceability, manuscript synthesis and documenting accepted limitations. Source-owner reproduction and independent external validation remain dependencies for stronger claims, not instructions to rerun analyses. [Publication plan](PUBLICATION_PLAN.md), [open questions](OPEN_QUESTIONS.md).

## Authorized targeted 0.200-arcsec continuation (2026-10-29)

After the archival task, the owner explicitly authorized the [targeted overlap audit](../analysis_results/ultimate_020_information_gap_20261029/overlap_and_novelty_audit.md) and conditional new work. An earlier0.200 Gaussian simulation was a single-galaxy privileged oracle, not a fixed-rest-band morphology/observable-ML test. The distinct Ks-only0.38955→0.200 experiment is now **COMPLETED** in a separate directory; earlier outputs/frozen receipts remain unchanged.

Fourteen development galaxies (13 fit-eligible +source-control13), five correlated views, no added noise, Gaussian and Moffat beta3.020805, shared saved apertures/labels, refined pixel integration. Direct dusty-radius MAE improves0.02669→0.01176kpc Gaussian and0.06371→0.01627kpc Moffat. Concentration also improves under both shapes. Full spatial ridge at0.200 is worse than g/J/Ks photometric ridge for all four prespecified operational targets; summary-model width gains are shape-dependent/adverse. No robust additional dust-ML benefit is demonstrated; no universal impossibility result follows.

**Decision: GO for the completed bounded information assessment; stop further computation and proceed to manuscript/workshop synthesis.** This exploratory13-galaxy grouped development exercise is not new confirmation and does not replace canonical final scores or select a preferred model. No validation/final inference, full120 retrain, new calibration, DR2 investigation or confirmation campaign occurred. [Scientific decision and full results](../analysis_results/ultimate_020_information_gap_20261029/scientific_decision.md), [workshop/paper implications](../analysis_results/ultimate_020_information_gap_20261029/workshop_paper_implications.md), [verification](../analysis_results/ultimate_020_information_gap_20261029/verification.json).
