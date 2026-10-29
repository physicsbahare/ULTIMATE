# Dust-induced morphology across 26 TNG50-SKIRT galaxies

## Executed scope and central findings

Analysed 26 independent galaxies, five correlated views each, 22 matched rest-frame broadband pairs: 2860 primary galaxy/view/band comparisons. Eight Gaussian noise draws (exact split-read first/second moments) per scene/strategy at one selected observing condition. The original benchmark and four additional galaxies were development objects; the remaining 21 were evaluated with the saved protocol. No new science data, packages, ML, or geometry fits were used.

- LSST_g: median of galaxy-mean dust ΔR50 = 0.4003 kpc; galaxy-bootstrap 95% interval [0.1704, 0.5459]. Galaxy means are positive / negative / near-zero in 24 / 1 / 1 objects. Range [-1.0664, 1.6856] kpc. The median within-galaxy viewing SD is 0.1922 kpc; between-galaxy SD is 0.4791 kpc.
- 2MASS_Ks: median of galaxy-mean dust ΔR50 = 0.1239 kpc; galaxy-bootstrap 95% interval [0.0827, 0.1702]. Galaxy means are positive / negative / near-zero in 25 / 1 / 0 objects. Range [-0.0585, 0.4961] kpc. The median within-galaxy viewing SD is 0.0556 kpc; between-galaxy SD is 0.1100 kpc.

Dust effects do not have an imposed sign. The wavelength comparison preserves filter identity; 2MASS, Euclid and LSST products are not labelled ULTIMATE filters. Native sizes refer to light within R<12 kpc, not total-galaxy sizes.

The paired contrasts include an unresolved source-product residual: zero projected-dust controls have nonzero differences. Small Δdust values must not be called calibrated physical dust effects (Figure 11).

## Conditional seeing versus GLAO

Predeclared gain = seeing mean absolute error minus GLAO mean absolute error. Each galaxy averages its views after averaging its noise draws. Positive values mean improved preservation/recovery. The following table reports **2MASS Ks only** and uses independent clear versus dusty observation noise; strategy innovations remain paired. The clear counterpart is simulation truth for scoring, not an available observational input.

| Metric | Target | Seeing mean error | GLAO mean error | Mean gain [95% galaxy bootstrap] | Improved galaxies |
|---|---|---:|---:|---:|---:|
| R50 | Dusty morphology | 0.08055 | 0.03942 | 0.04113 [0.02493, 0.05880] | 26/26 |
| C | Dusty morphology | 0.36702 | 0.19016 | 0.17686 [0.13928, 0.21350] | 26/26 |
| A | Dusty morphology | 0.14306 | 0.12731 | 0.01575 [0.01326, 0.01864] | 26/26 |
| q | Dusty morphology | 0.01461 | 0.01424 | 0.00037 [-0.00429, 0.00302] | 25/26 |
| R50 | Dusty-minus-clear | 0.02186 | 0.01848 | 0.00339 [0.00063, 0.00675] | 17/26 |
| C | Dusty-minus-clear | 0.09201 | 0.08243 | 0.00958 [-0.00255, 0.02085] | 19/26 |
| A | Dusty-minus-clear | 0.00652 | 0.00548 | 0.00103 [0.00058, 0.00153] | 22/26 |
| q | Dusty-minus-clear | 0.01270 | 0.01472 | -0.00202 [-0.00562, -0.00006] | 9/26 |

Noisy q failures use jointly valid strategy draws; each included galaxy needs at least 6/8 such draws in every view. The last column gives the actual eligible denominator. All original 26 objects remain in noiseless results. galaxy_observing_accuracy.csv records eligibility and valid-draw counts; missing/noisy moments are not repaired by clipping.

R50 errors have kpc units; C, A and q are dimensionless. Raw and noise-corrected asymmetry are both retained. The expected-|noise| subtraction is a defined estimator and can overcorrect genuine asymmetric pixels; neither estimator has a universal unbiasedness guarantee. g has the same seeing PSF and identical innovations in both strategies, providing a zero-gain control. Shared-counterfactual-noise results are separately tabulated and must not be mistaken for uncertainty from independent observations. Monte Carlo SE and between-view/galaxy scatter remain separate in the tables. Eight draws bound computational cost and do not establish tail probabilities.

## Sample and independence

