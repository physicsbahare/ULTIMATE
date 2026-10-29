# Calibrated DR1 dust-screen experiment: scientific report
Executed in the existing phd environment; previous data/results preserved. No DR2 work, downloads, installations or ML.

## Scientific conclusion
**The false-positive problem is exposed and conditionally calibrated, but not generally solved.** Known smooth/patchy screens remain detectable under a declared bounded population ensemble. However, stellar-population shifts outside its typical draws can still cause false dust claims, and model inadequacy affects the real SKIRT images. A robust observational identification of non-uniform dust, unique mixed geometry, or general GLAO advantage is **not demonstrated**.

## What was completed
Actual DR1 griz and 2MASS J/H/Ks images of galaxy294866 were used, with the clear/original dusty pair and independent smooth/patchy image-level screens. The local archive has240 members,22 band pairs per orientation including extra Euclid products, and no second galaxy. O1–O5 are correlated views, never five independent galaxies. Original HAWK-I data and prior inspection are unchanged; raw compact-source PSFs remain provisional, not ULTIMATE measurements.

A spatially separated, training-only empirical population hierarchy replaced the old aperture-independent template catalogue. Flux contrasts are fitted with each band's covariance/PSF, normalized using observed fluxes. Exact clear counterparts and physical maps are not inference inputs. Priors, code tests, attenuation law, seeds and exposure splitting are explicit. This is a regularized Gaussian colour-field approximation, not full physical SPS/SFH or exact nonlinear dust geometry fitting. The first population PC explains 96.26% of training colour variance and contains 97.96% of the centered dust direction, a strong identifiability warning.

## Independent calibration and final evaluation
Development:200 calibration plus200 evaluation noise draws per fixed scene; optical-only/NIR-only/joint, population and law priors, PSF shape, bin size, depth, all five views. Additional population stress tests failed at z=.3, so those outputs are retained as development evidence.

Final: frozen full-population model, five global-screen nulls,500 calibration draws **per null**, then500 independent population/noise draws **per scene**. The bounded generator varies two empirical population PCs over six fixed smooth/patch fields. Higher residual population PCs are in the likelihood but not generated. Calibration/evaluation coefficients and noises are separate; modes and controls use paired common random numbers. Threshold is the largest finite-sample95% null order statistic. Exact binomial intervals below condition on that threshold and chosen population ensemble; bootstrap intervals for GLAO also resample calibration and evaluation indices.

| z | PSF | mode | worst null | smooth | patchy | SKIRT rejection |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1 | matched | seeing | 5.4% [3.6, 7.8] | 100.0% [99.3, 100.0] | 100.0% [99.3, 100.0] | 100.0% [99.3, 100.0] |
| 0.1 | matched | glao | 5.2% [3.4, 7.5] | 100.0% [99.3, 100.0] | 100.0% [99.3, 100.0] | 100.0% [99.3, 100.0] |
| 0.1 | native | seeing | 3.4% [2.0, 5.4] | 100.0% [99.3, 100.0] | 100.0% [99.3, 100.0] | 100.0% [99.3, 100.0] |
| 0.1 | native | glao | 4.6% [2.9, 6.8] | 100.0% [99.3, 100.0] | 100.0% [99.3, 100.0] | 77.8% [73.9, 81.4] |
| 0.3 | matched | seeing | 2.2% [1.1, 3.9] | 100.0% [99.3, 100.0] | 78.0% [74.1, 81.6] | 4.4% [2.8, 6.6] |
| 0.3 | matched | glao | 3.4% [2.0, 5.4] | 100.0% [99.3, 100.0] | 86.0% [82.6, 88.9] | 2.8% [1.5, 4.7] |
| 0.3 | native | seeing | 4.0% [2.5, 6.1] | 100.0% [99.3, 100.0] | 96.2% [94.1, 97.7] | 5.4% [3.6, 7.8] |
| 0.3 | native | glao | 3.8% [2.3, 5.9] | 81.0% [77.3, 84.3] | 91.2% [88.4, 93.5] | 0.2% [0.0, 1.1] |

Entries are rejection fractions with95% exact binomial intervals; SKIRT rejection is not a true-positive rate for a simple-screen family. The worst joint null across these final conditions is 5.4% [3.6, 7.8], with500 draws in that condition. Finite confidence intervals do not certify a universal rate below5%. Results cannot be pooled across bands, controls, orientations or modes as independent objects.

