# ULTIMATE-like imaging: spatial structure and morphology feasibility

## Decision

**GO for a conditional dust-induced morphology and spatial-transfer result; NO-GO for interpreting generic red/dark structures as unique dust detections.** This executed pilot addresses image structure, not 3D dust geometry or absolute dust mass. The earlier catastrophic false positives and inadequate physical SED fits remain valid and are not superseded.

For O1 at illustrative z=0.1 and one hour per band, NIR-only J−Ks candidates at the 1kpc analysis scale recover 3.9% (seeing) / 25.7% (GLAO) of the positive reference area, with 5.3% / 1.2% contamination relative to that reference. The paired completeness change is 21.74 percentage points [95% Monte Carlo mean interval 17.90, 25.58]. This is an actual conditional result for one view, fixed coefficients/PSFs and a thresholded truth definition, **not a generic ULTIMATE dust-recovery forecast**. The NIR reference covers only a small fraction of the disk; its area is reported in `scale_transfer.csv`. Inspect all orientations and scales rather than promoting this single result as population performance.

The area gain must not be confused with a reliably detected individual object. In this O1 NIR example there is one scale-sized reference feature, but a scale-sized candidate component appears in only 5/40 GLAO draws (12.5%; exact 95% interval 4.2–26.8%) versus 0/40 seeing draws (upper95% limit 8.8%). The five paired discordances give a two-sided exact McNemar p=0.0625: this small experiment does **not** establish a 5%-level component-incidence advantage, even though the paired area gain is clear under its noise model. No multiple-test-adjusted significance is claimed.

The straightforward native Ks unsharp-deficit detector often identifies stellar morphology instead of the dust imprint. Optical–NIR structure can overlap dust-induced colour changes but is also present without spatially varying dust. Those unsuccessful cases are retained, not re-thresholded. The primary workshop outcome should therefore combine measured dust-induced morphology changes with conditional NIR spatial-transfer improvement.

## What ran

Five correlated views of **one** DR1 galaxy 294866, using actual LSST g and 2MASS J/Ks images and projected dust maps. O1: z=0.05/0.1, 0.25/1/4h per band, seeing/GLAO. O2–O5: z=0.1, 1h per band, both modes. Additional O1 z=0.1, 1h equal-D50 Moffat sensitivity. Each of 22 conditions has four scenes and **40 independent final noise draws**: clear, uniform screen, stellar-only positive colour shifts, original SKIRT. This is 3,520 paired-scene observations, with three bands each. Gaussian baseline has three methods at three analysis scales; Moffat sensitivity uses native Ks only, not an invalid Gaussian colour-matching prescription. All criteria were fixed in `PROTOCOL.md` before evaluation; no Bayesian classification grid, ML, installations or science downloads were performed.

Forty separate calibration draws per method/noise prescription check analytic variance, including exact aggregate Poisson counts plus independent summed read noise. Variance agreement is documented in `noise_covariance_validation.csv`; calibration did not select thresholds. Exposure depth is **per band**, so 1h means 3h on source over these three bands, before overheads. At 60s DIT this is 60 reads per band, not a single long exposure.

## Reference attenuation and interpretation

A_eff,b(x)=−2.5 log10[I_SKIRT,b(x)/I_clear,b(x)], with finite positive intensities, I_clear>10⁻⁴ of the band peak and R<12kpc. Source pixels are 100pc; this sampling does not establish independently resolved physical structure at 100pc. Negative A_eff is retained: scattering and/or SKIRT Monte Carlo fluctuations can enhance local flux; no component/error maps allow a decomposition. No conversion to optical depth, dust mass or a unique 3D arrangement is made.

`reference_summary.csv` gives the aperture-integrated attenuation, negative fractions and projected-mass rank associations separately by band and view. Their viewing-angle dependence is retained; projected dust is a post-measurement check, never an observational template. `projected_dust_checks.csv` and `scale_transfer.csv` also compare detector-grid attenuation/structure with projected mass. Smoothing, stellar weighting, scattering and line-of-sight projection prevent a unique attenuation–mass relationship.

