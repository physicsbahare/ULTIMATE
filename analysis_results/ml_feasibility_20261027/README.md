# Preliminary ULTIMATE ML feasibility — 2026-10-27

Start with [scientific_report.md](scientific_report.md), the executed
[ULTIMATE_preliminary_ML.ipynb](ULTIMATE_preliminary_ML.ipynb), and
[workshop_results.md](workshop_results.md). The notebook also has a portable
HTML export. This is a new isolated experiment: previous results, FITS and
archives were not overwritten. Existing `phd` packages were used; no installation,
DR2/snapshot acquisition or large neural-network training.

## Reading the results

Twenty-six previously inspected galaxies remain development-only. Four
zero-projected-dust objects are excluded from fitting/calibration, retaining22
independent galaxies for exploratory grouped CV. Every view/draw stays in its
galaxy. Labels are **operational DR1 paired contrasts**, with unresolved physical
source-product uncertainty; excluding the controls does not validate pure dust
labels. No 3D geometry, optical depth or dust-mass recovery is claimed.

NIR information improves several targets. A robust primary seeing-versus-GLAO
ML advantage is not established. Constant and photometric correction baselines,
failed spatial attenuation prediction, undercoverage, OOD errors and aperture
sensitivity are retained. The fixed-rest-band instrument experiment uses actual
LSSTg and2MASSJ/Ks products with provisional noise/PSFs; it is not exact
observer-frame ULTIMATE photometry. g-only versus three-band comparisons use
equal per-band time, not equal total time.

## Reproduce the ML work

