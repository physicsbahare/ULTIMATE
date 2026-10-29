# ULTIMATE–Subaru: verified expanded-project handoff

**2026-10-28. The project now has a verified 120-galaxy inventory and one completed, frozen final evaluation.** Its scientific result supports a conditional simulation-product prediction study. Physical dust calibration and an observer-frame ULTIMATE forecast remain unvalidated.

## Canonical final results

The pre-existing continuation in [ml_expanded_20261028](../ml_expanded_20261028/scientific_report.md) completed during this work. Its 86 development / 14 validation / 20 final assignments are unchanged. Models fit 74 positive-projected-dust development galaxies; 13 positive-dust validation galaxies calibrate intervals. The final 20 comprise **16 primary galaxies and four source controls** under a policy frozen before scientific access. All five orientations and four noise draws remain grouped by galaxy.

Recommended families/settings were selected using development cross-validation, before validation diagnostics and final access. Primary adaptive-aperture, nominal GLAO results are:

| Operational target | Constant MAE | Photometric ridge MAE, seeing | Recommended MAE, GLAO | GLAO RMSE | Seeing minus GLAO MAE, 95% paired galaxy interval |
| --- | --- | --- | --- | --- | --- |
| Integrated g attenuation, mag | 0.3003 | 0.0794 | 0.0741 | 0.1098 | −0.0007 [−0.0057, 0.0042] |
| Integrated Ks attenuation, mag | 0.0594 | 0.0150 | 0.0124 | 0.0163 | −0.0001 [−0.0003, 0.0002] |
| Ks ΔR50, kpc | 0.1282 | 0.0992 | 0.0799 | 0.1189 | −0.0022 [−0.0077, 0.0026] |
| Ks ΔC | 0.1521 | 0.1174 | 0.0887 | 0.1306 | 0.0000 [−0.0121, 0.0127] |

Equal-galaxy metrics describe the selected simulation sample; views and draws are repeated measurements. Source-product uncertainty and retraining uncertainty are outside these bootstrap intervals. The incremental g-attenuation gain over photometry has an interval spanning zero. The Ks radius-bias gain over the constant also has an interval spanning zero despite favorable point MAE. Ks concentration improves over both baselines under the stated conditional definitions. All model families, unfavorable outcomes and per-view predictions are retained.

Simple photometry remains competitive or superior to more complicated methods: final GLAO g-attenuation MAE is 0.0793 for photometric ridge, compared with 0.0971 for spatial boosting and approximately 0.135 for either forest family. The approximate foreground-screen colour baseline performs poorly (0.2720 mag). No family is assumed superior because it uses more features.

The spatial median target now modestly improves over the constant (0.0441 versus 0.0522 mag MAE), revising the preliminary negative result without concealing its tail: RMSE is 0.1397 mag. Spatial attenuation IQR reaches 0.0707 versus 0.1214 mag for the constant. These are effective projected statistics, not unique three-dimensional geometry.

## What resolution does and does not improve

No recommended target has a final GLAO dust-bias-prediction interval wholly above zero. The g-radius-bias prediction degrades under the narrower NIR condition. This does not establish intrinsic information loss: finite models, source labels and observable degeneracy remain possible limits.

There is a distinct morphology benefit. Observed dusty Ks R50 versus native dusty R50 has MAE **0.1238 kpc seeing / 0.0595 kpc GLAO**; the paired gain is 0.0642 [0.0398, 0.0890] kpc. After the frozen dust-bias correction, error relative to native clear R50 is **0.1210 / 0.0861 kpc**, a gain of 0.0349 [0.0091, 0.0633] kpc. In the GLAO branch, correction improves native-clear size error from 0.2325 to 0.0861 kpc. Better morphology transfer can therefore coexist with no demonstrated additional information about the dust bias itself.

Optical-only, seeing optical+NIR and assisted-NIR comparisons use matched galaxies. Extra bands use extra total observing time; they are not an equal-total-time efficiency comparison. Optical g stays seeing-limited. Adaptive apertures use a deep Ks reference, so fixed12 is the cleaner optical-only information control. Nominal Ks widths are approximately 0.588/0.390 arcsec; the experiment does not validate an actual 0.2-arcsec ULTIMATE PSF.

## Reliability and publication limits

