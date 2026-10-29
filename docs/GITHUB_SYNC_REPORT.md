# GitHub synchronization report

Archive date: **2026-10-29 (Asia/Taipei)**. Repository: [physicsbahare/ULTIMATE](https://github.com/physicsbahare/ULTIMATE). Initial repository metadata reported size0/default branch main; command-line remote inspection returned no refs. There were no local commits or configured remotes before initialization. No history was overwritten and no force-push is authorized.

**Status: PREPARED FOR COMMIT/PUSH.** The archive SHA, final upload outcome and remote verification will be recorded after synchronization. The final receipt references the science archive commit, rather than attempting to contain its own hash.

## Content and scientific coverage

The explicit allowlist includes **189 Python scripts plus 2 shell scripts (191 scripts total)**, **13 notebooks**, **115 Markdown reports/documents plus 11 HTML reports**, **180 figures (100PNG+80PDF)**, **1806 scientific CSV/compressed-CSV tables**, **318 saved models**,23 small diagnostic arrays,137 execution/verification logs and source/configuration/provenance records. Four additional CSV files are archive manifests rather than scientific result tables. Final Git counts and bytes are verified below after commit.

All 13 top-level result directories are indexed: attenuation_maps, extracted inputs and root figure/reproduction directories, screen_test_20261026, dr1_calibrated_screen_20261026, multiplicative_diagnosis_20261026, spatial_structure_pilot_20261026, multigalaxy_morphology_20261027, ml_feasibility_20261027, ml_expanded_20261028, ml_validation_20261028 and hawki_m4off_20261028. The exact directory names and every file are in [completed analyses](COMPLETED_ANALYSES.md) and their artifact inventories. Nested acquisition, independent verification, source-label, instrument/center/aperture, NGC3256 and supplementary integrated-Ks studies are included.

## Excluded scientific files and preservation

The baseline contains 9367 files /89,335,515,275bytes. **6026 original files are excluded individually**; 3341 originals are eligible. Exclusions include installed runtime/bytecode/transient state, raw FITS/FITS.gz, full simulation tar archives, bulk NPZ/image caches and downloaded third-party calculator/forward/template payloads without verified redistribution terms. Exact bytes, paths and reasons for every excluded scientific output: [EXCLUDED_FILES.csv](manifests/EXCLUDED_FILES.csv). Originals remain under `/home/bahareh/ULTIMATE/`; no deletion, rewrite, recompression, raw-data download or new science execution occurred.

## Fresh archival verification

[ARCHIVE_VERIFICATION.json](manifests/ARCHIVE_VERIFICATION.json) records read-only checks: all 9367 original file metadata records agree; 3,382 available original hashes agree; no selected file exceeds 25 MB; all 13 notebooks parse, contain execution counts and have zero recorded error outputs. Source AST inspection found no parse failures. The credential screen found no actual credentials; the downloader's exact `synthetic-test-key` fixture is documented as non-secret. No credential file was opened.

The headline constant/recommended MAEs and corrected radius values were checked directly against saved performance tables, and the canonical single-final receipt/freeze hash agrees. Original source/results were not executed. Saved scientific validation is distinguished from this fresh archive-only verification. New document/figure/table links resolve. Four inherited copied-JWST README links reference files absent from the original tree; [HISTORICAL_LINK_GAPS.json](manifests/HISTORICAL_LINK_GAPS.json) preserves their exact locations. Original historical prose was not rewritten to hide gaps.

## Remaining documentary/reproduction gaps

External source/data license terms and final publication attribution are not fully established; downloaded external payloads are withheld conservatively. Excluded raw/cached bytes require separate server retention/backup and access for full reproduction. Historical paths/local helper imports may need adaptation in a separate reconstruction copy; package metadata snapshots are not a universal solver lock. The exact historical source/operator calibration needed to interpret physical dust precision is missing. The four inherited absent-file links remain documented. No source precision, DR2 availability, new final holdout or measured ULTIMATE performance claim is invented.

## Commit and remote verification

Pending initial archival commit and push. Authentication/network blockers, if any, will be recorded exactly without exposing credentials. Git metadata initialization required elevated access because the workspace `.git` mount is read-only under ordinary sandbox execution; scientific content stayed in the original workspace.
