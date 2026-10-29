# Instrument and data archival review

Review scope: documentation/code/metadata inspection only on 2026-10-29. No scientific calculation, reduction, network request, download, notebook execution or verification rerun was performed. The pass statements below describe saved receipts, not a fresh independent rerun. Paths are relative to `/home/bahareh/ULTIMATE` unless absolute.

## Status that the archive must preserve

- **Completed:** raw NGC3256 inventory/integrity and exploratory PSF inspection (Oct26); discovery of official reduced products, certified CalSelector cascades and bounded Jan6 reduced cutouts/empirical diagnostics (Oct27); expanded M4-offset reduced-image PSF/background characterization and executed notebook (Oct28).
- **Not completed:** fresh local raw HAWK-I reduction; raw per-star nonlinearity histories; independent absolute photometric/astrometric calibration; a robust R32/galaxy-scale blank-sky law; instrument-specific ULTIMATE validation; any M4 model injection into mocks or new ML evaluation. These are limitations/future studies, not missing deliveries from the completed empirical characterization.
- The Oct26 root report says no local calibration/reduced products and asks for reduction. That describes its original local inputs, not current archive-wide availability. Oct27 explicitly establishes available reduced products and complete archive calibration associations. Do not repeat “archive calibrations missing” as current fact.
- M4 `completion_audit.json` records status pass, nine executed code cells, 965 selected measurements, 276 matched rows/244 Gaia identities, 54.8956 MiB ancillary transfers. Its saved HTML was exported and figures inspected; browser layout was not tested.

## NGC3256 empirical evidence and chronology

### Original raw frames

Evidence: `analysis_results/hawki_inspection_report.md`, `hawki_completeness.json`, `hawki_metadata.csv`, `hawki_detector_metadata.csv`, `hawki_headers.json`, `hawki_psf_candidates.csv`, `hawki_psf_per_exposure.csv`; sources `HAWKI_GRAAL/NGC3256/query_results.csv`, 22 FITS and `HAWKI_GRAAL/logs/ngc3256.log`.

Programme 60.A-9475(A), Ks/open, 14 exposures 2018-01-03 and 8 on 2018-01-06. All 22 expected IDs match files, four 2048² float32 image extensions per file, finite fraction 1 in all 88 image planes. Saved audit records 132/132 raw-byte HDU CHECKSUM and 132/132 DATASUM passes. Astropy's in-memory normalization of nonstandard PXSPACE cards produced apparent checksum warnings; original disk bytes passed and were not rewritten. This parser issue must not be described as corrupted input or a repaired file.

DIT 1.7 s, NDIT18: 30.6-s effective coaverage, nominal summed duration 673.2 s; not uniform on-target depth. Raw EXPTIME 1.7 s and absent BUNIT are not ADU/s or electrons. Pixel scale header 0.10643 arcsec/pixel. Header gain1.0 and saturation25000 are unvalidated configuration metadata. Requested seeing0.3 arcsec is not a measured PSF; DIMM0.27–1.54 and guide-camera0.57–1.28 arcsec are different measurements. Recorded HO/jitter loops true, tip-tilt false.

Raw exploratory circular Moffat fits: 677 detections (not unique stars), overall median0.329 arcsec, IQR0.274–0.377, exposure medians0.258–0.417 arcsec. No catalog identity, reduction, calibrated depth, flux or dust truth follows. The four-raw-frame elliptical subset subsequently had36 accepted candidates and median0.2724 arcsec; different cuts/frames explain why these summaries cannot be pooled.

### Official reduced Jan6 product and actual dependency resolution

Evidence under `analysis_results/ml_feasibility_20261027/hawki/`: `hawki_empirical_calibration_report.md`, `reduced_download_log.json`, `calibration_association_manifest.csv`, individual CalSelector trees, Datalink tables, `local_fits_inventory.csv`, `reduced_psf_spatial_bins.csv`, `empirical_model_inputs.json` and diagnostics.

