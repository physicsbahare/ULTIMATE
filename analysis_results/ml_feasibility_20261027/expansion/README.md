# Frozen DR1 expansion to120 galaxies

`partitions_frozen.json` and the hashed CSVs define86 development galaxies (all26 previously inspected galaxies plus60 new),14 validation galaxies and20 untouched final-test galaxies. The final20 are all new. Previous held-out labels from the26-galaxy feasibility analysis are retired because those galaxies have already been inspected. No new FITS image was opened for selection, partitioning or download verification.

## Selection and limits

The saved official Baes24 DR1 catalogue contains1154 unique galaxies. Excluding the26 existing IDs leaves1128 eligible galaxies; archive IDs are parsed from the suffix rather than the `50` in `TNG50`. The saved eligible catalogue supplies the established five stellar-mass strata crossed with zero SFR and four positive-specific-SFR strata. The source catalogue contains stellar/gas/dark-matter masses, SFR and stellar half-mass radius. It supplies no dust mass, morphological class or true inclination. Gas fraction and gas mass divided by2π times squared stellar half-mass radius are recorded only as rough metadata proxies. Gas surface density uses a stellar radius and is not a resolved gas measurement, dust measurement, or morphology label.

Seed20261027 chooses19 of25 strata to receive4 galaxies; the other6 receive3. Sampling is uniform without replacement within each stratum. The `selection_probability` column is conditional on that frozen quota allocation: n_h/N_h. Before quota allocation, each stratum has probability19/25 of receiving4, and each eligible galaxy has marginal inclusion probability(94/25)/N_h. The selected94 are randomly permuted into60 development,14 validation and20 final-test objects; their partition probabilities conditional on selection are60/94,14/94 and20/94. Joint probabilities in the CSV are conditional on frozen quota allocation. Their unconditional counterparts are60/(25N_h),14/(25N_h),20/(25N_h). The old26 are a fixed, historically selected development set and have no claimed population inclusion probability. This balanced feasibility design is not a volume-representative or disk-only sample.

Selection is independent of archive sizes and image measurements. All94 must pass size/range preflight before any full transfer. `strata.csv` records exact eligible counts and quotas. `galaxy_partitions.csv` includes the120 exact IDs and official metadata; separate CSVs provide each partition. The freeze file records creation time and SHA256 hashes. Reproduction refuses to redraw an existing frozen selection.

## Acquisition and holdout protection

Only the official TNG50-1/snapshot99 DR1 `skirt_atlas.tar.gz` API route is used. `data/TNG50_SKIRT_DR1_ml_expansion/download_expansion.py` imports and configures the existing secure downloader without modifying it. The owner-only `~/.tng_api_key` is read internally; it is never passed in argv/environment or logged. API-key headers are removed on cross-host redirects and only approved HTTPS hosts are allowed. Signed URLs and response bodies are never saved. No DR2 or snapshot package is requested.

The compressed archive cap is100GiB, with a100GiB free-space floor plus256MiB headroom checked for every chunk. Partial downloads resume with Range/If-Range. Verification drains gzip for CRC, reads tar payload lengths and computes SHA256; it does not parse FITS values, extract files, inspect images, calculate image-derived quantities or use the final-test sample for tuning. All final-test archives remain sealed for scientific analysis. A verified archive is atomically renamed from `.part`; already verified unchanged files are skipped on restart. An exclusive lock prevents concurrent full batches.

`acquisition_status.json` is a timestamped snapshot, not a promise of current completion. The live authoritative state is `data/TNG50_SKIRT_DR1_ml_expansion/download_state.json`. A stale PID file alone does not prove liveness.

## Reproduction and monitoring

```sh
cd /home/bahareh/ULTIMATE
# This refuses to redraw the existing freeze; use only when initially reproducing
# into an empty expansion output directory.
/home/bahareh/miniforge3/envs/phd/bin/python analysis_results/ml_feasibility_20261027/expansion/freeze_selection.py

# Network access outside the restricted sandbox is needed for these two steps.
/home/bahareh/miniforge3/envs/phd/bin/python data/TNG50_SKIRT_DR1_ml_expansion/download_expansion.py --preflight
sh data/TNG50_SKIRT_DR1_ml_expansion/start_download.sh

tail -n20 data/TNG50_SKIRT_DR1_ml_expansion/download.log
/home/bahareh/miniforge3/envs/phd/bin/python -m json.tool data/TNG50_SKIRT_DR1_ml_expansion/download_state.json
ps -p "$(cat data/TNG50_SKIRT_DR1_ml_expansion/download.pid)" -o pid,etime,stat,args
df -h /home/bahareh/ULTIMATE
du -sh data/TNG50_SKIRT_DR1_ml_expansion
```

After checking that the recorded PID still belongs to this downloader, stop gracefully with `kill -TERM "$(cat data/TNG50_SKIRT_DR1_ml_expansion/download.pid)"`. Restart using the same launch command to resume. Do not rerun or alter selection in response to transfer sizes or outcomes.
