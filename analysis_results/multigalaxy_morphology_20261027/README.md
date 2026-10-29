# Multi-galaxy dust morphology — 2026-10-27

Start with [scientific_report.md](scientific_report.md), [workshop_summary.md](workshop_summary.md), and the executed [notebook](ULTIMATE_multigalaxy_morphology.ipynb) / [HTML preview](ULTIMATE_multigalaxy_morphology.html). All outputs are isolated here; all earlier experiments and original inputs are preserved.

## Reproduce with existing phd environment

From `/home/bahareh/ULTIMATE`:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/ultimate-mpl PYTHONDONTWRITEBYTECODE=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/multigalaxy_morphology_20261027/run_stages.py
```

The staged command streams and checks the five development archives first, executes their selected observing cases, and writes `development_gate.json`. Only a passed gate permits the 21 held-out galaxies. It then completes intrinsic measurements and the selected observing cases, five-object sensitivity tests, galaxy statistics, figures and reports. Completed per-galaxy archive measurements and per-view observing results resume from the compact cache; no existing expensive grids are rerun. It never installs packages or uses network credentials.

To execute the notebook with actual tables and embedded figures:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/ultimate-mpl JUPYTER_RUNTIME_DIR=/tmp/ultimate-jupyter IPYTHONDIR=/tmp/ultimate-ipython PYTHONDONTWRITEBYTECODE=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/multigalaxy_morphology_20261027/execute_notebook.py
```

The existing `phd` Jupyter kernel requires local sockets. `build_notebook.py` creates the editable notebook; `execute_notebook.py` executes it top to bottom and exports HTML. The notebook reruns validation/aggregation/presentation and resumes the archive/observation pipeline.

For an independent cache-free rerun, copy the small `.py` files and `PROTOCOL.md` into another sibling directory under `analysis_results/` and run `run_stages.py` there. It reads the same original archives, recomputes current archive/member hashes and measurements, and creates only its own compact cache. No raw FITS archives are fully extracted. Keep the relative location under `analysis_results` so read-only imports resolve. Do not delete previous experiment outputs. To rerun only the expensive observing calculation, move this run's `cache/*/O*_observed.csv` checkpoint files to a backup location first; the staged entrypoint will regenerate the corresponding spatial/transfer products too. Never manually modify checkpoint tables and treat them as original measurements.

Numerical tests and final delivery validation:

```sh
cd /home/bahareh/ULTIMATE/analysis_results/multigalaxy_morphology_20261027
OPENBLAS_NUM_THREADS=1 /home/bahareh/miniforge3/envs/phd/bin/python -m unittest discover -p 'test_*.py' -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/ultimate-mpl /home/bahareh/miniforge3/envs/phd/bin/python validate_science.py
OPENBLAS_NUM_THREADS=1 /home/bahareh/miniforge3/envs/phd/bin/python validate_delivery.py
```

## Output map

