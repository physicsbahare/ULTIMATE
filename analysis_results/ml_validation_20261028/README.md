# ULTIMATE–Subaru continuation

Start with [project_continuation_report.md](project_continuation_report.md). It separates the verified canonical single final evaluation from this directory's supplementary validation-only models.

The canonical final20 evaluation is complete in `../ml_expanded_20261028/`; it must not become a tuning set. No supplementary final inference was performed. `canonical_final_provenance_check.json`, `canonical_final_score_audit.json` and `FINAL_EVALUATION_NOT_REPEATED.json` document that boundary. Supplementary final-stage scripts are disabled for the spent project test set.

Use existing `/home/bahareh/miniforge3/envs/phd/bin/python`. Model tables and fitted artifacts record exact settings; `environment.json` records package versions. `model_study.py` implements the supplementary grouped methods; `integrated_Ks_study.py` adds the same model family for integrated Ks. `verify_results.py`, `verify_tables.py` and `audit_canonical_final.py` retain independent numerical checks. The earlier canonical directory remains read-only to this continuation.

`scientific_report.md` describes supplementary validation results. `expanded_training_evaluation.ipynb` executes representative development refits and held-out checks, then reads the saved canonical final summary without any new final inference.