Official ObsCore returned12 related records, three tiles/three pawprints/six catalogues, observing-block groups8/6/8 inputs and nominal244.8/183.6/244.8 s. CalSelector for one exposure in each of three OBs returned certified=true, complete=true, Raw2Master. Masters include dark, twilight flat, confidence, readgain, photcal, 2MASS astrometric/photometric references, Schlegel maps and standard-related products. No short-window Ks flat in a January query does not imply shortage: actual reduction used a December25 flat. Local EsoRex/CPL/HAWKI recipes and master/static images remain absent, so a new local reduction was not performed; reduced archive products exist.

Final target-centered science/variance/confidence cutouts are2364² around (156.96365,-43.90355) deg, radius0.035deg. Their total67,299,840bytes (64.18MiB); replaced first centering doubles actual transfer128.36MiB. Products:

- image ADP.2018-02-14T09:20:46.500 → `reduced_jan6_image.fits`
- variance ...46.501 → `reduced_jan6_varmap.fits`
- relative confidence ...46.502 → `reduced_jan6_weightmap.fits`

Saved checksums/datasums all pass, grids agree <1e-9pixel; hashes/exact SODA URLs retained in download log. BUNIT ADU; PHOTSYS VEGA, FLUXCAL ABSOLUTE, PHOTZP26.298326, PHOTZPER0.182821mag, CASUEXPT30.6s, EXPTIME244.8s, pipeline2.4.1, QCFLAG0000000. These are pipeline metadata, not independent external calibration. Variance operationally means ADU² despite inherited BUNIT ADU. Confidence is relative weight, not inverse variance. WCS scale0.10659569arcsec/pixel; background pedestal~1983.499ADU is not physical residual sky brightness.

103/109 accepted compact candidates, not all validated stars: circularized FWHM median0.3166arcsec/IQR0.2920–0.3329, q0.8199, beta4.753; pipeline FWHM0.302691 is another estimator. Finite-fit Moffat D50/R80 extrapolations are not measured circular growth radii. More defensible later same-estimator comparison of nine quality-selected 2MASS stars gives FWHM~0.2942arcsec,q~0.855,beta~3.92, finite-R2 empirical R50~0.200arcsec (`analysis_results/hawki_m4off_20261028/ngc3256_same_estimator.csv`). Neither later sample invalidates the preserved earlier candidate summary.

Earlier reduced noise diagnostic: robust pixel sigma1.8397ADU, sqrt propagated variance3.1570ADU, normalized robust width0.529; rho_x0.2753/rho_y0.2932. Radius2/4/8/16/32pixel aperture excess over pixel-MAD white scaling1.5705/1.7061/2.1833/2.7873/3.4213. Applies to that mask/mesh/cutout only; 500 random centers may overlap. Do not force variance normalization to unity or mix this with the later same-operator results below.

## M4-offset completed characterization

Authoritative narrative/protocol: `analysis_results/hawki_m4off_20261028/scientific_report.md`, `protocol.md`, `README.md`; numerical source tables below. Same Ks band and a different scene, not a matched observation of NGC3256 or a ULTIMATE measurement.

Inputs `data/HAWKI_M4off_2019/ADP.2021-12-16T10_45_25.739.fits` (four-plane pawprint) and `...26.018.fits` (single tile). Same28 raw IDs in both, programme0103.D-0061(C), 2019-08-20T23:31:15.4187 to last start2019-08-21T00:17:04.296, DIT10s,NDIT6,total header1680s with variable coverage. UT4 HAWK-I GRAAL AO_IMG, pipeline2.4.7. Both are reduced/resampled products; pawprint versus tile is not raw versus resampled. Extension order CHIP1,CHIP2,CHIP4,CHIP3. Headers snapshot loop states, not uptime of all28 exposures.

`input_integrity.json` records:

| Product | Bytes | SHA256 |
|---|---:|---|
| pawprint ...25.739 |632062080|c80e5a9726688c105cba8e19f7a4e81503b1d5ba79e6b13ecef6b30bd55ece7e|
| tile ...26.018 |287801280|b7258f2cbe60dfb97e9c64672a009b0bee16c67bb258f2cca4aee98b6e8e81c7|

