# Persistent project instructions

This is the existing **Beyond the Foreground Screen: Machine-Learning Dust Geometry with ULTIMATE-Subaru** feasibility project, not a blank research project.

1. Before starting, read `docs/NEW_SESSION_HANDOFF.md`, `docs/PROJECT_STATE.md`, `docs/SCIENTIFIC_DECISIONS.md`, `docs/COMPLETED_ANALYSES.md` and `docs/OPEN_QUESTIONS.md`.
2. Search existing scripts, notebooks, reports, tables and manifests before writing replacements or recommending experiments. Older `next_experiments.md` files are historical, superseded proposals.
3. Preserve archived scientific outputs, original data, freeze receipts and negative results. Never silently overwrite completed results; new authorized work needs a distinct output directory and provenance.
4. Never repeat a completed analysis without identifying and documenting a genuinely new scientific requirement. Do not automatically run acquisition, verification, report-builder or notebook scripts: many write outputs or refit models.
5. The galaxy-level 120 partition is frozen: 86 development, 14 validation, 20 **spent final**. Five orientations are correlated. The final20 was evaluated exactly once; never reuse it as untouched data or run disabled supplementary final scripts.
6. Separate established numerical findings from hypotheses, and distinguish physical dust inference, operational dust-bias prediction, direct morphology recovery and instrumental biases.
7. Maintain reproducibility: retain exact sample IDs, hashes, model settings, package versions, seeds, source paths, metrics and original receipts. See `docs/REPRODUCTION.md`.
8. Update project state, decisions, completed/open work and history after every meaningful authorized change; keep claim-to-artifact links current.
9. Avoid unnecessary downloads and expensive computations. DR2 suitability/availability was checked and required data remain unavailable for planned use; reopen only with new evidence. HAWK-I/GRAAL empirical calibration is completed.
10. File-screen publication explicitly; never blindly `git add .`. Exclude credentials, restricted data, raw bulk FITS/archives and caches; record every excluded scientific artifact in the manifest. Do not infer redistribution rights from public access.

Read-only archival verification: `/home/bahareh/miniforge3/envs/phd/bin/python tools/verify_archive.py`. Scientific reproduction is a separate explicitly authorized task in a separate copy. No new ML training, observational forward modeling, source-label audits, DR2 investigations or HAWK-I reductions were authorized by the 2026-10-29 archival task.
