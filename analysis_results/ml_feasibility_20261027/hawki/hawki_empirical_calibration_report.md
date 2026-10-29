# HAWK-I/GRAAL empirical PSF and calibration feasibility
Audit and executed analysis: 2026-10-27. All outputs are confined to this new directory. Existing FITS and prior analysis were opened read-only. No packages or pipeline software were installed.

## Result and data provenance
Official **reduced products exist** for the same NGC3256 raw observations. The live ESO `tap_obs/ivoa.ObsCore` query returned 12 records: three tiles, three detector pawprints and six catalogues. Their observation groups contain 8, 6, and 8 frames (244.8, 183.6, and 244.8 nominal seconds). These are separate observing-block products; their exposure times cannot be interpreted as uniform coverage of every sky pixel. The downloaded Jan6 tile is an existing ESO pipeline reduction, not a locally fabricated calibrated stack.

We retrieved only a target-centered **2364×2364** SODA cutout of the Jan6 tile, variance and confidence map: center (156.96365, -43.90355) degrees, radius0.035degrees, approximately4.2arcmin bounding box. The three final cutouts total67,299,840bytes (64.18MiB). An initial pointing-centered cutout was visually found to put the galaxy near the edge and was replaced with these corrected cutouts; combined pixel transfers were134,599,680bytes (128.36MiB), below250MiB. No additional raw frames or calibration images were downloaded. The center agrees closely with the [SIMBAD target position](https://simbad.cds.unistra.fr/simbad/sim-id?Ident=NGC3256); it is a cutout/masking coordinate, not a new astrometric determination.

- Science: `ADP.2018-02-14T09:20:46.500` → `reduced_jan6_image.fits`.
- Variance: `ADP.2018-02-14T09:20:46.501` → `reduced_jan6_varmap.fits`.
- Confidence/relative weight: `ADP.2018-02-14T09:20:46.502` → `reduced_jan6_weightmap.fits`.

All three FITS CHECKSUM and DATASUM values pass. Dimensions match; corresponding WCS coordinates agree to better than1e-9pixel (CRPIX float representations differ at~1e-14). SHA256, exact URLs, cutout region and byte counts are in `reduced_download_log.json`. All source/progenitor/ancillary links are preserved in the downloaded Datalink XML/CSV. The relative confidence map is **not treated as inverse variance**.

The [official ESO/CASU collection description](https://doi.eso.org/10.18727/archive/34) identifies ESO QC as the processor after September2015. The [March2026 release description](https://www.eso.org/rm/api/v1/public/releaseDescriptions/87) describes dark/flat/gain/sky corrections, 2MASS calibration, bilinear resampling and accompanying variance/confidence maps; it distinguishes observing-block stacks from tiles. Thus these 2018 products are ESO reductions using the CASU-developed pipeline. Release notes are not substituted for inspection of the downloaded headers.

## Calibration completeness and dependencies
The full workspace FITS inventory (`local_fits_inventory.csv`) and earlier HAWKI inspection were checked. The original local HAWKI tree contains22 raw science frames and no darks/flats/master confidence/zeropoint products. Venv/package files account for most of its other files. The live raw archive query confirms22 NGC3256 programme60.A-9475(A) frames in January2018, all present locally,14 on January3 and8 on January6. The broader programme query contains36 frames, including another target.

CalSelector was executed for one science frame in **each of the three observing blocks**. All three returned `certified="true" complete="true" mode="Raw2Master"`, with no association error. There is therefore **no evidence of missing archive calibrations**. Exact associations include MASTER_DARK, MASTER_TWILIGHT_FLAT, MASTER_CONF, MASTER_READGAIN, PHOTCAL_TAB, MASTER_2MASS_CATALOGUE_ASTROM/PHOTOM, SCHLEGEL_MAP_NORTH/SOUTH, and standard-star related products. See `calibration_association_manifest.csv` and individual association trees. A bounded January1–7 raw-calibration query returns620 records, including70 darks with DIT≈1.7s; no Ks twilight flats occur in that short window. This is not a flat-field shortage: the certified cascade and actual reduced header use a December25 Ks flat.

Local `esorex` is absent from PATH and checked common binary locations; no HAWKI recipes were found locally. The missing local dependencies for a fresh reduction are the executable ESO CPL/EsoRex HAWKI recipe installation and the associated master/static calibration files above. No reduction was attempted with missing inputs. ESO documents the [calibration cascade](https://www.eso.org/observing/dfo/quality/HAWKI/pipeline/pipe_calib.html), the [pipeline installation and recipes](https://www.eso.org/sci/software/pipelines/hawki/hawki-pipe-recipes.html) and [CalSelector metadata access](https://archive.eso.org/cms/application_support/calselectorInfo.html). Prefer the already reduced products unless a scientific need for custom sky subtraction justifies rebuilding that environment.

## Downloaded reduced product: inspected calibration claims
Header values: BUNIT=ADU; PHOTSYS=VEGA; FLUXCAL=ABSOLUTE; PHOTZP=26.298326mag; PHOTZPER=0.182821mag; EXPTIME=TEXPTIME=244.8s; CASUEXPT=30.6s; eight input frames; PROCSOFT=2.4.1; QCFLAG=0000000; OB_GRADE=A. The header records a January5 1.7s dark and December25 Ks twilight flat. Pipeline PSF_FWHM=0.302691arcsec. Header WCS fit RMS=0.129458arcsec using386 sources; header photometric source count395. These are **pipeline claims**, not independent validation against a new external astrometric/photometric catalogue.

The TAN CD matrix yields scale=0.10659569arcsec/pixel. Background pedestal is approximately1983.499ADU and is removed locally for these diagnostics. Do not interpret this pedestal as residual physical sky brightness. No pixel-to-flux conversion or absolute surface-brightness measurement was attempted. PHOTZP/PHOTZPER must be used with the release convention, aperture correction, magnitude system and appropriate background. Raw inputs store1.7s DIT coaverages with NDIT18, while nominal duration is30.6s; neither raw nor reduced values are assumed to be accumulated electrons or ADU/s. Variance/weight headers inherit BUNIT=ADU; variance is operationally interpreted as squared science units from its VARMAP product category, and this metadata inconsistency is retained explicitly.

## Empirical reduced-image PSF
SEP detects sources after64pixel background detrending. Candidate selection uses no tight roundness preference: b/a≥0.5, broad size cut, detection flag0,40pixel nearest-neighbor isolation,24pixel edge clearance, a15000ADU peak veto, peak S/N>40, and exclusion of the central~69arcsec galaxy region and low-confidence pixels. The fit is an elliptical Moffat plus a plane on31×31pixels, numerically integrated with3×3subpixels. All fits are preserved. Acceptance requires convergence,1.5<FWHM_circ<12pixels, q>0.4,1.17<beta<11.8 and RMS residual/amplitude<0.04. The provided variance supplies diagonal fitting weights; formal least-squares uncertainties would neglect correlation and are not quoted.

Accepted103/109 compact sources. Their identities are **not externally catalog-confirmed stars**; residual contamination by compact galaxies, blends and model mismatch remains possible. Visual inspection of source/model/residual panels and the full cutout was performed. Some sources show asymmetric cores or nearby faint companions. This supports provisional empirical sensitivity inputs, not a precision PSF calibration.

| Quantity | Median | Candidate25–75percentiles |
| --- | ---: | ---: |
| Circularized FWHM (arcsec) | 0.3166 | 0.2920–0.3329 |
| Elliptical circularized D50 (arcsec) | 0.3533 | 0.3428–0.3684 |
| Elliptical circularized R80 (arcsec) | 0.2873 | 0.2802–0.2964 |
| q=minor/major | 0.8199 | 0.7750–0.8589 |
| Moffat beta | 4.753 | 3.859–6.109 |

These intervals describe field/sample scatter, **not confidence intervals**. D50=2sqrt(alpha_major alpha_minor)sqrt(0.5^(1/(1-beta))-1); R80 replaces0.5 with0.2 and omits the factor2. They are circularized radii of elliptical isophotes, not directly measured circular-aperture growth curves. They extrapolate the fitted profile outside the finite cutout: two beta<2 cases give unstable large wings. Excluding those retains101 sources with median FWHM unchanged and beta4.787 (`reduced_beta2_sensitivity.json`). Spatial591pixel bins with≥4sources have median FWHM0.286–0.346arcsec, but selection and source mixtures also vary spatially; no smooth optical PSF field is inferred. `reduced_psf_spatial_bins.csv` preserves these counts.

## Reduced background and correlated noise
Mask: low confidence<80, invalid/nonpositive variance, central650pixel galaxy radius,15pixel dilation of5sigma detections, local6sigma outliers,32pixel boundaries. The masked fraction is0.397. Robust blank-pixel sigma=1.8397ADU; ordinary sigma=1.9332ADU. Median propagated sqrt(variance)=3.1570ADU; robust normalized residual width=0.529. Do not rescale the variance to force unit per-pixel residuals: bilinear interpolation and correlations alter these comparisons.

Adjacent reduced-background correlations are rho_x=0.2753, rho_y=0.2932. These are actual measurements on a reduced, resampled product. They combine resampling, detector and remaining sky structure; their individual physical contributions have not been separated.

500random fully unmasked blank apertures were measured per radius; apertures may overlap and their scatter is not an uncertainty on the noise estimate. Each uses locally detrended sums, without an extra local annular subtraction.

| radius_pix | radius_arcsec | sum_robust_sigma_ADU | noise_ratio_to_pixel | noise_ratio_to_variance |
| --- | --- | --- | --- | --- |
| 2.0000 | 0.2132 | 10.4171 | 1.5705 | 0.9098 |
| 4.0000 | 0.4264 | 21.9711 | 1.7061 | 0.9951 |
| 8.0000 | 0.8528 | 56.3751 | 2.1833 | 1.2702 |
| 16.0000 | 1.7055 | 144.7619 | 2.7873 | 1.6394 |
| 32.0000 | 3.4111 | 356.5457 | 3.4213 | 2.0121 |


The first ratio compares measured robust aperture scatter with sigma_pixel sqrt(N). The second compares with median sqrt(sum VARMAP) for the same apertures. Correlations and longer-scale residual structure inflate aperture noise, especially on larger scales. The measured aperture relation is more defensible than treating one adjacent-pixel rho as a complete stationary kernel. These curves apply to this source mask, cutout, coverage selection and detrending scale, not universally to HAWKI or ULTIMATE.

## Raw-frame subset and earlier measurements
The earlier read-only audit and677circular raw-candidate fits remain in `analysis_results/hawki_inspection_report.md` and companion CSVs. They cover all22frames. This new analysis uses first/last exposure of each night (four raw frames,16detector images) to check native behavior independently of the downloaded mosaic. It broadens the ellipticity selection, integrates the elliptical model, and masks the galaxy for sky diagnostics. A first brightest-sector selection identified hot pixels; all63were rejected as subpixel/beta-boundary fits. The final selection adds SEP a>1pixel and maximum central3×3pixel concentration≤0.5 before fitting one bright isolated candidate per detector quadrant. This is an explicit detector-artifact safeguard, not stellar identity confirmation.

Final accepted raw candidates: 36. Median circularized FWHM=0.2724arcsec; q=0.8632; beta=2.682. Per-exposure medians and candidates are in `psf_per_exposure.csv` and `elliptical_moffat_candidates.csv`.

Across the16native detector images the median robust blank-pixel sigma is29.2544raw detector units, and median adjacent covariance correlations are x=0.1676, y=0.0947. Native aperture-noise ratios and masked background tile statistics are recorded separately. These are unflatfielded/raw-coaverage diagnostics; **native covariance is not reduced-image resampling covariance**. No electron conversion, calibrated depth or native-to-reduced noise equivalence is claimed.

## Use in the main feasibility analysis
`empirical_model_inputs.json` exports the reduced-image medians, IQRs, scatter, q, beta, D50/R80, pixel scale, covariance lags and aperture-noise measurements. Use beta/ellipticity and plausible correlated-noise stress tests as explicitly conditional **HAWKI-only empirical sensitivities**. Do not use the observed0.317arcsec FWHM as ULTIMATE resolution, treat it as dust truth, or infer dust geometry from this single Ks band. Keep the main seeing/GLAO specifications and D50 fixed when varying profile wings. The existing baseline ML experiment remains independent of whether a new local HAWKI reduction can be run.

## Reproduction and inspectable outputs
Interpreter: `/home/bahareh/miniforge3/envs/phd/bin/python`; existing NumPy/SciPy/Astropy/SEP/pandas/Matplotlib only. Set `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MPLCONFIGDIR=/tmp/hawki_mpl` for diagnostics. Code and logs are in this directory.

1. `query_archive.py`: official ObsCore and Datalink metadata. `query_raw_fixed.py` repeats raw queries via the documented `tap_obs` endpoint (the initial `tap_raw` attempt returned404; that failure is preserved in the archive log).
2. `query_calibrations.py`: representative CalSelector association tables and trees, no pixel downloads.
3. `fetch_reduced_cutouts.py`: bounded SODA science/variance/confidence transfer, hashes and exact URLs.
4. `diagnose_reduced.py`, `diagnose_raw.py`: read-only fits/background/covariance/apertures and figures.
5. `summarize_archive.py`, `export_empirical_model.py`, `write_report.py`: inventory, manifests, model inputs and report.

Primary figures: `reduced_overview.png`, `reduced_fit_inspection.png`, `reduced_noise.png`, `fit_inspection.png`, `psf_field.png`, `native_noise.png`. Tables retain accepted/rejected fits, sample counts and per-aperture predictions. Original previous results are not overwritten.

## Addendum: executed catalogue consistency and stellar subset
A focused follow-up retrieved the associated certified PHOTCAL_TAB (20,160bytes), ESO source catalogue ADP.2018-02-14T09:20:46.487 (1,713,600bytes) and149rows from NASA/IPAC IRSA's 2MASS All-Sky Point Source Catalogue (12,183bytes). Total additional retrieval was1,745,943bytes. Exact queries, URLs, files and byte limits are in `fetch_catalogue_validation.py`, `irsa_2mass.adql` and `catalogue_download_log.json`. No further image products were fetched.

`validate_catalogue.py` independently transforms our reduced-image fitted centroids through the downloaded WCS and crossmatches with IRSA2MASS. There are23mutual nearest-neighbor matches within1arcsec among103accepted compact-source fits. Nine pass the quality subset: Ks photometric qualityA/B, contamination flag0, read flag1/2/4, 2MASS nearest-neighbor distance>5arcsec; accepted HAWKI fits already require40pixel isolation, central-galaxy exclusion and conservative image-peak veto. For photometry, the associated ESO source catalogue must additionally match within0.3arcsec, have stellar Classification=-1 and aperture-flux S/N>10; |H-Ks|<1mag. These nine ESO catalogue peaks are1521–9136ADU, comfortably below the reduced selection's15000ADU veto. This is a conservative saturation screen, not a new detector-linearity certification. Match flags and measurements are saved for every original accepted candidate in `catalogue_crossmatches.csv`; no photometric outlier was removed after looking at the residuals.

For these nine qualitymatches, median radial separation is**0.1210arcsec**, RMS0.1688arcsec. Median HAWKI-minus-2MASS offsets are RA cosDec=+0.06774arcsec and Dec=-0.03503arcsec. Corresponding robust coordinate scatters are0.1071 and0.0693arcsec. Positions were not propagated between the2MASS and2018epochs, so proper motions, source-dependent2MASS errors and any residual confusion remain contributors.

Photometry follows the explicit source-catalogue equation in the [ESO release description](https://www.eso.org/rm/api/v1/public/releaseDescriptions/87): m_Vega=PHOTZP−2.5log10(Aper_flux_3)−APCOR3. The catalogue extension supplies PHOTZP=26.29832554 and APCOR3=0.0472784; fluxes are ADU under the product's existing normalization. **No extra division by EXPTIME244.8s or CASUEXPT30.6s is applied** to these catalogue fluxes. We have not recalibrated arbitrary pixels or inferred surface brightness.

An actual-reference-file discrepancy was discovered: both extensions of the associated `M.HAWKI.2017-01-13T09:32:55.220` PHOTCAL_TAB specify Ks_HAWKI=0.03J_2MASS+0.97Ks_2MASS (`coleq_columns=Jmag,Kmag`), whereas the current release description prints0.03H+0.97Ks. Using the **downloaded associated calibration table** gives median HAWKI-minus-transformed2MASS **−0.05576mag**, robust scatter**0.13902mag**, RMS0.24292mag. Using the release-document H formula instead gives−0.04091mag and0.13848mag robust scatter. Both are preserved in the match table and summary, so this convention disagreement is not hidden or folded into a fitted correction. A high residual of about+0.54mag remains in the nine-object sample; this check does not demonstrate uniform0.05mag calibration accuracy.

The nine catalogue-associated stellar sources provide a useful **selection sensitivity**: circularized FWHM median**0.29352arcsec**, IQR0.28698–0.32296; beta median**3.74148**, IQR3.43351–3.95007; q median0.85829; analytic elliptical circularized D50 median0.36283arcsec and R80 median0.29289arcsec. This differs from the full provisional103candidate sample, particularly in beta. It warrants retaining stellar-selection uncertainty when using empirical PSF wings. The original `empirical_model_inputs.json` is deliberately unchanged so that the already executed conditional ML sensitivity retains exact input provenance; the nine-star sensitivity is in `catalogue_validation_summary.json`.

These are **recomputed catalogue-consistency measurements**, not a held-out independent calibration: the ESO pipeline itself uses2MASS. Nine positional/quality stellar associations strengthen identification for this subset; they do not certify all103compact sources, remove astrophysical compact-source contamination, or establish a new absolute astrometric/photometric accuracy. A proper-motion-aware external reference and an independent photometric check remain outstanding. The [official 2MASS catalogue quality documentation](https://www.ipac.caltech.edu/2mass/releases/allsky/doc/ancillary/pscformat.html) defines the flags used here. `catalogue_validation.png` was visually inspected; code, full match table and numerical summary are saved beside it.