The official saved catalogue has 1154 galaxies; 1153 were eligible for the seeded 25-cell selection. Zero-SFR fraction: parent 0.125, selected extra sample 0.200. Selection probabilities vary from 0.0080 to 0.1000; there is one new galaxy per mass-quintile/activity cell. Selected extra log stellar mass spans 9.826–11.379. The original galaxy is an additional convenience benchmark. The four extra development objects all came from the lowest mass quintile (the first four selected cells), so the held-out 21-object subset has only one object in that quintile and five in each other quintile; it is not a fresh balanced or population-random draw. Equal-weight results describe this balanced sample, not a volume-complete population. The bootstrap is a conditional resampling summary of selected galaxies, not a design-corrected population confidence statement. Five fixed directions do not represent five independent galaxies or a verified isotropic inclination sample.

There are 5 zero-SFR galaxies, of which 1 have positive field dust mass. Physical projected dust maps, not SFR, supply these diagnostics. Field masses are mean sums over projections on the 160-kpc FITS field; R12/R30 masses and inter-view scatter are supplied. Tiny signed projection roundoff in physical maps is recorded without altering the images. Apparent light q is not a physical inclination. Stellar half-mass radius is not an assigned morphology class.

## Zero-projected-dust controls and attribution limit

The four zero-projected-dust objects are empirical source-product checks, not assumed perfect nulls for every unresolved attenuation component. They show nonzero pair attenuation and shape residuals; zero_projected_dust_summary.csv quantifies them before and after 0.5/1-kpc smoothing. These differences may reflect source/filter integration, projection, radiative-transfer noise or unresolved components. Their origin cannot be separated with the supplied products. No universal offset is subtracted and no error map is invented. Thus the tables measure operational DR1 dusty-minus-clear contrasts; small values are not validated as pure physical dust effects. Numerical implementation validation passes, but source-product physical-null calibration is unresolved.

Asymmetry preservation gains reverse sign between raw and noise-subtracted estimators in this scenario. Report both, and do not promote a robust asymmetry benefit. Concentration and R50 are the stronger instrumental comparisons; dust-difference recovery remains a separate test.

## Methods and quality

All original archives are read only. Current SHA256 and byte lengths are reconciled with the downloader state for the 25 extra archives; the extra archives are byte-identical to the downloader CRC-validated files, and the original archive receives an independent gzip EOF/trailer check. CRC_evidence records whether the check is inherited through identical SHA256 or independent; no redundant extra-archive CRC scan is claimed. All 240 members per galaxy are checked for identity, field/pixel dimensions, centered WCS, units, finite values and complete dusty/clear matching. A compact g/J/Ks/dust cache avoids full FITS extraction. Broadband pixels are nonnegative; physical projection maps allow documented floating-point roundoff only. No failed pairs or inconvenient signs are silently discarded. See archive_inventory.csv, fits_inventory.csv and galaxy_inventory.csv.

Primary measurement uses the same simulation origin, circular R<12 kpc aperture, coordinate grid, PSF and segmentation for each pair. No data-dependent segmentation or center minimization is used. R20/R50/R80 use the first signed cumulative-flux crossing on pixel-center radii; C=5 log10(R80/R20); asymmetry is the full |I−I180| sum divided by flux (no extra factor 1/2); q uses fixed-origin flux-weighted second moments. Noise can make signed curves nonmonotonic; the rule remains fixed and finite/nonpositive-flux failures are recorded. Integrated attenuation uses the aperture flux ratio. Effective local attenuation keeps valid negative values, but is neither optical depth nor a physical dust-mass measurement.

Analytic morphology tests: 4; original pilot reproduction max absolute error 1.78e-15; maximum tested Gaussian padded flux loss 1.44e-14. Exact aggregate Poisson plus independent read-noise sampling validates split-exposure moments. The numerical gate passed before held-out evaluation. These tests validate implementation, not the unresolved radiative-transfer/source uncertainty or final instrument calibration.

## Aperture, center, spatial scale and instrument robustness

