# Inspection, dependencies and reproduction boundaries

This archive was prepared without executing scientific scripts, fitting/loading models, running notebooks, reducing data, downloading science products or refreshing their reports. Read saved artifacts first. Historical pass receipts are evidence of prior checks, not newly rerun scientific validation.

## Inspect an archive clone

Read README, PROJECT_STATE, SCIENTIFIC_DECISIONS, COMPLETED_ANALYSES, OPEN_QUESTIONS and NEW_SESSION_HANDOFF. Per-study inventories link every included result/figure and identify server-only files. All13 notebooks are retained in their original form with embedded outputs, each below8.1MB; no stripped publication copy was necessary. HTML/PDF/PNG provide inspection without notebook execution. Some notebooks contain development demonstration refits: opening is safe, executing is a different task.

Use the existing interpreter for the read-only archive checker:

```sh
cd /home/bahareh/ULTIMATE
/home/bahareh/miniforge3/envs/phd/bin/python tools/verify_archive.py
```

It hashes eligible originals, checks available original metadata, validates required documents/links, compares committed bytes when Git is available, and checks archive selection/credentials/size. It does not import project scientific code or write original results. A clone lacks excluded server bytes; missing excluded files are reported as expected rather than fabricated.

## Recorded environment

[requirements-archive.txt](../requirements-archive.txt) pins the direct scientific dependencies from the existing `phd` environment; [python-packages.txt](environment/python-packages.txt), [conda-packages.json](environment/conda-packages.json) and [runtime.json](environment/runtime.json) record the broader environment. These are observed metadata snapshots, not a solver lock guaranteeing package availability on every platform. The separate `HAWKI_GRAAL/.venv` is an installed environment cache and is not redistributed.

Direct dependencies include NumPy, SciPy, pandas, Matplotlib, Astropy, SEP, scikit-learn, joblib, nbformat, nbclient, nbconvert and BeautifulSoup. Original [environment.json](../analysis_results/environment.json) and per-study execution provenance preserve historical versions. No packages were installed or original environments modified for the archive.

Every source file/notebook has a [static inventory entry](inventories/SOURCE_AND_NOTEBOOK_INDEX.md) listing imports/definitions or cells/kernel. Local helper imports require executing from the intended study context; some modules use absolute `/home/bahareh/ULTIMATE` paths. Scikit-learn joblib models require matching dependencies and local module definitions; do not load untrusted pickles. This archive did not deserialize or rescore saved models.

## Full historical reproduction, only if separately required

A clone contains source/settings/seeds/splits/models/receipts and modest artifacts, but excludes raw FITS, simulation atlases and bulk caches. Recover exact files from [EXCLUDED_FILES.csv](manifests/EXCLUDED_FILES.csv) using their server locations and recorded original checksum manifests. Retrieve external templates/calculator code by pinned source IDs only with appropriate rights/access; never publish credentials or signed URLs. There is no new download instruction in this archival task.

Use a separate working copy and a distinct output root; preserve frozen receipts. Existing scripts often use script-relative paths or absolute historical roots, so inspect and explicitly adapt paths in the working copy before execution. Do not assume a new shell cwd redirects output. Preserve original definitions before making portability changes. The archived source is unchanged; reconstruction does not imply a new scientifically independent evaluation.

| Stage | Historical entry points / dependencies | Existing reproduction instructions |
|---|---|---|
| Pilot/five views | inspect_inputs.py, inspect_hawki.py, build_notebooks.py, write_reports.py; original atlas/raw inputs | [Historical root README](../analysis_results/README.md); beware writers rebuild notebooks/metadata. |
| Observer-band screen | instrument.py/forward_physics.py → run_experiment.py/run_robustness.py → postprocess/report/notebook | [Study README](../analysis_results/screen_test_20261026/README.md), [instrument audit](../analysis_results/screen_test_20261026/instrument_audit.md). |
| Calibrated screen | experiment.py, final_ensemble.py, final_stress.py, publish.py | [Final protocol](../analysis_results/dr1_calibrated_screen_20261026/FINAL_PROTOCOL.md); keep development and frozen final tables distinct. |
| Positive-model diagnosis | run_focused.py and physical_model.py, bounded pilot; gate disallows large evaluation | [README](../analysis_results/multiplicative_diagnosis_20261026/README.md), [pilot protocol](../analysis_results/multiplicative_diagnosis_20261026/PILOT_EVALUATION_PROTOCOL.md). |
| Spatial pilot | pilot.py, secondary_analysis.py, boundary/depth scripts | [README](../analysis_results/spatial_structure_pilot_20261026/README.md), [protocol](../analysis_results/spatial_structure_pilot_20261026/PROTOCOL.md). |
| 26-galaxy morphology | audit_sample.py → staged observe/statistics/robustness → presentation/notebook | [README](../analysis_results/multigalaxy_morphology_20261027/README.md); independent replay already completed. |
| Preliminary ML | ml_data.py → ml_benchmark.py → ml_postprocess.py → report/notebook; development-only history | [Protocol](../analysis_results/ml_feasibility_20261027/PROTOCOL.md), [README](../analysis_results/ml_feasibility_20261027/README.md). |
| Canonical expanded ML | prepare_data.py, expanded_features.py, expanded_models.py, diagnostics/correction/domain/report/notebook | [README](../analysis_results/ml_expanded_20261028/README.md), [freeze protocol](ML_EVALUATION_PROTOCOL.md). **Do not rerun final20; inspect saved predictions and receipts.** |
| Supplementary ML | model_study.py, integrated_Ks_study.py, empirical_sensitivity.py, saved-canonical audits | [Continuation report](../analysis_results/ml_validation_20261028/project_continuation_report.md). Final-stage drivers disabled; retain this boundary. |
| NGC3256 empirical | diagnose_raw.py/diagnose_reduced.py, validate_catalogue.py, export_empirical_model.py | [Empirical report](../analysis_results/ml_feasibility_20261027/hawki/hawki_empirical_calibration_report.md); acquisition scripts are history, not routine re-download requirements. |
| M4 empirical | provenance/configuration → broad/fainter PSF → noise/refinements/confusion → identities/models/diagnostics/uncertainties → report/notebook/seal | [README](../analysis_results/hawki_m4off_20261028/README.md), detailed ordered sequence in [instrument review](evidence/INSTRUMENT_ARCHIVE_REVIEW.md). Preserve broad/faint passes; report builders and validators write outputs. |

A safe arithmetic audit may read saved prediction/summary CSVs without model inference. Running original verification scripts is not necessarily read-only: some create tables, receipts, kernels, figures or model refits. The read-only archive verifier is the appropriate check for this preservation task.

## Separate authorized0.200 continuation

The later owner-authorized [targeted assessment](../analysis_results/ultimate_020_information_gap_20261029/scientific_decision.md) adds new outputs in its own directory. Its [provenance](../analysis_results/ultimate_020_information_gap_20261029/provenance.json) records95 input/source hashes, exact14 development IDs, source-array paths, environment and seeds. Original cache/raw inputs remain under existing server-only manifest restrictions. [verify_results.py](../analysis_results/ultimate_020_information_gap_20261029/verify_results.py) reads saved continuation outputs and checks arithmetic/folds/hashes without importing scientific code, fitting or inference. The simulation/ML driver has explicit stages and overwrite guards; do not run it for inspection. The summary script regenerates only these new summaries/figures from saved tables; it preserves original operator-table execution bytes while clarifying grid metadata. No canonical scientific driver or notebook was rerun. The [continuation manifest](manifests/CONTINUATION_20261029.csv) extends file eligibility without replacing the original9367-file baseline.