Truth-only structure references are the difference between the same observable computed on SKIRT and clear images, with area-integrated sampling but no observational PSF, and analysis smoothing FWHM 0.5/1/2kpc. PSF-limited references are saved separately. A kernel FWHM is **not an inferred feature diameter**; the effective width combines analysis smoothing and instrumental PSF. The reference excludes positive dust effects below 0.05mag (colours) or 0.03 fractional deficit. Features outside those operational cuts are not necessarily dust-free.

## Observable methods and results

The measurement function receives observed band images, variance, pixel scale and PSFs only. Counterparts and physical maps enter rendering/scoring, never feature selection. Positive candidates must exceed both 3 propagated noise SD and the fixed amplitude cut; fine and broad fluxes require S/N>10. This is a local significance requirement, not an image-wide false-alarm or false-discovery calibration.

- g−Ks fine-minus-broad colour, matched to 0.8arcsec in both modes; g always has its seeing-limited 0.7arcsec PSF.
- J−Ks colour, matched within NIR to each strategy's J width, preserving finer GLAO information relative to optical matching.
- Native Ks brightness deficit, 1−I_fine/I_broad, without smoothing to g resolution.
- Concentration C=5log10(R80/R20), circular R50, second-moment axis ratio, and noise-corrected 180° asymmetry, measured in R<12kpc about the fixed simulation centre. Signed sky-subtracted pixels are retained. These are defined pilot measurements, not optimized survey morphology estimates.

O1, z=0.1, 1h/band (pixel-area measures; all independent noise draws retained):

| mode | method | scale_kpc | completeness | contamination | correlation |
| --- | --- | --- | --- | --- | --- |
| glao | J_Ks_NIR | 0.5 | 0.000 | nan | 0.542 |
| glao | J_Ks_NIR | 1.0 | 0.257 | 0.012 | 0.850 |
| glao | J_Ks_NIR | 2.0 | 0.817 | 0.025 | 0.910 |
| glao | Ks_native | 0.5 | 0.004 | 1.000 | -0.084 |
| glao | Ks_native | 1.0 | 0.000 | 1.000 | -0.221 |
| glao | Ks_native | 2.0 | 0.000 | 1.000 | -0.371 |
| glao | g_Ks_matched | 0.5 | 0.064 | 0.158 | 0.447 |
| glao | g_Ks_matched | 1.0 | 0.387 | 0.112 | 0.668 |
| glao | g_Ks_matched | 2.0 | 0.481 | 0.052 | 0.761 |
| seeing | J_Ks_NIR | 0.5 | 0.000 | nan | 0.403 |
| seeing | J_Ks_NIR | 1.0 | 0.039 | 0.053 | 0.814 |
| seeing | J_Ks_NIR | 2.0 | 0.738 | 0.010 | 0.906 |
| seeing | Ks_native | 0.5 | 0.003 | 1.000 | -0.070 |
| seeing | Ks_native | 1.0 | 0.000 | 1.000 | -0.220 |
| seeing | Ks_native | 2.0 | 0.000 | 1.000 | -0.372 |
| seeing | g_Ks_matched | 0.5 | 0.065 | 0.159 | 0.446 |
| seeing | g_Ks_matched | 1.0 | 0.386 | 0.112 | 0.668 |
| seeing | g_Ks_matched | 2.0 | 0.480 | 0.052 | 0.761 |

Distance/view sensitivity at 1kpc in J−Ks, one hour per band:

| view | z | mode | completeness | contamination |
| --- | --- | --- | --- | --- |
| O1 | 0.05 | glao | 0.722 | 0.001 |
| O1 | 0.05 | seeing | 0.600 | 0.000 |
| O1 | 0.1 | glao | 0.257 | 0.012 |
| O1 | 0.1 | seeing | 0.039 | 0.053 |
| O2 | 0.1 | glao | undefined: no reference/candidate | undefined: no reference/candidate |
| O2 | 0.1 | seeing | undefined: no reference/candidate | undefined: no reference/candidate |
| O3 | 0.1 | glao | 0.384 | 0.004 |
| O3 | 0.1 | seeing | 0.223 | 0.003 |
| O4 | 0.1 | glao | 0.676 | 0.006 |
| O4 | 0.1 | seeing | 0.620 | 0.011 |
| O5 | 0.1 | glao | 0.817 | 0.015 |
| O5 | 0.1 | seeing | 0.759 | 0.017 |

