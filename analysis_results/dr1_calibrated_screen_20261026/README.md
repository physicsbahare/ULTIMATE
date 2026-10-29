# Reproduce the calibrated DR1 screen experiment

All outputs here are new. Previous `../screen_test_20261026/` and original data/notebooks are preserved. Use `/home/bahareh/miniforge3/envs/phd/`; no packages need installing. No downloads or DR2 work occur.

Read `scientific_report.md` first. **Do not present the likelihood ratio as a calibrated physical dust-geometry detection.** The final bounded-ensemble rates, new-noise population-anchor failures, predictive inadequacy and matched-rest-band limitation must be presented together.

## Run the executed notebook

```sh
cd /home/bahareh/ULTIMATE
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/ultimate-mpl JUPYTER_RUNTIME_DIR=/tmp/ultimate-jupyter IPYTHONDIR=/tmp/ultimate-ipython PYTHONDONTWRITEBYTECODE=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/dr1_calibrated_screen_20261026/execute_notebook.py
```

The existing `phd` kernel is used. Local Jupyter sockets must be permitted; the restricted sandbox initially rejected them, and execution was retried with authorized local execution permission. The notebook runs the full pipeline from existing inputs, not merely loading result tables. It exports a standalone HTML preview. The one-cell timeout is1800s. `build_notebook.py` rebuilds the unexecuted notebook only if desired, replacing this new notebook, never the old experiment.

## Pipeline and output meanings
1. `experiment.py`: matched fixed-scene development tests;200 calibration +200 evaluation draws for five nulls and alternative scenes. Fixed sky/read/sampling assumptions. `calibrated_rates.csv`, `evaluation_statistics.csv.gz`, `posterior_predictive.csv`, `transfer_validation.csv`; these are DEVELOPMENT results.
2. `diagnostics.py`: inventory, training/evaluation colour-basis audit, finite-band attenuation sensitivity, post-fit physical-map checks,10000-draw normalization test. Maps/clear evaluation images here diagnose failures, never feed templates to fitting.
3. `population_stress.py`: development null stress tests,200 new evaluation noises. These failed and motivated a broader *calibration ensemble*, without changing fitted priors.
4. `FINAL_PROTOCOL.md` / `final_ensemble.py`: final bounded two-PC population ensemble;500 calibration draws PER global-screen null and500 independent evaluation draws PER scene; five nulls, smooth/patchy alternatives and original SKIRT. `FINAL_calibrated_rates.csv` is the final rate table. `FINAL_calibration_statistics.csv.gz` / `FINAL_evaluation_statistics.csv.gz` preserve per-draw scores and flags. Coefficients and six fixed fields are saved in `final_population_ensemble_definition.npz`.
5. `final_stress.py`:500 NEW noise draws on fixed population anchors and a uniform-E within-band-SED coefficient sensitivity, using frozen final cutoffs. `FINAL_population_anchor_stress.csv` tests individual settings beyond ensemble-average error control. These are final robustness checks, not threshold tuning.
6. `publish.py`: PNG/PDF figures, physical control summary, paired GLAO comparisons, calibration+evaluation bootstrap and scientific reports. `GLAO_power_comparison.csv` includes conditional exact McNemar tests (Bonferroni12 primary joint comparisons), conservative paired-discordance intervals and bootstrap intervals that also resample calibration. Non-joint comparisons are exploratory, regardless of nominal corrected-p column. Degenerate bootstrap endpoints at saturated power do not imply exact knowledge of population power; use exact binomial intervals.
7. `test_validation.py` / `validate_delivery.py`: numerical tests, execution/output integrity and previous-file preservation checks.

## Inputs and provenance
Read-only dependency: `../screen_test_20261026/input_cache/O1..O5_structured_broadbands.npz`, previous `instrument.py`/`forward_physics.py`, pinned calculator/FSPS files. Local original archive supplies only three O1 physical maps for post-fit diagnostics; no additional images are downloaded. `input_provenance.json` records hashes, and `previous_results_sha256.json` / `validation.json` check preservation.

`matched_DR1_scenes_O1.npz` retains actual A/B/C/D images. `screen_definitions.npz` defines positive smooth/patchy E maps and band coefficients. The physical scene is fixed between z=.1/.3; population perturbations vary across robustness trials, not with redshift. `parameters.json`, `attenuation_coefficients.csv`, `instrument_parameters.csv` and source reports record assumptions. Random seeds and separate-stage coefficient RNGs are in the code and final definition NPZ. Every within-condition noise draw is independent; bands/modes/truths/views reuse paired streams and cannot be pooled as independent galaxies.

Only galaxy294866 is available. Additional orientations are correlated development checks. Training fields and the six perturbation modes are fixed, not a representative astrophysical population distribution. Residual colour PCs are in the likelihood but not generated in the final ensemble. Exact noise means/covariances supplied by simulation do not include unmodelled reduction/calibration systematics. Posterior predictions shown are the prespecified first held-out realization, not a full coverage test.

The seven rest-band degradation tests are **not exact observer-frame ULTIMATE forecasts**. In particular rest Ks lies beyond ordinary Ks atz=.3. See `redshift_bandpass_limitations.md`; narrower PSFs never improve the original resolution by convolution or binning.
