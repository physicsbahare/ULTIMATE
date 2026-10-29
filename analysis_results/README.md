# ULTIMATE analysis handoff

Start with [scientific summary](scientific_summary.md), [HAWK-I audit](hawki_inspection_report.md), and [prioritized next experiments](next_experiments.md).

- `TNG294866_five_orientations.ipynb`: executed five-view analysis, input assertions, complete code, embedded plots/tables.
- `pilot_reproduced.ipynb`: executed copy of the original notebook; only input/output paths changed.
- `*_preview.html`: portable notebook rendering.
- `tng_orientation_summary.csv`: one row per view of the same galaxy, not independent galaxies.
- `tng_mask_aperture_sensitivity.csv`: 135 rows (27 analysis choices × five views).
- `tng_input_validation.csv`: source paths, SHA256, units, zero counts for 25 inputs.
- `attenuation_maps/O*_maps_500pc.fits`: full-frame g/Ks effective attenuation, projected dust and R20 joint valid mask, 500-pc grid. Negative attenuation retained.
- `figures/`: main TNG and HAWK-I figures, each PNG and PDF.
- `hawki_metadata.csv`: 22 exposure records including integrity, acquisition, seeing and provisional image widths.
- `hawki_detector_metadata.csv`: 88 detector records; `hawki_psf_candidates.csv`: individual compact-source fits; `hawki_psf_per_exposure.csv`: summaries.
- `hawki_headers.json`: all original parsed header values; `hawki_completeness.json`: query-to-file match.
- `extracted_294866/`: exactly 20 required O2–O5 files copied from the existing archive; not a new download.
- `input_inventory.json`, `archive_inventory.json`, `extraction_manifest.json`: provenance.
- `environment.json`, `environment_inspection.md`: reused environment and versions.
- `workshop_10min.pdf`, `workshop_talk_outline.md`: preliminary talk draft with figures and timed notes.
- `validation.json`: executed checks and known scientific limitations.

All scripts and new outputs are confined to this directory. No original FITS, notebook, download log or previous result was edited.

## Rerun using the existing environment

```sh
cd /home/bahareh/ULTIMATE
export MPLCONFIGDIR=/tmp/ultimate-mpl
export JUPYTER_RUNTIME_DIR=/tmp/ultimate-jupyter
export IPYTHONDIR=/tmp/ultimate-ipython
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/inspect_inputs.py
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/inspect_hawki.py
/home/bahareh/miniforge3/envs/phd/bin/python -m jupyter nbconvert --execute --to notebook --inplace --ExecutePreprocessor.kernel_name=phd analysis_results/pilot_reproduced.ipynb analysis_results/TNG294866_five_orientations.ipynb
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/write_reports.py
```

Jupyter requires local kernel sockets. The initial sandbox blocked socket creation; the notebook executions succeeded using the approved local-kernel execution outside that restriction. This did not require any package/environment changes. Output reruns replace only newly generated artifacts here. `build_notebooks.py` rebuilds the notebooks from source, clearing their execution outputs; it is optional and must be followed by execution. Markdown prose in the reports states this run's results; if methods or inputs change, review and regenerate the narrative and presentation as well. `inspect_hawki.py` resets its metadata CSV; rerun `write_reports.py` afterward to reattach per-exposure PSF statistics.