- `PROTOCOL.md`, `implementation_plan.md`: fixed primary methods, development/evaluation split and pre-evaluation noisy-q amendment.
- `archive_inventory.csv`: actual SHA256/size/mtime reconciliation and CRC/tar evidence for 26 archives. Extra-file SHA256 identity preserves the downloader CRC proof; the original has an independent gzip trailer check. `CRC_evidence` distinguishes these.
- `fits_inventory.csv`: 6240 FITS identities, filters/physical products, units, dimensions, coordinates, member hashes and data quality. No science archives are redownloaded.
- `galaxy_metadata.csv`, `galaxy_inventory.csv`: catalogue metadata, physical dust properties, development role and aperture/availability flags.
- `selection_audit.json`, `selection_cells.csv`: parent/selected distributions and unequal cell inclusion probabilities. Equal-weight results target this balanced sample.
- `intrinsic_morphology.csv`: 7800 absolute native measurements, including all paired bands plus g/Ks aperture/center sensitivity.
- `primary_dust_bias.csv`: 2860 primary galaxy/view/band comparisons, with clear/dusty observables and dust differences.
- `intrinsic_pairs.csv`: all primary and alternative aperture/center pairs.
- `effective_attenuation.csv`, `physical_maps.csv`: local effective attenuation summaries (negative values retained) and independently projected physical dust/stellar masses.
- `galaxy_level_morphology.csv`, `galaxy_bootstrap_summary.csv`: equal-galaxy means, medians, viewing ranges/SD, bootstrap intervals, signs, between-galaxy scatter, all-26 and held-out-21 results.
- `property_associations.csv`: exploratory galaxy-level associations; unadjusted p-values, no scaling-law or causal claims.
- `observed_morphology.csv`: PSF-free detector-sampled references, noiseless PSF images, and eight noise draws; actual rest LSST g and 2MASS J/Ks.
- `observed_dust_pairs.csv`, `measurement_accuracy_draws.csv`: signed biases and predeclared absolute errors for morphology preservation versus dust-difference recovery.
- `galaxy_observing_accuracy.csv`: per-galaxy error means, view SD, Monte Carlo SE, actual valid draws and eligibility per target.
- `galaxy_GLAO_gains.csv`, `GLAO_bootstrap_summary.csv`: paired strategy error reduction, per-galaxy signs, independent-clear versus shared-counterfactual-noise results and galaxy-bootstrap intervals.
- `spatial_information.csv`, `galaxy_spatial_information.csv`: native Ks structure errors/correlations at 0.5/1/2 kpc, dusty morphology versus truth dust imprint, surface-brightness strata, weak-reference flags.
- `aperture_quality.csv`, `aperture_center_robustness.csv`: F12/F30, R20/R30 and ±0.2-kpc center checks for every g/Ks pair.
- `sensitivity_morphology.csv`, `sensitivity_accuracy.csv`, `cache/*/sensitivity_spatial.csv`: five-development-galaxy O1 PSF-wing, exposure and distance sensitivities.
- `noisy_morphology_failures.csv`, `noisy_metric_galaxy_exclusions.csv`: explicitly retained noisy failures and metric/target exclusions.
- `instrument_parameters.csv`, `transfer_validation.csv`, `benchmark_reproduction.csv`, `noise_validation.csv`, `numerical_validation.json`, `development_gate.json`, `validation.json`: provenance, numerical checks and validation scope.
- `figures/01_…11_*.png` and `.pdf`: publication-sized figures; 02/03/05/09 are suggested main workshop figures. Each PDF has a raster preview.
- `representative_cases.csv`: deterministic selection provenance; examples always show O1, not a favorable selected orientation.
- `previous_results_sha256.json`: hashes of earlier scientific result files; checked again at delivery.
- `execution_provenance.json`, `output_manifest.sha256`: environment/code/output provenance generated at delivery.
- `cache/<galaxy>/`: compact three-band-plus-dust image cache and streamed/checkpoint tables; no full FITS duplication. Only O1 example detector images are retained. Other expected/noisy images can be regenerated deterministically.

## Reading the science correctly

Δdust = dusty − clear. R50 is aperture-conditioned. The apparent q statistic is not inclination. Physical projected dust is not attenuation, and zero SFR is not a dust test. All five views and all noise draws remain repeated measures within a galaxy. Galaxy bootstrap intervals describe selected-sample variability; they do not repair the intentionally balanced sampling design or unprovided source-model uncertainty.

The instrumental experiment is fixed-rest-band distance degradation of z=0 scenes using provisional PSFs/noise, not exact observer-frame ULTIMATE imaging. Rest Ks is not observer Ks at z=0.1. The clear counterpart is truth for scoring, not an observed input. No unique dust feature, geometry or mass inference is made. Earlier negative inference experiments remain preserved.

Source-product calibration: `zero_projected_dust_residuals.csv`, `zero_projected_dust_summary.csv`, and Figure 11 quantify nonzero contrasts in four zero-projected-dust objects. Their origin is unresolved; no offset is subtracted. Treat small paired changes and all dust-specific instrumental gains with this additional limitation. `four_view_morphology_robustness.csv` and `four_view_GLAO_robustness.csv` exclude antipodal O5 as a post-protocol sensitivity. `detector_sampling_robustness.csv` separates resampling from PSF effects.
