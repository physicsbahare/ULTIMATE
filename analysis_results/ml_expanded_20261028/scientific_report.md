# Expanded ULTIMATE-like interpretable ML feasibility study

Completed 2026-10-28T02:57:04.093714+00:00. All numerical tables below come from the single frozen final evaluation; no final-outcome tuning or model reselection occurred.

## Main result and scope

All **120 independent galaxy IDs / 600 orientations** were prepared and verified. The original frozen assignment remains 86 development, 14 validation and 20 final evaluation. Twelve development and one validation galaxy have exactly zero projected dust fields: **74 galaxies fit models**, **13 calibrate intervals**. The final set contains **16 primary positive-dust galaxies and 4 source controls**. Every orientation and noise draw stays with its galaxy. These are independent subhalo sampling units within one simulation, not independent simulation volumes or orientations.

The predictions learn **operational dusty-minus-clear DR1 image-product contrasts**. A coherent full-field offset of ≈0.12 mag in four exact-zero-dust control galaxies remains unexplained. High predictive accuracy therefore does not establish equally accurate physical dust attenuation. Physical attenuation calibration is a publication gate. No universal offset was subtracted and no negative attenuation, adverse orientation or failed target was hidden.

None of the eight recommended-model final paired GLAO-gain intervals excludes zero on the positive side. Intervals support adverse effects for dR50_g. This addresses extra NIR resolution conditional on these images, features, noise assumptions and fixed models. Additional NIR bands and GLAO resolution are separate comparisons. The optical+NIR experiment uses one hour per band, hence more total time than g alone. Adaptive g-feature models share a deep Ks-defined reference aperture and are not a fully g-selected survey pipeline; fixed12 results supply the cleaner optical-only aperture control.

## Final out-of-sample accuracy

All entries are equal-galaxy MAE except the named RMSE column. Attenuation values are magnitudes, R50 differences kpc, concentration dimensionless. Constant is the development median; photometric ridge is independently selected within its family using development folds. Recommended family/settings are frozen by development CV mean over both NIR strategies; they are not the best model selected after seeing final outcomes.

| target | constant | phot_seeing | optical | seeing | GLAO | GLAO_RMSE | gain | gain_low | gain_high |
|---|---|---|---|---|---|---|---|---|---|
| A_g | 0.3003 | 0.0794 | 0.2622 | 0.0734 | 0.0741 | 0.1098 | -0.0007 | -0.0057 | 0.0042 |
| A_Ks | 0.0594 | 0.0150 | 0.0552 | 0.0124 | 0.0124 | 0.0163 | -0.0001 | -0.0003 | 0.0002 |
| A_g_p50_1kpc | 0.0522 | 0.0497 | 0.0493 | 0.0441 | 0.0441 | 0.1397 | -0.0000 | -0.0005 | 0.0005 |
| A_g_IQR_1kpc | 0.1214 | 0.1207 | 0.0848 | 0.0745 | 0.0707 | 0.1639 | 0.0038 | -0.0003 | 0.0079 |
| dR50_Ks | 0.1282 | 0.0992 | 0.1240 | 0.0777 | 0.0799 | 0.1189 | -0.0022 | -0.0077 | 0.0026 |
| dC_Ks | 0.1521 | 0.1174 | 0.1519 | 0.0887 | 0.0887 | 0.1306 | 0.0000 | -0.0121 | 0.0127 |
| dR50_g | 0.4939 | 0.2814 | 0.4327 | 0.2044 | 0.2236 | 0.3167 | -0.0192 | -0.0341 | -0.0062 |
| dC_g | 0.4808 | 0.2953 | 0.3562 | 0.2339 | 0.2445 | 0.3277 | -0.0106 | -0.0225 | 0.0021 |

Gain = seeing MAE − GLAO MAE; positive favors GLAO. The bounds are 95% percentile intervals from **5000 paired galaxy bootstrap draws**, conditional on the fitted models. They do not include retraining, uncertain source labels, simulation-to-observation shift or selection uncertainty. Eight targets and many model/condition comparisons are exploratory; no multiple-testing correction was used. A single favorable interval is not an omnibus instrument claim.