Saved original checksum/datasum passes in all6 HDUs. WCS self-roundtrips<1e-6pixel and ancillary alignment<1e-5pixel do not prove absolute astrometry. Unit ADU, Vega; PHOTZP28.044921 pawprint/28.085096 tile, PHOTZPER0.0485/0.2760mag. Released count convention m=ZP−2.5log10(flux)−aperture correction; do not divide by1680 again. Variance operational ADU², confidence relative and may exceed100. Ancillary54.90MiB consists of source catalogue, tile/pawprint small variance-confidence cutouts and capped Gaia query, not raw/full-map downloads. URLs/sizes/hashes: `ancillary_download_log.json`, `ancillary_integrity.csv`, `ancillary_grid_checks.csv`. Source and calibration identities: `fits_provenance.csv`, `raw_provenance_ids.csv`, `calibration_reference_manifest.csv`.

### PSF, identities, floors

`science_star_table.csv`, `PSF_summary.csv`, `PSF_spatial_cells.csv`, `empirical_profiles.csv`, `EE_uncertainty.csv`: conservative Gaia/ESO validated primary candidates, 41² plane+elliptical Moffat fit integrated3×3 subpixels. FWHM is geometric mean pre-pixel major/minor model widths. Fainter selection peak<5000ADU above sky and local core<22000 product ADU; it reduces risk without proving raw linearity.

| Plane | Stars/clean wings | FWHM arcsec [95% spatial CI] |q|beta|finite-R2 R50/R80 arcsec|
|---|---|---|---|---|---|
|pawprint1|158/18|0.2925 [0.2823,0.3025]|0.916|2.84|0.206/0.383|
|pawprint2|118/4|0.3200 [0.3120,0.3290]|0.873|3.28|0.214/0.386|
|pawprint3|164/19|0.2946 [0.2906,0.3036]|0.874|3.02|0.207/0.384|
|pawprint4|169/12|0.2982 [0.2915,0.3033]|0.833|3.02|0.205/0.376|
|tile0|356/45|0.3032 [0.3005,0.3070]|0.874|3.02|0.209/0.386|

Counts repeat stars across products. CIs condition on these fields and selections, not total instrumental/temporal uncertainty. `matched_stars_primary.csv`/`paired_changes.csv`:276 pairs/244 unique Gaia IDs; repeated pawprint identity averaged before global median. Tile−pawprint global FWHM+0.00077arcsec spatial CI[-0.00005,+0.00329]: no robust global sharpening/broadening. Extension3 nominal positive difference omits model floors/multiple testing. Preserve Gaia IDs as integers, not rounded floats; local IDs differ between broad/faint passes and cannot identify the same star across passes.

Gaia capped25000 references, G faintest~19.731, propagated2016→2019.635; absent association is not evidence against stellar identity. Tile image−Gaia offset(+0.235,+0.416)arcsec; registered residual median0.039arcsec. Possible old-2MASS epoch contribution is interpretation, not proven historical cause.

`quadrature_sensitivity.csv`: independent11×11 integration grid finds maximum3×3-fit width bias0.0018arcsec/0.82%, with one undersampled q error0.058. Fit-window shifts~0.0004–0.0009arcsec; brightness matched-cell shifts~0–0.0017. Floors outside bootstrap CIs preclude precision milliarcsecond transfer claims. QCFLAG10000 padded0010000 is nonlinear-pixel warning. Conservative cuts and final removal of eight flat-core pawprint measurements do not recover raw per-source linearity histories; this remains unresolved.

Finite growth retains signed sky subtraction,1.8–2.5arcsec sky annulus, references R1.5/R2arcsec and first crossings without artificial monotonicity. Clean wings are sparse, especially four stars in detector2. Moffat tails beyond measured2arcsec are extrapolations; core+halo fits are phenomenological, not scattered-light measurements. Detector2 halo optimum reaches3arcsec boundary with RMS~0.011; others~0.002–0.004. No unique infinite PSF/optical deconvolution/halo fraction is established.

### Noise and explicitly rejected inference

