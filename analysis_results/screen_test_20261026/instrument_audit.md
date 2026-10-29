# ULTIMATE sensitivity calculator audit

Read and executed the [published calculator](https://github.com/sali131/ULTIMATE-Subaru-Sensitivity-Calculator) at commit `2187748a40d4207519a8eff0d2a5b6701db8da0d`. The unchanged script ran with its defaults; outputs and execution log are saved. The reference curves are approximately 14.35 MB total, fetched with byte-size and Git blob SHA-1 checks; no instrument package was installed.

## What is specified by that code

Defaults: MOIRCS broadband proxy filters, GLAO, 0.1 arcsec/pixel, RN=16 e−, 1 h, SNR=5, instrument+filter throughput 0.45, PWV=1.6 mm, airmass=1, temperature=273 K. Telescope diameter=8.0819 m, central obscuration diameter ratio=0.277, mirror reflectivities 0.95 and 0.98; source collecting area is 47.363744 m². These are calculator design assumptions, **not measured ULTIMATE performance**.

Y/J/H/Ks centre/width (µm): 1.02/0.10, 1.26/0.17, 1.64/0.28, 2.15/0.31. MOIRCS/SWIMS/custom tables supply centres, widths and peak transmission, not measured wavelength-dependent ULTIMATE filter curves. The code divides the fixed instrument+filter throughput by filter peak and then multiplies it back, so its supplied per-filter optics throughput column is not used in the final 0.45 default. The filter-name choices are proxies/proposals, not a finalized filter set.

Sky uses the repository's Gemini-derived photon spectrum with its thermal component removed, adding atmospheric blackbody emission at 273 K weighted by (1−transmission). Sky-line scaling is 0.58 in H, 1 elsewhere. Telescope thermal emission uses a warm optical-emissivity model including the centre cone. The prompt says instrument temperature, but this variable enters the telescope thermal calculation; cold-instrument self-emission is not separately specified. Moon background is always added from the bundled spectrum with no user-selected moon phase/separation; its lunar conditions are not established. Sky spectrum units and wavelength grids were inspected and the script's photon/electron conversions reproduced.

## Reproduced default outputs

One-hour 5σ **point-source** AB limits (median conditions):

| Proxy | GLAO | No AO |
| --- | ---: | ---: |
| Y | 25.337 | 25.115 |
| J | 25.206 | 24.924 |
| H | 24.837 | 24.471 |
| Ks | 25.164 | 24.716 |

These use D50 apertures, 50% flux and a background-dominated approximation. They are not resolved-surface-brightness limits. `calculator_original_1h_output.csv` preserves all reported columns; `calculator_exact_components.json` preserves unrounded rates.

## Corrections and interpretation for this experiment

1. The original read term is one RN² per aperture pixel for the **entire** integration, regardless of hours. There is no DIT/exposure count. Here T is split into N=T/60 s exposures; variance includes N RN². Aggregate draws use the exact summed-Poisson and summed-Gaussian distributions, mathematically equivalent to independent exposures. H background is about 58,000 e− per pixel per 60 s under these assumptions; full-well and nonlinearity are not supplied, so saturation safety and operational DIT require instrument-team confirmation.
2. Original sky/moon collection uses full primary area while sources use the centrally obscured area. Our consistent diffuse sky/moon rates multiply those original rates by (1−0.277²). The telescope thermal term retains its explicitly modelled optical geometry.
3. The original omits dark current and source shot noise in its limiting-flux approximation. We include source/sky/thermal/moon/dark Poisson terms and per-exposure RN. Dark current 0.01 e− s−1 pixel−1 is **provisional**, not supplied by the calculator.
4. Source electron conversion integrates Fν A T(λ)/(h λ) over the observer-frame band. At 1 Jy, rates agree closely with the calculator's central-wavelength approximation; any difference is saved in numerical validation. Intensity in MJy/sr is first converted using the actual angular pixel solid angle. No Poisson distribution is drawn directly from surface-brightness units.
5. `D50_am=1.0.csv` supplies encircled-energy diameters. In the primary model we explicitly assume a circular Gaussian; **only for a Gaussian does D50 equal FWHM**. Median Ks D50≈0.390 arcsec with GLAO and 0.588 arcsec without. We do not substitute the project's optimistic 0.2 arcsec target for these calculator values. A separate 0.2-arcsec case is labelled optimistic; Moffat-wing tests hold D50 fixed and are not PSF measurements.
6. Native detector noise is generated before any matching/smoothing. Aperture uncertainties use the squared effective matching-and-aperture kernel. Well-separated apertures reduce cross-aperture covariance; the remaining covariance diagnostic is recorded and limits the approximate factorized evidence.
7. Optical griz is **a provisional complementary-imaging scenario**: top hats, 0.7 arcsec Gaussian FWHM, 0.1 arcsec sampling, effective instrument/filter throughput 0.35, atmospheric factor 0.9, RN=5 e− and dark=0.001 e− s−1. Dark-sky AB/arcsec² assumptions are 22.0/21.0/20.3/19.5. These are not calculator outputs or an ULTIMATE optical capability. They are held fixed between seeing and GLAO comparisons.
8. The synthetic noise model is an instrument-informed, known-mean-sky statistical baseline, not a full on-sky forecast. It does not establish flat-field floors, persistence, nonlinearity, cosmic-ray losses, sky-estimation covariance, weather distribution, dither coverage, correlated resampling noise or final exposure efficiency. No raw HAWK-I counts are used as a Subaru background. The 5% photometric model-discrepancy term belongs to inference and is not a claim of a measured instrument systematic.

Machine-readable settings: `instrument_parameters.csv`, `instrument_bandpasses.npz`, `sources/calculator_tree.json`, `sources/curve_download_manifest.json`. All unverified operational numbers remain provisional.

## Additional proposed filter tables inspected

MOIRCS/SWIMS medium tables each contain the same nine J1/J2/H1–H3/K1–K4 entries (1.17–2.41 µm). The narrow tables contain 13 MOIRCS and 10 SWIMS entries, including line/continuum proxies; `custom.asc` has four examples. These are centre/width/peak specifications only, not resolved ULTIMATE transmission curves. `calculator_proposed_filters.csv` records all entries. The executed image experiment uses broadbands only: DR1 broadband samples cannot substantiate medium/narrow-band line forecasts.
