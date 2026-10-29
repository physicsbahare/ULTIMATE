# Authenticated DR2 catalogue investigation

Checked 2026-10-26 using the existing local API credential (never copied into outputs).

- Authenticated `https://www.tng-project.org/api/TNG50-1/snapshots/99/subhalos/294866/` returned subhalo metadata. Its `supplementary_data.skirt_images` links identify the older SDSS/POGS image products; none identifies TSA DR2.
- Following the atlas link in the published specifications, authenticated `https://www.tng-project.org/api/TNG50-1/files/skirt_atlas/` returned 1154 archive URLs, including `http://www.tng-project.org/api/TNG50-1/snapshots/99/subhalos/294866/skirt/skirt_atlas.tar.gz`. This does not identify DR2. Existing local FITS have DR1 characteristics (1600², 160-kpc field, five views), so that endpoint is not relabelled.
- Authenticated `https://www.tng-project.org/api/TNG50-1/files/` lists the older SKIRT image and integrated-SED categories. It exposes no DR2-specific or release-labelled atlas entry.
- The downloaded specifications page describes 18 broadband filters, 160-kpc field and five orientations, and links Baes et al. 2024. It provides no release-specific DR2 broadband download location.

The [DR2 paper, §3.3](https://arxiv.org/html/2608.01908v1#S3.SS3) states that broadband images/catalogue are distributed via IllustrisTNG and spectral cubes are on request. That statement alone does not establish an exact API endpoint. **Exact DR2 broadband download location remains unverified.** No guessed endpoint was downloaded or HEAD-probed as a purported DR2 dataset. No image archive was retrieved in this investigation. The saved metadata/listings are the audit evidence; contact the atlas/data-release team for the release-specific catalogue URL or consult an updated authenticated catalogue when published.

The DR2 paper also documents a dust-allocation issue affecting a subset of DR1 galaxies. This does not establish that 294866 is affected; it is an additional reason to validate against DR2 before a population-level physical interpretation. The current experiment is explicitly conditional on the existing DR1 realization.

Evidence: `sources/tng_subhalo_metadata.json`, `sources/tng_catalogue_probe_0.txt` (atlas listing), `_1.txt` (file categories), `_2.txt` (specifications), and `tng_catalogue_probe.json`. Read-only metadata requests only.