Evidence: `background_regions.csv`, `background_covariance.csv`, `aperture_noise.csv`, `aperture_samples.csv`, `aperture_noise_uncertainty.csv`, `confusion_*.csv`, `same_operator_noise_summary.csv`, `ngc_noise_*.csv`.

Same operator (mask growth/mesh aligned) median results:

|Field|rho_x1/rho_y1|R2/R4/R8/R16 excess|
|---|---|---|
|M4 tile|0.371/0.354|1.73/2.64/4.60/6.53|
|NGC3256|0.265/0.292|1.41/1.66/1.88/1.98|

Excess=aperture MAD/(pixel MAD sqrt(Npixels)), dimensionless and dependent on mask/mesh/coverage/population. M4 ancillary-only R16~7.34, extra faint-catalogue masking~5.37: unresolved stellar light and sky residuals materially contribute. These fields have different depths and populations, not isolated instrumental-noise controls. Hundreds of overlapping aperture centers are not independent realizations. AtR32 only11–23 geometrically nonoverlap grid apertures per plane, often1–2 in ancillary regions; correlation further limits independence. R32 is rejected and excluded from models. Large-scale falling MAD is not a calibrated low-noise law.

`sensitivity_models/README.md`:15 positive unit-sum129pixel finite analytic Moffat kernels; five core+halo finite-growth sensitivity templates; joint FWHM/q/beta/orientation samples; five local unit-L2 positive covariance filters; five PSD nonnegative variance-mixture total-background stresses. Local filters pass saved independent Gaussian-realization response checks, but total-background response discrepancies remain13–37%, noR32 constraint. Broad stresses include confusion, not unique detector/resampling noise. Preserve angular sampling and joint parameters, re-integrate on future rendering grid and check aperture response after resampling; set amplitude from future observing model rather than observed ADU. Do not double-convolve covariance, omit source Poisson noise, or present model extrapolations as empirical infinite-radius measurements. No actual mock injection/ML usage here.

## ULTIMATE assumptions, observations and limitations

Evidence: `analysis_results/screen_test_20261026/instrument_audit.md`, `instrument.py`, `instrument_parameters.csv`, `instrument_bandpasses.npz`, `sources/pinned_source_manifest.json`, `sources/curve_download_manifest.json`; `analysis_results/dr1_calibrated_screen_20261026/instrument_provenance.md`.

Calculator repo https://github.com/sali131/ULTIMATE-Subaru-Sensitivity-Calculator pinned2187748a40d4207519a8eff0d2a5b6701db8da0d. Forward methods https://github.com/physicsbahare/astro-forward-modeling pinned78dce5ad96038fe7a702d3e2f2b434a2c7d7e8af. Source files have bytes/SHA256/Git blob SHA1; original calculator unchanged defaults were executed in prior work, not this review.

Design defaults:8.0819m diameter,0.277 obscuration diameter ratio,47.363744m² collecting area,0.1arcsec/pixel,RN16e,throughput0.45,mirrors0.95×0.98,PWV1.6mm,airmass1,T273K. MOIRCS/SWIMS/custom centers/widths are proxy filters, not measured ULTIMATE transmission curves. NIR median D50 seeing/GLAO J0.658/0.508,H0.624/0.446,Ks0.588/0.390arcsec. Gaussian primary assumption makes D50=FWHM; equal-D50 Moffat beta2.5 instead has FWHM/D50=0.737519. Optimistic0.2arcsec remains separate assumed scenario. Neither raw0.329/reduced~0.294–0.317arcsec HAWK-I measurements nor AO flags validate ULTIMATE performance.

Prior unchanged calculator one-hour5sigma point-source AB limits: Y25.337/25.115,J25.206/24.924,H24.837/24.471,Ks25.164/24.716 GLAO/noAO; D50 aperture/50% flux/background-dominated approximation, not surface-brightness limits. Local baseline corrected original one-RN²-for-whole-integration treatment to Nread×RN² (DIT60s), included source/sky/thermal/moon/dark Poisson terms and obscuration-consistent diffuse sky/moon area. NIR dark0.01e/s/pixel is provisional. H background~58ke/pixel/read makes operational DIT/fullwell/nonlinearity unverified. Moon conditions unknown; telescope thermal model is not a separate measured cold-instrument emission specification.

