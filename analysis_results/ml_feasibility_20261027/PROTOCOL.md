# Preliminary grouped ML protocol

Frozen before fitting the preliminary benchmark. Earlier experiments are read-only.
The user's detailed execution specification is the authority for this continuation.

## Scientific scope and labels

The 26 already explored galaxies are development data only. Four objects with
zero projected field dust are excluded from all ML fitting/calibration and used
as a separate source-product/control challenge. They are not assigned fabricated
zero attenuation labels. Primary fits use 22 independent galaxies; these labels
are operational DR1 dusty-minus-clear contrasts, with unresolved source-model
systematics even after the four objects are excluded. No dust optical depth,
3D geometry or physical dust mass prediction is attempted.

Targets, per view: aperture-integrated effective attenuation in actual LSST g
and 2MASS Ks; median effective g attenuation after 1-kpc-FWHM smoothing of each
image, retaining negative valid ratios; native R<12-kpc dusty-minus-clear R50
and concentration in g and Ks. Smoothing ratios use finite positive flux,
clear >1e-4 of its smoothed peak, same circular aperture. Integrated attenuation
is -2.5log10(sum dusty/sum clear). The spatial median is not optical depth.
Masks, centers and physical apertures inherit the validated previous fixed-origin
protocol; known center/distance are idealizations, not recovered from images.

The four zero-dust source residual envelopes and R20/R30/center-sensitivity labels
are audit outputs, not a universal correction or Gaussian label-error estimate.
No physical claim below these unresolved systematics follows from ML accuracy.

## Observable inputs and ablations

Only properties measured on mock **dusty observed images** enter X: aperture
flux in Jy, R50, C, raw asymmetry, apparent q, central light fraction, integrated
colors and inner/outer color differences. Distance and center are known mock
settings. Source mass/SFR/dust maps, identifiers, true labels, clear morphology,
inclination and clear pixels are never model inputs. Missing moments are imputed
using training rows only. No observed-image dust map or truth mask is supplied.

Actual g/J/Ks DR1 bands, fixed-rest-band z=0.1, 1h per band, inherited provisional
band-specific Gaussian PSFs and split-read noise. g is unchanged between modes.
This is not exact observer-frame ULTIMATE photometry. No sharpening is performed.

Three image conditions per strategy: no observational noise; original exact-moment
Gaussian noise; and common equal noise using max(seeing variance, GLAO variance)
per detector pixel with paired innovations. The latter isolates PSF response at
matched added-noise variance. Use the existing eight draw seeds. g-only versus
g/J/Ks is an extra-band ablation at equal per-band depth, not equal total telescope
time. Noiseless and equal-noise comparisons separate PSF gains from noise effects.

## Models and splits

Five outer shuffled galaxy folds, seed20261027, shared across every model and
scenario. Every view/noise draw stays with its galaxy. Within each outer training
pool, five seeded calibration galaxies are held out completely; the remaining
12 or13 galaxies fit the model. No parameter is tuned on outer test outcomes.

Compare training median; color-only ridge; morphology-only ridge; full ridge
(standardized features, alpha10); and random forest (80 trees, maximum depth4,
minimum leaf20 rows, random_state20261027, one CPU). Parameters are fixed rather
than selected from these tiny outer tests. Ridge preprocessing and imputation
fit only the fitting galaxies. Equal numbers of views/draws give equal galaxy
weight. No CNN or geometry classifier.

Split-conformal diagnostic: calibration score is the maximum absolute residual
across all views/draws of each calibration galaxy. For nominal80% simultaneous
galaxy intervals, use order ceil((ncal+1)*0.8), hence the maximum of five scores.
Report both row and entire-galaxy coverage, widths and denominators; this small
selected sample cannot certify population coverage. These intervals exclude
unknown physical-label systematics and do not certify OOD calibration.

Primary error: average absolute residuals over draws then views within each
galaxy, then equal-weight galaxy MAE. Paired GLAO gain = seeing MAE minus GLAO
MAE, with5000 galaxy-bootstrap resamples. Intervals condition on trained models
and folds; overlapping training folds are not independent and bootstrap does
not include training-set resampling. Report signs/outliers rather than selecting
the best model after evaluation. Results are exploratory development CV, not
the untouched120-galaxy final test.

OOD diagnostics: unseen zero-projected-dust controls; leave-high-mass-quartile
out using metadata for split/scoring only; and feature-space distance from the
training sample. No physical metadata enter model X. Explicitly retain294866
as a previously known opposite-sign morphology case.

Correction scoring: observed dusty morphology minus predicted native dust bias,
compared to native clear morphology, alongside uncorrected error. This leaves
observational PSF/noise errors and can worsen an individual object. It is not a
claim that a clear image can be uniquely reconstructed.

## Expansion and HAWK-I

Freeze120 galaxy IDs metadata-only, with86development (all original26 plus60new),
14validation and20untouched final evaluation. No final-test science image/label
inspection; archive integrity checks are allowed. Data acquisition and HAWK-I
calibration assessment proceed independently. Raw HAWK-I diagnostics are not
promoted to calibrated reduced mosaics or a final ULTIMATE PSF.
