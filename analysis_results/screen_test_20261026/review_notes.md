# Independent scientific review

A fresh reviewer inspected the modules and ran independent checks in the existing `phd` environment. It found no critical physics implementation bug: radiometry, photon conversion, N RN² exposure variance, squared-kernel aperture variance and exclusion of intrinsic maps from fits were consistent.

Material limitation confirmed: at high redshift the restricted stellar prior yields positive variable-screen evidence for physically uniform controls. A physical geometry detection is therefore not calibrated. Wider population freedom changes the answer. This is recorded as a scientific result, not hidden or “fixed” by tuning the null away.

Independent Av grid check, z=0.6, 1 hour, seeing (reviewer's independent draw):

| Truth / prior | 31 Av points | 61 | 121 |
| --- | ---: | ---: | ---: |
| Mixed / near_clear | 8.698 | 8.721 | 8.694 |
| Mixed / broad | 6.055 | 6.133 | 6.165 |
| Uniform / near_clear | 8.953 | 8.803 | 8.735 |
| Uniform / broad | −3.070 | −2.889 | −2.873 |

Values are ln B(variable/uniform), not detection probabilities. Grid refinement does not repair the false uniform-control preference. Main script's saved-case resume was adjusted to preserve prior transfer records; recomputation starts a fresh transfer ledger. Marginal z=1 aperture selection uses the same noisy fluxes later fitted, without a selection-conditioned likelihood. This is explicitly uncalibrated and does not explain the high-SNR z=0.6 null failure.

The review supports the restrained interpretation: observable colour structure; a conditional known-population separation gain; no demonstrated robust mixed-geometry detection.