Optical griz0.7arcsec Gaussian,throughput0.35×0.9,RN5e,dark0.001e/s/pixel,skyAB22/21/20.3/19.5 are analyst complementary-imaging scenarios, held fixed across seeing/GLAO; not an optical ULTIMATE capability. Main exposure1h/band×7=7on-source hours before overhead;0.25/4h sensitivities. Known-mean-sky model omits unknown flat/persistence/sky-estimation/dither/weather/resampling/operational floors. Recorded numerical tests validate bounded implementation moments, not those unknown systematics. Broadband-only DR1 cannot support medium/narrow-band line forecasts; rest/observer-band support limits especially shifted Ks atz0.3 remain.

## Simulation provenance and rights/access uncertainty

TNG50-SKIRT DR1 citation Baes et al.2024 A&A683 A181, DOI https://doi.org/10.1051/0004-6361/202348418; methodology https://arxiv.org/html/2401.04224v1. Dataset route in `TNG50_SKIRT/download_one.py`: `https://www.tng-project.org/api/TNG50-1/snapshots/99/subhalos/{sid}/skirt/skirt_atlas.tar.gz`, local initial archive `TNG50_SKIRT/downloads/TNG50_DR1_294866.tar.gz`. Credential required by script; its actual value was never read in this review. Legacy downloader checks filename existence and unexpected content type, streams partial then renames; existence alone is not its own full-integrity proof. Later downloader documentation describes stronger CRC/tar/SHA256/expected-size checks.

Original pilotO1 five selected FITS in `TNG50_SKIRT/pilot_294866/`;20 O2–O5 files extracted to `analysis_results/extracted_294866/`. `analysis_results/inspect_inputs.py` streams the existing archive and selects exactly20 basename matches, writing manifests and skipping preexisting extraction outputs; it is an output-writing extraction script, not pure validation. `archive_inventory.json`, `extraction_manifest.json`, `input_inventory.json`, `tng_input_validation.csv` retain provenance/SHA256/zero counts/units for25 selected inputs. Images1600²,100pc/pixel,160kpc field,brightnessMJy/sr,dust surface densityMsun/pc²; no physical observer distance follows from the FITS scale and100pc sampling is not100pc independent physical resolution. Five orientations are same galaxy; nodust is a simulation counterfactual absent in real HAWK-I. No error maps/component separation isolate scattering from Monte Carlo effects; negative effective attenuation is retained, not corrected to zero.

Additional-data acquisition docs `data/TNG50_SKIRT_DR1_extra/README.md`: official Baes24 catalogue1154 distinct galaxies,25 seed20261026 mass/activity-balanced selections, no morphology class or disk-only claim; actual state/selection manifests under that tree and copied in `analysis_results/ml_expanded_20261028/data_audit/`. Expansion archives under `data/TNG50_SKIRT_DR1_ml_expansion/`. Later downloader verifies expected bytes,gzip CRC/full tar payload,SHA256 and validators; protects credentials across API→data-eu hostname redirect, does not save signed URLs. API keys/signed URLs are access material, not archival metadata to publish. Selection strata and deliberately balanced feasibility sample should accompany any reuse.

External source copies also include EAZY/FSPS templates commitf651e94d91042a84906090a66d2a3fec75504e21 (`sources/eazy/templates/README`, pinned manifest), Gemini-derived Mauna Kea atmospheric/sky/moon curves bundled with calculator, forward-repository methods/code. No license file was found in the inspected source copies; README/pinned hashes prove origin, not redistribution rights. Local presence, public retrieval and publication citation do not establish a blanket redistributable license. Rights/terms for TNG original archives, ESO products/catalogues/Gaia/2MASS and third-party code/template/sky content are not archived as verified terms in the reviewed material. Mark redistribution **unverified**, preserve original attribution/provenance, and avoid asserting CC-BY/MIT/public-domain status. This is a documentary gap, not a claim that reuse is prohibited; no current rights determination was attempted.

