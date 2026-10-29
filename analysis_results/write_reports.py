from pathlib import Path
import pandas as pd
import numpy as np
R=Path('/home/bahareh/ULTIMATE'); O=R/'analysis_results'
s=pd.read_csv(O/'tng_orientation_summary.csv'); h=pd.read_csv(O/'hawki_metadata.csv'); p=pd.read_csv(O/'hawki_psf_candidates.csv'); c=pd.read_csv(O/'hawki_detector_metadata.csv')
ps=p.groupby('filename').fwhm_arcsec.agg(['count','median','min','max']); ps.columns=['psf_candidate_count','psf_candidate_median_arcsec','psf_candidate_min_arcsec','psf_candidate_max_arcsec']; ps.to_csv(O/'hawki_psf_per_exposure.csv')
h=h.drop(columns=list(ps.columns),errors='ignore').merge(ps,left_on='filename',right_index=True,how='left'); h.to_csv(O/'hawki_metadata.csv',index=False)
def table(frame):
 return '| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None))
t=s[['orientation','A_g_full_mag','A_ks_full_mag','rho_g','rho_ks','n_bins']].copy()
for k in t.columns[1:-1]: t[k]=t[k].map(lambda v:f'{v:.6f}')
(O/'scientific_summary.md').write_text(f'''# ULTIMATE–Subaru: Beyond the Foreground Screen
Verified pilot results prepared 2026-10-26 for the October 28 progress meeting and November 9–11 workshop.

## Actual results
The original O1 numerical results reproduce: A_g = 0.334442 mag, A_Ks = 0.020562 mag; Spearman ρ = 0.924164 and 0.548340, with the original 1,264 spatial bins. A separate notebook copy executes the original calculation and plotting code, changing only input/output locations. An Astropy-based implementation independently reproduces the pilot's custom FITS reader calculations.

Five orientations of **one galaxy**, subhalo 294866, DR1:

{table(t)}

Attenuation columns are full-frame flux ratios in magnitudes; ρ columns describe the shared pilot spatial mask. Full-frame g attenuation changes by {s.A_g_full_mag.max()-s.A_g_full_mag.min():.3f} mag and Ks by {s.A_ks_full_mag.max()-s.A_ks_full_mag.min():.3f} mag across views. Optical association is consistently strong under the original selection. Ks association is strongly view dependent: O2 is weakly negative, while O3–O5 are positive. This is a scientific finding to present with the mask definition, not a failed reproduction.

## What the measurements mean
Images are 1600×1600, 100 pc/pixel, with a 160×160 kpc full field. Brightness units are MJy/sr and projected dust surface density is M☉/pc². All 25 inputs are finite, nonnegative and have identical within-view coordinate headers. Common pixel area/solid angle cancels in the intensity ratios. We do not infer a physical observer distance from the FITS scale.

Integrated attenuation is −2.5 log10(sum I_dust / sum I_nodust), not mean pixel attenuation. Within R < 20 kpc the integrated attenuations are larger: g {s.A_g_R20_mag.min():.3f}–{s.A_g_R20_mag.max():.3f} mag and Ks {s.A_ks_R20_mag.min():.3f}–{s.A_ks_R20_mag.max():.3f} mag. This aperture dependence is included in the CSV and should accompany comparisons to observed photometry.

Statistics use 1-kpc block-mean intensities before ratios, R < 20 kpc from the image centre, positive dust surface density, both dust-free intensities >10⁻⁴ of their band-specific binned full-frame peaks, and finite attenuation in both bands. Counts vary across views because eligibility changes. Maps use 0.5-kpc block means and their own equivalent mask. The figure colour limits clip display values only; FITS maps preserve them. Sensitivity CSV covers 0.5/1/2-kpc bins, R < 10/20/30 kpc, and relative brightness thresholds 10⁻⁵/10⁻⁴/10⁻³: 27 choices per view. These are selection ranges, **not error bars**. O2 Ks ρ ranges approximately −0.843 to +0.066 over this grid. Optical ρ ranges 0.680–0.937 over the entire grid. Radius-detrended rank associations are exploratory; they do not isolate causality.

Local negative attenuation is retained. In the selected 1-kpc bins, the negative Ks fraction is {100*s.negative_fraction_ks.min():.1f}–{100*s.negative_fraction_ks.max():.1f}% by view. Scattering can enhance local brightness, and Monte Carlo noise can contribute; these files provide no error maps or component separation to determine how much of either is responsible. Faint cuts do not constitute a measured S/N threshold. We do not report independent-pixel p-values or invented uncertainties. SKIRT's stellar smoothing and simulation resolution also mean a 100-pc grid is not proof of independently resolved 100-pc physical structure. [Baes et al., DR1 methodology](https://arxiv.org/html/2401.04224v1).

The map integral gives about 3.106×10⁸ M☉ of projected dust, with a {100*(s.projected_dust_mass_msun.max()-s.projected_dust_mass_msun.min())/s.projected_dust_mass_msun.mean():.3f}% range between views. This is an internal projection consistency check, not independent dust-mass measurements or an uncertainty estimate.

## HAWK-I status
All 22 expected science exposures are present, readable, and complete by FITS block lengths. All 132 unchanged on-disk HDU checksums and all DATASUM checks pass; all 88 detector images contain finite values. Astropy's apparent checksum warnings arise after it normalizes a nonstandard PXSPACE header card in memory; no original file was repaired or modified. The explicit raw-byte checksum checks distinguish this parsing effect from corruption.

These are raw Ks exposures on January 3 (14) and January 6 (8), 2018 UTC. Each has DIT=1.7 s and NDIT=18, hence 30.6 s exposure duration; nominal total {h.dit_ndit_s.sum():.1f} s across offsets, **not** uniform integration at every sky location. No local science stack or calibrations were found. Detailed audit: [HAWK-I report](hawki_inspection_report.md).

{len(p)} accepted compact-source Moffat fits yield per-exposure medians of {ps.psf_candidate_median_arcsec.min():.3f}–{ps.psf_candidate_median_arcsec.max():.3f} arcsec at the header scale 0.10643 arcsec/pixel. These are provisional raw-frame estimates, not validated final-stack PSFs. HAWK-I can support an empirical NIR imaging comparison after calibration. It does not supply dust-free truth, a 3D dust label, or a 0.2-arcsec image to be recovered by binning/convolution.

## Safe workshop claims
- The original pilot is reproducible, with documented units, apertures and masks.
- Five views show substantial variation in effective attenuation and especially Ks–dust association for one galaxy.
- Projected dust is associated with optical attenuation in these ideal simulations, but correlation does not demonstrate unique 3D dust geometry recovery.
- HAWK-I observations exist and pass file-integrity checks; provisional image widths and calibration needs are measured/documented.
- ULTIMATE mock-observation feasibility and learning from observable colours remain **planned experiments**. No realistic-noise recovery result or ML accuracy is claimed.

Use `figures/five_orientation_maps.*`, `five_orientation_correlations.*`, and `viewing_dependence.*`; show the raw HAWK-I preview only with its uncalibrated label. See `workshop_talk_outline.md` and `workshop_10min.pdf` for a timed presentation draft.

## Reproducibility and limits
Reused `/home/bahareh/miniforge3/envs/phd/bin/python`; no installs, new environments, large downloads, or training runs. `environment.json` records versions. Both notebooks execute top-to-bottom with saved tables/plots. `pilot_reproduced.ipynb` and `TNG294866_five_orientations.ipynb` preserve original notebook/data. Only the new directory is written. HTML previews are included; PNGs and representative rendered PDFs were visually reviewed. Further experiment specifications and outstanding instrument assumptions are in [next experiments](next_experiments.md).
''')
(O/'hawki_inspection_report.md').write_text(f'''# HAWK-I/GRAAL NGC 3256: local data inspection
Audit date: 2026-10-26. Inputs: `HAWKI_GRAAL/NGC3256/`, local ESO query CSV and download log. No additional data were downloaded.

## Completeness and integrity
- Local query has 22 unique dp_id values; all match local FITS filenames exactly, with no missing or extra exposure files.
- All 22 files have the expected padded FITS length (about 67.27 MB each), four 2048×2048 float32 image extensions, and a primary header. A sixth HDU is the zero-row SPARTA_ATM_DATA table. Full image arrays read; finite fraction is 1.0 in all 88 images.
- All 132 raw-byte HDU CHECKSUM values validate; all 132 DATASUM values validate (including empty data HDUs). No evidence of truncation or pixel-data corruption.
- Important parser diagnostic: `ESO DET CHIP PXSPACE` uses a nonstandard value string. Astropy normalizes the card **in memory** when parsing and reports four CHECKSUM failures per file, even though DATASUM passes. Independently summing each unchanged on-disk HDU byte range returns the FITS one's-complement checksum 0xffffffff in every case. Metadata preserves both the in-memory failures and raw-byte success. Original headers were not rewritten. Script reads are readonly.
- The download log ends with “Done!”. The byte-level audit is stronger evidence of completed downloads than filenames/logs alone.

## Acquisition and calibration metadata
Programme 60.A-9475(A), target NGC3256, Ks + OPEN; all SCIENCE/OBJECT/IMAGE, no ESO PRO pipeline-history keywords. There are 14 exposures on 2018-01-03 UTC and 8 on 2018-01-06 UTC. The directory contains no reduced stacks, weight/variance maps, darks, flats, standard-star products or bad-pixel masks. Four-chip plus AO-table structure, acquisition filenames and absence of reduction provenance identify these as **raw detector frames**, consistent with [ESO pipeline format documentation](https://www.eso.org/observing/dfo/quality/HAWKI/pipeline/pipe_gen.html).

DIT is 1.7 s, NDIT is 18, EXPTIME is 1.7 s; effective duration per stored co-average is 30.6 s. Archive query exposure=30.6 s agrees with DIT×NDIT. The nominal sum is {h.dit_ndit_s.sum():.1f} s. Offsets and chip gaps require an exposure map before quoting on-target depth. Raw pixel values are co-averages, not accumulated counts for the full DIT×NDIT duration; avoid multiplying the raw signal by the total duration as if it were a rate. Verify the pipeline's rate normalization in reduced products. [ESO raw-data exposure convention](https://archive.eso.org/eso/eso_archive_help.html).

Header instrument pixel scale=0.10643 arcsec/pixel. Extension CD matrices are present; registration and distortion still need calibration. Native detector dimensions are 2048×2048 for each of four chips; they are not a single continuous 4096×4096 sky image. BUNIT is absent; previews say raw counts, not calibrated surface brightness. `ESO DET CHIP GAIN` is 1.0 in the inspected raw header; do not assume that this is a validated physical electron/ADU calibration. The header saturation level is 25,000. Confirm gain, nonlinearity, saturation and read noise against calibration products and readout configuration.

AO high-order and jitter-loop flags are true in all 22 files; tip-tilt-loop flag is false. This establishes recorded loop status, not the final PSF. Requested `ESO OBS AMBI FWHM`=0.3 arcsec is a constraint, not a measured image width. Ambient DIMM start/end values span 0.27–1.54 arcsec; guide-camera FWHM spans 0.57–1.28 arcsec. Neither should substitute for the Ks image PSF. [ESO distinguishes seeing from focal-plane image quality](https://www.eso.org/observing/etc/doc/helphawki.html).

## Provisional empirical image widths
SEP estimates 64-pixel local backgrounds and detects at 8× local RMS, minimum 8 connected pixels. Candidate cuts: unflagged detection, roundness b/a≥0.85, SEP size 1<a<6 pixels, separation >35 pixels, >20-pixel edge clearance, raw cutout peak ≤20,000 and background-subtracted peak >30× global background RMS. Fit a circular Moffat plus constant on a native 31×31 pixel cutout, with free centroid, amplitude, alpha and beta. FWHM = 2 alpha sqrt(2^(1/beta)−1). Retain converged fits with 2<FWHM<15 pixels, 1.21<beta<9.8 and RMS model residual/amplitude <0.04. These are explicit exploratory quality cuts, not an optimal or complete star selection.

Accepted: {len(p)} compact-source detections across 22 frames; repeated detections are not unique stars. Per-exposure medians span {ps.psf_candidate_median_arcsec.min():.3f}–{ps.psf_candidate_median_arcsec.max():.3f} arcsec. All-candidate median is {p.fwhm_arcsec.median():.3f} arcsec, interquartile range {p.fwhm_arcsec.quantile(.25):.3f}–{p.fwhm_arcsec.quantile(.75):.3f} arcsec. This spread is **not a confidence interval**. Circular fits, uncorrected flat fields/artifacts, selection toward round objects, lack of catalog-confirmed stellar identities, and finite pixel integration can bias the widths. Refit isolated catalog-confirmed stars with elliptical pixel-integrated Moffat or empirical PSFs after reduction, across chips and field position, and measure final-stack PSF separately. Six inspected examples are plausible stellar profiles; that inspection does not certify all fits. HAWK-I resolution of 0.2 arcsec is not assumed.

Per-exposure measurements:

{table(ps.reset_index().round(4))}

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
''')
