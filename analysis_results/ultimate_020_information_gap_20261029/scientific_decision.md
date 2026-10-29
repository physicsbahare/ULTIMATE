# Scientific decision: targeted 0.200-arcsec information assessment

2026-10-29, Asia/Taipei. **GO — the bounded new assessment was scientifically justified and is complete.** It supplies a previously unavailable fixed-rest-band Ks-only .390→.200 comparison. Stop further computation now. There is **no demonstrated robust additional dust-related ML advantage**, and this pilot does not justify the cost of an independent confirmation campaign for a positive dust-inference claim.

The new positive result is direct morphology transfer; the negative/shape-dependent predictive result is equally part of the deliverable. This does not change the canonical frozen models, spent-final scores or earlier no-robust-extra-GLAO conclusion under .588/.390 conditions.

## Design and evidence

The [overlap audit](overlap_and_novelty_audit.md) found that .200 images already existed for a one-galaxy privileged screen-separation oracle, but neither fixed-rest-band morphology nor observable-only spatial ML was tested there. The [protocol](experiment_protocol.md) froze14 development objects, including13 fit objects spanning stellar mass plus the retained pilot outlier, and one source control. All five views stay with each galaxy. No validation/final images or inference were used; control13 labels retain their signed source residuals and are never forced to zero. Three actual input bands are g/J/Ks; conclusions about photometric information refer to this baseline.

Native .100-kpc cells at z=.1 subtend .0542217arcsec, with D_A=380.4098Mpc and1.8442789kpc/arcsec. Detector pixels are .100arcsec=.184428kpc. Nominal Gaussian FWHM .38955078125arcsec gives .718441kpc, assumed .200 gives .368856kpc. Two detector pixels per narrow FWHM do not support unrestricted high-frequency reconstruction. Native pixels are not independent physical resolution elements; tiny errors in an integrated radius statistic do not imply resolution of structures at that error scale.

Only Ks changes; g=.700 and J=.5076568274arcsec remain fixed. We use no added noise, identical measurement centers, the saved shared deep-reference adaptive aperture and native labels. PSF families are Gaussian and circular Moffat beta3.020805, informed by the completed M4 tile shape. Both comparisons hold **FWHM** at the requested value. Moffat D50 is .490658/.251910arcsec; it is not equated to FWHM. This is an assumed analytic wing sensitivity, not a rescaled measured ULTIMATE PSF, and does not sharpen HAWK-I observations.

The original radiometry/area-overlap operator is retained. A native-grid numerical preflight showed up to5.7% L1 point-pixel disagreement at .2, so Ks uses2× subdivision of constant source cells and2×2 PSF quadrature at **both widths**, with a new matched .390 reference. Refinement4/quadrature4 on preselected control13 O1 changes discrete R50/C by zero and image L1 by at most.00142. Analytic detector-pixel tests at two phases have at most1.012% L1 error. Peak-pixel values change substantially with phase even with conserved flux, as expected at two samples/FWHM. This is a finite numerical check, not a phase-invariant galaxy measurement guarantee. Noiseless renders lose at most1.52e-7 padded flux. [Checks](psf_definition_and_operator_checks.csv), [raw execution table](operator_checks_execution_original.csv), [provenance](provenance.json).

The summary script clarifies an execution-table column name: `convolution_pixel_arcsec` is the refined integration grid; `source_native_pixel_arcsec` is the actual .0542217arcsec source sampling. Original execution bytes are retained in `operator_checks_execution_original.csv`; no numerical value was replaced.

## A. Direct morphology transfer

Equal-galaxy means over13 positive-dust development galaxies, each averaging5 views. Gain means MAE(.390)−MAE(.200), so positive favors .200. Radius units kpc; concentration dimensionless. Native dusty morphology is the reference, not native clear morphology.

| PSF | Statistic | MAE .390 | MAE .200 | Gain [conditional95% interval] |
|---|---|---:|---:|---:|
| Gaussian | Ks R50 | .02669 | .01176 | .01493 [.00587,.02758] |
| Moffat | Ks R50 | .06371 | .01627 | .04744 [.02425,.07547] |
| Gaussian | Ks concentration | .16001 | .06483 | .09518 [.05177,.14367] |
| Moffat | Ks concentration | .28371 | .11357 | .17014 [.11705,.22759] |