ESO source attribution: https://doi.eso.org/10.18727/archive/34 and release https://www.eso.org/rm/api/v1/public/releaseDescriptions/87. Raw conventions https://archive.eso.org/eso/eso_archive_help.html; calibrations https://www.eso.org/observing/dfo/quality/HAWKI/pipeline/pipe_calib.html. DataLink/catalogue URLs are retained locally; example public M4 catalogue https://dataportal.eso.org/dataPortal/file/ADP.2021-12-16T10:45:25.815. Gaia/2MASS are calibration-reference families, not independent dust truth; the existing 2MASS match is also pipeline-reference-family consistency, not independent absolute calibration.

## Reproduction instructions from saved docs and inspected code (not executed)

Existing interpreter `/home/bahareh/miniforge3/envs/phd/bin/python`, project root `/home/bahareh/ULTIMATE`; no installation required for saved diagnostics. M4 saved environment Python3.12.15,NumPy2.5.4,pandas3.0.6,SciPy1.18.1,Astropy8.0.2,SEP1.4.1,Matplotlib3.11.2,nbformat5.11.1,nbclient0.11.0 (`verification.json`). These are saved environment facts, not fresh probes.

Archive review should read artifacts. Reproduction writes outputs; use a separate copy with original source paths retained, not overwrite archived evidence. M4 routines use script-relative analysis root; `provenance_audit.py` rewrites provenance CSVs, verifies same28 raw IDs/checksums/WCS and hashes cached ancillaries. Fetch scripts are acquisition history only; cached/offline reproduction need not call them.

Documented M4 sequence:

1. `provenance_audit.py`, `extract_instrument_configuration.py`.
2. `measure_psf.py` broad selection (skips existing per-plane source tables); preserve broad source/profile/stamp/audit products.
3. `measure_fainter_sample.py` conservative extraction/promoted primary tables; copy its detection audit to top level, preserve previous audit separately.
4. `measure_noise.py`, `analysis_refinements.py`, `confusion_stress.py`, `compare_ngc3256.py`, `compare_noise_ngc3256.py`.
5. `validate_stars.py`, `fit_sensitivity.py`, `build_models_and_figures.py`, `noise_model_validation.py`.
6. `finalize_diagnostics.py`, `summarize_uncertainties.py`, `quadrature_check.py`, `fit_growth_sensitivity.py`.
7. `write_report.py`, `verify_results.py`, `make_notebook.py`, `execute_notebook.py`, `seal_deliverables.py`.

Every script prefix is `analysis_results/hawki_m4off_20261028/`. Routine saved-results reproduction is `verify_results.py` then `execute_notebook.py`. Inspected executor creates `/tmp/hawki_m4_jupyter/kernels/hawki-phd` using current interpreter, executes existing notebook with180s timeout/cell, validates, writes executedipynb/HTML and PNG figures. Needs local kernel sockets; no external service. `make_notebook.py` clears execution by rebuilding scaffold and must be followed by execution. Both are mutations, not appropriate for this read-only review.

NGC3256 scripts under `analysis_results/ml_feasibility_20261027/hawki/`: query_archive/query_raw_fixed/query_calibrations and fetch_reduced_cutouts are provenance/acquisition steps; diagnose_reduced/diagnose_raw are original measurement scripts, summarize_archive etc build reports. Historical tap_raw404 retained; successful raw queries used tap_obs. Do not rerun network acquisition merely to review completed evidence.

Root `analysis_results/README.md` specifies inspect_inputs.py,inspect_hawki.py,nbconvert execute pilot_reproduced and TNG294866_five_orientations,write_reports.py in existing phd environment. `inspect_hawki.py` resets metadata CSV; report writer reattaches per-exposure widths. `build_notebooks.py` rebuilds unexecuted notebooks. These are reproduction instructions, not nonmutating archive checks. Root and M4 verification receipts and archived hashes must remain preserved during documentation work.
