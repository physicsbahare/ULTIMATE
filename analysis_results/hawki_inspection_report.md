# HAWK-I/GRAAL NGC 3256: local data inspection
Audit date: 2026-10-26. Inputs: `HAWKI_GRAAL/NGC3256/`, local ESO query CSV and download log. No additional data were downloaded.

## Completeness and integrity
- Local query has 22 unique dp_id values; all match local FITS filenames exactly, with no missing or extra exposure files.
- All 22 files have the expected padded FITS length (about 67.27 MB each), four 2048×2048 float32 image extensions, and a primary header. A sixth HDU is the zero-row SPARTA_ATM_DATA table. Full image arrays read; finite fraction is 1.0 in all 88 images.
- All 132 raw-byte HDU CHECKSUM values validate; all 132 DATASUM values validate (including empty data HDUs). No evidence of truncation or pixel-data corruption.
- Important parser diagnostic: `ESO DET CHIP PXSPACE` uses a nonstandard value string. Astropy normalizes the card **in memory** when parsing and reports four CHECKSUM failures per file, even though DATASUM passes. Independently summing each unchanged on-disk HDU byte range returns the FITS one's-complement checksum 0xffffffff in every case. Metadata preserves both the in-memory failures and raw-byte success. Original headers were not rewritten. Script reads are readonly.
- The download log ends with “Done!”. The byte-level audit is stronger evidence of completed downloads than filenames/logs alone.