The package preserves all eight model families, optical/seeing-NIR/GLAO-NIR scenarios, both apertures, all per-orientation/four-noise-draw predictions, constants and approximate screen-color baselines. `performance_summary.csv` and `paired_galaxy_gains.csv` retain unfavorable or weaker-than-photometry results. Simple photometry can be superior; the extra spatial features are not assumed to help.

## Morphology correction versus prediction of dust bias

| scenario | target | uncorrected_MAE | corrected_MAE | MAE |
|---|---|---|---|---|
| GLAO_NIR | dC_Ks | 0.4814 | 0.3297 | 0.0887 |
| GLAO_NIR | dR50_Ks | 0.2325 | 0.0861 | 0.0799 |
| optical | dC_Ks | 0.7053 | 0.5783 | 0.1519 |
| optical | dR50_Ks | 0.2983 | 0.1870 | 0.1240 |
| seeing_NIR | dC_Ks | 0.7053 | 0.5544 | 0.0887 |
| seeing_NIR | dR50_Ks | 0.2983 | 0.1210 | 0.0777 |

Uncorrected and corrected errors compare observed dusty morphology to **native clear** morphology; correction subtracts predicted native dusty-minus-clear bias. Thus PSF and measurement errors remain. A better corrected morphology under GLAO can reflect improved PSF transfer even when the predicted dust difference has no reliable resolution gain. This is not deconvolution and does not identify an individual feature as dust.

## Calibration, scatter and failures

Nominal80% intervals use the rank12 order statistic of maximum absolute residual over all five views and four draws for each of 13 calibration galaxies, separately for each target and model. This is a cluster-level split-conformal construction under exchangeable galaxies, not joint coverage across eight targets or a calibrated error on physical truth. Validation coverage used the calibration sample itself and is descriptive; the following final coverages are genuinely held out, although based on only 16 primary galaxies.

| target | n_galaxies | bias | galaxy_coverage | point_coverage |
|---|---|---|---|---|
| A_g_IQR_1kpc | 16 | -0.0320 | 0.8750 | 0.9250 |
| dC_g | 16 | -0.0924 | 0.8125 | 0.9125 |
| A_g_p50_1kpc | 16 | -0.0244 | 0.8125 | 0.9250 |
| dC_Ks | 16 | 0.0042 | 0.8750 | 0.9625 |
| dR50_g | 16 | 0.0516 | 0.9375 | 0.9812 |
| A_Ks | 16 | 0.0032 | 1.0000 | 1.0000 |
| A_g | 16 | -0.0407 | 0.7500 | 0.9313 |
| dR50_Ks | 16 | 0.0478 | 0.9375 | 0.9750 |

`galaxy_metrics.csv` retains individual objects and `within_view_noise_and_orientation_residuals.csv` separates repeated-draw scatter from view means. `property_stratified_errors.csv` reports descriptive stellar mass, SFR, projected dust content, apparent axis ratio and surface-brightness strata. Axis ratio is not true inclination; zero SFR is not zero dust. `observable_distance.csv` measures nearest-development distance using training-only standardized observable summaries. The high-mass held-out-quartile experiment uses fixed ridge10 and excludes all upper-quartile galaxy views from training; it is an internal covariate-shift diagnostic, not independent simulation-to-real validation.

Learning curves use 12/24/48/74 independent development galaxies and three fixed subset seeds, with settings frozen by the full development CV. The 13 validation galaxies are unchanged. Their shaded seed range is not a population confidence interval. No new complex image network was trained; spatial features use explicit radial fractions, harmonics, texture and training-only PCA8 of 8×8 image cells. This tests coarse image information beyond aperture compression without a large CNN.

## Labels, apertures and source controls

Targets are integrated signed effective attenuation in actual LSST g and 2MASS Ks, g attenuation median/IQR after 1-kpc FWHM smoothing, and paired native ΔR50/ΔC in g/Ks. Concentration is 5log10(R80/R20). Paired products share origin, mask, sampling and aperture. Spatial ratios require finite positive clear/dusty smoothed flux and clear >1e-4 of its peak inside the aperture; negative effective attenuation remains valid. Dust-free truth supplies supervision/scoring only. No physical map or simulator metadata enters the predictor allowlist.

