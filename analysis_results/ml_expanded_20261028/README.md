# Expanded ULTIMATE-like ML study — executed 2026-10-28

Start with [scientific_report.md](scientific_report.md), [workshop_summary.md](workshop_summary.md), and [expanded_ml_executed.ipynb](expanded_ml_executed.ipynb). The executed notebook also has a self-contained [HTML export](expanded_ml_executed.html).

120 verified galaxies / 600 views. Frozen assignments:86 development,14 validation,20 final. Exact-zero projected-dust sources remain separate controls:74 development fits,13 calibration galaxies,16 final primary galaxies and17 total source controls. Final20 were opened **after**136 code/model/calibration/protocol artifacts were frozen and were evaluated once. No final-outcome tuning. Do not reuse this final set as a fresh holdout.

These are predictions of **operational matched DR1 source-product contrasts**. Source-label calibration is unresolved, especially the ≈0.12-mag g offset in zero-projected-dust controls. Neither unique3D geometry nor validated observer-frame ULTIMATE performance is established. Reported prediction intervals omit this systematic.

## Outputs

| Location | Contents |
|---|---|
| `expanded_galaxy_inventory.csv`, `sample_quality_counts.csv` | All120 IDs, immutable partition/selection probabilities, metadata, dust/aperture/label quality flags |
| `data_audit/` | Archive/member/FITS/cache inventories, selection snapshots, all120 hash verification and streaming code |
| `data_audit/final_unseal/` | Final-only audit receipts; the original100-stage audit snapshot remains unchanged |
| `target_table.csv`, `final_target_table.csv` |1000+200 paired labels, five views×two apertures per galaxy |
| `feature_table.csv.gz`, `final_feature_table.csv.gz` |24000+4800 observable-feature rows, all conditions; no truth predictors |
| `derived/<ID>/` | Per-galaxy labels, features, aperture policies and render checks |
| `development_group_folds.csv`, `cv_checkpoints/` | Whole-galaxy folds and all255 fitted-candidate out-of-fold prediction records |
| `chosen_family_settings.csv`, `recommended_settings.csv` | Development-only settings, including recommended model per target |
| `models/`, `execution_provenance.json` |108 trained joblib artifacts, settings/version/count provenance |
| `validation_and_control_predictions.csv.gz`, `final_predictions.csv.gz` | Per-view/per-noise predictions, truth, residuals, correction errors and intervals |
| `performance_summary.csv`, `galaxy_metrics.csv` | Equal-galaxy MAE/RMSE/bias/coverage, conditional galaxy-bootstrap intervals |
| `paired_galaxy_gains.csv`, `recommended_gains.csv` | Paired gains for GLAO, added NIR, and model-versus-constant/photometry comparisons |
| `final_native_dusty_morphology_transfer*`, `final_morphology_correction_gains.csv` | Absolute PSF/noise morphology error and native-clear correction gains |
| `learning_curves.csv` |12/24/48/74 training galaxies×three subset seeds×two NIR strategies |
| `shift_and_noise_predictions*`, `observable_OOD*` | High-mass holdout, common-variance/noiseless and exploratory feature-distance diagnostics |
| `source_control_recommended*`, `source_control_performance.csv` | All source controls retained separately, including four final controls |
| `within_view_noise_and_orientation_residuals.csv`, `property_stratified_errors.csv` | Repeated-view/draw and descriptive physical/observable-property diagnostics |
| `label_audit/` | Fresh source-null audit, quality policy and primary-source literature context |
| `instrument_sensitivity/` | Executed PSF-wing/covariance/binning and center/aperture tests; HAWK-I sharing manifest only |
| `figures/` | Publication figures as PNG and PDF, including selected successes/failures |
| `*_VALIDATION.json`, `FINAL_*json`, `PREVIOUS_RESULTS_PRESERVED.json` | Numerical, notebook, hash, sealing and previous-output preservation evidence |

## Exact safe replay

Use the existing environment; no installation or download is needed. From `/home/bahareh/ULTIMATE`:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_expanded_20261028/verify_results.py

PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/ultimate_matplotlib IPYTHONDIR=/tmp/ultimate_ipython JUPYTER_RUNTIME_DIR=/tmp/ultimate_jupyter OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_expanded_20261028/execute_notebook.py
```

Jupyter needs localhost kernel sockets. The notebook genuinely refits the frozen recommended integrated-g model on74 development galaxies, reproduces its saved predictions on13 validation galaxies to1e-10, computes/loads the reviewed metrics and renders figures. It reads the saved single-evaluation final predictions; it never reruns final inference or selection. All eight notebook code cells were executed and saved. The HTML is useful without a running kernel. Editable figure code is in `figures.py`; actual training and final inference code is in `expanded_models.py`.

To recompute the numerical scoring from saved predictions without training or reopening final science:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_expanded_20261028/summarize.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_expanded_20261028/correction_analysis.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_expanded_20261028/domain_diagnostics.py
PYTHONDONTWRITEBYTECODE=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_expanded_20261028/write_reports.py
```

Do not run the `expanded_models.py` main entrypoint in this frozen directory: it is the original development-selection/fitting stage and would rewrite protected artifacts. Full training definitions, hyperparameters, folds, inputs and saved out-of-fold predictions are supplied for reproduction in a separate output directory. The default notebook replay validates a real refit without overwriting the original models. `evaluate_final()` refuses a second evaluation after its completion receipt.

## Executed stage history

1. Read previous morphology/ML/multiplicative reports and reused validated rendering/morphology modules.
2. Checked the finished94/94 downloader state; no duplicate process or transfer launched. Streamed100 nonfinal archives, checked integrity, units/grids/all22 band pairings and selectedg/J/Ks+dust pixels; cached only seven800² arrays/view.
3. Reproduced old26 member hashes and294866 fixed12 measurements; diagnosed four historical source-null cases across22 full-field bands. Froze operational label/quality/aperture definitions before model selection.
4. Ran `expanded_features.py --watch`:100 nonfinal galaxies. Ran `expanded_models.select()` and `fit_calibrate()`:17 candidate configurations×three scenarios×five grouped folds, then84 nominal saved models across two apertures/three scenarios. Validation was not used to select settings.
5. Ran `diagnostics.py`: learning curves, high-mass shift, common-variance/noiseless and fixed-model instrument stress scoring.24 sensitivity model artifacts added. Executed focused center/aperture tests and prefinal numerical/allowlist/grouping checks.
6. Wrote `FINAL_PROTOCOL_FROZEN.json`; `data_audit/unseal_final.py --run` verified all hashes and opened20 final archives. `expanded_features.py --final --watch` produced separate final tables. `expanded_models.evaluate_final()` loaded frozen models once and wrote153600 prediction rows across all families/targets/apertures/scenarios/views/draws.
7. Ran postfinal verification, scoring, morphology transfer/correction, descriptive OOD/control diagnostics, reports, figures and notebook. A fresh independent audit rehashed all120 archives and600 caches; previous result manifests verified1056 files unchanged.

The final-data guard and hash receipt make the evaluation history auditable; they do not create statistical independence beyond galaxy-level sampling. Four correlated noise draws×five repeated views are never counted as100 independent test galaxies. The sample is balanced in mass/activity, not volume-complete, and selection metadata did not supply actual dust or morphology classes. HAWK-I files are referenced for potential collaborator sharing but were not packaged/transferred. No raw-reduction task was duplicated.

## Conditions that remain provisional

Known center/distance and a deep observed-Ks selection reference; finite circular apertures; no background/source segmentation uncertainty propagated into the reference; fixed-rest-band z=0.1 transformations using actual LSST/2MASS identities; provisional throughput, Gaussian PSFs and moment-noise model. HAWK-I stress shapes/covariance are conditional nuisance cases, not ULTIMATE specifications or empirical dust validation. Full large-aperture correlated background noise is not reproduced. See the scientific report for uncertainty and publication gates.
