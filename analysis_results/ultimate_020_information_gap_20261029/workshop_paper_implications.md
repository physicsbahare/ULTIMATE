# Workshop and short-paper implications

2026-10-29. The targeted assessment is complete. Use the [scientific decision](scientific_decision.md) for all numerical qualifications and the [overlap audit](overlap_and_novelty_audit.md) to explain novelty. This document synthesizes local evidence; it does not claim a fresh literature verification or a completed manuscript.

## Central narrative

Radiative-transfer simulations permit paired operational benchmarks that cannot be measured directly in a real galaxy. Interpretable optical–NIR ML predicts some of these statistics, while a narrower Ks PSF separately improves the preservation of observed morphology. These two capabilities must be measured independently. Even an assumed .200-arcsec PSF does not demonstrate a robust additional dust-prediction benefit with the present features and small development sample. The negative result constrains the observing claim without invalidating the useful morphological capability.

Stay close to **Beyond the Foreground Screen: Machine-Learning Dust Geometry with ULTIMATE-Subaru**, retaining its radiative-transfer, optical–NIR, attenuation, interpretable-ML and GLAO motivation. The project title is motivation, not proof of uniquely recovered geometry. A separate exact accepted-abstract text was not identified in the inspected current records, so no unverified verbatim abstract is reproduced or rewritten here.

## Ten-minute presentation

| Time | Message | Existing/new artifact |
|---|---|---|
| 0:00–1:00 | Scientific question: what does sharper NIR imaging add beyond broadband photometry? Distinguish paired operational statistics from physical geometry. | Project title and one simple paired-image schematic from existing material; no new physical claim. |
| 1:00–2:15 | DR1 radiative-transfer dusty/clear pairs, five correlated views per galaxy, frozen86/14/20 and spent final. Zero-dust source residuals limit physical precision. | Existing [source-control figure](../multigalaxy_morphology_20261027/figures/11_source_and_estimator_controls.pdf). Use a cropped panel only in a newly authored slide, preserving the original file. |
| 2:15–4:15 | Canonical interpretable ML compared with photometry and constant baselines; show both attenuation and morphology-bias prediction. | Existing [model/observing comparison](../ml_expanded_20261028/figures/model_and_observing_strategy_comparison.pdf) and saved recommended-performance table. Label single spent-final evaluation, operational units and denominator. |
| 4:15–5:15 | Earlier nominal seeing→GLAO ML gain is not robust; direct morphology is a separate question. | Existing [paired GLAO gains](../ml_expanded_20261028/figures/paired_GLAO_gains.pdf); do not choose a post-final winner. |
| 5:15–6:45 | New targeted extension: .390→.200 FWHM directly improves radius/concentration in a noiseless development subset. | New [morphology width gain](figures/morphology_width_gain.pdf). Explicit13 galaxies, two shapes, fixed rest bands, no noise. |
| 6:45–8:15 | More structure changes the input, but does it help dust ML? Shape-dependent or adverse gains; spatial ridge loses to photometry here. | New [ML width gain](figures/ml_width_gain.pdf), all four prespecified targets. Do not display only the favorable Moffat concentration panel. |
| 8:15–9:15 | HAWK-I empirical anchor: completed measured nuisance characterization, not a .200 measurement or clear-galaxy dust truth. | M4 [PSF summary](../hawki_m4off_20261028/PSF_summary.csv) as one factual annotation, not a new calibration presentation. |
| 9:15–10:00 | Conditional feasibility supports a short paper: useful morphology capability, bounded operational ML, no demonstrated extra .200 dust advantage. | One conclusion slide with source-label, observer-band, sample and instrument limits. |

If slides become crowded, keep the two new figures on adjacent slides and move detailed PSF conversion/sampling and full model tables to backup. The negative result stays in the main talk. This is a slide-authoring recommendation; no existing archived deck was overwritten.

## Manuscript structure and figure selection

