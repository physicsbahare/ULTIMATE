# New-session scientific handoff

**Before proposing any new experiment, read PROJECT_STATE.md, SCIENTIFIC_DECISIONS.md, COMPLETED_ANALYSES.md and OPEN_QUESTIONS.md. Check existing code/results for overlap. Never repeat a completed analysis without identifying a genuinely new scientific requirement.**

This is the existing **Beyond the Foreground Screen: Machine-Learning Dust Geometry with ULTIMATE-Subaru** project. Local root `/home/bahareh/ULTIMATE/`; GitHub `https://github.com/physicsbahare/ULTIMATE`; Python `/home/bahareh/miniforge3/envs/phd/`. The 2026-10-29 task archived existing science; it did not start another experiment. Git synchronization outcome and archive SHA are in [GITHUB_SYNC_REPORT.md](GITHUB_SYNC_REPORT.md).

## What the study is asking

Task A predicts effective attenuation statistics from optical–NIR photometric/spatial observations. Task B predicts and corrects dust-induced morphology biases. Distinguish (1) physical dust inference, (2) operational dust-induced morphology-bias prediction, (3) direct observed morphology measurement/recovery and (4) instrumental/observational biases. Success in one is not evidence for the others.

TNG50–SKIRT DR1 provides simulated dusty/clear paired images and projected dust. No-dust counterparts are unobservable in real galaxies; source residuals mean the difference is not validated pure dust truth. Images are 100 pc/pixel, not 100-pc independent physical resolution. Five orientations belong to one galaxy. NGC3256/M4 provide empirical nuisance information, not dust truth.

## What has already happened

The original galaxy294866 pilot was reproduced, expanded to five views and tested over masks/apertures. Screen-model tests found false positives from stellar populations; ensemble calibration still produced 98.4% rejection of a plausible fixed null anchor. Positive multiplicative diagnosis found a covariance/push-forward problem and failed physical-null adequacy/convergence gates. These are negative results to preserve, not unfinished classifiers.

A spatial pilot separated feature/morphology transfer from dust specificity and diagnosed depth-threshold noise crossings. A completed 26-galaxy study measured wavelength/viewing dust-pair morphology and better conditional Ks preservation with GLAO; independent verification/replays and aperture/center/noise/resolution/sampling/depth controls were completed. Original galaxy294866 is an opposite-sign outlier, retained rather than excluded.

Preliminary ML led to metadata-frozen expansion. All120 galaxies/600 views are now prepared. Canonical ML is `analysis_results/ml_expanded_20261028/`; later `ml_validation_20261028/` is supplementary **validation-only**, with zero additional final inference. Existing learning curves, OOD cases, source-label checks, center/aperture and empirical instrument sensitivity studies are complete. Detailed indexes: [COMPLETED_ANALYSES](COMPLETED_ANALYSES.md), [source/notebooks](inventories/SOURCE_AND_NOTEBOOK_INDEX.md).

## Non-negotiable evaluation history

The frozen partition is **86 development /14 validation /20 spent final**. All previously inspected26 are development. Twelve development source controls leave74 fit objects; one validation control leaves13 canonical interval calibrators; four final controls leave16 primary final objects. Exact IDs/folds/hashes: [ML_EVALUATION_PROTOCOL](ML_EVALUATION_PROTOCOL.md).

The canonical final20 evaluation happened **exactly once**, bound to freeze SHA-256 `587aab56d39e6b29ad47f381c4b1440c8dd28eb52811ebc4ae3842b6fc220ce4`; saved receipt records153,600 rows and count1. The supplementary workflow blocked its own final stage, recorded count0 and only audited saved predictions. Never rerun final inference, tune on these galaxies or call them an untouched sample. A revised confirmatory model needs a new independent holdout.

## Results to preserve verbatim in meaning

| Canonical GLAO target | Constant MAE | Recommended ML MAE |
|---|---:|---:|
| A_g (mag) |0.3003|0.0741|
| A_Ks (mag) |0.0594|0.0124|
| Delta R50_Ks (kpc) |0.1282|0.0799|
| Delta C_Ks |0.1521|0.0887|

No robust additional GLAO benefit for ML dust-bias prediction was established under tested conditions. Separately, direct corrected Ks radius error improves **0.1210 kpc seeing→0.0861 kpc GLAO**. These are operational DR1 paired-image statistics, **not validated physical dust precision**. Read [PROJECT_STATE](PROJECT_STATE.md) for supporting artifacts, conditional intervals and tails.

Zero-projected-dust controls still have coherent signed spectral and spatial residuals. Crop/unit/precision/full-field/band/smoothing audits already exist. Historical source/filter/operator or RT causes remain unresolved; do not subtract a universal offset or call a hypothesis proven.

DR2 suitability and availability were already checked. Required data are not available for planned use. Do not reopen generic DR2/authentication/download work without new evidence.

HAWK-I/GRAAL empirical characterization using NGC3256 and M4-offset is complete. M4 tile median fitted FWHM≈**0.3032 arcsec**; spatial PSF/background/noise vary. R32 large-aperture noise calibration is rejected. Empirical shapes/covariance are sensitivity inputs; they do not measure ULTIMATE 0.2-arcsec performance. Historical raw/no-calibration statements were superseded by official reduced products and complete archive associations; no fresh local raw reduction was performed.

## How to continue responsibly

Aim for a bounded publishable feasibility paper. Current next work is manuscript synthesis, defensible novelty/claims, final citations/rights and honest limitation statements. Stronger physical/source and instrument-transfer claims need genuinely new independent evidence. See [OPEN_QUESTIONS](OPEN_QUESTIONS.md) before suggesting work. MaNGA validation is a documented proposal, not executed validation; owner/collaborator requests are prepared documents, not sent messages.

Read artifacts before running scripts. Notebook/report/verification drivers may overwrite outputs or refit development models. All13 notebooks are retained with outputs; saved ML models/settings/receipts and small/moderate tables/figures are in Git. Large FITS/archives/caches and unlicensed downloaded third-party payloads remain on the server, individually described in [excluded manifest](manifests/EXCLUDED_FILES.csv). Full reconstruction needs those inputs and [recorded dependencies](REPRODUCTION.md); a clone alone cannot regenerate missing images.

Follow [AGENTS.md](../AGENTS.md), preserve original/frozen outputs, use new output locations for authorized extensions and update project documentation after meaningful changes. The archival user request specifically prohibited new training, forward modeling, source-label audits, DR2 investigation and HAWK-I reduction, and required stopping after synchronization verification.

## Latest continuation: targeted0.200 information assessment

After the archival task described above, the owner explicitly authorized a separate targeted extension. It is now **complete**: [audit](../analysis_results/ultimate_020_information_gap_20261029/overlap_and_novelty_audit.md), [scientific decision](../analysis_results/ultimate_020_information_gap_20261029/scientific_decision.md), [writing implications](../analysis_results/ultimate_020_information_gap_20261029/workshop_paper_implications.md).14 development objects,13 fit+one source control, no added noise, two FWHM-defined shapes, five grouped folds. Direct morphology improves0.390→0.200; full spatial ridge loses to photometry and summary width gains are shape-dependent. No final/validation inference or canonical retuning. This supersedes any inference that0.200 morphology/ML remains untested. Do not rerun it. Next work is workshop/manuscript synthesis; no confirmation campaign. Latest Git state is in [continuation sync receipt](../analysis_results/ultimate_020_information_gap_20261029/github_sync.md).
