# Static screen-test handoff

Start with [scientific report](scientific_report.md), [instrument audit](instrument_audit.md), and [DR2 catalogue status](catalogue_status.md).

- `ULTIMATE_static_screen_test.ipynb`: executed reproducible notebook; editable companion modules are in this directory.
- `ULTIMATE_static_screen_test_preview.html`: portable rendered notebook.
- `parameter_provenance.json`: settings, priors, assumptions, versions and limitations.
- `screen_model_results.csv`, `screen_model_summary.csv`: all main fits, failures and three-draw summaries.
- `robustness_results.csv`: population/discrepancy/interpolation/Av-grid checks.
- `observable_uniform_screen_residuals.csv`: observational residuals, without intrinsic truth supplied to the fitter.
- `psf_robustness_oracle.csv`, `glao_oracle_gain.csv`: explicitly privileged known-population separation bounds.
- `instrument_parameters.csv`, `instrument_bandpasses.npz`, `corrected_point_source_sensitivity.csv`: provisional instrument model.
- `calculator_original_1h_output.csv`, `calculator_exact_components.json`: reproduced published calculator.
- `transfer_validation.csv`, `physics_validation.json`, `validation.json`: numerical and delivery checks.
- `figures/`: six comparison figures, each PNG and PDF.
- `sources/`: pinned upstream code/docs/templates, bounded reference curves, authenticated metadata and SHA manifests. No credentials are stored.
- `input_cache/`: cropped structured broadband arrays streamed from the existing local archive; original FITS/archives untouched.
- `implementation_plan.md`, `review_notes.md`: experiment design and independent review.

All new files are isolated here. No existing project result was overwritten, no package installed, no new environment created, no large dataset downloaded and no ML run started.

Rerun from this directory in `/home/bahareh/miniforge3/envs/phd/bin/python` with `MPLCONFIGDIR=/tmp/ultimate-mpl`, `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`. The notebook can recompute the complete local experiment without network access; `prepare_skirt.py` rebuilds its cache from the original archive if necessary. `run_experiment.run(recompute=True)` forces all cases; `recompute=False` resumes saved cases and preserves transfer records. `run_robustness.py`, `validation_extra.py`, `postprocess.py` and `write_scientific_report.py` rebuild the other outputs in order. Notebook kernel name is `phd`; execution needs local Jupyter sockets. Reference network scripts are for provenance/metadata retrieval only and are unnecessary for rerunning the analysis.
