# Independent scientific/code review — 2026-10-27

Reviewed source directly: ml_data.py, ml_benchmark.py, ml_postprocess.py,
label_quality_audit.py, empirical_stress.py, protocol and scientific report,
including inherited rendering/measurement interfaces. No science data, source
code or prediction files changed; no fitting grids executed. This note is the
only review artifact written.

No material information-leakage, grouping, calibration-score implementation,
correction-sign or aggregation bug found in this scoped review.

Independent recomputation from heldout_predictions.csv.gz (without benchmark
summary helpers):

- 369,600 records, no duplicate condition/mode/bandset/model/target/galaxy/view/draw
  keys; each galaxy contributes exactly 40 rows per configuration/target.
- All five fold test sets equal their frozen outer-test roles. Four source-null
  controls occur in neither fitting/calibration partitions nor primary predictions.
  Source inspection confirms every imputer, feature scaler and target scaler is
  fit on fitting galaxies only. No forbidden truth/physical metadata enter X.
- All prediction truth values exactly equal separate operational labels.
  Recomputed absolute errors and every galaxy-weighted mean MAE agree with saved
  summaries to <=1.7e-16. All paired galaxy GLAO gains agree to <=3.2e-16.
  Every g-only seeing/GLAO gain is exactly zero.
- Independently regenerated 5,000 galaxy-bootstrap samples reproduce all seven
  full-ridge original-noise GLAO intervals; each includes zero. Example: Ks R50
  gain 0.00018094 kpc, 95% interval [-0.00094969, 0.00156720].
- Independent raw-feature and separate native-clear joins reproduce correction
  errors to <1e-15: ridge corrected MAEs are g/Ks R50=0.294253/0.064846 kpc and
  g/Ks concentration=0.335973/0.204342. The implementation subtracts predicted
  native dusty-minus-clear bias, while retaining PSF/noise residuals as described.
- Interval halfwidth is constant within fold/configuration/target, finite and
  nonnegative. Saved covered flags equal abs_error <= halfwidth everywhere.
  Whole-galaxy coverage counts independently reproduce 16,19,19,15,19,20,20 of22
  in the report target order. The score is a per-calibration-galaxy maximum over
  views/draws; ceil(6*0.8)=5 correctly selects the largest of five galaxy scores.
- All 49,280 empirical-stress predictions are finite, without duplicate keys.
  Every g and J feature in empirical stress exactly matches original-noise
  features, confirming the change is confined to Ks. The local filter correctly
  specifies only adjacent-pixel correlations, not full mosaic covariance.

Scientific qualifications already made in the report are necessary: galaxy
bootstrap intervals condition on overlapping fitted folds; 22 selected galaxies
cannot certify population coverage; source-null residuals are unresolved physical
label systematics, not a transferable error distribution; correction performance
is relative to native clear morphology with observational errors remaining;
g-only versus three bands is unequal total exposure; HAWK-I stress retains proxy
D50/noise amplitude and omits measured large-aperture sky excess, anisotropy and
field variation. These restrictions support the report's limited feasibility
conclusion and its negative result on a robust GLAO ML advantage.

Minor clarity issue: tables/figure labels say "Colours", but photometric_ridge
also includes g_logJy (absolute apparent flux). The surrounding report discloses
this luminosity prior, and provenance names exact features. "Photometry" would
be the most precise short label. This does not change numerical conclusions.
