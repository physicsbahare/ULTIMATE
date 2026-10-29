# Spatial-structure feasibility pilot

New objective: observable dust-induced brightness/colour structure and morphology, not 3D geometry discrimination. Read `scientific_report.md` first; previous negative model-inference findings are preserved.

## Environment and reproduction

No packages installed. Use the existing environment:

```sh
cd /home/bahareh/ULTIMATE/analysis_results/spatial_structure_pilot_20261026
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export MPLCONFIGDIR=/tmp/ultimate-mpl PYTHONDONTWRITEBYTECODE=1
/home/bahareh/miniforge3/envs/phd/bin/python validation_checks.py
/home/bahareh/miniforge3/envs/phd/bin/python pilot.py
/home/bahareh/miniforge3/envs/phd/bin/python secondary_analysis.py
/home/bahareh/miniforge3/envs/phd/bin/python boundary_sensitivity.py
/home/bahareh/miniforge3/envs/phd/bin/python depth_threshold_diagnostic.py
/home/bahareh/miniforge3/envs/phd/bin/python presentation.py
/home/bahareh/miniforge3/envs/phd/bin/python execute_notebook.py
/home/bahareh/miniforge3/envs/phd/bin/python validate_delivery.py
```

Only this directory is written. Reproduction replaces this new pilot's outputs, so copy the directory first if preserving its current execution is desired. The original input caches, notebooks, reports and results are read-only. Do not run the old experiment drivers.

The notebook defaults to consuming the already executed image ensemble and recomputing selected measurements, tables/figures and integrity checks. Its `RECOMPUTE_ENSEMBLE=True` switch executes the full new image pilot. It does not execute the old Bayesian grids. `execution.log` records the ensemble's completed CLI run; `notebook_execution.log` records notebook execution. Kernels need local socket access; restricted launchers may need their standard sandbox approval for Jupyter. No network is required for reproduction.

## Main artifacts

- `ULTIMATE_spatial_structure_pilot.ipynb` and HTML: executed companion with embedded figures and report.
- `pilot.py`: renderer, observed-image-only feature methods, full-image morphology, independent evaluation draws, summaries. `PROTOCOL.md`: fixed generation/measurement criteria.
- `references/O?_effective_attenuation.npz`: central 40kpc truth images, positive-flux masked effective attenuation, projected dust. `clear` and `dusty` units MJy/sr; `A_eff` mag; projected dust M_sun/pc²; 100pc source pixels. Negative attenuation retained; NaN denotes masked values.
- `observations/*.npz`: one fixed first noise draw per condition/scene, expected native detector rate [electron/s/pixel], variance [(electron/s/pixel)²], derived structure/sigma/detection maps at 1kpc, intrinsic and PSF-limited dust-imprint references, radius and pixel scale. All remaining draws are reproducibly generated from stored seed formula and summarized in per-draw CSVs; saving every full noise image is unnecessary.
- `feature_draws.csv`, `feature_summary.csv`: every scale/scene/noise outcome; separate controls, native-reference area completeness, contamination, IoU, spatial correlation, PSF-limited overlap, component overlap and surface-brightness strata.
- `control_structure_incidence.csv`: probability that each control shows at least one scale-sized candidate component, with exact 95% binomial intervals over independent noise draws. This measures false dust attribution if those structures were called dust, not noise-only false detections of real structure.
- `paired_GLAO_summary.csv`: paired GLAO-minus-seeing changes; uncertainty is Monte Carlo uncertainty of the mean for a fixed source/PSF/noise model, not an instrument/generalization forecast.
- `scale_transfer.csv`: truth-isolated spatial-transfer diagnostic. Its known-counterpart imprint S/N is optimistic and not an observed dust-detection statistic.
- `depth_threshold_diagnostic.csv`: noiseless reference-pixel contrasts and expected noise-assisted crossings explain non-monotone depth completeness without changing any thresholds.
- `component_incidence.csv`: scale-sized component incidence for every scene; kept distinct from recovery of reference-component area by a union of smaller candidate pixels.
- `dust_morphology_bias_summary.csv`: paired SKIRT-minus-clear morphology. `morphology_noise_bias.csv`: noise-minus-noiseless measurement bias. Intrinsic no-observational-PSF morphology uses `draw=-1` in `morphology_draws.csv`.
- `conditional_scale_recoverability.csv`: descriptive 50% area-completeness/50% contamination summary, not a calibrated acceptance test or a universal resolution limit.
- `boundary_sensitivity.csv`: finite 32kpc versus 48kpc measurement field at fixed R<12kpc; largest 2kpc analysis scale has edge sensitivity, especially Ks deficits.
- `noise_covariance_validation.csv`, `numerical_validation.json`, `validation.json`: numerical/ensemble/notebook checks. No independent-pixel statistical errors.
- `instrument_parameters.csv`: provisional detector/noise/PSF parameters copied by read-only function from previous audit. Nominal Ks detector conversion is a proxy for degraded rest-frame Ks, not an exact observer-Ks forecast.
- `input_provenance.json`, `execution_provenance.json`, `previous_results_sha256.json`: input/code hashes, environment, random seeds, preservation checks.
- `MaNGA_validation_note.md`: public DR17 documentation-based feasibility proposal; no MaNGA science data obtained, no messages sent.

## Scope and decisions

O1 has z=0.05/0.1, 0.25/1/4h per band, both strategies. O2–O5 have z=0.1, 1h/band. Equal-D50 Moffat sensitivity is O1/z=0.1/1h, native Ks only. Each of 22 conditions has four scenes ×40 independent draws. Three actual bands mean three times the per-band exposure budget, excluding overheads. g remains seeing limited. Gaussian PSF matching uses positive kernels; combined fine/broad kernels propagate induced covariance. Known-sky subtraction, independent detector-pixel noise and perfect astrometric/PSF knowledge are explicit idealizations.

The same standard normal pixel innovations are used across strategies/scenes at fixed view/z/depth, with correct source-dependent variance and 60s read splitting. Different orientations/distances/depths use different recorded seeds. No thresholds depend on final evaluation outcomes. Calibration uses seed761902, evaluation base982310 plus view/distance/depth terms, stellar-control field seed73921. These repeated noise samples are not additional galaxies.

No unsupported observer-filter interpolation, DR2 work, datacube reconstruction, new science downloads, ML or intrinsic evolution. At z=0.1 even rest Ks shifts to ~2.375µm, so results are conditional image degradation. Reference extinction screens use broad-band approximate coefficients; SKIRT is the independent radiative-transfer scene. Rejecting or locating a structure cannot identify unique dust geometry.
