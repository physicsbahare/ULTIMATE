# Publication plan from existing evidence

Current aim: a publishable **ULTIMATE–Subaru feasibility study**, with an operational DR1 benchmark and a separate instrumental morphology-transfer result. Last reviewed 2026-10-29; this is manuscript planning, not authorization for new experiments.

The defensible central question is how optical–NIR observables predict paired DR1 attenuation/morphology statistics and what improved NIR imaging changes under stated assumptions. Foreground-screen failure motivates the empirical approach; the title does not establish unique physical geometry recovery.

## Manuscript structure and evidence

| Section | Existing evidence | Required boundary |
|---|---|---|
| Motivation and failed physical classifiers | Screen, calibrated-screen, multiplicative reports | Preserve population-null failures; no validated geometry classification. |
| Data and operational definitions | Frozen selection, preparation audits, label audit | Deliberate sampling; paired source residuals; galaxies/views distinguished. |
| Baselines and protocol | Canonical development/freeze/final receipts | Single final; recommended settings chosen before final. |
| Task A and Task B benchmark | Recommended performance, residuals, source controls, uncertainty/OOD/learning curves | Operational statistics; tails and limited coverage accompany means. |
| Observing-strategy comparison | Canonical paired gains, 26-galaxy transfer | No robust extra ML dust-bias gain; separately positive direct/corrected Ks morphology transfer. |
| Instrumental sensitivity | Existing PSF/noise/sampling/center/aperture stresses, NGC3256/M4 | Empirical nuisance inputs, not measured ULTIMATE 0.2-arcsec performance or a universal large-scale sky model. |
| Discussion | Source-label limitation, selection, reference aperture, observer-band support | Bound physical/instrumental claims; keep DR2 blocked absent new evidence. |

Use existing canonical figures/tables indexed in [completed analyses](COMPLETED_ANALYSES.md), with supporting negative/source-control panels. Do not pick a post-final family for a better headline. Keep g/Ks units, aperture definitions, source-control denominators, seeing/GLAO error target and uncertainty conditioning in captions.

## Publication readiness and remaining writing work

Evidence is sufficient for a workshop and a bounded benchmark manuscript draft. It is insufficient for a validated physical dust precision, unique 3D geometry or measured ULTIMATE performance claim. Complete bibliography/novelty comparison against the already recorded Fu, Dobbels/Baes, Pastrav and same-atlas Bokona Tulu work; one requested Dobbels/Baes year attribution remains unresolved in the existing literature note. Review external source/data terms and final attribution before distributing external assets. No new literature investigation occurred during this archive.

Prepare manuscript prose from saved tables, retain failure/selection/label caveats, choose publication figures from the archive and attach reproducibility/data-access statements. Stronger physics claims depend on genuinely new historical source calibration or independent data; they are not prerequisites to honestly reporting the operational feasibility result. [Open questions](OPEN_QUESTIONS.md) identifies those dependencies without reopening completed work.

## Targeted0.200 extension available for writing (2026-10-29)

The new [bounded assessment](../analysis_results/ultimate_020_information_gap_20261029/scientific_decision.md) strengthens the separation of direct morphology capability from dust-prediction information. It extends assumed Ks FWHM0.38955→0.200 with matched numerical operators and Gaussian/Moffat shapes on13 fit-eligible development galaxies plus one control. No added noise, no independent confirmation, no final/validation inference. Direct radius/concentration transfer improves; full spatial ridge at0.200 loses to photometric ridge for every tested target, and summary-model width gains depend on shape. This does not justify stronger physical/instrument forecast language or selecting a new final model.

Use the new [morphology figure](../analysis_results/ultimate_020_information_gap_20261029/figures/morphology_width_gain.pdf) and [ML gain figure](../analysis_results/ultimate_020_information_gap_20261029/figures/ml_width_gain.pdf) in an explicitly exploratory sensitivity section, with canonical frozen results kept separate. [Workshop/paper implications](../analysis_results/ultimate_020_information_gap_20261029/workshop_paper_implications.md) provides a10-minute sequence, figure choices, captions and results paragraph. Next work is drafting these artifacts into slides/manuscript and completing bibliography/rights, not more simulations.