## Remaining false positives and GLAO benefit
A new500-noise evaluation of fixed population anchors uses the FINAL cutoffs without adjustment. The worst joint anchor is null_population_1.0_-1, z=0.3, matched/seeing: **98.4% false positives [96.9, 99.3]**. These anchors are empirical colour perturbations, not verified SFH realizations; their failure is sufficient to reject a claim of robust population-independent calibration. Ensemble-average error control is different from protection at every plausible population setting.

For the z=.3 matched-PSF patchy case, conditional power is 78.0% seeing versus 86.0% GLAO: **+8.0 percentage points**, calibration+evaluation bootstrap95% interval [2.8, 14.4] points. This is a conditional numerical comparison, not a validated instrument gain. Other controls/strategies do not show a consistent improvement. Native z=.3 posterior predictions are inadequate; the narrower PSF exposes structure beyond this model. A worse classifier outcome does not mean GLAO destroys information. Model approximation and conservative cutoffs can prevent it from using the extra information.

At z=.1 all controlled screen powers in the joint primary cases saturate at100% (500/500; interval99.26–100%), so these bright controls cannot measure a positive GLAO power increment. The original SKIRT images fail the posterior predictive model in several cases; rejection cannot be promoted to a recovered geometry. Full tables preserve optical-only/NIR-only comparisons, sensitivity cases, posterior contrast amplitudes and predictive checks.

## Physical and observational limitations
- All fits use actual rest DR1 bands. z=.1/.3 mean **matched-rest-band image degradation** with fixed intrinsic size/luminosity/population/dust, frequency-specific I_nu/(1+z)^3, angular resampling and provisional electron/noise proxies. There is no exact observer-filter synthetic photometry or hidden K correction.
- Rest Ks would be observed near2.807µm at z=.3, beyond ordinary Ks coverage. Keeping its nominal Ks noise/throughput is a conditional proxy, not a realizable seven-band ULTIMATE forecast. This materially prevents a general observing-performance conclusion.
- Screen law is explicitly E*k(lambda), n=1 primary; within-band SED effects and n=.7/1.3 are sensitivities. Broadband screens do not reproduce wavelength-resolved radiative transfer. Scattering in SKIRT can create negative local attenuation; such complexity is retained, not clipped into a screen.
- Normalized contrasts discard absolute stellar colours and uniform E. Dust-like and population directions nearly coincide; posterior field amplitudes are not physical dust parameters. Physical source-SPS/birth-cloud uncertainties remain beyond the empirical hierarchy.
- Noise uses known sky mean, provisional throughput/sky/thermal/dark/read settings and60s reads. Exact first/second moments, full aperture covariance and bounded Poisson/normalization checks pass; unknown reduction and calibration systematics are absent.
- Only one galaxy and a limited spatial train/evaluation split are available. No independent-galaxy validation, arbitrary spectral recovery, unique3D geometry or physical high-z evolution is established.

## Safe workshop statement and next experiments
Present the matched controls, original false-positive failure, population/dust direction overlap, and the distinction between conditional recovery and robust physical inference. Show the numerical GLAO comparison only with its bandpass, population and adequacy qualifications. The supported overall conclusion is that **these data and the current empirical inference do not yet robustly separate non-uniform dust from all plausible population changes**.

Priorities: (1) improve physically positive, multiplicative spatial population+attenuation forward modelling and validate on held-out population anchors; (2) retain joint band-specific PSFs and require predictive adequacy; (3) obtain supported observer-band mappings or resolved spectra and final instrument/sky calibrations before forecasting ULTIMATE; (4) validate on an independent locally supplied galaxy before generalizing; (5) only then consider ML. No further data acquisition is required to reproduce this result.

## Reproduction and files
`README.md`, `Calibrated_DR1_screen_experiment.ipynb`, `experiment.py`, `final_ensemble.py`, `test_validation.py`; final rates `FINAL_calibrated_rates.csv`, paired differences `GLAO_power_comparison.csv`, pointwise checks `FINAL_population_anchor_stress.csv`, posterior predictions `FINAL_posterior_predictive.csv`; all figures in `figures/` PNG/PDF. `false_positive_audit.md`, `redshift_bandpass_limitations.md`, `instrument_provenance.md`, `FINAL_PROTOCOL.md` give the scientific contract. `validation.json` records execution and preservation checks.