From `/home/bahareh/ULTIMATE`, using the existing environment:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/ultimate-mpl
export PYTHONDONTWRITEBYTECODE=1
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_feasibility_20261027/ml_data.py
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_feasibility_20261027/ml_benchmark.py
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_feasibility_20261027/ml_postprocess.py
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_feasibility_20261027/label_quality_audit.py
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_feasibility_20261027/empirical_stress.py
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_feasibility_20261027/write_ml_report.py
```

`ml_data.build(recompute=True)` regenerates the small observable-feature table
from the existing verified compact images. `ml_benchmark.run(recompute=True)`
refits all primary models. Defaults resume completed work rather than repeating
it. No full archives are unpacked. `empirical_stress.py` resumes its feature table
and refits the separate sensitivity models; use a backup/move of only its own
feature table if regenerating that stress is necessary. Never alter prior-study
inputs or frozen partitions to improve outcomes.

The original verified sample cache must remain available at
`analysis_results/multigalaxy_morphology_20261027/cache/`. Input and code hashes,
package versions and frozen-protocol hash are recorded in
`execution_provenance.json`. Models are reproduced from code/seeds; no opaque
pickled final estimator is promoted for use on real data.

To execute the notebook and regenerate its embedded figures/report:

```sh
JUPYTER_RUNTIME_DIR=/tmp/ultimate-jupyter-ml IPYTHONDIR=/tmp/ultimate-ipython-ml /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_feasibility_20261027/execute_ml_notebook.py
```

The existing `phd` kernel needs local Jupyter sockets, which were permitted for
this execution. The notebook resumes primary fits and recomputes aggregation,
figures and label-quality diagnostics. It reads the separately executed empirical
stress by default to avoid redundant fitting; the command above reproduces that
stress explicitly. Acquisition and new-galaxy image analysis are never triggered
by the notebook.

```sh
/home/bahareh/miniforge3/envs/phd/bin/python -m unittest discover -s analysis_results/ml_feasibility_20261027 -p 'test_*.py' -v
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_feasibility_20261027/validate_ml_delivery.py
```

## Output map

- `PROTOCOL.md`: fixed primary target/feature/model/grouping/uncertainty rules.
- `operational_labels.csv`:130 per-galaxy/view truth records, explicitly separate
  from X; source-null flags and metadata are audit-only.
- `observable_features.csv`:6240 rows measured only on noisy/noiseless dusty images.
- `feature_provenance.json`, `feature_render_validation.csv`: forward-model settings,
  exact original-noise reconstruction and optical-control checks.
- `preliminary_cv_splits.csv`, `train_test_provenance.json`: all galaxy fit/calibration/
  outer-test roles, feature allowlists, fixed hyperparameters and label caveats.
- `heldout_predictions.csv.gz`:369600 target-level held-out records, including
  intervals, feature-space distances and correction scoring.
- `galaxy_heldout_errors.csv`, `heldout_summary.csv`: equal-galaxy MAE/coverage/bias,
  without pooling orientations/noise draws as independent galaxies.
- `galaxy_GLAO_ML_gains.csv`, `GLAO_ML_gain_summary.csv`: paired resolution gains,
  galaxy signs and5000-resample conditional intervals.
- `paired_model_comparisons.csv`, `correction_summary.csv`: extra-band and baseline
  comparisons, correction effects and uncertainty.
- `within_scene_noise_prediction_spread.csv`: repeated-noise scatter, kept separate
  from between-galaxy uncertainty.
- `OOD_split_provenance.csv`, `OOD_predictions.csv.gz`, `OOD_galaxy_errors.csv`,
  `OOD_summary.csv`: high-mass and source-control challenges, with no calibration
  guarantee inferred for these shifts.
- `source_null_label_audit.csv`, `source_null_uncertainty_envelopes.csv`,
  `label_policy_uncertainty_summary.csv`, `label_aperture_center_sensitivity.csv`,
  `fixed_prediction_label_definition_stress.csv`: unresolved source and measurement
  policy sensitivity; no offset subtraction or invented Gaussian label error.
- `empirical_stress_*`: post-protocol Ks wing and local-covariance stress informed
  by HAWK-I, with all limitations recorded in `empirical_stress_assumptions.json`.
- `prediction_checkpoints/`: resumable per-condition held-out predictions.
- `figures/01_…06_*.png/.pdf`: baseline MAEs, GLAO/noise ablations, NIR comparison,
  per-galaxy predictions, uncertainty/OOD and morphology correction.
- `test_ml_integrity.py`, `unit_tests.log`, `validation.json`, `ml_review_notes.md`:
  tests, fresh delivery/preservation checks and independent read-only review.
- `execution_provenance.json`, `output_manifest.sha256`: environment/code/input and
  output hashes. Acquisition status files are timestamped snapshots and can evolve.

## Sample expansion: acquired separately, final science images sealed

[expansion/README.md](expansion/README.md) records the exact selection function,
strata, missing dust/morphology metadata, secure preflight and restart/monitoring
commands. `galaxy_partitions.csv` fixes86development (26old+60new),14validation,
20final-test galaxies. The94 additional archives total56.032GiB by actual preflight.

The download is a **resumable background acquisition**, not a completed120-object
analysis. Actual counts and timestamp are in `expansion/acquisition_status.json`;
the live state/log are in `data/TNG50_SKIRT_DR1_ml_expansion/`. PID27948 was
confirmed live from the host process namespace. Restricted sandbox PID namespaces
cannot reliably probe that host process; refresh status with host access rather
than mistaking an invisible PID for a stopped transfer. Every chunk enforces the
100GiB reserve plus256MiB margin. No duplicate archive is deliberately downloaded;
the original files remain in their original locations.

CRC/tar integrity checks read payload bytes without opening FITS science arrays.
No final-evaluation science image or label has been inspected. Do not open those
objects for feature/label choices or hyperparameter tuning. Plan separate tuning
and interval calibration before a single frozen final evaluation.

## HAWK-I/GRAAL empirical calibration

[hawki/hawki_empirical_calibration_report.md](hawki/hawki_empirical_calibration_report.md)
contains executed official-archive queries, complete calibration associations,
downloaded reduced science/variance/confidence cutouts, isolated-source fits,
encircled-energy profiles, field dependence, masked sky covariance and aperture
noise measurements. It includes a small2MASS consistency check and documents the
actual associated PHOTCAL-table colour term versus the release-note discrepancy.
This is a consistency check with the pipeline reference system, not independent
external calibration. Candidate and quality-matched stellar subsets remain distinct.

The HAWK-I directory provides exact reproduction scripts, measured model inputs,
match tables and plots. No incomplete local raw reduction was passed off as a
calibrated product. The real measured PSF is not relabelled as ULTIMATE resolution,
and no image is sharpened to manufacture0.2arcsec information.
