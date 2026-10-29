# Bounded 0.200-arcsec experiment protocol and implementation plan

Recorded before new outcomes on 2026-10-29, following [Phase-0 audit](overlap_and_novelty_audit.md). User authorized conditional phases 1–3. Native scientific inputs and canonical outputs are read-only. All new outputs belong here; no original driver or notebook will run.

## Design

Scientific estimands: A, direct observed-dusty morphology error against native dusty R50/C; paired-image observed dusty-minus-clear transfer error is a diagnostic, not ML. B, out-of-galaxy prediction of native paired dR50_Ks/dC_Ks; C, prediction of integrated operational A_g/A_Ks. B/C are not calibrated physical truth. The incremental comparison is photometric ridge versus summary/spatial ridge under .38955078125 and .200 FWHM. Nothing changes g/J PSFs.

Use existing 800-square .1-kpc source arrays, radiometry at fixed z=.1, FlatLCDM H0=70 Om0=.3 Tcmb=2.725, exact area-overlap integration to .1-arcsec detector pixels and existing FeaturePlan/measure/model implementations. Native sampling is not independent physical resolution. No galaxy evolution/K correction is introduced; rest Ks would appear beyond ordinary observer Ks at z=.1. This is a distance-degraded fixed-rest-band experiment. No added noise: isolates resolution; no fixed-exposure forecast or general depth rerun needed.

Selection before outcomes: positive-dust development objects sorted by log stellar mass then ID; select 12 indices round(i*(74−1)/11), i=0..11. Add historical pilot outlier294866 and source-control13. Final IDs: 13,96763,184931,294866,448830,521429,535051,576516,578834,589873,594731,626408,630760,638950. Twelve mass-spaced objects plus the distinct pilot yield13 fit-eligible galaxies and1 control. Mass range includes compact low-mass, intermediate and massive structures without choosing on new images/outcomes. All O1–O5 are paired, correlated views. Use saved adaptive radii/labels without re-auditing their source origin. Control13 is never forced to zero or included in fitting/primary means.

PSFs: Gaussian and circular Moffat beta=3.0208050586423507 (completed M4 tile median, **shape-informed assumption**, not rescaled empirical truth). Both requested widths are **FWHM**, with alpha=FWHM/[2 sqrt(2^(1/beta)−1)] and D50=2 alpha sqrt(2^(1/(beta−1))−1). At equal FWHM, Moffat D50 differs; this deliberately differs from legacy equal-D50 tests. Finite support at ≥30 alpha, analytic missing-tail fraction recorded, nonnegative normalized kernels. Preserve original radiometry and area-overlap operator; subdivide each native source cell into2×2 constant elements before Ks convolution, without inventing intrinsic structure. Both widths use this matched refined operator. Test source-grid refinement for a synthetic point source and .5-detector-pixel phase offsets with analytic pixel integration. Compare source-grid quadrature2/4 for Moffat kernel convergence on one preselected control O1. Retain the legacy center-sampled Gaussian only as an operator diagnostic; record its difference from the matched2× refined PSF integration. Do not upsample galaxy images to claim new intrinsic structure.

## Gates and ML design

First verify kernel positivity/unit sum, rendered padded flux loss<1e-4, analytic point-source detector-pixel integration accuracy (relative L1<.02), and native/subpixel kernel convergence on control13 O1 (R50<.03kpc; C<.03). Record phase behavior as a floor rather than assume phase invariance. Aliasing at two detector samples/FWHM is explicitly limited: no reconstruction claim above detector Nyquist.

Phase2 gate: for each family, median galaxy absolute fractional change in the existing Ks_texture_0.5 feature >1%, and at least half positive-dust galaxies exceed1%; report morphology-error and paired contrast changes even if adverse. This is a gate for testing *available observables*, not proof of additional target information. If gate fails, omit ML and explain. If both families pass, proceed with one small matched ML exercise; no architecture search.

Four prespecified targets A_g,A_Ks,dR50_Ks,dC_Ks. Reuse `expanded_models.model`, families phot_ridge/summary_ridge/spatial_ridge with fixed alpha=10 (existing candidate setting, chosen in advance; no tuning). Preprocessing and spatial PCA8 fit inside each fold. Five galaxy folds from sorted13 eligible IDs, KFold shuffle seed20261029; keep every view in its galaxy fold, identical conditions. No validation or final targets/features are loaded. Equal5 views per galaxy make training row weights equal across galaxies.

Resolution-specific fitting: train/predict within each width's matching train/test split. Fixed-model transfer: use each fold's .390-trained estimator on held-out .200 galaxies and vice versa; never on its training galaxies. Control13 predictions from each fold ensemble are reported separately; it is never a fit object. No saved canonical model is replaced, no new preferred model chosen.

MAE is mean per-galaxy mean absolute view error. Report photometric/summary/spatial MAE, photo-minus-model incremental MAE, .390-minus-.200 paired MAE gain, and change in incremental gain. Positive favors narrower/spatial model. Save signed residuals, absolute errors and galaxy gains/failures. Bootstrap5000 independent galaxies seed20261029 for percentile95% intervals of paired changes and MAE; exploratory conditional intervals do not include retraining/selection/systematic uncertainty. Small13-galaxy results are not new confirmation; crossing zero is inconclusive rather than proof of equality.

## Implementation and verification plan

1. Freeze selected metadata, subset-only saved labels/radii, input/source hashes and environment; preserve old output hashes. No original result writes.
2. Implement small `run_assessment.py` wrapper around existing operator/measure/features/model; numerical checks exercise width conversion, pixel integration, flux and grouped splitting. Save new operator check rows before moving on.
3. Extract noiseless features/morphology for14 galaxies×5views×2families×2widths. Save phase2 gate. Run only conditional ML above if gate passes; retain failed/adverse cases.
4. Save requested CSVs, read-only verification receipt and two static publication figures with units/conditional captions. No optional .300 intermediate, exposure sensitivity, new source audits or complex models.
5. Audit output arithmetic, folds, original hashes, figures and links. Update state/decision/completed/open/publication/history/handoff records; screen every new file and list exclusions. Commit explicit eligible files and push without rewriting history; verify remote SHA.

This protocol is the short design and plan for an already specified, authorized scientific continuation. Methods were settled locally from existing artifacts; no additional user approval is required by the task. New experiment claims remain exploratory after the spent-final study.

## Numerical preflight amendment, before galaxy outcomes

Analytic point-source test failed on the unrefined native grid: at .2 FWHM, relative L1 pixel-flux disagreement .05698/.05156 for Gaussian and .03793/.03506 for Moffat (two phases). Subdividing the convolution grid by2 yielded .00937/.01010 Gaussian and .00626/.00770 Moffat. Use refinement2 for both widths and both families, with2×2 PSF subcell quadrature; compare refinement4/quadrature4 on control13 O1. Original source cells are constant elements, not new spatial evidence. This is precisely why a minimum new matched .390 reference is necessary. Thresholds, sample, features, targets, ML setting and gate remain as prespecified. Legacy results are preserved.
