# M4-offset HAWK-I/GRAAL Ks calibration

Start with [scientific_report.md](scientific_report.md), [empirical_calibration.ipynb](empirical_calibration.ipynb) or the self-contained [HTML notebook](empirical_calibration.html). The executed notebook reads completed source measurements and runs integrity/numerical verification. The expensive source extraction is recorded in scripts and logs; it is not rerun on notebook opening.

No completed ML result, frozen partition or model was modified. The only prior-ML access was the read-only freeze hash guard. No science/final-test data were opened for model development. All calibration outputs are new and local to this directory. The NGC3256 sources were read without modifying their earlier results. No data were shared or transferred to a collaborator.

## Main artifacts

* Inputs: `input_integrity.json`, `fits_provenance.csv`, `image_planes.csv`, original header JSON and DataLink records.
* Ancillary source/calibration references: `ancillary_download_log.json`, `ancillary_integrity.csv`, `ancillary_grid_checks.csv`, `raw_provenance_ids.csv`, `calibration_reference_manifest.csv`. Public retrievals are small catalogue/cutouts/Gaia only; no raw dataset.
* All source fits/rejections: `psf_fits.csv`; final validated/masked selection: `science_star_table.csv` (unique key field/source_local_id). Local IDs differ between bright and faint extractions; never join these by local ID.
* Matched identities: `matched_stars_primary.csv` (276 rows,244 Gaia IDs); `paired_changes.csv` includes unique-star and spatial bootstrap uncertainty. Gaia IDs are integers; do not load into floating-point spreadsheets and round them.
* PSF statistics/maps: `PSF_summary.csv`, `PSF_spatial_cells.csv`, `empirical_profiles.csv`, `EE_uncertainty.csv`, `figures/` PNG/PDF. Extension3 is physical CHIP4, extension4 is CHIP3.
* Systematic checks: `fit_window_paired.csv`, `brightness_selection_matched_cells.csv`, `saturation_profile_checks.csv`, `quadrature_sensitivity.csv`, `astrometry_and_selection.csv`. The first broader sample is retained in `broad_peak_selection/`; the fainter extraction is in `faint_peak_selection/`.
* Noise: `background_regions.csv`, `background_covariance.csv`, `aperture_noise.csv`, `aperture_samples.csv`, `aperture_noise_uncertainty.csv`, `confusion_*.csv`; same-estimator NGC3256 comparison tables.
* Injection-ready sensitivity definitions, with explicit limitations: `sensitivity_models/README.md`. No actual mock injection has been performed.
* Verification/environment: `verification.json`, `verification.log`, `notebook_execution.log`, `artifact_manifest.json`.

## Reproduction

Use `/home/bahareh/miniforge3/envs/phd/bin/python` (no installation needed). Work from the project root. Prefix each named script below with this interpreter and `analysis_results/hawki_m4off_20261028/`.

For routine review, run `verify_results.py`, then `execute_notebook.py`. The latter creates a temporary local kernelspec under `/tmp`, uses the existing phd interpreter, executes every cell, exports HTML and saves rendered notebook figures. A sandbox must permit localhost sockets; no external service is needed. The notebook also works from this directory or the project root. `make_notebook.py` rebuilds its unexecuted scaffold and must be followed by `execute_notebook.py`.

To reproduce the full measurement pipeline, use a **new copy of this analysis directory** while retaining source data paths and cached ancillary files. Do not remove or overwrite the archived evidence here. The scripts use paths relative to their own location and the project analysis_results hierarchy. The documented execution order is:

1. `provenance_audit.py` reads uploaded science and cached ancillary FITS; `extract_instrument_configuration.py` records instrument and AO-loop header snapshots. Network fetch scripts are provenance records; offline reproduction does not call them.
2. `measure_psf.py` creates the broader selection. It skips existing per-plane source tables. Preserve its aggregate/per-plane source/profile/stamp files under `broad_peak_selection/` before the next step. It creates the fixed detection catalogues and image-plane manifest.
3. `measure_fainter_sample.py` extracts the conservative primary sample into `faint_peak_selection/` and promotes source/profile/stamp tables. Its `detection_spatial_audit.csv` belongs to this extraction and should be copied to the top level; preserve the previous broad audit separately. Both passes sample different stars.
4. `measure_noise.py`, then `analysis_refinements.py` (finite signed-growth first crossings and geometric aperture packing counts). `confusion_stress.py` performs additional catalogue masking. `compare_ngc3256.py` and `compare_noise_ngc3256.py` apply the same estimators to existing NGC3256 products.
5. `validate_stars.py`, `fit_sensitivity.py`, `build_models_and_figures.py`, then `noise_model_validation.py`. The final flat-core mask explicitly casts nullable flags to bool before inversion; the final verification asserts none pass.
6. `finalize_diagnostics.py` adds spatial shape maps, brightness/window summaries and explicit kernel wing-support annotations. `summarize_uncertainties.py` adds EE and regional noise intervals. `quadrature_check.py` independently tests integration/optimizer sensitivity. Then `fit_growth_sensitivity.py` fits and records the finite-growth core+halo stress grid.
7. `write_report.py`, `verify_results.py`, `make_notebook.py`, `execute_notebook.py`, then `seal_deliverables.py`.

The protocol fixes sample cuts, definitions, seeds and limitations. Source fits use local constant weights; independent-pixel formal errors are not calibrated and are not promoted as uncertainty. Bootstrap intervals describe these fixed products and spatial samples. They are not total instrumental or temporal repeatability errors.

The selected stars are conservatively unsaturated candidates in the reduced products. The global nonlinear-pixel QC flag remains unresolved at the raw per-source level. R32 aperture calibration is rejected because of sparse independent void apertures. Fitted Moffat tails and broad total-background mixtures remain labelled extrapolations/stresses. No unique instrumental PSF, dust truth or real ULTIMATE0.2-arcsec measurement is claimed.