Every primary galaxy has a positive galaxy-mean gain for these two morphology measures under each family. This is conditional robustness to **these two shapes**, with one source-control numerical refinement check; it is not exhaustive PSF/sampling robustness. Larger equal-FWHM Moffat errors reflect broader wings. [Per-view measurements](morphology_resolution_results.csv), [summary](morphology_summary.csv), [per-galaxy gains](galaxy_morphology_gains.csv), [figure](figures/morphology_width_gain.png).

Observed dusty-minus-clear morphology differences are a privileged transfer diagnostic, not an observer-accessible dust estimate. Their improvement is much weaker: R50 gains .00150[-.00134,.00420] Gaussian and .00170[-.00338,.00681] Moffat kpc; concentration gains .00118[-.01187,.01610] Gaussian and .01858[-.00137,.03967] Moffat. Every interval crosses zero. This is inconclusive about the sign of a population effect; it does not establish zero information.

## B/C. Held-out operational morphology-bias and integrated-attenuation prediction

Five identical galaxy folds across widths/families, fixed ridge alpha10, imputation/scaling/PCA inside training folds. Each primary galaxy is evaluated only by a model that excluded it.60 total small fold fits, not a120-object retrain. Five views are repeated measurements, not65 independent galaxies. Source control predictions are separate fold-ensemble diagnostics. The fixed-model transfer and resolution-specific fitting estimands are kept separate in [prediction rows](ml_predictions.csv.gz).

The table reports resolution-specific MAE .390→.200. A_g/A_Ks are magnitudes, dR50_Ks is kpc, dC_Ks is dimensionless. These are new small-development-pilot scores, not comparable fresh-final replacements for the canonical16-object primary final benchmark.

| PSF | Operational target | Photometric ridge | Summary ridge | Spatial ridge |
|---|---|---:|---:|---:|
| gaussian | A_g | 0.11044 → 0.11043 | 0.11132 → 0.11207 | 0.13510 → 0.13436 |
| gaussian | A_Ks | 0.01886 → 0.01887 | 0.01913 → 0.02056 | 0.03028 → 0.03154 |
| gaussian | dR50_Ks | 0.11746 → 0.11760 | 0.09755 → 0.10585 | 0.14250 → 0.14858 |
| gaussian | dC_Ks | 0.12508 → 0.12512 | 0.11291 → 0.11583 | 0.12935 → 0.13654 |
| moffat | A_g | 0.11043 → 0.11043 | 0.10255 → 0.11225 | 0.13372 → 0.13506 |
| moffat | A_Ks | 0.01884 → 0.01887 | 0.01568 → 0.01949 | 0.02906 → 0.03059 |
| moffat | dR50_Ks | 0.11712 → 0.11751 | 0.10209 → 0.10090 | 0.14035 → 0.14456 |
| moffat | dC_Ks | 0.12498 → 0.12509 | 0.12513 → 0.11426 | 0.13093 → 0.13352 |

At .200, **spatial ridge has higher MAE than photometric ridge for every prespecified target under both shapes**. Summary ridge does beat photometry for the two morphology-bias targets in these point estimates, but narrowing the PSF does not produce a shape-robust extra benefit. For example:

- Gaussian summary dR50: gain **−.00830kpc** [−.01170,−.00508]; narrower input worsens prediction despite improving direct morphology.
- Moffat summary dR50: +.00120kpc [−.01489,.02245], unresolved.
- Summary concentration gain changes sign: Gaussian −.00292[−.00621,.00086], Moffat +.01088[.00013,.02342]. This positive exploratory Moffat interval is not a robust discovery across shapes/models or multiple comparisons.
- Summary A_Ks gains are adverse under both shapes: −.00142[−.00256,−.00047] Gaussian and −.00381[−.00749,−.00072] Moffat mag. Spatial A_g gains are small with intervals spanning zero. No supported positive integrated-attenuation gain is established.

[ml_information_gain_results.csv](ml_information_gain_results.csv) supplies every model/target MAE, photometric MAE, photo-minus-model incremental MAE, paired width gain, change in incremental gain and galaxy-bootstrap interval. [galaxy_level_uncertainties.csv](galaxy_level_uncertainties.csv) supplies each galaxy's signed gain (positive or adverse), both width errors and incremental effects; [galaxy_level_ml_errors.csv](galaxy_level_ml_errors.csv) retains signed prediction residuals. Spatial-median/IQR attenuation targets were not added to this prespecified four-target pilot; no universal result for attenuation maps or untested estimators follows.

