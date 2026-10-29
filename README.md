# Beyond the Foreground Screen: Machine-Learning Dust Geometry with ULTIMATE-Subaru

An archived, artifact-backed record of the existing TNG50–SKIRT DR1 and HAWK-I/GRAAL **ULTIMATE–Subaru feasibility study**. This repository preserves successful, failed and superseded work. It is not a new experiment or a claim of validated physical dust precision.

**Start here:** [current project state](docs/PROJECT_STATE.md), [scientific decisions](docs/SCIENTIFIC_DECISIONS.md), [completed analyses](docs/COMPLETED_ANALYSES.md), [open questions](docs/OPEN_QUESTIONS.md), and the self-contained [new-session handoff](docs/NEW_SESSION_HANDOFF.md).

Task A predicts effective attenuation statistics from optical–NIR photometric and spatial observations. Task B predicts and corrects dust-induced morphology biases. Physical dust inference, paired-image dust-bias prediction, direct morphology measurement and instrumental biases are separate questions.

The frozen partition contains **86 development, 14 validation and 20 spent final galaxies**. Five orientations of each galaxy are correlated. **The final20 evaluation was completed exactly once. It is never again an untouched test set.** [Evaluation protocol and provenance](docs/ML_EVALUATION_PROTOCOL.md).

Canonical GLAO results from the saved single final evaluation:

| Target | Constant MAE | Recommended ML MAE | Unit |
|---|---:|---:|---|
| A_g | 0.3003 | 0.0741 | mag |
| A_Ks | 0.0594 | 0.0124 | mag |
| Delta R50_Ks | 0.1282 | 0.0799 | kpc |
| Delta C_Ks | 0.1521 | 0.0887 | dimensionless |

No robust additional GLAO benefit for ML dust-bias prediction was established under tested conditions. Direct corrected Ks radius error improved from **0.1210 kpc seeing to 0.0861 kpc GLAO**. These are different claims. [Canonical report](analysis_results/ml_expanded_20261028/scientific_report.md), [later provenance audit](analysis_results/ml_validation_20261028/project_continuation_report.md).

Zero-projected-dust source residuals remain a limitation. DR2 was already investigated; required data are not available for planned use. Empirical HAWK-I/GRAAL characterization is complete using NGC3256 and M4-offset; M4 tile median FWHM is about **0.3032 arcsec**, with spatial PSF and correlated-background variations. These constrain sensitivity assumptions and do not measure ULTIMATE 0.2-arcsec performance. [Instrumental assumptions](docs/INSTRUMENTAL_ASSUMPTIONS.md).

The archive includes source, all 13 executed/original notebooks, reports, inspection figures, tables, saved models and small configurations/receipts. Large raw FITS, simulation downloads and caches remain on the original server. Downloaded third-party assets with unverified redistribution terms are also withheld individually. No original analysis was rerun or rewritten for this archive.

- [Complete file manifest](docs/manifests/FILE_INVENTORY.csv), [excluded files and exact server locations](docs/manifests/EXCLUDED_FILES.csv), [source/notebook index](docs/inventories/SOURCE_AND_NOTEBOOK_INDEX.md).
- [Data provenance](docs/DATA_PROVENANCE.md), [dependencies and reproduction](docs/REPRODUCTION.md), [archival verification](docs/ARCHIVE_POLICY.md).
- [Failures and negative results](docs/FAILED_EXPERIMENTS.md), [chronological history](docs/PROJECT_HISTORY.md), [publication plan](docs/PUBLICATION_PLAN.md).
- [GitHub synchronization report](docs/GITHUB_SYNC_REPORT.md). Repository: https://github.com/physicsbahare/ULTIMATE.

The 2026-10-29 commit imports an existing scientific history reconstructed from artifacts; it does not manufacture backdated Git commits. Existing scientific timestamps and hashes are preserved. Archived reports retain their historical wording; current documentation explains supersession. Citation and third-party rights records remain incomplete; no blanket license is asserted over external data or source copies.
