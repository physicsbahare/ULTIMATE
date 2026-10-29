# Data provenance and server-only holdings

Inventory verified **2026-10-29** at `/home/bahareh/ULTIMATE`. The recursive baseline contains **9,367 files / 89,335,515,275 bytes** including the installed HAWK-I environment; 4,430 files outside that environment. Directory-size tools round this to about 84 GiB. No original data or scientific output was modified.

The authoritative file-level ledger is [FILE_INVENTORY.csv](manifests/FILE_INVENTORY.csv). Every row records relative and absolute server paths, exact byte size, format, category, disposition/reason, original modification time and SHA-256 where computed. [EXCLUDED_FILES.csv](manifests/EXCLUDED_FILES.csv) lists every excluded scientific file as well as runtime/environment files. Empty checksum cells mean **not computed**, not failed integrity. Historical checksum receipts are indexed in [EXISTING_CHECKSUM_RECORDS.md](manifests/EXISTING_CHECKSUM_RECORDS.md); preserve their original semantics. Full raw-file hashing was not repeated for this archival task.

| Holding | Local location | Origin / content | Units and access |
|---|---|---|---|
| Initial TNG50 DR1 atlas | `TNG50_SKIRT/downloads/` | Galaxy 294866, official TNG50-1 snapshot99 SKIRT atlas | API credential required by downloader; never published |
| Extracted original pilot | `TNG50_SKIRT/pilot_294866/`, `analysis_results/extracted_294866/` | O1 and O2–O5 selected broadband/dust maps | 1600²; 100 pc/pixel, 160 kpc field; MJy/sr images, Msun/pc² projected dust |
| Extra DR1 sample | `data/TNG50_SKIRT_DR1_extra/` | 25 selected additions to original pilot; seed 20261026, mass/activity strata from 1,154-galaxy catalogue | Full downloaded tar/FITS held locally; selection/download records uploaded |
| Expanded DR1 sample | `data/TNG50_SKIRT_DR1_ml_expansion/` | Frozen 120-galaxy project partition; source archives and acquisition receipts | Galaxy IDs and checksums retained; archive access needed for full image reproduction |
| Prepared analysis images | `analysis_results/**` | Matched scenes, observation arrays, attenuation maps, feature/label caches | Per-file disposition; small diagnostic arrays included, bulk images/caches server-only |
| NGC3256 raw | `HAWKI_GRAAL/NGC3256/` | 22 ESO HAWK-I exposures, programme 60.A-9475(A), January 2018 | Four 2048² detector planes/exposure; raw BUNIT absent; EXPTIME is DIT, not calibrated ADU/s |
| NGC3256 reduced cutouts | `analysis_results/ml_feasibility_20261027/hawki/` | Official Jan6 science/variance/confidence cutouts; SODA URLs/hashes in reduced download log | ADU image, operational ADU² variance, relative confidence; Vega pipeline metadata |
| M4-offset reduced products | `data/HAWKI_M4off_2019/` | ESO programme 0103.D-0061(C), observed 2019-08-20/21; pawprint and tile, same 28 inputs | Reduced/resampled ADU, Vega; variance ADU², confidence relative, not inverse variance |
| Ancillary M4 calibration/catalogues | `analysis_results/hawki_m4off_20261028/` | Capped Gaia/ESO references, small variance/confidence cutouts, provenance | 54.90 MiB ancillary transfer recorded; catalogue selection/epoch caveats in report |
| Saved ML models | `analysis_results/*/models/` and other manifest paths | 318 project `.joblib` artifacts | Included, hashed; requires matching scikit-learn/joblib and original local-module imports |
| External method/calculator/templates | `analysis_results/screen_test_20261026/sources/` | Pinned calculator, forward code, EAZY/FSPS, sky/throughput curves | Source manifests included; downloaded third-party payloads individually excluded pending license verification |

TNG provenance: Baes et al. 2024, A&A 683 A181, DOI `10.1051/0004-6361/202348418`. Existing download route: `https://www.tng-project.org/api/TNG50-1/snapshots/99/subhalos/{id}/skirt/skirt_atlas.tar.gz`. [Downloader/readme](../data/TNG50_SKIRT_DR1_extra/README.md), [selection manifest](../data/TNG50_SKIRT_DR1_ml_expansion/selection_manifest.json), [input validation](../analysis_results/tng_input_validation.csv), [archive inventory](../analysis_results/archive_inventory.json) document exact selected files and credentials handling. The 100-pc pixel sampling is not independent physical resolution. Five orientations share the same galaxy. The no-dust counterfactual is unavailable in real imaging. Negative effective attenuation values were retained.

M4 original SHA-256 receipts ([input integrity](../analysis_results/hawki_m4off_20261028/input_integrity.json)):

| Product suffix | Bytes | SHA-256 |
|---|---:|---|
| `25.739.fits` pawprint | 632062080 | `c80e5a9726688c105cba8e19f7a4e81503b1d5ba79e6b13ecef6b30bd55ece7e` |
| `26.018.fits` tile | 287801280 | `b7258f2cbe60dfb97e9c64672a009b0bee16c67bb258f2cca4aee98b6e8e81c7` |

ESO provenance and exact original/ancillary identities are in [fits_provenance.csv](../analysis_results/hawki_m4off_20261028/fits_provenance.csv), [ancillary download log](../analysis_results/hawki_m4off_20261028/ancillary_download_log.json), [raw provenance IDs](../analysis_results/hawki_m4off_20261028/raw_provenance_ids.csv) and [calibration manifest](../analysis_results/hawki_m4off_20261028/calibration_reference_manifest.csv). Original acquisition logs and failed query records are preserved.

Public archive availability and attribution do not establish redistribution permission. No blanket data/source license was established from local records. Raw FITS, simulation archives, downloaded third-party source/template payloads and collaborator-owned data are not redistributed. Generated scientific tables/figures/reports are included after screening; original third-party source terms and final publication attribution remain documentary gaps. No confidential credentials were read for inventorying.

A clone supports inspection of claims and saved tables/models. Full image reproduction additionally requires the exact excluded files at the manifest paths, source access, historical template/calculator assets, and the recorded environment. This repository alone does not replace an independently backed-up data archive; server retention and a separate preservation copy remain necessary for excluded bytes.