Lead with the question of incremental resolution value rather than an assertion of new dust physics. Describe the canonical frozen benchmark first; place the new small development exercise in an explicitly exploratory sensitivity section. Its scores must not be pooled with or substituted for the spent-final metrics. State that all0.200 fitting settings were fixed for this bounded continuation; no new preferred final model was chosen.

A compact main-figure set is:

1. Existing representative matched images and source-control inset: [representative success/failure](../ml_expanded_20261028/figures/representative_success_and_failure_images.pdf), with the existing [source controls](../multigalaxy_morphology_20261027/figures/11_source_and_estimator_controls.pdf). Keep data/rights screening in the publication workflow.
2. Existing [canonical ML comparison](../ml_expanded_20261028/figures/model_and_observing_strategy_comparison.pdf), with paired nominal resolution gains or a companion panel from the saved [paired-gain figure](../ml_expanded_20261028/figures/paired_GLAO_gains.pdf).
3. New [direct morphology width comparison](figures/morphology_width_gain.pdf).
4. New [matched-fold ML width comparison](figures/ml_width_gain.pdf).

Place the operator checks, complete per-target tables, all-galaxy failures, fixed-model-transfer scores, existing aperture/centering/depth tests and empirical-noise limitations in supplement/table links. Reuse archived figures or compose new manuscript layouts without modifying originals. No fresh observational reduction, model sweep or general morphology pipeline is needed.

## Caption text for the new panels

**Direct morphology panel.** Noiseless transfer from native dusty DR1 images to detector-integrated images with assumed Ks FWHM .38955 and .200arcsec. Positive differences mean lower absolute error at .200 relative to the native dusty statistic measured with the same saved aperture. Points are galaxy means over five correlated views; diamonds and bars are the mean and conditional95% galaxy-bootstrap interval over13 development galaxies. Gaussian and Moffat beta3.020805 families share the requested FWHM, not D50. Only Ks changes; g/J, aperture and center are fixed. The two analytic shapes and numerical refinement checks do not validate ULTIMATE performance or the physical resolution of native source cells.

**ML panel.** Differences in held-out operational-target MAE between matched .38955 and .200 FWHM conditions for fixed-alpha photometric, summary and spatial ridge. Both conditions use identical fivefold galaxy splits and existing fold-fitted preprocessing/features. Bars resample independent galaxies, conditional on fitted fold estimators; thirteen galaxies limit power and omit retraining/source/instrument uncertainty. Displayed results use resolution-specific fitting; fixed-model transfer is tabulated separately. These are exploratory development results with no final/validation inference. Improvement in image morphology does not imply a gain in dust prediction.

## Suggested results paragraph

“In a separately prespecified development sensitivity, decreasing the assumed Ks FWHM from0.390 to0.200arcsec reduced noiseless direct dusty-radius MAE from0.0267 to0.0118kpc for Gaussian PSFs and from0.0637 to0.0163kpc for a Moffat wing model. The same inputs did not establish a shape-robust improvement in predicting paired morphology biases or integrated effective attenuation beyond g/J/Ks photometry. Spatial ridge performed worse than photometric ridge for all four tested targets at0.200arcsec, while summary-feature changes depended on PSF shape. This conditional result separates improved morphology transfer from additional operational dust-prediction value.”

## What remains before submission

Draft the manuscript and ten-minute slides from these artifacts. Finish the already identified bibliography/novelty comparison and source/data attribution/rights review; this task did not search new literature or establish priority. Explain signed zero-projected-dust source residuals, deliberately selected sample, fixed rest bands at z=.1, deep-reference aperture/known centers, two assumed PSF shapes, absence of realistic noise in the new pilot and conditional intervals. Report original positive and negative results unchanged. Do not claim physically calibrated attenuation precision, unique3D geometry or guaranteed ULTIMATE observing performance.

An independent confirmation sample is not justified solely to chase a positive0.200 dust-ML result after this pilot. If stronger physics or observer-frame performance becomes the scientific objective, it requires new source/instrument evidence and a separately justified independent protocol. No such campaign is begun or implicitly recommended here.
