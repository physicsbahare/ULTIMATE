# Workshop summary — actual expanded results

**Beyond the Foreground Screen: Machine-Learning Dust Geometry with ULTIMATE-Subaru**

A120-galaxy DR1 inventory is verified, preserving86/14/20 galaxy partitions. Models use observable g/J/Ks photometry and bounded spatial features; dust-free images and simulation physics enter labels/scoring only. All five views and noise draws remain grouped by galaxy.

Validation 14 numerical results, nominal seeing fixed12:

- **A_g:** best numerical MAE 0.06274 (ridge_summary); photometric ridge 0.07273; median constant 0.23784. The best row is descriptive across the recorded models, not a new test-driven model selection.
- **dR50_Ks:** best numerical MAE 0.04335 (ridge_summary); photometric ridge 0.05112; median constant 0.11218. The best row is descriptive across the recorded models, not a new test-driven model selection.
- **dC_Ks:** best numerical MAE 0.07939 (ridge_summary); photometric ridge 0.10259; median constant 0.13963. The best row is descriptive across the recorded models, not a new test-driven model selection.

The comparison distinguishes additional NIR bands from narrower NIR PSFs. All favorable and adverse resolution outcomes are retained; multiple comparisons and conditional observing assumptions limit instrument claims. Signed source-control residuals and aperture-dependent labels prevent equating predictive accuracy with physical dust precision.

The strongest defensible message is learning selected effective attenuation statistics and morphology-bias corrections relative to simple baselines. This is neither unique3D dust-geometry recovery nor a validated observer-frame ULTIMATE forecast. Empirical HAWK-I PSF/covariance tests improve realism but supply no dust truth. Source/filter calibration and simulation-to-observation transfer remain the publication-critical next evidence.

The pre-existing pipeline completed the project’s single frozen final evaluation in ../ml_expanded_20261028/. These supplementary models remain validation-only and were never evaluated on the final galaxies. Consult project_continuation_report.md for the verified canonical final results; no second final scoring is performed here.
