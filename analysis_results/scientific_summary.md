# ULTIMATE–Subaru: Beyond the Foreground Screen
Verified pilot results prepared 2026-10-26 for the October 28 progress meeting and November 9–11 workshop.

## Actual results
The original O1 numerical results reproduce: A_g = 0.334442 mag, A_Ks = 0.020562 mag; Spearman ρ = 0.924164 and 0.548340, with the original 1,264 spatial bins. A separate notebook copy executes the original calculation and plotting code, changing only input/output locations. An Astropy-based implementation independently reproduces the pilot's custom FITS reader calculations.

Five orientations of **one galaxy**, subhalo 294866, DR1:

| orientation | A_g_full_mag | A_ks_full_mag | rho_g | rho_ks | n_bins |
| --- | --- | --- | --- | --- | --- |
| O1 | 0.334442 | 0.020562 | 0.924164 | 0.548340 | 1264 |
| O2 | 0.231069 | 0.006577 | 0.902894 | -0.075546 | 1261 |
| O3 | 0.581156 | 0.069152 | 0.926491 | 0.737539 | 1249 |
| O4 | 0.594782 | 0.078292 | 0.882434 | 0.745232 | 1264 |
| O5 | 0.603715 | 0.083102 | 0.882507 | 0.727067 | 1264 |

Attenuation columns are full-frame flux ratios in magnitudes; ρ columns describe the shared pilot spatial mask. Full-frame g attenuation changes by 0.373 mag and Ks by 0.077 mag across views. Optical association is consistently strong under the original selection. Ks association is strongly view dependent: O2 is weakly negative, while O3–O5 are positive. This is a scientific finding to present with the mask definition, not a failed reproduction.

## What the measurements mean
Images are 1600×1600, 100 pc/pixel, with a 160×160 kpc full field. Brightness units are MJy/sr and projected dust surface density is M☉/pc². All 25 inputs are finite, nonnegative and have identical within-view coordinate headers. Common pixel area/solid angle cancels in the intensity ratios. We do not infer a physical observer distance from the FITS scale.

Integrated attenuation is −2.5 log10(sum I_dust / sum I_nodust), not mean pixel attenuation. Within R < 20 kpc the integrated attenuations are larger: g 0.288–0.752 mag and Ks 0.013–0.100 mag. This aperture dependence is included in the CSV and should accompany comparisons to observed photometry.

Statistics use 1-kpc block-mean intensities before ratios, R < 20 kpc from the image centre, positive dust surface density, both dust-free intensities >10⁻⁴ of their band-specific binned full-frame peaks, and finite attenuation in both bands. Counts vary across views because eligibility changes. Maps use 0.5-kpc block means and their own equivalent mask. The figure colour limits clip display values only; FITS maps preserve them. Sensitivity CSV covers 0.5/1/2-kpc bins, R < 10/20/30 kpc, and relative brightness thresholds 10⁻⁵/10⁻⁴/10⁻³: 27 choices per view. These are selection ranges, **not error bars**. O2 Ks ρ ranges approximately −0.843 to +0.066 over this grid. Optical ρ ranges 0.680–0.937 over the entire grid. Radius-detrended rank associations are exploratory; they do not isolate causality.

Local negative attenuation is retained. In the selected 1-kpc bins, the negative Ks fraction is 20.8–46.4% by view. Scattering can enhance local brightness, and Monte Carlo noise can contribute; these files provide no error maps or component separation to determine how much of either is responsible. Faint cuts do not constitute a measured S/N threshold. We do not report independent-pixel p-values or invented uncertainties. SKIRT's stellar smoothing and simulation resolution also mean a 100-pc grid is not proof of independently resolved 100-pc physical structure. [Baes et al., DR1 methodology](https://arxiv.org/html/2401.04224v1).

The map integral gives about 3.106×10⁸ M☉ of projected dust, with a 0.106% range between views. This is an internal projection consistency check, not independent dust-mass measurements or an uncertainty estimate.

## HAWK-I status
All 22 expected science exposures are present, readable, and complete by FITS block lengths. All 132 unchanged on-disk HDU checksums and all DATASUM checks pass; all 88 detector images contain finite values. Astropy's apparent checksum warnings arise after it normalizes a nonstandard PXSPACE header card in memory; no original file was repaired or modified. The explicit raw-byte checksum checks distinguish this parsing effect from corruption.

These are raw Ks exposures on January 3 (14) and January 6 (8), 2018 UTC. Each has DIT=1.7 s and NDIT=18, hence 30.6 s exposure duration; nominal total 673.2 s across offsets, **not** uniform integration at every sky location. No local science stack or calibrations were found. Detailed audit: [HAWK-I report](hawki_inspection_report.md).

677 accepted compact-source Moffat fits yield per-exposure medians of 0.258–0.417 arcsec at the header scale 0.10643 arcsec/pixel. These are provisional raw-frame estimates, not validated final-stack PSFs. HAWK-I can support an empirical NIR imaging comparison after calibration. It does not supply dust-free truth, a 3D dust label, or a 0.2-arcsec image to be recovered by binning/convolution.

## Safe workshop claims
- The original pilot is reproducible, with documented units, apertures and masks.
- Five views show substantial variation in effective attenuation and especially Ks–dust association for one galaxy.
- Projected dust is associated with optical attenuation in these ideal simulations, but correlation does not demonstrate unique 3D dust geometry recovery.
- HAWK-I observations exist and pass file-integrity checks; provisional image widths and calibration needs are measured/documented.
- ULTIMATE mock-observation feasibility and learning from observable colours remain **planned experiments**. No realistic-noise recovery result or ML accuracy is claimed.

Use `figures/five_orientation_maps.*`, `five_orientation_correlations.*`, and `viewing_dependence.*`; show the raw HAWK-I preview only with its uncalibrated label. See `workshop_talk_outline.md` and `workshop_10min.pdf` for a timed presentation draft.

## Reproducibility and limits
Reused `/home/bahareh/miniforge3/envs/phd/bin/python`; no installs, new environments, large downloads, or training runs. `environment.json` records versions. Both notebooks execute top-to-bottom with saved tables/plots. `pilot_reproduced.ipynb` and `TNG294866_five_orientations.ipynb` preserve original notebook/data. Only the new directory is written. HTML previews are included; PNGs and representative rendered PDFs were visually reviewed. Further experiment specifications and outstanding instrument assumptions are in [next experiments](next_experiments.md).