Primary radius = clip(1.5R80,8,30) kpc, derived from a common seeing-convolved **dusty** Ks reference within R35; fixed12 is a sensitivity. The deep-reference radius has no propagated measurement uncertainty, known distance and fixed center are assumed, and finite R35 light truncation/clipping are flagged. `aperture_target_sensitivity.png` and target tables show operator dependence; they are not measurements of total light.

The focused20-nonfinal-galaxy O1 test changes radius by ±20% and center by0.5 kpc in each direction. For 14 validation objects, radius×0.8 changes |Ag| by median0.0190 mag, |ΔR50Ks| by0.0229 kpc and |ΔCKs| by0.0321. Center offsets change |ΔCKs| by median0.047–0.079 and up to0.447. Hence concentration correction is materially sensitive to center definition. Full details and exact direct-geometry checks are in `instrument_sensitivity/center_aperture_report.md`.

Four historical controls were freshly decoded from original full-field products: matching units/WCS/cached pixels, zero dust maps and persistent band-dependent integrated offsets were confirmed. Across22 bands, signs alternate (e.g. g positive, r/z/FUV negative); this is not a simple extinction law or cropped-aperture explanation. Spatial RMS declines after smoothing, consistent with an additional Monte Carlo component, but the integrated systematic is not adequately explained by zero-mean Monte Carlo noise. Analytic clear-source projections versus Monte Carlo dusty instruments, potentially with differing spectral integration, are plausible source mechanisms; historical .ski/SED/filter configuration is unavailable and the cause is **unresolved**, not established as a particular SKIRT error.

`old_control_operator_envelopes.csv` is descriptive only. Adaptive old-four control maxima include Ag0.12433 mag, AKs0.02259 mag, ΔR50Ks0.03749 kpc and ΔCKs0.23982. They are not sigma values, universal thresholds or calibrated systematic bounds. All newly identified exact-zero-dust cases follow the predeclared separate-control policy, including final cases. Exclusion from fitting does not remove source-systematic uncertainty for positive-dust galaxies.

## Observing assumptions and HAWK-I sensitivities

Fixed-rest-band z=0.1/1h,0.1-arcsec pixels and inherited band-dependent Gaussian PSFs use validated angular resampling, flux transfer and source/sky/thermal/dark/read variance components. g remains0.7 arcsec; nominal Ks is≈0.588/0.390 arcsec seeing/GLAO. These are **provisional conditional resolution experiments**, not exact observer-frame ULTIMATE forecasts. The galaxies do not evolve with assigned distance. Rest Ks shifts outside ordinary observer Ks at this redshift; 2MASS filters are not ULTIMATE passbands. Four Gaussian moment-noise draws are paired across strategies; rare-tail detector and sky residuals are not fully modeled.

The official reduced HAWK-I products were reused; no raw-data reduction was duplicated and no new large observations downloaded. Previous empirical measurements: median compact-candidate FWHM≈0.317 arcsec (103 candidates), quality2MASS-associated FWHM≈0.294 arcsec (9 sources), Moffat beta≈3.74, adjacent background correlations≈0.28–0.29. These describe those HAWK-I conditions, not a calibrated ULTIMATE PSF; they provide neither dust truth nor0.2-arcsec image information.

`instrument_sensitivity/` keeps four predeclared O1-only cases on20 nonfinal galaxies: A baseline Gaussian; B empirical-informed Ks Moffat wings at the **same nominal D50**; C B plus local correlated noise preserving marginal variance; D flux/variance-preserving2×2 software binning of A. Existing nominal models are applied without retuning. Only Ks wings change; g remains seeing-limited. The local covariance model does not reproduce measured large-aperture excess (≈3.42× pixel-noise prediction) or full sky structure. `instrument_stress_predictions_summary.csv` reports all outcomes and uncertainty/gains. `shift_and_noise_predictions_summary.csv` separately tests common added variance and noiseless conditions with settings held fixed, isolating noise assumptions from additional bands. Morphology A/texture features remain noisy without empirical noise subtraction.