15/26 galaxies have at least one g/Ks view/scene with F12/F30<0.8. These are retained and flagged; interpreting the primary R50 as a total size would be wrong. R20/R30 apertures and ±0.2-kpc center shifts are evaluated for every g/Ks pair in aperture_center_robustness.csv. Figures show the consequences rather than selecting the best aperture after seeing the sample.
- LSST_g, 30: median |change in dust ΔR50| = 0.1415 kpc; 6/130 material view-level sign flips (>10⁻⁶ kpc in each measurement).
- 2MASS_Ks, 30: median |change in dust ΔR50| = 0.0257 kpc; 4/130 material view-level sign flips (>10⁻⁶ kpc in each measurement).
- LSST_g, offset0.2: median |change in dust ΔR50| = 0.0093 kpc; 1/130 material view-level sign flips (>10⁻⁶ kpc in each measurement).
- 2MASS_Ks, offset0.2: median |change in dust ΔR50| = 0.0041 kpc; 0/130 material view-level sign flips (>10⁻⁶ kpc in each measurement).
- LSST_g, offset-0.2: median |change in dust ΔR50| = 0.0064 kpc; 0/130 material view-level sign flips (>10⁻⁶ kpc in each measurement).
- 2MASS_Ks, offset-0.2: median |change in dust ΔR50| = 0.0046 kpc; 0/130 material view-level sign flips (>10⁻⁶ kpc in each measurement).

Ks fine/broad fractional structure is measured natively at 0.5/1/2-kpc smoothing FWHM, without matching away the finer NIR PSF. Noiseless structure errors and correlations separate dusty morphology preservation from a truth-isolated dusty-minus-clear imprint. R<8 kpc avoids the most severe broad-filter edge sensitivity. Near-zero reference RMS≤10⁻⁵ is excluded from normalized error only; absolute errors remain. Surface-brightness terciles and all excluded normalized cases are tabulated. This is information transfer, not individual dust-feature identification.

Focused sensitivity covers the five development galaxies, O1 only: equal-D50 Moffat beta=2.5, lower distance z=0.05 and 0.25/4h per band. It does not establish sample-wide robustness to all PSF wings or exposure assumptions. The Gaussian spatial comparison has no noise threshold-crossing classifier. Longer exposure cannot recover frequencies eliminated by a PSF.

## Physical scope of the observing experiment

Primary physical results are direct z=0 rest-band paired measurements, conditional on the unresolved source-product residuals above. The observing comparison artificially places each unchanged scene at z=0.1, with fixed size, luminosity, populations and dust; Flat LCDM H0=70, Om0=0.3, frequency-specific intensity /(1+z)^3, flux-conserving area resampling and 0.1-arcsec detector pixels. It is not galaxy evolution or exact observer-frame synthetic photometry. Rest 2MASS Ks shifts beyond ordinary observer Ks at this distance. Nominal-band throughput/noise conversion is therefore a conditional proxy; no missing spectral cube, K correction, or final ULTIMATE passband is invented.

Gaussian D50=FWHM widths: g 0.700 arcsec both modes, J 0.658/0.508 arcsec, Ks 0.588/0.390 arcsec. Detector, throughput, sky, thermal, moon, dark and read assumptions are inherited provisionally from the audited pilot. One hour per band uses 60 independent 60-s reads; source and background shot-noise variance plus split-read variance are included in the Gaussian approximation. Independent exact aggregate Poisson plus read draws validate its moments; this is not exact Poisson sampling for every science realization. Sky mean, PSF and registration are known. Sky residuals, flat-field errors, reduced-image covariance, actual detector saturation/DIT constraints and calibrated PSF variability are absent. No universal ULTIMATE sensitivity/resolution forecast follows.

## Quantitative cross-checks

- Zero projected-dust controls, 2MASS_J: median pair attenuation 0.0127 mag; median normalized shape-residual RMS 0.0184; maximum view-level |ΔR50| 0.0268 kpc. These four objects provide an empirical warning, not a transferable error distribution.
- Zero projected-dust controls, 2MASS_Ks: median pair attenuation 0.0205 mag; median normalized shape-residual RMS 0.0203; maximum view-level |ΔR50| 0.0392 kpc. These four objects provide an empirical warning, not a transferable error distribution.
- Zero projected-dust controls, LSST_g: median pair attenuation 0.1214 mag; median normalized shape-residual RMS 0.0181; maximum view-level |ΔR50| 0.0311 kpc. These four objects provide an empirical warning, not a transferable error distribution.

Held-out evaluation (21 galaxies), median of galaxy-mean paired R50 contrasts:
- 2MASS_Ks: 0.1470 kpc [0.0833, 0.1820], galaxy bootstrap.
- LSST_g: 0.4190 kpc [0.1704, 0.5512], galaxy bootstrap.

Excluding antipodal O5 (four-view sensitivity), mean Ks gains with independent clear noise:
- R50, preservation_abs_error: 0.04189 [0.02569, 0.05968].
- R50, dust_delta_abs_error: 0.00381 [0.00130, 0.00655].
- C, preservation_abs_error: 0.17826 [0.13996, 0.21668].
- C, dust_delta_abs_error: 0.00762 [-0.00535, 0.01939].

