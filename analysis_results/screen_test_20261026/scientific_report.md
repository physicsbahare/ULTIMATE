# Can ULTIMATE-like imaging reveal dust non-uniformity?
Executed 2026-10-26. **Result:** spatial colour structure remains observable in these instrument-informed scenarios, and narrower NIR PSFs improve a known-population separation bound. However, this experiment does **not** establish a robust observational rejection of a uniform foreground screen or uniquely detect mixed star–dust geometry. Template uncertainty, spectral interpolation and physical null controls change the inference. This negative calibration finding is a defensible workshop result.

## What was actually executed
- Reused the existing `phd` environment and structured DR1 SKIRT images for subhalo 294866. Five orientations remain views of one galaxy. Streamed 135 necessary FITS members from the existing archive into cropped 80-kpc structured broadband caches; no galaxy archive download or smooth Sérsic replacement.
- O1 grid: artificial z=0.1, 0.3, 0.6, 1.0; 0.25, 1 and 4 hours **per band**; seeing versus calculator-informed GLAO; three noise draws; mixed SKIRT, uniform-screen and varying-screen controls. O2–O5 repeat z=0.3, 1 hour. Eight observed bands are griz + YJHKs. The assumed total on-source allocation is eight times the listed per-band depth, before overheads.
- 574 marginalized screen fits and 1 retained insufficient-aperture case; 200 additional prior, discrepancy, interpolation and Av-grid tests; 20 native-PSF upper-bound cases including Gaussian/Moffat and an optimistic 0.2-arcsec NIR scenario.
- Executed the published sensitivity calculator, audited its photon/thermal terms and corrected exposure splitting. External FSPS templates and population mixtures are marginalized; intrinsic images/dust maps are **not** observational fit inputs.

## Static transfer, not galaxy evolution
Each truth scene keeps physical size, luminosity, stellar populations and dust fixed across redshifts. Flat ΛCDM H0=70 km/s/Mpc, Ωm=0.3 sets D_A and D_L. A native physical pixel subtends 100 pc / D_A radians. At matched rest frequency, Iν,obs=Iν,em/(1+z)^3, equivalently Fν,obs=(1+z)Lν,em/(4πD_L²). The wavelength shift is λrest=λobs/(1+z); no additional Tolman or size-evolution factor is multiplied in. This is an observational transfer of a z=0 template, not a claim that its old stellar populations or galaxy structure existed at the target epoch.