`instrument_sensitivity/hawki_sharing_manifest.csv` lists six existing reduced/calibration product references, paths, sizes, checksums and official links for potential collaborator use. No large products were packaged or transferred. Actual collaborator raw reduction remains independent.

## Selection, verification and resource use

The existing secure downloader completed94/94 new DR1 archives before this stage. Current hashes and sizes match recorded gzipCRC/tar integrity proofs for all120; all archives were then streamed, without full extraction. The100 nonfinal stage checked24000 FITS headers/3500 selected full arrays; final20 added4800 headers/700 arrays only after the frozen receipt. All22 bands have paired header/member validation; only g/J/Ks and projected dust arrays have full numerical pixel checks. Units/grid/filter identities are explicit; filenames identify actual source filters when header filter keywords are absent. Native pixels100pc; source1600², reusable seven-array central800² caches. No duplicate download, full TNG snapshot or new software installation occurred. Current available disk≈284.6 GiB, exceeding100GiB.

Original26 raw member hashes agree (6240 matches), benchmark294866 R12 R50/C/q reproduce to machine precision and attenuation to3.5e-16; tiny A differences reflect float32 order. Four meaningful numerical tests pass, with pre-final grouped/allowlist/calibration/transfer checks and postfinal disjointness/hash checks.136 artifacts were frozen before scientific access to final20; all20 were evaluated once. Existing result manifests verify1056 files unchanged. Exact stage receipts and logs are retained rather than overwriting old status reports.

The saved official DR1 catalogue has1154 galaxies. Selection of the94 new galaxies balanced five mass ×five activity strata (zero SFR plus four positive-sSFR groups), conditional quota3/4 per stratum with recorded inclusion/partition probabilities. Original26 are historically chosen and only development. Official selection metadata lack true dust mass, morphology class and inclination: gas proxies are not substitutes. Dust/morphology coverage is characterized after acquisition, not claimed as direct dust-stratified selection. The sample is not volume-complete, host-environment-independent or representative of all TNG50 galaxies. Single-simulation correlations and finite final N limit universality and scaling-law precision.

## Additional quantitative checks

**Improvement beyond baselines:** the integrated-g model strongly improves on the constant, but its incremental gain over photometric ridge has a 95% interval spanning zero. The Ks R50 reduction in point MAE is promising, but its paired interval versus the constant also spans zero. Ks concentration and spatial IQR have positive paired gains over both these baselines, conditional on their label and measurement limitations. The expanded spatial median target improves modestly over the constant, unlike the initial22-galaxy experiment; however its final GLAO RMSE0.1397 mag far exceeds MAE0.0441, showing an important error tail. Do not describe this as uniformly reliable resolved attenuation recovery.

| target | comparison | gain | low | high |
|---|---|---|---|---|
| A_g_IQR_1kpc | median_minus_model_MAE | 0.0469 | 0.0148 | 0.0869 |
| dC_g | median_minus_model_MAE | 0.2469 | 0.1117 | 0.4045 |
| A_g_p50_1kpc | median_minus_model_MAE | 0.0081 | 0.0006 | 0.0176 |
| dC_Ks | median_minus_model_MAE | 0.0634 | 0.0209 | 0.1230 |
| dR50_g | median_minus_model_MAE | 0.2896 | 0.1139 | 0.5008 |
| A_Ks | median_minus_model_MAE | 0.0470 | 0.0252 | 0.0737 |
| A_g | median_minus_model_MAE | 0.2270 | 0.1523 | 0.3076 |
| dR50_Ks | median_minus_model_MAE | 0.0505 | -0.0042 | 0.1084 |
| A_g_IQR_1kpc | phot_ridge_minus_model_MAE | 0.0462 | 0.0214 | 0.0739 |
| dC_g | phot_ridge_minus_model_MAE | 0.0613 | 0.0123 | 0.1142 |
| A_g_p50_1kpc | phot_ridge_minus_model_MAE | 0.0056 | 0.0012 | 0.0108 |
| dC_Ks | phot_ridge_minus_model_MAE | 0.0287 | 0.0119 | 0.0472 |
| dR50_g | phot_ridge_minus_model_MAE | 0.0770 | 0.0065 | 0.1444 |
| A_Ks | phot_ridge_minus_model_MAE | 0.0027 | -0.0021 | 0.0079 |
| A_g | phot_ridge_minus_model_MAE | 0.0060 | -0.0148 | 0.0305 |
| dR50_Ks | phot_ridge_minus_model_MAE | 0.0215 | -0.0074 | 0.0477 |