Native Ks structure transfer at 1-kpc analysis FWHM (median galaxy normalized RMS error):
- dust_imprint: seeing 0.4268, GLAO 0.2446; valid normalized references 26/26 and 26/26. A dust-imprint reference is a paired source-product contrast with the same unresolved residual caveat.
- dusty_morphology: seeing 0.2418, GLAO 0.1257; valid normalized references 26/26 and 26/26. A dust-imprint reference is a paired source-product contrast with the same unresolved residual caveat.

Detector-grid resampling changes are supplied separately in detector_sampling_robustness.csv. All noise failures and valid-draw denominators are retained; no object is removed from the native analysis.

## Findings, publication readiness and next requirements

1. **Simulation-based contrasts (source-systematic caveat):** the executed matched pairs support dust-induced, wavelength- and viewing-dependent shifts in fixed-aperture light morphology across multiple independent galaxies. Sign, scatter and outliers are retained. Associations with stellar mass, positive sSFR, actual projected dust mass and apparent morphology are exploratory (property_associations.csv); zero sSFR/dust are not logged as finite detections. There are multiple unadjusted comparisons, so no precise scaling law or causal property driver is claimed.
2. **Conditional resolution comparisons:** absolute morphology preservation and dusty-minus-clear recovery are distinct metrics, with galaxy-bootstrap gains in the table. A smaller PSF can preserve structure while offering little or adverse improvement for a weak dust difference. Examine metric-specific gains and finite-noise controls rather than declaring success from resolution alone.
3. **Future observational tests:** measure sizes, concentration, q and spatial NIR light structure at calibrated PSFs and surface brightness; compare against seeing-limited images of the same galaxies. A real clear counterpart is unavailable, so direct observational Δdust requires extra modelling/constraints. No physical geometry, unique feature attribution, or mass recovery is supplied here.
4. **Claims needing more evidence:** population relations require a representative or design-weighted sample and broader orientation handling; a publishable instrument forecast requires actual observer bands or spectral synthesis, PSF/sky/detector calibration, independent observational validation and systematic-error tests. DR1 Monte Carlo image uncertainty and subgrid radiative-transfer assumptions are not quantified here.

**Workshop readiness: GO with explicit scope and the zero-projected-dust residual control.** Use Figures 02, 03, 05 and 09, with the sample-selection and aperture limitations. This is a substantial multi-galaxy feasibility result rather than another geometry classifier. **Publication readiness: a methods/results foundation, not yet a validated ULTIMATE forecast.** A paper centered on conditional morphology transfer is plausible after resolving aperture/systematic sensitivity and positioning novelty against prior morphology/radiative-transfer literature. A bounded primary-literature check finds direct overlap with the larger atlas study below; physical morphology trends alone are not a defensible novelty claim.

## Prior work and paper positioning

Dust-induced structural-parameter changes were already quantified with radiative-transfer disk/bulge models by [Pastrav et al. (2013)](https://arxiv.org/abs/1301.5602). More directly, [Bokona Tulu et al. (2026)](https://arxiv.org/abs/2605.20886) used the larger TNG50-SKIRT atlas for wavelength-dependent nonparametric morphology and dust effects. Their StatMorph apertures/centers and noise treatment differ from our fixed-origin apertures, so numerical concentrations are not interchangeable. They also report asymmetry instability and identify O4/O5 as antipodal. Our four-view robustness excludes O5 without changing the frozen five-view primary results. The viable distinctive contribution is instrument-specific preservation/recovery calibration with realistic systematics, not rediscovery of dust-dependent morphology in 26 atlas galaxies.

## Provenance and prior negative evidence

The four earlier scientific reports were inspected in chronological order, with protocol, validation and code. The 98.4% uniform-screen false-positive case, failed positive-model predictive adequacy, stellar-structure contamination, and noise-assisted area crossings remain valid. No expensive inference grid was rerun. previous_results_sha256.json permits an end-of-run preservation check.

Atlas reference: [Baes et al. (2024), TNG50-SKIRT DR1 methodology and data release](https://arxiv.org/abs/2401.04224). Its z=0 image/map format is checked against the actual FITS headers here. Instrument provenance remains the pinned sources in ../screen_test_20261026/ and the read-only pilot code. No new simulation dataset or package was downloaded.

All calculations and full numerical tables are linked in README.md; PROTOCOL.md records the choices fixed before held-out evaluation.
