# Targeted ULTIMATE dust–population diagnosis

**Decision: NO-GO for a robust dust-geometry claim or ML using the current pipeline.** This is not proof that full broadband images lack the information: the sparse apertures discard significant structure for a demonstrated positive model pair.

Start with `scientific_report.md` and the executed `ULTIMATE_targeted_positive_model.ipynb` (HTML preview provided). Six figures have PNG/PDF versions. Prior experiments and original data remain unchanged.

## What actually executed
- Exact reproduction of the named old control, not the old full grid:4 PSF strategies × original500 noise draws, plus deterministic covariance/spatial/spectral mechanism checks.
- One new positive multiplicative model: positive luminosity field, nonnegative mixtures of independent training-region source SEDs, positive E-dependent attenuation before each band's PSF. No target clear aperture template, source map or true mass enters fitting.
- Numerical tests and a small development gate. Absolute-colour physical nulls fail, so no large evaluation or new validated GLAO power forecast is performed.
- Bounded diagnostic pilot:19 known-model-family calibration noises per statistic;17 separate population/screen cases; one absolute-colour and3 contrast noises per case. Same data also tested with the old Gaussian model. Each population remains separate. Every optimizer and local predictive check is saved. These counts cannot certify5% error control.
- Native seeing/GLAO adequacy audits, spatial-mode/aperture-size sensitivity, spectral coverage and source-grid isolation, absolute-colour invariance test, positive counterexample and pixel-versus-aperture information analysis.

## Run the notebook
```sh
cd /home/bahareh/ULTIMATE
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/ultimate-mpl JUPYTER_RUNTIME_DIR=/tmp/ultimate-jupyter IPYTHONDIR=/tmp/ultimate-ipython PYTHONDONTWRITEBYTECODE=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/multiplicative_diagnosis_20261026/execute_notebook.py
```
The existing phd kernel needs local socket permission. The notebook reruns tests, the specific old failure, two physical-model fits and the information-bound calculations. It reads the already-executed bounded pilot by default, to avoid rerunning it unnecessarily. Set `RECOMPUTE_PILOT=True` in its cell to reproduce that pilot. This distinction is explicit in the notebook, not a hidden cache.

To reproduce every focused result from existing data:
```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/ultimate-mpl PYTHONDONTWRITEBYTECODE=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/multiplicative_diagnosis_20261026/run_focused.py
```
This writes only this new results directory and temporary caches. It does not invoke any previous full-grid, download or catalogue code. No packages need installing. `validate_results.py` checks scientific-file consistency, notebook outputs, numerical tests and previous-file hashes.

## Key files
- `old_method_mechanism.csv`, `population_transform_projection.csv`, `spatial_span_diagnostic.csv`: exact false-positive mechanism.
- `physical_model.py`, `stellar_training.npz`: new positive forward model and disjoint training provenance.
- `development_gate.csv/json`, `development_fits.npz`: physical gate failures and successful known-family checks.
- `pilot_calibration.csv`, `pilot_thresholds.json`, `heldout_pilot_per_draw.csv`, `heldout_pilot_rates.csv`, `heldout_pilot_fits.npz`: actual pilot, intervals, optimizer flags, predictions, parameters and local covariance. Raw rejection flags are not physical detections when fits fail.
- `old_gaussian_same_pilot.csv`: Gaussian method on exactly the same observed pilot draws, with both matched pilot cutoff and previous published cutoff. Known-family calibration is not a population-wide guarantee.
- `native_adequacy_sensitivity.csv`: seeing/GLAO, coarse/fine spatial fields and1.5/3kpc apertures; adequacy only.
- `absolute_failure_isolation.csv`: source-grid and SED-coverage diagnostics. Independent-aperture NNLS is an optimistic coverage diagnostic only, not the inference model or a calibrated global likelihood test.
- `parameter_identifiability.csv`, `absolute_information_invariance.csv`, `positive_degeneracy_tradeoff.csv`, `conditional_identifiability_bound.csv`, `aperture_information_loss.csv`: information loss and precisely conditional counterexamples.
- `existing_u_band_diagnostic.csv`: training-only unweighted geometry using local LSST u; no throughput/noise/survey claim.

## Statistical and physical limits
The pilot statistic is penalized MAP-objective improvement, including declared priors. It is not a Bayes factor. Null and alternative use the same deterministic fitting policy: independent data-derived starts for each null, then its nested alternative; no cross-realization warm starts. A 19-sample maximum cutoff has nominal5% finite-sample predictive meaning only under its one exchangeable model-family null; it does not repair population-domain mismatch. Tiny held-out binomial intervals are pointwise and conditional on the cutoff.

Local Laplace posterior checks do not validate multimodal/nonlinear parameter inference. Optimizer failures remain failures. The effective-dof chi-square tail is descriptive and never a calibrated acceptance probability. Source Monte Carlo and physical SPS discrepancy error maps are unavailable; no invented residual floor forces acceptance.

Templates are empirical broadband source mixtures, not an independently validated SFH/age/metallicity grid. The143 gray and108 stellar-mixture parameters are shared spatial nuisance fields with fixed proper regularizing priors; their number exceeds sparse observations. Positivity and smoothness do not supply data identification. Global uniform E is exactly unidentifiable after per-band normalization. Full-pixel fixed-pair bounds assume known positive hypotheses and cannot replace population-marginalized recovery tests.

Only O1 of galaxy294866 is used. Actual DR1 griz/2MASS JHKs are rest bands; z=.3 is conditional image degradation, not exact ULTIMATE observer-filter synthesis. Rest Ks shifts beyond ordinary ground Ks. Instrument/sky/read/PSFs remain the previous provisional scenario. No intrinsic size evolution or new HAWK-I reduction is claimed. No DR2 work, new datasets, installation or ML occurs.