**Absolute PSF/noise morphology transfer:** comparing observed dusty to native dusty directly gives:

| scenario | metric | MAE | bias | n_galaxies | RMSE |
|---|---|---|---|---|---|
| GLAO_NIR | C | 0.3200 | -0.3199 | 16 | 0.4102 |
| GLAO_NIR | R50 | 0.0595 | 0.0562 | 16 | 0.0762 |
| seeing_NIR | C | 0.5439 | -0.5439 | 16 | 0.6693 |
| seeing_NIR | R50 | 0.1238 | 0.1220 | 16 | 0.1563 |

These errors depend on PSF resolution even with no learned dust correction. The paired gains are:

| metric | comparison | gain | low | high | n_galaxies | scenario |
|---|---|---|---|---|---|---|
| C | seeing_minus_GLAO_native_dusty_error | 0.2239 | 0.1526 | 0.2985 | 16 | nan |
| R50 | seeing_minus_GLAO_native_dusty_error | 0.0642 | 0.0398 | 0.0890 | 16 | nan |
| dC_Ks | uncorrected_minus_corrected_native_clear_error | 0.1516 | 0.0836 | 0.2305 | 16 | GLAO_NIR |
| dC_Ks | uncorrected_minus_corrected_native_clear_error | 0.1270 | 0.0740 | 0.1736 | 16 | optical |
| dC_Ks | uncorrected_minus_corrected_native_clear_error | 0.1509 | 0.0868 | 0.2267 | 16 | seeing_NIR |
| dR50_Ks | uncorrected_minus_corrected_native_clear_error | 0.1464 | 0.0817 | 0.2222 | 16 | GLAO_NIR |
| dR50_Ks | uncorrected_minus_corrected_native_clear_error | 0.1113 | 0.0819 | 0.1356 | 16 | optical |
| dR50_Ks | uncorrected_minus_corrected_native_clear_error | 0.1773 | 0.1062 | 0.2591 | 16 | seeing_NIR |
| dC_Ks | seeing_minus_GLAO_corrected_native_clear_error | 0.2247 | 0.1430 | 0.3124 | 16 | nan |
| dR50_Ks | seeing_minus_GLAO_corrected_native_clear_error | 0.0349 | 0.0091 | 0.0633 | 16 | nan |

Native-dusty R50 transfer improves by0.0642kpc [0.0398,0.0890]; after the frozen learned dust correction, native-clear R50 error improves by0.0349kpc [0.0091,0.0633]. These are resolution/morphology benefits, while the dust-bias prediction gain itself remains consistent with zero. This distinction is central to the instrument interpretation.

**Learning from more independent galaxies:** three-seed mean validation MAE at12 and74 development objects:

| scenario | target | n_training_galaxies | MAE |
|---|---|---|---|
| GLAO_NIR | A_g | 12 | 0.1087 |
| GLAO_NIR | A_g | 74 | 0.0561 |
| GLAO_NIR | dC_Ks | 12 | 0.1780 |
| GLAO_NIR | dC_Ks | 74 | 0.0725 |
| GLAO_NIR | dR50_Ks | 12 | 0.1408 |
| GLAO_NIR | dR50_Ks | 74 | 0.0651 |
| seeing_NIR | A_g | 12 | 0.1204 |
| seeing_NIR | A_g | 74 | 0.0592 |
| seeing_NIR | dC_Ks | 12 | 0.2030 |
| seeing_NIR | dC_Ks | 74 | 0.0775 |
| seeing_NIR | dR50_Ks | 12 | 0.1356 |
| seeing_NIR | dR50_Ks | 74 | 0.0644 |

