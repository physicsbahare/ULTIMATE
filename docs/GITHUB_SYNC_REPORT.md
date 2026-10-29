# GitHub synchronization report

**Historical archival-task receipt below.** The authentication blocker was subsequently resolved externally. The later owner-authorized targeted continuation was pushed successfully as `7834fb29b77ffa19c7433445d04522c3982db1d8`, with matching remote SHA. See the [latest continuation synchronization receipt](../analysis_results/ultimate_020_information_gap_20261029/github_sync.md). The earlier failed-push record is preserved unchanged in meaning.

Verified **2026-10-29 (Asia/Taipei)**. Repository: [physicsbahare/ULTIMATE](https://github.com/physicsbahare/ULTIMATE).

**Status: LOCAL ARCHIVE COMPLETE; GITHUB PUSH BLOCKED BY AUTHENTICATION. No project files were uploaded.** A complete screened local commit is preserved. The repository still has no remote refs; no unrelated commits were overwritten and no force-push occurred.

## Commit, branch and exact blocker

- Scientific archive commit: `160f0bad5cae1ddfea8d7690904be6afbe8c0a7b`.
- Archive tree: `580e51ac898712a635b478f38e0206be0d605965`; branch `main`; origin `https://github.com/physicsbahare/ULTIMATE.git`.
- The archival commit contains 3,389 files / 571,329,552 working-tree bytes (about 545 MiB). Largest committed blob: 24,063,245 bytes, below the 25 MB selection limit.
- This final report, refreshed archive-verification receipt and [remote receipt](manifests/REMOTE_VERIFICATION.json) are preserved in a following local documentation commit. The report references the archive parent SHA to avoid a self-referential commit hash; `git rev-parse HEAD` identifies the final local receipt commit.

Native HTTPS push returned exactly:

```text
fatal: could not read Username for 'https://github.com': terminal prompts disabled
```

The existing SSH route also failed strict host verification; no SSH agent was connected and the inspected SSH directory contained configuration/known_hosts only, no identity files. No credentials/private keys were read, printed, generated or published. The connected GitHub app reports push/admin permission, but that does not configure native Git credentials; its per-file/object API is not a native bulk Git-pack transport for this archive. No partial remote substitute was created. Authentication must be configured externally before the existing commit can be pushed. This is an authentication blocker, not an automatic-approval rejection.

## Prepared versus uploaded content

| Category | Prepared locally | Uploaded |
|---|---:|---:|
| Python scripts |189|0|
| Shell scripts |2|0|
| Notebooks |13|0|
| Markdown reports/documentation |115|0|
| HTML reports/notebook renderings |11|0|
| Scientific figure files (100 PNG + 79 PDF) |179|0|
| PDF workshop presentation |1|0|
| Scientific result tables (CSV/CSV.gz) |1806|0|
| Archive CSV manifests |4|0|
| Saved joblib models |318|0|
| Small diagnostic NPZ arrays |23|0|
| Execution/verification logs |137|0|

Script total 191 includes the two new archive-administration Python tools; original eligible project source is 187 Python + 2 shell. Report/HTML total 126 includes original scientific reports and new archive documentation. Counts classify the workshop PDF separately from figure files. Final additional receipt is JSON and does not change these category counts. [Published-file allowlist](manifests/PUBLISHED_FILES.csv) records all prepared paths/current hashes; final/self-referential receipts use Git objects as authority.

## Scientific coverage

All 13 top-level result directories are indexed: `attenuation_maps`, `extracted_294866`, `figures`, `pilot_reproduction_figures`, `screen_test_20261026`, `dr1_calibrated_screen_20261026`, `multiplicative_diagnosis_20261026`, `spatial_structure_pilot_20261026`, `multigalaxy_morphology_20261027`, `ml_feasibility_20261027`, `ml_expanded_20261028`, `ml_validation_20261028`, `hawki_m4off_20261028`.

[Completed analyses](COMPLETED_ANALYSES.md) adds nested acquisition, independent morphology verification, source-label, instrument/center/aperture, NGC3256 empirical and supplementary integrated-Ks studies. Scientific decisions preserve screen/positive-model failures, non-robust GLAO ML gain and rejected large-aperture noise. Current state/handoff preserve operational versus physical claims, completed DR2 checks, completed empirical HAWK-I characterization, exact frozen partitions and spent final20. No scientific study was rerun.

## Excluded datasets and outputs

The original baseline contains 9,367 files /89,335,515,275bytes; 3,341 originals are eligible and 6,026 are individually excluded. [EXCLUDED_FILES.csv](manifests/EXCLUDED_FILES.csv) gives every excluded scientific output's exact preserved server path, size, original mtime, available hash and reason.

Excluded: raw HAWK-I/TNG FITS, downloaded simulation archives, bulk NPZ/image/input caches, installed environment/bytecode/process state, and downloaded third-party calculator/forward/template payloads with unverified redistribution terms. None was deleted, rewritten or recompressed. Figures, tables, source, notebooks, fitted models and small receipts were selected at file level; no scientific analysis directory was blindly excluded. No credential/confidential/raw oversized payload was committed.

## Verification results

[ARCHIVE_VERIFICATION.json](manifests/ARCHIVE_VERIFICATION.json) records fresh read-only checks, separate from saved scientific pass receipts:

- All 9,367 original paths/sizes/modification times agree with the baseline; all 3,382 available original hashes agree. Large raw/bulk files were checked by size/mtime plus historical integrity records rather than a new full 84 GiB hash pass.
- All 13 notebooks parse, contain executed code cells and record zero error outputs. All project Python sources parsed with AST; no scientific import, notebook execution, model deserialization, fitting or inference occurred.
- Literal credential/private-key/access-URL screening found no actual credentials. One exact synthetic downloader-test query fixture was manually confirmed and documented. No credential file was opened.
- All newly authored local document/figure/table links resolve. Four inherited copied-JWST README links point to files already absent from the original local project; [HISTORICAL_LINK_GAPS.json](manifests/HISTORICAL_LINK_GAPS.json) records them. Original prose is preserved.
- Saved constant/recommended MAEs and corrected radius errors match the claimed rounded numbers. Canonical freeze SHA-256 is `587aab56d39e6b29ad47f381c4b1440c8dd28eb52811ebc4ae3842b6fc220ce4`; completion receipt has 153,600 rows / count 1; supplementary no-repeat receipt count 0. No new final inference.
- Initial staging exactly matched the explicit allowlist; all 3,389 staged Git blobs matched working-file bytes. No blob exceeded 25 MB. Remote inspection still returns no refs after the failed push. [Remote verification](manifests/REMOTE_VERIFICATION.json) records the blocker.

## Remaining documentation and preservation gaps

External licenses/final bibliography/attribution remain incomplete; third-party payloads are withheld conservatively. Excluded bytes need independent server backup/retention and access for full reproduction. Historical absolute paths/local helper imports need adaptation in a separate reconstruction copy; environment snapshots are not universal solver locks. Historical source/operator calibration needed for physical dust precision remains missing. Four inherited missing-file links remain explicit. GitHub durability/synchronization cannot be claimed until authentication permits pushing.

After authentication is configured by the owner, the prepared repository can be pushed without rerunning science:

```sh
cd /home/bahareh/ULTIMATE
git push -u origin main
git ls-remote origin refs/heads/main
git rev-parse HEAD
```

Compare the two SHAs, then update this receipt. The archival task stops here with the prepared local commits preserved; it does not authorize new ML training, forward modeling, source-label audits, DR2 investigation or HAWK-I reduction.
