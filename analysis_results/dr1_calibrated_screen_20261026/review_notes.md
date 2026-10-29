# Independent numerical review and disposition
An independent reviewer examined the implementation and final protocol without editing original or new files.

Corrected before final execution:
1. Posterior predictive discrepancy now compares observation and replication conditional on the same posterior latent draw. A correctly specified Gaussian check returns approximately0.517 rather than the old plug-in value1.
2. Spatial-field coefficient normalization is fixed in intrinsic coordinates, shared across PSFs, band subsets and distance. It is no longer renormalized after blur.
3. Normalization covariance uses each measured flux realization; the exact generating mean is not used in the inference Jacobian. Unit test replaces the legacy means argument by0 and1e20 and obtains identical inference inputs.
4. Moffat widths are explicitly equal half-light diameters; FWHM/D50=.737519 for beta2.5. They are not mislabelled as equal-FWHM seeing.

Reviewer checks: explicit H J C Jᵀ Hᵀ matches implementation to5.4e-20; bounded generator maximum fractional perturbation.2111 and intensities remain positive; separate coefficient streams for calibration/evaluation; population perturbation precedes screen and PSF. No blocking numerical error was found in the revised code.

Scientific limits retained: only two generated population PCs and six fixed spatial fields; higher residual modes not generated; smooth generator mode matches the injected dust-gradient shape (declared stress choice); known source-dependent photometric covariance; only one galaxy; first-realization PPC diagnostics; physical multiplicative model mismatch; conditional matched-rest-band electron proxies. Numerical review does not validate physical dust identifiability, SPS histories, final ULTIMATE performance or universal false-positive control. Final new-noise anchor failures are retained rather than tuned away.