These conventions and clean-versus-noisy distinctions follow the inspected [forward-repository method](https://github.com/physicsbahare/astro-forward-modeling/blob/78dce5ad96038fe7a702d3e2f2b434a2c7d7e8af/docs/PASSIVE_DISK_Z3_METHOD.md) and [noise/wavelength limitations](https://github.com/physicsbahare/astro-forward-modeling/blob/78dce5ad96038fe7a702d3e2f2b434a2c7d7e8af/docs/JWST_ARTIFICIAL_REDSHIFTING_METHOD_AND_LIMITATIONS.md). Their parametric galaxy morphology is not reused.

Native structured SEDs are reconstructed by linear Fν interpolation in log wavelength between approximate broadband pivots, integrated over observer-frame proxy passbands with atmospheric transmission. No extrapolation is allowed. **This is not an exact K correction:** broadbands do not resolve emission lines, absorption features or a bandpass crossing the 4000-Å break. The original band images are band averages, not exact monochromatic values. Alternative wavelength-coordinate interpolation changes selected aperture photometry by median ~1–3%, with maxima ~6–11% in the tested z=0.3/0.6 cases; these are method differences, not measured uncertainties. The unavailable resolved spectral cube/final filters prevent a fully validated wavelength-transfer forecast.

## Instrument and noise provenance
The [calculator](https://github.com/sali131/ULTIMATE-Subaru-Sensitivity-Calculator/tree/2187748a40d4207519a8eff0d2a5b6701db8da0d) supplies a design scenario: PWV=1.6 mm, airmass=1, 273 K warm-background calculation, combined instrument/filter efficiency 0.45, 16-e− read noise and 0.1 arcsec pixels. Its filters are MOIRCS/SWIMS-based top-hat proxies, not finalized ULTIMATE curves. Its tabulated widths are D50, so the primary model explicitly assumes Gaussian PSFs, for which D50=FWHM. Median Ks widths are 0.588 arcsec without AO and 0.390 arcsec with GLAO. The 0.2-arcsec case is separate and optimistic.

All source rates are converted to detector electrons using collecting area, pixel solid angle and the photon-weighted throughput integral. Exposures are split into 60-second integrations (15/60/240 reads at the tested depths); variance includes N RN² plus source, sky, thermal, moon and provisional dark-current Poisson terms. The exact distribution of the summed independent exposures is drawn, rather than treating the whole observation as one read. The original calculator's one-read point-source limits are preserved separately. Source rate conversions agree with its central-wavelength approximation to within 0.15%.

Optical settings are an explicitly provisional complementary-imaging scenario, not an ULTIMATE optical specification. Sky mean is known in the simulation. Final flat-field/sky-subtraction floors, full-well/nonlinearity, persistence, correlated reduction noise, dithering/coverage and actual seeing/GLAO PSFs remain unvalidated. H-band sky alone reaches about 58,000 electrons per pixel per assumed 60-second read, so operating DIT must be confirmed against detector limits. No HAWK-I raw frame is used as a calibrated Subaru sky. See [instrument audit](instrument_audit.md) and `instrument_parameters.csv` for all assumptions.

## Fairness and remaining model limitations
The generator alone may use dust-free SKIRT maps to construct controlled truths. Uniform and varying controls use the same structured stellar scene; both match the mixed scene's R<20-kpc integrated g attenuation before transfer. Their screen law is an analyst-selected Aλ=Av(λ/0.55µm)^−1. The varying column pattern follows the projected dust map with a bounded contrast; it is not a measured opacity or 3D geometry. Each generated scene is then frozen across redshift.

Observational fitting uses linear noisy fluxes, their propagated errors, external SEDs and priors only. Every aperture has an unknown nonnegative normalization and a marginalized population/mixture/continuum tilt. A global-screen model shares Av across apertures; a variable-screen model allows separate Av per aperture, with one shared slope. Both share Av∈[0,3], slopes 0.7/1.0/1.3 and the same population and amplitude priors. Amplitude is integrated analytically under a proper positive uniform prior, and finite population/dust alternatives are summed with explicit normalized prior weights. This is discrete-grid marginalization, not an exhaustive SFH/metallicity posterior.

The near-clear population prior uses five external FSPS templates with supplied effective Av<0.15 and mixtures. Those templates are not perfectly dust-free. The broad robustness prior includes all 12 templates, including internally reddened ones, deliberately allowing substantial stellar/baseline-SED degeneracy. Consequently the fitted Av refers to an **additional** foreground screen relative to these baseline SEDs; the test cannot cleanly classify all baseline reddening as stellar or dust. No absolute total-screen or unique mixed-geometry claim follows from these evidence ratios.

All eight-band fits use a 0.8-arcsec common Gaussian PSF. This prevents differing optical/NIR resolution from masquerading as colour structure. It also removes much of GLAO's intrinsic spatial advantage; remaining differences reflect information/noise propagation. A separate NIR colour diagnostic retains the mode-specific common NIR width. Convolution precedes noise matching, and aperture variance uses the squared effective matching-plus-aperture kernel. Five-pixel squares are separated by 2 arcsec; maximum adjacent background correlation in the main fit is 7.8e-05. The factorized aperture likelihood is an approximation, not a fully reconstructed mosaic covariance model.

Eligibility is observed r and Ks SNR>5 within a fixed R<18-kpc lattice; other-band nondetections stay in the linear-flux likelihood. No selection-conditioned likelihood is used, so marginal z=1 detections are not calibrated. The single insufficient-aperture case is retained. Three repeated draws show numerical repeatability, not precise detection probabilities or independent-galaxy uncertainties. The 5% model-discrepancy term is an assumed nuisance budget, not an observed instrument calibration; 2% and 10% alternatives were tested.

## Actual screen-model results
ln B is ln(evidence for varying / uniform extra screen), median over three noise draws. Positive values **alone do not establish a valid rejection**, especially when a physical uniform control also gives positive values.

| z | truth | population_prior | logB_median | n_apertures_median |
| --- | --- | --- | --- | --- |
| 0.1 | mixed_SKIRT | broad | -22.477 | 69.0 |
| 0.1 | mixed_SKIRT | near_clear | -25.441 | 69.0 |
| 0.1 | uniform_control | broad | -33.095 | 69.0 |
| 0.1 | uniform_control | near_clear | -28.878 | 69.0 |
| 0.3 | mixed_SKIRT | broad | -4.49 | 13.0 |
| 0.3 | mixed_SKIRT | near_clear | -4.937 | 13.0 |
| 0.3 | uniform_control | broad | -5.955 | 13.0 |
| 0.3 | uniform_control | near_clear | -13.182 | 13.0 |
| 0.6 | mixed_SKIRT | broad | 5.56 | 5.0 |
| 0.6 | mixed_SKIRT | near_clear | 9.481 | 5.0 |
| 0.6 | uniform_control | broad | -3.255 | 5.0 |
| 0.6 | uniform_control | near_clear | 7.318 | 5.0 |
| 1.0 | mixed_SKIRT | broad | 4.338 | 5.0 |
| 1.0 | mixed_SKIRT | near_clear | 8.512 | 5.0 |
| 1.0 | uniform_control | broad | 0.583 | 5.0 |
| 1.0 | uniform_control | near_clear | 20.161 | 5.0 |

At z=0.1/0.3 the O1 mixed images do not favor the additional variable-screen model under the 5% main discrepancy assumptions. This does not prove uniform dust; model flexibility and prior penalties can hide genuinely varying screens, as the variable controls demonstrate. At z=0.6/1.0 restricted-population positive evidence is not physically calibrated because known uniform controls also yield positive values, sometimes larger than mixed SKIRT. Widening the population prior changes these outcomes. At z=0.6, increasing the broad-prior discrepancy allowance from 5% to 10% reduces a selected mixed-scene ln B from ~5.9 to ~0.0. At z=0.1 a 2% assumption produces false variable-screen evidence even in a uniform control. The independent reviewer verified that refining Av from 31 to 61/121 points does not repair the null failure.

Viewing direction also matters: at z=0.3, 1 hour, O4's mixed scene favors varying screens with the restricted population prior but not the broad prior. These repeated views cannot establish population generalization. Profile χ² reductions are saved as fit diagnostics; no independent-pixel p-value or χ² model-selection significance is claimed.

**Detected colour structure is not a dust-only detection.** The uniform-screen controls show strong spatial r−Ks variation from their varying stellar populations. At O1 z=0.3, 1 hour, GLAO, the constant-colour statistic is about 15,689 for 12 nominal degrees of freedom in mixed SKIRT, but about 76,454 for the uniform-screen control. This is a noise-only colour-homogeneity diagnostic, not a foreground-screen likelihood or a calibrated geometry significance. Colour and uniform-model residual plots are supplied with both population priors to expose that distinction.

## What GLAO improves — and what is not demonstrated
The native-NIR known-population separation bound compares mixed SKIRT with the matched-integrated-g uniform control, optimizing one flux amplitude per band. Because it holds the intrinsic stellar scene known, it is **not observational recovery** or a Bayes factor for geometry. For the calculator Gaussian scenario, the GLAO/seeing separation ratios are:

| z | GLAO_gain_percent |
| --- | --- |
| 0.1 | 2.38 |
| 0.3 | 5.54 |
| 0.6 | 9.17 |
| 1.0 | 12.47 |

Thus the idealized gain is about 2–12%, increasing with redshift for this fixed galaxy. Moffat wings at matched D50 and the optimistic 0.2-arcsec case change the bound; all PSF assumptions are recorded. Signals shrink with redshift and improve with depth in this photon-noise baseline. The full population-marginalized screen comparison does **not** show a robust, repeatable GLAO improvement in physical screen rejection. The much larger known-population signal-to-noise values must not be presented as a dust-detection significance.

## Validation and data-release status
Core analytic/Monte Carlo tests pass: distance duality, Fν radiometry, exact pixel-overlap flux, spectral bounds, source-electron conversion, exposure-splitting moments, squared-kernel aperture variance, and synthetic known-family uniform/varying evidence controls. Maximum full-field Gaussian transfer flux error is 1e-13. Original pilot notebook hash matches the previous analysis. 37 pinned source blobs were verified against upstream Git hashes. Independent review found no critical physics error; it confirmed the population/null and marginal-selection limitations above. The executed notebook retains code, tables and figures; PNGs and representative PDF renders are visually checked at delivery.

The authenticated catalogue investigation succeeded, but an exact DR2 broadband-image endpoint remains **unverified**: returned listings/documentation expose the legacy 1154-object atlas and do not identify a DR2-specific route. No unverified archive was downloaded. See [catalogue audit](catalogue_status.md). The current physical interpretation remains conditional on DR1, including its unprovided per-pixel Monte Carlo uncertainties and possible release-specific modelling limitations.

## What can safely go into the workshop talk
1. Show the structured galaxy and real electron-count forward transfer, with intrinsic properties fixed.
2. Show colour structure surviving, alongside the uniform-screen control that also has colour gradients.
3. Show population-prior/discrepancy sensitivity and a failed physical null: this is why colour structure is insufficient evidence for dust geometry.
4. Show the explicitly labelled known-population GLAO sensitivity bound, not a claimed observational dust significance.
5. State that no robust physical uniform-screen rejection or unique mixed-geometry detection has yet been demonstrated under the audited assumptions.

The next decisive experiment needs a verified DR2 release path, resolved SEDs or validated matched-filter synthesis, and population libraries/mixtures that recover known uniform controls across redshift. Then forward-fit per-band PSFs jointly (rather than discarding NIR resolution through common-PSF matching), include calibrated sky/systematic covariance, and test genuinely distinct dust geometries at comparable projected columns. Additional galaxies must be held out by galaxy. No large download or ML training was started.