## Acquisition and calibration metadata
Programme 60.A-9475(A), target NGC3256, Ks + OPEN; all SCIENCE/OBJECT/IMAGE, no ESO PRO pipeline-history keywords. There are 14 exposures on 2018-01-03 UTC and 8 on 2018-01-06 UTC. The directory contains no reduced stacks, weight/variance maps, darks, flats, standard-star products or bad-pixel masks. Four-chip plus AO-table structure, acquisition filenames and absence of reduction provenance identify these as **raw detector frames**, consistent with [ESO pipeline format documentation](https://www.eso.org/observing/dfo/quality/HAWKI/pipeline/pipe_gen.html).

DIT is 1.7 s, NDIT is 18, EXPTIME is 1.7 s; effective duration per stored co-average is 30.6 s. Archive query exposure=30.6 s agrees with DIT×NDIT. The nominal sum is 673.2 s. Offsets and chip gaps require an exposure map before quoting on-target depth. Raw pixel values are co-averages, not accumulated counts for the full DIT×NDIT duration; avoid multiplying the raw signal by the total duration as if it were a rate. Verify the pipeline's rate normalization in reduced products. [ESO raw-data exposure convention](https://archive.eso.org/eso/eso_archive_help.html).

Header instrument pixel scale=0.10643 arcsec/pixel. Extension CD matrices are present; registration and distortion still need calibration. Native detector dimensions are 2048×2048 for each of four chips; they are not a single continuous 4096×4096 sky image. BUNIT is absent; previews say raw counts, not calibrated surface brightness. `ESO DET CHIP GAIN` is 1.0 in the inspected raw header; do not assume that this is a validated physical electron/ADU calibration. The header saturation level is 25,000. Confirm gain, nonlinearity, saturation and read noise against calibration products and readout configuration.

AO high-order and jitter-loop flags are true in all 22 files; tip-tilt-loop flag is false. This establishes recorded loop status, not the final PSF. Requested `ESO OBS AMBI FWHM`=0.3 arcsec is a constraint, not a measured image width. Ambient DIMM start/end values span 0.27–1.54 arcsec; guide-camera FWHM spans 0.57–1.28 arcsec. Neither should substitute for the Ks image PSF. [ESO distinguishes seeing from focal-plane image quality](https://www.eso.org/observing/etc/doc/helphawki.html).

## Provisional empirical image widths
SEP estimates 64-pixel local backgrounds and detects at 8× local RMS, minimum 8 connected pixels. Candidate cuts: unflagged detection, roundness b/a≥0.85, SEP size 1<a<6 pixels, separation >35 pixels, >20-pixel edge clearance, raw cutout peak ≤20,000 and background-subtracted peak >30× global background RMS. Fit a circular Moffat plus constant on a native 31×31 pixel cutout, with free centroid, amplitude, alpha and beta. FWHM = 2 alpha sqrt(2^(1/beta)−1). Retain converged fits with 2<FWHM<15 pixels, 1.21<beta<9.8 and RMS model residual/amplitude <0.04. These are explicit exploratory quality cuts, not an optimal or complete star selection.

Accepted: 677 compact-source detections across 22 frames; repeated detections are not unique stars. Per-exposure medians span 0.258–0.417 arcsec. All-candidate median is 0.329 arcsec, interquartile range 0.274–0.377 arcsec. This spread is **not a confidence interval**. Circular fits, uncorrected flat fields/artifacts, selection toward round objects, lack of catalog-confirmed stellar identities, and finite pixel integration can bias the widths. Refit isolated catalog-confirmed stars with elliptical pixel-integrated Moffat or empirical PSFs after reduction, across chips and field position, and measure final-stack PSF separately. Six inspected examples are plausible stellar profiles; that inspection does not certify all fits. HAWK-I resolution of 0.2 arcsec is not assumed.

Per-exposure measurements:

| filename | psf_candidate_count | psf_candidate_median_arcsec | psf_candidate_min_arcsec | psf_candidate_max_arcsec |
| --- | --- | --- | --- | --- |
| HAWKI.2018-01-03T08:22:19.465.fits | 27 | 0.3831 | 0.3508 | 0.432 |
| HAWKI.2018-01-03T08:23:49.797.fits | 25 | 0.3988 | 0.3801 | 0.4538 |
| HAWKI.2018-01-03T08:25:16.602.fits | 23 | 0.4172 | 0.3898 | 0.4619 |
| HAWKI.2018-01-03T08:28:01.919.fits | 31 | 0.3842 | 0.353 | 0.4192 |
| HAWKI.2018-01-03T08:29:28.736.fits | 25 | 0.393 | 0.3658 | 0.4473 |
| HAWKI.2018-01-03T08:30:59.055.fits | 29 | 0.355 | 0.2998 | 0.3788 |
| HAWKI.2018-01-03T08:32:29.380.fits | 27 | 0.4049 | 0.3591 | 0.4694 |
| HAWKI.2018-01-03T08:33:59.699.fits | 36 | 0.3501 | 0.322 | 0.395 |
| HAWKI.2018-01-03T08:38:05.077.fits | 23 | 0.3935 | 0.3642 | 0.4453 |
| HAWKI.2018-01-03T08:39:36.396.fits | 24 | 0.3768 | 0.3301 | 0.3978 |
| HAWKI.2018-01-03T08:42:34.810.fits | 29 | 0.3401 | 0.3129 | 0.3781 |
| HAWKI.2018-01-03T08:44:05.107.fits | 24 | 0.3596 | 0.3262 | 0.4023 |
| HAWKI.2018-01-03T08:45:18.811.fits | 23 | 0.3319 | 0.2932 | 0.3584 |
| HAWKI.2018-01-03T08:46:49.130.fits | 26 | 0.3306 | 0.2846 | 0.3676 |
| HAWKI.2018-01-06T08:25:19.803.fits | 38 | 0.2641 | 0.2187 | 0.2824 |
| HAWKI.2018-01-06T08:26:50.126.fits | 39 | 0.274 | 0.25 | 0.2978 |
| HAWKI.2018-01-06T08:28:16.891.fits | 48 | 0.2843 | 0.2423 | 0.3107 |
| HAWKI.2018-01-06T08:29:44.701.fits | 32 | 0.2788 | 0.2481 | 0.3004 |
| HAWKI.2018-01-06T08:31:12.560.fits | 42 | 0.2585 | 0.2223 | 0.2943 |
| HAWKI.2018-01-06T08:32:42.920.fits | 38 | 0.2584 | 0.2266 | 0.3091 |
| HAWKI.2018-01-06T08:34:09.695.fits | 33 | 0.2697 | 0.2337 | 0.2935 |
| HAWKI.2018-01-06T08:35:37.495.fits | 35 | 0.2619 | 0.2338 | 0.2967 |

## Preview and required reduction
`figures/hawki_raw_preview.png/.pdf` displays the first valid exposure in four separate chip panels, 4×4 means only for display. It is not astrometrically mosaicked, sky-subtracted, flat-corrected or flux-calibrated. Visible illumination patterns, stripes, blemishes and gradients reinforce the need for reduction. `hawki_psf_diagnostics.*` shows compact-source cutouts and fitted half-maximum contours.

Before quantitative surface brightness/colour work:
1. Associate same-configuration DIT/read-mode darks, Ks twilight flats, confidence/bad-pixel masks and nonlinearity information. Check persistence, saturation, crosstalk and illumination corrections.
2. Construct time-local, source-masked sky estimates using the offset sequence, carefully masking the extended galaxy. Check whether independent off-target sky is needed; all 22 local files are OBJECT, so none is independently established as a dedicated blank-sky calibration.
3. Correct distortion and refine astrometry with external reference stars. Register chips/exposures, track sky footprints and dither gaps, reject artifacts, and propagate variance/weights and correlated resampling noise.
4. Establish a photometric zeropoint/extinction calibration using standards or suitable 2MASS stars, accounting for passband/colour terms, magnitude system and aperture corrections. Validate sky residuals and surface-brightness uncertainty.
5. Measure native-frame and final-stack PSFs with spatial/time dependence; decide whether to retain separate seeing groups rather than degrade the best frames with a broad stack.

These steps follow the available [ESO calibration recipes](https://www.eso.org/observing/dfo/quality/HAWKI/pipeline/recipe_calib.html). Calibration association and a full reduction were not executed because the necessary local calibration data are absent. No uncalibrated science stack was promoted to a scientific product.

## Suitability
Suitable now for a labelled raw morphology preview and provisional sampling/width diagnostics. Suitable after reduction for studying real NIR sky/artifacts, PSF variation and matched-resolution morphology. Not sufficient alone for an attenuation map or dust-geometry truth: only Ks data are locally available and there is no dust-free counterpart. NGC 3256 and TNG294866 are different systems; no object-by-object match is claimed. Additional registered optical/NIR imaging and independent dust constraints would be needed. Smoothing or binning can only degrade original resolution; a sharper ULTIMATE prediction must start from adequate-resolution simulations, not from sharpening HAWK-I.

Machine-readable evidence: `hawki_metadata.csv`, `hawki_detector_metadata.csv`, `hawki_psf_candidates.csv`, `hawki_psf_per_exposure.csv`, `hawki_headers.json`, `hawki_completeness.json`; rerun `inspect_hawki.py` in the recorded phd environment.