At O1/z=0.1 the 0.5kpc analysis-scale NIR reference is not recovered by the fixed selector in either mode; the 2kpc area recovery is about74%/82% seeing/GLAO. This is evidence for recoverable structures after kpc-scale smoothing in these particular scenes, not a universal minimum dust-cloud size. At z=0.1 the native Ks Gaussian width is1.085kpc seeing/0.718kpc GLAO, and within-NIR matching gives1.213/0.936kpc before analysis smoothing. At1kpc smoothing the J−Ks effective widths are therefore about1.572/1.370kpc. The actual candidate feature shapes, brightness, amplitude cut and stellar structure matter as much as this nominal width. O2 has no positive J−Ks reference above the chosen cut, so its undefined completeness is not a failed recovery estimate.

Completeness is reference area recovered; contamination is candidate area outside the positive reference. It includes stellar structures and dust effects not captured by the operational reference cut, so it is **not a universal astrophysical false-discovery probability**. Reference-component area recovery uses overlap with the union of thresholded pixels (30% area), while candidate-component counts require the separate minimum scale-related area. Thus reference-component area recovery alone does not certify detection of a connected object. Both are recorded; `component_incidence.csv` provides component counts and exact noise-realization intervals. No independent-pixel error bars are used. The 95% mean intervals describe uncertainty in the repeated-noise mean for a fixed scene; they exclude instrument, SPS, simulation and galaxy-to-galaxy uncertainty. Pixelized radii have finite sampling precision.

## Controls: dust attribution remains limited

Candidate area for O1 z=0.1, 1h, 1kpc, GLAO:

| scene | method | candidate_area_fraction |
| --- | --- | --- |
| clear | J_Ks_NIR | 0.00% |
| clear | Ks_native | 48.98% |
| clear | g_Ks_matched | 5.60% |
| population_shift | J_Ks_NIR | 0.00% |
| population_shift | Ks_native | 48.98% |
| population_shift | g_Ks_matched | 7.66% |
| uniform | J_Ks_NIR | 0.00% |
| uniform | Ks_native | 48.97% |
| uniform | g_Ks_matched | 5.61% |

The clear and uniform-screen scenes share the actual structured stellar populations. The shifted control adds a fixed smooth-plus-patchy, positive non-screen spectral perturbation. Its NIR colour variation is deliberately limited by the stated generator; low contamination on this control does **not** establish robustness to arbitrary NIR population shifts. In the controls every varying-dust attribution is false, even though the measured structure itself can be real. `control_structure_incidence.csv` gives per-scene incidence and exact binomial intervals across noise draws. Null controls have no varying-dust reference, so completeness is undefined; NaN is retained rather than converted to zero.

There is no credible single dust-feature resolution limit. `conditional_scale_recoverability.csv` gives a descriptive completeness≥50%, contamination≤50% summary separately for every view, PSF, depth and scale, not a preregistered acceptance test or a universal resolution limit. Passing that truth-overlap criterion is not sufficient for dust specificity when control scenes generate similar candidates. No measurement thresholds were changed after seeing these failures.

## Morphology, GLAO and observing conditions

For O1 g at z=0.1, 1h, seeing, dust changes C by 0.209, asymmetry by 0.029, and R50 by -1.311kpc. This is a **paired simulation counterfactual**, not something directly measurable for one real galaxy lacking its dust-free counterpart. The five-view paired table and figure show the full viewing dependence, including sign changes where present. Morphological noise bias, dust-induced bias and PSF changes are separate outputs. Orientation second-moment axis ratios characterize apparent flattening; exact inclinations are not inferred.

`scale_transfer.csv` measures how much of each truth-isolated dust imprint survives the PSF; `paired_GLAO_summary.csv` gives paired changes in actual candidate overlap and contamination. Narrower NIR PSFs can preserve more structure without making it uniquely attributable to dust. For the O1 dusty Ks image, the measured-minus-no-observational-PSF concentration bias changes from -0.291 (seeing) to -0.126 (GLAO); this is conditional morphology preservation, not a dust-specific statistic. `PSF_morphology_bias_summary.csv` retains all corresponding cases. g−Ks colour resolution is intentionally capped by optical matching; its near-equality between modes is a design consequence. Native NIR structure, PSF wings, depth and surface-brightness terciles are evaluated separately. Longer exposures cannot recover spatial frequencies removed by the PSF. Some metrics may worsen when resolution reveals more non-dust stellar structure; no guaranteed GLAO advantage is asserted for every metric/view.