- Exact-zero projected-dust controls retain coherent full-field g offsets around 0.12 mag and filter-dependent sign reversals. Raw/cache, units, coordinates and full-field checks disfavor a crop/unit explanation. Spatial smoothing supports a Monte Carlo component, but cannot explain the integrated spectral pattern alone. An analytic-probe versus Monte Carlo spectral/filter operator mismatch is a candidate; the historical configuration is unavailable. No universal offset is subtracted. Positive-dust labels remain affected by this unresolved calibration.
- Matched apertures have reproducible definitions. Adaptive R=clip(1.5R80 within R35, 8, 30) kpc uses observed dusty Ks. Its deep-reference radius, known center and distance are idealizations. Old-control |ΔC_Ks| reaches 0.2398 under this aperture versus 0.0460 at fixed12. Center offsets of 0.5 kpc materially alter concentration labels. These are task-definition/systematic sensitivities, not Gaussian error bars.
- Final integrated-g whole-galaxy interval coverage is **12/16 (75%)**, below the nominal 80%; small final counts and broad intervals limit calibration conclusions. The four final source controls have mean predicted g contrast approximately 0.199 mag versus mean atlas contrast approximately 0.121 mag. Their failures remain visible.
- Learning curves support more independent, calibrated training data, particularly for spatial models. High-mass holdouts and observable-distance diagnostics remain same-simulation checks. No independent simulation-to-real dust validation has been obtained.
- HAWK-I informs PSF wings, sampling and covariance stresses only. Its approximately 0.294–0.317 arcsec measured FWHM is separate from provisional ULTIMATE conditions. Matching adjacent-pixel correlations does not reproduce the measured large-aperture noise excess. No raw reduction, large file packaging or collaborator transfer was duplicated.
- Fixed-rest-band z=0.1 degradation is not exact observer-frame synthetic photometry. Current design/filter/spectral information, realistic centering/sky/segmentation, source-label reconciliation and independent domain tests are required before a physical ULTIMATE forecast.

A workshop is supported. A paper can present a bounded interpretable benchmark, failure accounting and the distinction between morphology preservation and incremental physical inference. It cannot yet claim calibrated physical attenuation precision or unique 3D dust recovery.

## Independent checks and supplementary executed work

This continuation created a separate validation-only study with 252 configurations and 180 fitted artifacts, using the same verified nonfinal image products. It includes independent per-scenario development tuning, regularized regressions, forest/boosting comparisons, six attenuation/morphology targets, 7/7 validation calibration/assessment, nested development learning curves, high-mass OOD refits, per-view/draw predictions, aperture/control masks, coefficients and additional HAWK-I-informed stresses. Its fixed12 validation summary-ridge MAEs are 0.0627 mag for Ag, 0.0434 kpc for Ks ΔR50 and 0.0794 for Ks ΔC. These are **validation results on a different sample/operator/model protocol**, not replacements for canonical final numbers. Its spatial ridge loses to photometry for Ag (0.0812 versus 0.0727 mag).

The supplemental final-freeze check detected a source-file change before any supplemental final science access. Inspection established that the feature/target operators are AST-identical; only final driver/isolation guards changed. The pre-existing continuation had independently frozen and completed the project's final evaluation. **No second final inference was run.** The additional models remain validation-only, and their final entrypoints now reject use of this spent final set. Future confirmatory revisions need a new independent holdout.

Independent audit evidence retained here:

- All 120 current compressed hashes/lengths match the downloader's CRC/tar-validated records; no duplicate download.
- All 500 nonfinal cache views / 3,500 arrays checked; 24,000 FITS headers and 6,240 original raw-member hashes reconcile.
- Supplementary 131,040 prediction rows and 504 score rows verified; observational allowlists, grouped weighting, optical controls and calibration/assessment separation pass.
- Canonical frozen artifact hashes match the original receipt; 153,600 final prediction rows have complete unique view/draw keys, and 384 metric rows independently reproduce from stored predictions. This is verification, not a new model evaluation.
- Earlier pilot and morphology output manifests pass preservation checks. No prior result is modified by this continuation.

## Literature position

[Fu et al. (2025)](https://academic.oup.com/mnras/article/540/3/2081/8140852) establishes a high-redshift image-based attenuation-ML precedent. [Dobbels & Baes (2021)](https://arxiv.org/abs/2110.01704) predicts resolved dust-emission properties from UV–MIR inputs; the requested 2022 reference was not uniquely identified and is not silently misdated. [Pastrav et al. (2013)](https://arxiv.org/abs/1301.5602) already quantifies dust-induced photometric structural biases with radiative transfer. [Bokona Tulu et al. (2026)](https://arxiv.org/abs/2605.20886) directly overlaps the same atlas's morphology science. [DeepMerge II](https://arxiv.org/abs/2103.01373) demonstrates the separate problem of simulation-to-observation domain shift. The contribution must be defensible observational prediction and incremental resolution value, with source/systematic controls; neither first dust ML nor unique geometry is supported.

## Deliverables

- [Canonical scientific report](../ml_expanded_20261028/scientific_report.md), [workshop summary](../ml_expanded_20261028/workshop_summary.md), [executed canonical notebook](../ml_expanded_20261028/expanded_ml_executed.ipynb).
- [Supplementary executed training/evaluation notebook](expanded_training_evaluation.ipynb), [supplementary validation report](scientific_report.md), [method protocol](protocol.md).
- Canonical `models/`, `final_predictions.csv.gz`, `recommended_performance.csv`, `recommended_gains.csv`, calibration, learning/OOD, correction and sensitivity tables; PNG/PDF figures and HTML notebook export.
- Supplementary `models/`, `feature_table.csv.gz`, `target_table.csv`, `heldout_predictions.csv.gz`, `model_comparison.csv`, `learning_curves.csv`, `uncertainty_calibration.csv`, `OOD_per_orientation_predictions.csv.gz`, `model_feature_interpretation.csv`, quality flags and sensitivity tables; PNG/PDF figures.
- [HAWK-I product/reference manifest](hawki_collaborator_manifest.md) and [minimal source-owner reconciliation experiment](source_owner_reproduction_request.md). No message or large-file transfer has been sent.
