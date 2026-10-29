# Expanded interpretable-ML protocol — 2026-10-28

Earlier studies and frozen86/14/20 galaxy assignments are read-only. No scientific
access to the final20 before a separate hashed FINAL_PROTOCOL_FROZEN receipt.
Development science gate: four streamed galaxies and exact old294866 R12 checks.
Physical-label audit: source_label_report.md establishes reproducible operational
contrasts and unresolved spectral-operator/systematic ambiguity, not calibrated
physical attenuation. No fitted global offset is subtracted.

## Targets and measurements

Eight target outputs: integrated effective attenuation in actualLSSTg and2MASSKs;
median andIQR of1-kpc-smoothed effectiveg attenuation; dusty-minus-clear R50 and
C=5log10(R80/R20) inKs andg. Retain signed ratios, negative attenuation and
orientation outliers. All use common fixed origin, coordinates and aperture for
the pair. Clear truth is supervision/scoring only. No optical depth/3D geometry.

Primary aperture: R=clip(1.5R80,8,30)kpc, withR80 measured on the dustyKs scene
after the common seeing PSF insideR35kpc. This represents a deep, observed selection
reference with known center/distance, not a clear image. The same aperture is used
for both seeing/GLAO, all bands, clear/dusty and noise draws. It is not reoptimized
using target accuracy. R35 truncation, clipping and enclosed fraction are flagged.
FixedR12 is the retained legacy sensitivity. The adaptive aperture is not a claim
of total light or sky-independent size. Measurement uncertainty in the deep
reference is not fully propagated; center/radius sensitivity is separately tested.

Quality: complete pairs, finite positive integrated flux, finite native labels;
invalid noisy moments are training-imputed, not positive-pixel clipped. All exact
zero projected-field-dust objects are primary-fit/calibration exclusions and
separate source controls, even if discovered in new development/validation/test
data. This policy precedes opening final science. Small contrasts inside old
control envelopes are warning flags, not automatic removals or exact noise sigma.
Old control envelopes are remeasured with this new operator/aperture. Physical
source calibration remains unresolved for positive-dust galaxies as well.

## Observable features and observing scenarios

Only noisy dusty-image flux, integrated colors, morphology, radial fractions,
angular-harmonic amplitudes, unsharp RMS and8x8 circular cell-flux fractions enterX.
No physical dust/stellar maps, mass,SFR,ID,clear image,label or noise index entersX.
The adaptive g-feature-only comparison is conditional on this common Ks-selected
aperture; it is not an independently g-selected pipeline. Fixed12 is the clean
g-only aperture control. Nominal80% intervals are per-target, not simultaneous
across all eight targets; calibration-set coverage is descriptive only.
Spatial PCA is fit on fitting rows only; equal views/draws give equal galaxy weight.
Physical metadata are permitted for post-fit diagnostics and declaredOOD splitting.

Primary mocks: fixed-rest-bandz0.1,1h per band,0.1arcsec detector pixels, inherited
band-dependent Gaussian PSFs and source/sky/thermal/dark/60split-read moments.
g remains seeing-limited. Four paired noise draws per view keep computation bounded;
five views are repeated measurements. Noiseless and equal-added-variance mocks
are sensitivities, with identical optical control. Optical-only versusg/J/Ks is
equal per-band time, not equal total time. No exact observer-frameULTIMATE claim.
HAWKI-informed wing/covariance and sampling sensitivities remain conditional and
do not duplicate raw reduction or transfer realADU noise amplitudes.

## Model selection, calibration and final use

Select hyperparameters only with five galaxy folds withindevelopment. Validation14
is reserved for out-of-sample calibration and diagnostics, not hyperparameter
selection. Models: constant trainingmedian; fixed-slope screen-color baseline
(approximate lambda^-1 law with training population-color intercept); photometric,
summary andspatial ridge alpha1/10/100; shallowforest depth4/8 with100trees;
histogramgradientboosting depth2/3,100iterations,learning_rate0.05,l2=10.
Spatial models use summary/radial/harmonic/texture features plus training-only
PCA8 of observedg/Ks cells. Multioutput model targets are fitting-standardized.
Same candidate settings for seeing/GLAO andg-only; select common per-target/family
settings by mean developmentCVMAE over bothNIR strategies. Do not tune a special
GLAO model on validation/test outcomes. All model families remain reported.

Select a recommended family/settings per target solely by developmentCV, before
validation diagnostics or final opening. Refit on eligibledevelopment only, keep
validation galaxies for split-calibration. Nominal80% simultaneous galaxy interval
uses maximum residual across views/draws per calibration galaxy and order
ceil((ncal+1)*0.8). If unavailable/too few, mark interval unavailable. It does not
include uncalibrated physical-label systematics or guaranteeOOD coverage.

Score equal-galaxy MAE,RMSE,bias; within-view/noise scatter; paired model andGLAO
gains with5000 galaxy bootstrap draws. Bootstrap conditions on fitted models and
does not fully resample training-set uncertainty. Correction subtracts predicted
native dust bias from observed dusty morphology and compares to nativeclear;
PSF/noise errors remain. Preserve per-view predictions and adverse corrections.

Learning curves fit increasing independentdevelopment galaxy counts(12,24,48,all
eligible), three seeds, fixed selected hyperparameters, score onvalidation; these
diagnostics do not reopen tuning. OOD: developmenthigh-massquartile heldout,
new/oldzero-dust source controls, and observable-feature distance andSB strata.
No final labels may influence features,aperture,model selection or calibration.

Once definitions/settings/calibration/sensitivity code are frozen, write exact
hashes,IDs,settings and evaluation policy to FINAL_PROTOCOL_FROZEN.json. Only then
may the final20 be streamed and evaluated once. All final cases, exclusions and
controls must be reported; no retuning/reselection follows. If scientific gates
fail, leave final sealed and document why rather than spend it on a moving method.
