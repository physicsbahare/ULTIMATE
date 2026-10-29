# Static SKIRT screen-test implementation plan

Goal: Execute a bounded, instrument-informed test of non-uniform optical/NIR signatures in subhalo 294866 while separating observational transfer, stellar-population degeneracy and geometry inference.

User authorization: execute locally; preserve all prior files; no large downloads/training. All new work is isolated in this directory. No edits/commits to either upstream repository.

1. [x] Read pinned forward-repository methods and numerical primitives. Preserve static E0, cosmological distance duality, Fν conventions, wavelength bracketing, PSF/pixel bookkeeping, independent exposure noise and clean/noisy stage distinctions.
2. [x] Read and execute calculator at pinned commit. Save published outputs and raw sky/transmission curves with hashes. Audit missing dark/split-read terms, D50 versus PSF, filter approximations and collecting-area inconsistency.
3. [x] Query authenticated TNG metadata/listings only; do not fetch an unidentified archive. Record that the returned listing is the legacy 1154-object atlas and no DR2-specific endpoint has been established.
4. [x] Validate radiometry, exact-overlap flux transfer, wavelength bounds, split-exposure noise moments and hierarchical evidence with analytic/synthetic tests before using science outputs.
5. [x] Stream only necessary broadband inputs from the existing archive into compact cropped spectral stacks. Preserve SKIRT spatial structure. Generate mixed, constant-screen and variable-screen controls from the same fixed dust-free simulation only in the generator; never pass those intrinsic maps into observational fitting.
6. [x] Reconstruct provisional spatial SEDs from bracketing DR1 broadband intensities; integrate through declared observer-frame top hats and atmospheric transmission. Flag the absence of spectral cubes and final filter curves. Static redshifts, no luminosity or intrinsic size evolution.
7. [x] Compare seeing/GLAO with identical areas, throughput, exposure and noise assumptions. Use audited median D50 as Gaussian FWHM explicitly; add optimistic 0.2-arcsec and PSF-wing checks only as labelled assumptions.
8. [x] Draw source+background Poisson and per-exposure read noise in detector electrons. Retain native detector draws and variance. Matched-PSF photometry must propagate the convolution kernel squared; use well separated apertures and audit cross-aperture covariance. Select only using observable data and fixed geometry.
9. [x] Fit local SEDs with unknown amplitudes and marginalize over external stellar SED alternatives. Compare global uniform screen with aperture-varying screens under the SAME priors. Include near-clear EAZY templates as a conditional baseline and a broad/dusty-template robustness prior. Report template mismatch with uniform-screen controls. A flexible-screen fit or uniform-screen rejection is not unique evidence for mixed geometry.
10. [x] Save repeated-noise/model results, angular/physical scales, masks, parameter provenance, clean signal/colour residuals, likelihood diagnostics and figures. Execute notebook top-to-bottom; independently validate and review outputs; write a restrained workshop conclusion including null outcomes.

Key scope rulings: Phenomenological screen law and population priors are analyst scenarios. Broadbands do not permit exact K corrections; synthetic filters and interpolated SEDs are conditional. A definitive mixed-versus-variable-screen discrimination may be unidentifiable. Report it as such instead of treating the known SKIRT truth as an observational model.
