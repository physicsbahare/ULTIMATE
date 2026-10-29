# Open questions and accepted limits

Cross-checked on **2026-10-29** against [completed analyses](COMPLETED_ANALYSES.md), [decisions](SCIENTIFIC_DECISIONS.md), [failures](FAILED_EXPERIMENTS.md) and the three evidence reviews. Inclusion here does not authorize execution.

## Scientifically important unresolved dependencies

1. **Physical source-product calibration (OPEN; external dependency).** Which historical source/filter/RT operators and Monte Carlo/subgrid effects produce signed residuals even in zero projected dust? The minimal decoder, full-field/band-sign/crop/precision/smoothing controls **were completed**. A source spectral-operator mismatch is a hypothesis. [Source audit](../analysis_results/ml_expanded_20261028/label_audit/source_label_report.md) and [prepared owner reproduction specification](../analysis_results/ml_validation_20261028/source_owner_reproduction_request.md) identify missing historical .ski/SED/filter/packet information. No message has been sent and no new source audit is proposed by this archive. Strong physical precision claims are blocked pending genuinely new source evidence.
2. **External scientific/instrument transfer (OPEN).** Independent observer-frame photometry, calibrated spatial PSF/sky/segmentation/centering and observational validation would be needed for stronger ULTIMATE forecasts. Existing NGC3256/M4 characterization and prior instrument/noise/center/aperture stresses already answer narrower questions. Any extension must specify what new measurement it provides. [Instrument assumptions](INSTRUMENTAL_ASSUMPTIONS.md).
3. **Publication novelty and scope (OPEN).** Synthesize existing operational ML and morphology transfer, compare against already documented dust-ML and same-atlas morphology literature, and establish a defensible manuscript claim. No first-dust-ML, first-dust-morphology, unique-geometry or sim-to-real validation claim is currently justified. [Publication plan](PUBLICATION_PLAN.md).
4. **Preservation/rights completeness (OPEN, documentary).** Confirm third-party redistribution terms, complete final bibliography/attribution and independently back up excluded server data. These are archive/paper dependencies, not scientific reruns. [Provenance](DATA_PROVENANCE.md).

## Known limitations accepted for a bounded feasibility paper

Operational DR1 labels rather than calibrated physical truth; fixed matched-rest-band/deep-reference/known-center scenarios; selected 120 objects from one simulation volume; five correlated fixed views; conditional finite-sample bootstrap/coverage; no universal dust scale or geometry; omitted realistic background/PSF/segmentation floors. R32 empirical noise, infinite PSF tails, raw-star linearity and absolute independent HAWK-I calibration remain limited. Document these instead of automatically escalating the study into a new experiment.

Aperture, center, sampling, depth, resolution, source controls and empirical-noise sensitivities **already exist**. Full propagation of a deployed noisy segmentation/centering process is a broader unanswered question; it must not be confused with absence of any sensitivity tests.

## Previously investigated or blocked

- **DR2 — BLOCKED for planned use.** Suitability/availability and authenticated catalogue routes were already checked. Required matched data are not available; a verified applicable release-specific replacement is absent. Reopen only when new release-specific evidence arrives; no generic discovery/download task is pending.
- **Revised final20 models — BLOCKED permanently as an untouched evaluation.** Final20 is spent. Revised confirmatory modeling needs a genuinely independent holdout, not a relabeling or a second inference on the same20.
- **Screen classification — NEGATIVE_RESULT.** Conditional calibration, false-positive anchor diagnosis and positive model were already tested and failed adequate general identification. Do not automatically repeat them with changed priors/grids.
- **HAWK-I reduction/calibration discovery — COMPLETED in empirical scope.** Official reduced products/calibration associations, NGC3256 and M4 PSF/noise characterization are delivered. A fresh raw reduction or absolute external calibration is a distinct long-term task, not missing completion of those analyses.

## Optional long-term extensions

A genuinely new independent calibrated simulation/source set and holdout; observational validation using a bounded MaNGA/imaging design (the existing [MaNGA note](../analysis_results/spatial_structure_pilot_20261026/MaNGA_validation_note.md) is a proposal, not executed validation); full-image population-constrained inference only after adequate controls; representative/design-weighted sampling; eventual observer-frame spectral cubes when genuinely available. Source-owner requests and collaborator manifests are prepared documents, not completed communication or transfer.

**Before recommending anything, search the artifact indexes for overlap, name the new scientific requirement and explain why an existing result cannot answer it.**

## Resolved targeted0.200 gap and remaining boundary (2026-10-29 continuation)

The owner-authorized [overlap audit and assessment](../analysis_results/ultimate_020_information_gap_20261029/scientific_decision.md) established a missing fixed-rest-band Ks-only estimand and completed it on14 development galaxies. Direct morphology improves under Gaussian/Moffat assumptions; no robust additional dust-ML gain is demonstrated. Do not re-propose this as unperformed0.200 work or rerun general sampling/aperture/calibration studies.

Whether a larger independent, observer-frame and source-calibrated set would improve operational dust prediction is still unknown. This limited pilot does not establish zero possible gain, but does not justify a new confirmation campaign merely to chase a favorable result. No campaign is authorized here. The immediate task is the [ten-minute workshop and short-paper synthesis](../analysis_results/ultimate_020_information_gap_20261029/workshop_paper_implications.md), with bibliography/rights and existing source/instrument limitations.