The trend motivates more calibrated training data, but does not remove source bias or prove a universal learning law. **Final source-control behavior:**

| target | n_galaxies | operational_MAE | signed_mean_prediction | mean_atlas_contrast |
|---|---|---|---|---|
| A_g | 4 | 0.0789 | 0.1992 | 0.1207 |
| A_g_IQR_1kpc | 4 | 0.0195 | 0.0270 | 0.0075 |
| A_g_p50_1kpc | 4 | 0.0036 | 0.1081 | 0.1111 |
| dC_Ks | 4 | 0.0845 | 0.0182 | -0.0327 |
| dR50_Ks | 4 | 0.0384 | -0.0249 | 0.0119 |

For the four final zero-projected-dust source controls, the mean predicted g contrast≈0.199mag exceeds their mean atlas contrast≈0.121mag. These failures are preserved rather than trained away. Their spatial median can be predicted accurately as an operator contrast without establishing physical attenuation. Exact-zero projected fields are a challenge/control condition, not verified full three-dimensional absence of all attenuation processes. `observable_OOD_summary.csv` gives exploratory training-distance strata, with a95th-percentile nearest-neighbor threshold determined only from development features; this post-evaluation diagnostic does not change models, calibration or primary performance.

The spatial-target scatter figure explicitly shows regression toward typical values and failure on highly attenuated/inhomogeneous views. The development spatial median range ends at0.977mag, versus a final maximum1.329mag; the IQR maximum is0.815mag in development versus1.544mag in final. Tree regressors cannot extrapolate the training target range, and the features may remain degenerate even with more data. These truth-range diagnostics (`target_range_diagnostics.csv`) are post-evaluation explanations, not observationally available OOD flags or a reason to exclude difficult final cases. Empirical HAWK-I ellipticity and full field-dependent PSF variation have not been propagated; the current wing stress uses circular kernels. These remain additional instrumental-transfer requirements.

## Publication assessment and literature

A workshop presentation is supported by the executed grouped benchmark, transparent source-control failure, comparison with photometric baselines, native-morphology correction and conditional resolution tests. Strong figures are `model_and_observing_strategy_comparison`, `paired_GLAO_gains`, `learning_curves`, `aperture_target_sensitivity`, and the predeclared lowest/median/highest-error galaxy examples. Include negative/no-gain targets and the source-label caveat on the main results slides.

A dedicated paper is **not yet a validated physical-dust or universal ULTIMATE performance demonstration**. The immediate gate is obtaining historical DR1 simulation/filter configuration or corrected matched products and demonstrating calibrated zero-dust/positive-dust labels. Additional requirements: propagate centroid/segmentation/background uncertainty; verify spectral/observer-frame transformations and instrument throughput/PSF/noise with current design information; test independent simulations/observations and realistic population/redshift selection; assess robustness with more independent calibration/test galaxies. This final20 has been spent once and must not become a tuning set; future revisions need a new independent holdout or a clearly labelled post-test study. HAWK-I constrains instrumental nuisance experiments only.

[Fu et al.2025](https://academic.oup.com/mnras/article/540/3/2081/8140852) already predicts attenuation from simulated high-redshift JWST images. The closest verified resolved-dust mapping reference is [Dobbels & Baes2021](https://arxiv.org/abs/2110.01704), A&A655A34; the requested2022 item was not uniquely identified and should not be silently misdated. [Bokona Tulu et al.2026](https://arxiv.org/html/2605.20886v1) directly studies dust/wavelength morphology using the same1154-galaxy atlas. [Baes et al.2024 methodology](https://arxiv.org/html/2401.04224v1) and [effective-radii work](https://arxiv.org/abs/2401.04225) constrain interpretation. [DeepMergeII](https://arxiv.org/abs/2103.01373) illustrates the separate simulation-to-observation transfer problem. The defensible novelty here is calibrated, grouped **incremental NIR-resolution value**, observable-only morphology-bias correction and explicit failure/control accounting, rather than first dust ML or unique3D geometry recovery. See `label_audit/literature_context.md` for source details.