**An important unsuccessful depth trend:** O1 1kpc J−Ks completeness decreases as depth increases in some cases. This is not improved physical recovery at lower depth. `depth_threshold_diagnostic.csv` shows that none of the46 reference pixels has a noiseless seeing observable above0.05mag (median0.0429mag), while12 do for GLAO (median0.0474mag). PSF dilution and stellar colour change the observable relative to the known dust-only imprint. Noise scatters pixels across the amplitude threshold: first-order expected seeing completeness0.137/0.037/0.003 at0.25/1/4h agrees with measured0.159/0.039/0.007 within Monte Carlo intervals. Thus an area-overlap increase can itself be noise-assisted; do not turn the quoted GLAO area gain into a robust feature-detection forecast.

Finite-field sensitivity is explicit in `boundary_sensitivity.csv`: a 32kpc versus48kpc measurement field changes 1kpc structures by at most0.00023mag in g−Ks and0.00033 in Ks fractional deficit for checked O1 cases. At the largest2kpc analysis scale, boundary differences reach0.0133mag/0.0258 fractional deficit near the edge, material relative to the cuts; those largest-scale edge classifications deserve caution. This check does not validate every orientation's boundary effects.

## Bandpass, distance and noise limitations

This is **matched-rest-band distance degradation**, not exact observer-frame ULTIMATE synthetic photometry. Physical size/luminosity/populations/dust are fixed. Flat ΛCDM H0=70, Ωm=0.3 supplies D_A; MJy/sr is frequency-specific, hence I_nu/(1+z)^3 and source pixel solid angle, with flux-conserving area overlap. No extra bolometric (1+z)^−4 factor, intrinsic size evolution, or interpolation into unsupported observer bands is used. Even at z=0.1, rest Ks shifts to ~2.375µm, so its nominal Ks electron/noise conversion is a conditional proxy. z=0.3 rest-Ks is deliberately not used as a realizable observer-Ks forecast.

Gaussian design widths are g=0.700arcsec both modes; J=0.658/0.508 and Ks=0.588/0.390arcsec seeing/GLAO. The calculator D50 is equated to Gaussian FWHM only in the Gaussian baseline. Equal-D50 Moffat β=2.5 is a wings sensitivity case, not another measured instrument PSF. There is no guaranteed 0.2arcsec resolution. Detector 0.1arcsec pixels and existing sky/thermal/throughput/read/dark parameters are provisional; actual DR1 bands are not exact ULTIMATE passbands. Source electrons are derived through the stored photon-per-Jy coefficient. Noise includes source, sky, thermal, dark and split-read terms; sky subtraction is assumed known, with no flat-field, sky-residual, PSF-estimation or registration errors. Smoothing-induced noise covariance is propagated through combined kernels, including fine–broad covariance and first-order nonlinear derivatives. The mocks assume independent native detector pixels, so realistic reduced-image resampling covariance remains a future requirement.

## Workshop and future paper

**Strongest workshop claim:** for one structured galaxy, dust measurably changes spatial light distribution and morphology; GLAO-like NIR PSFs conditionally retain more small-scale information, while straightforward red/dark-feature selection has population/morphology contamination. Present paired morphology plots plus observed images, spatial-transfer curves and explicit successful/unsuccessful overlap examples. Retain the previous negative geometry result as motivation, not as a claim disproving all broadband information.

**Plausible future paper:** a multi-galaxy study of dust-induced morphology bias and spatial information transfer, with actual passbands/PSFs/sky systematics and independent observational validation. Feature attribution would need additional stellar-population constraints and a diverse independent galaxy sample. The present five views cannot provide that generalization. A focused [MaNGA proposal](MaNGA_validation_note.md) is supplied; no acquisition or request to Anil was made, and its connection to GECKOS remains unresolved.