Failure examples are retained rather than excluded: under Moffat spatial ridge, galaxy594731 dR50 MAE rises .04472→.08037kpc (gain−.03565),578834 rises .30908→.34159 (−.03251), and535051 rises .15010→.17682 (−.02672). The historical pilot294866 remains in the sample. Negative results cannot justify a new model search against the spent-final set.

Fixed-model transfer is not silently described as information available after refitting. For example, Moffat summary ridge trained at .390 and applied to held-out .200 galaxies has dR50 MAE .11664kpc, whereas separately trained .200 ridge yields .10090. Gaussian spatial ridge .390→.200 transfer MAE is .14198kpc, versus .14858 after resolution-specific fitting. Neither ordering is universal. All96 model/target/train/test scores are saved; no preferred family is selected.

Intervals resample13 independent galaxies5000 times, condition on fitted overlapping-fold estimators and selected sample, and omit refitting, source-label, representative-selection and instrument uncertainty. These are exploratory summaries, not confirmatory p-values. An interval crossing zero is not proof of no effect. The result is a failure to demonstrate robust incremental prediction **with these features/models/sample**, not an information-theoretic impossibility result.

## Ten publication decisions

1. **Already adequately tested?** .200 was simulated, but only an earlier privileged oracle answered a different question. The present fixed-rest-band morphology/ML comparison was missing.
2. **Exactly new?** Matched Ks-only .38955/.200 FWHM, two analytic shapes, explicit integration,14 development galaxies, preserved feature/target definitions and genuinely galaxy-held-out paired ridge tests. No independent confirmation data.
3. **Morphology improves?** Yes for R50/concentration in this noiseless selected sample under both shapes, with positive conditional gain intervals. This is measurement transfer, not dust inference.
4. **Additional dust-related predictive information beyond photometry?** Not robustly demonstrated. Full spatial ridge is worse than photometry; summary-model width gains are target- and shape-dependent, often adverse.
5. **Robust to PSF/sampling?** The direct-morphology sign survives both tested families; dust-ML improvement does not. Sampling checks are bounded numerical preflights, not a calibrated detector/phase/segmentation distribution.
6. **Different noise/conventions explain gains?** Noise is absent, definitions/centers/labels/apertures fixed, and both widths use the same refined operator. This isolates the imposed width effect. It does not establish equal-exposure detectability or cross-shape equivalence (equal FWHM gives different D50).
7. **Workshop can be strengthened now?** Yes: explicitly extend morphology transfer to assumed .200 while retaining the separation from dust ML and original source-control caveat. Describe this extension as exploratory development evidence.
8. **Independent confirmation sample worth its cost now?** Not for a positive .200 dust-inference claim on this evidence. A future campaign needs a distinct physical/source or observer-frame requirement and a prespecified effect/cost rationale; no campaign begins here.
9. **Carefully qualified short paper supported?** Yes, as a conditional operational benchmark with interpretable ML, radiative-transfer images, optical–NIR information and separate GLAO morphology capability. Bibliographic novelty, source rights/attribution and manuscript writing remain; calibrated physical attenuation, unique3D geometry and guaranteed observing performance remain unsupported.
10. **Which figures?** Existing frozen benchmark/paired-gain and source-control figures plus the new [morphology](figures/morphology_width_gain.pdf) and [ML width-gain](figures/ml_width_gain.pdf) panels; the [workshop/paper plan](workshop_paper_implications.md) specifies placement and captions.

## Deliverables and stopping boundary

All requested conditional scientific outputs are present: protocol, operator checks, morphology results, ML information gains, galaxy uncertainties, verification and two figure pairs. Additional traceability files contain selected IDs/folds, observable features, source-control predictions, all CV predictions, per-galaxy errors, gate and source/environment hashes. [verification.json](verification.json) records current checks; original scientific outputs/frozen receipts remain preserved. No .300 case, noisy exposure sensitivity, calibration repeat, full120 retrain, new confirmation sample or new geometry claim was needed. The next action is manuscript/workshop synthesis, not another simulation.
