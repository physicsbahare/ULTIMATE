# Guarded final20 extraction (prepared; not yet run)

The entrypoint is `unseal_final.py`. It never opens final science on import, `--help`, or `--check`. Execution requires the explicit `--run` switch and a valid `../FINAL_PROTOCOL_FROZEN.json`. The receipt is written by the root workflow only after models, calibration, development CV, integrity tests and sensitivity choices are frozen.

Receipt schema:

```json
{
  "protocol_frozen": true,
  "allow_final_unseal": true,
  "stages_frozen": ["development_cv_settings", "models", "calibration", "integrity_tests", "sensitivity_choices"],
  "final_test_ids": ["replace with the exact 20 integer IDs from frozen_galaxy_partitions.csv"],
  "artifacts": [
    {"path": "ULTIMATE-relative/path", "sha256": "64-character SHA256", "roles": ["code"]}
  ]
}
```

Each artifact can use `role` (single string) or `roles` (list). Collectively require `code`, `model`, `calibration`, and `protocol` roles; a saved model containing calibration can have both roles. Include every frozen code/model/calibration/protocol/sensitivity artifact. Mandatory artifact paths, relative to ULTIMATE, all start `analysis_results/ml_expanded_20261028/`:

- `data_audit/unseal_final.py`
- `data_audit/prepare_data.py`
- `data_audit/frozen_galaxy_partitions.csv`
- `data_audit/validation.json`
- `data_audit/archive_inventory.csv`
- `data_audit/cache_file_integrity.csv`
- `expanded_features.py`
- `expanded_models.py`

No receipt self-hash is required. The entrypoint records its full receipt hash. Every listed artifact is hashed before extraction, before each final galaxy, and after extraction; any mismatch aborts. The default `prepare_data.stream()` continues rejecting final-test galaxies without that receipt. It independently checks frozen partition membership, so a final ID cannot bypass the guard by being labeled development.

After explicit RUN authorization, execute from ULTIMATE:

```sh
PYTHONDONTWRITEBYTECODE=1 /home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_expanded_20261028/data_audit/unseal_final.py --check
PYTHONDONTWRITEBYTECODE=1 /home/bahareh/miniforge3/envs/phd/bin/python -u analysis_results/ml_expanded_20261028/data_audit/unseal_final.py --run
```

Final caches use the existing `data_audit/cache/<finalsid>/O1.npz` through `O5.npz` seven-key native800 schema. Final-only archive/member/physical/cache tables and completion receipt are written under `data_audit/final_unseal/`. A process lock prevents concurrent extraction. The start marker binds subsequent extraction resumes to the same frozen receipt, and complete galaxies are reused only when their receipt hash matches.

The original `data_audit/{archive_inventory,fits_inventory,available_galaxies,physical_maps}.csv` and `validation.json` remain the pre-unseal100nonfinal stage snapshots: their final rows retain `sealed_final=true,science_opened=false`. Final-only successful records instead have `audit_stage=final_unseal`, `sealed_final_at_preunseal_audit=true`, `sealed_final=false`, `science_opened=true`, and `frozen_receipt_sha256`. The final completion receipt records hashes proving old stage snapshots stayed unchanged. No final science has been opened while preparing this entrypoint.
